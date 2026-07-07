#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solux Store — Tienda de aplicaciones de Solux OS
© 2026 Pollocrudo Company. Licencia GPLv3.

Frontend gráfico (GTK3) sobre APT y Flatpak. Lee el catálogo de `catalog.json`,
muestra las apps por categoría y permite instalar/desinstalar con privilegios vía
pkexec. Incluye el arsenal completo de Kali clasificado por disciplina.
"""

import json
import os
import shutil
import subprocess
import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk, Pango

APP_ID = "com.pollocrudo.SoluxStore"
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(DATA_DIR, "catalog.json")

CSS = b"""
window { background-color: #0D0D1A; color: #F1F5F9; }
.sidebar { background-color: #15152A; }
.sidebar row { padding: 10px 14px; border-radius: 8px; }
.sidebar row:selected { background-color: #F97316; color: #0D0D1A; }
.hero { background: linear-gradient(90deg, #F97316, #3B82F6); padding: 22px; border-radius: 14px; }
.hero-title { font-size: 22px; font-weight: 800; color: #0D0D1A; }
.hero-sub { color: #0D0D1A; }
.app-card { background-color: #15152A; border: 1px solid #2A2A4A; border-radius: 12px; padding: 14px; }
.app-card:hover { border-color: #F97316; }
.app-name { font-weight: 700; font-size: 15px; }
.app-desc { color: #94A3B8; }
.pill { background-color: #1E1E38; color: #22D3EE; border-radius: 10px; padding: 2px 8px; font-size: 11px; }
.install-btn { background: linear-gradient(#FBBF24, #F97316); color: #0D0D1A; font-weight: 700; border-radius: 8px; border: none; padding: 6px 14px; }
.remove-btn { background-color: #EF4444; color: #0D0D1A; font-weight: 700; border-radius: 8px; border: none; padding: 6px 14px; }
.search-entry { background-color: #0D0D1A; border: 1px solid #2A2A4A; border-radius: 10px; padding: 6px 10px; }
.section-title { font-size: 18px; font-weight: 800; color: #F97316; }
.subsection-title { font-size: 14px; font-weight: 700; color: #3B82F6; margin-top: 8px; }
"""


def load_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def is_installed(app):
    """Comprueba si un paquete ya está instalado (apt o flatpak)."""
    backend = app.get("backend", "apt")
    pkg = app["pkg"]
    try:
        if backend == "apt":
            out = subprocess.run(
                ["dpkg-query", "-W", "-f=${Status}", pkg],
                capture_output=True, text=True, timeout=5)
            return "install ok installed" in out.stdout
        elif backend == "flatpak":
            out = subprocess.run(
                ["flatpak", "info", pkg],
                capture_output=True, text=True, timeout=5)
            return out.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
    return False


def install_cmd(app):
    backend = app.get("backend", "apt")
    if backend == "apt":
        return ["pkexec", "apt-get", "install", "-y", app["pkg"]]
    return ["flatpak", "install", "-y", "flathub", app["pkg"]]


def remove_cmd(app):
    backend = app.get("backend", "apt")
    if backend == "apt":
        return ["pkexec", "apt-get", "remove", "-y", app["pkg"]]
    return ["flatpak", "uninstall", "-y", app["pkg"]]


class AppCard(Gtk.Box):
    """Tarjeta de una aplicación con botón instalar/quitar."""

    def __init__(self, app, on_action):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.app = app
        self.on_action = on_action
        self.get_style_context().add_class("app-card")

        icon = Gtk.Image.new_from_icon_name("package-x-generic", Gtk.IconSize.DIALOG)
        self.pack_start(icon, False, False, 0)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        name = Gtk.Label(label=app["name"], xalign=0)
        name.get_style_context().add_class("app-name")
        desc = Gtk.Label(label=app.get("desc", ""), xalign=0)
        desc.get_style_context().add_class("app-desc")
        desc.set_line_wrap(True)
        desc.set_max_width_chars(60)

        pill = Gtk.Label(label=app.get("backend", "apt").upper())
        pill.get_style_context().add_class("pill")
        pill_box = Gtk.Box()
        pill_box.pack_start(pill, False, False, 0)

        info.pack_start(name, False, False, 0)
        info.pack_start(desc, False, False, 0)
        info.pack_start(pill_box, False, False, 0)
        self.pack_start(info, True, True, 0)

        self.btn = Gtk.Button()
        self.btn.connect("clicked", self._clicked)
        self.pack_end(self.btn, False, False, 0)
        self.spinner = Gtk.Spinner()
        self.pack_end(self.spinner, False, False, 0)

        self.refresh_state()

    def refresh_state(self):
        def worker():
            installed = is_installed(self.app)
            GLib.idle_add(self._apply_state, installed)
        threading.Thread(target=worker, daemon=True).start()

    def _apply_state(self, installed):
        self.installed = installed
        self.btn.set_label("Quitar" if installed else "Instalar")
        ctx = self.btn.get_style_context()
        ctx.remove_class("install-btn")
        ctx.remove_class("remove-btn")
        ctx.add_class("remove-btn" if installed else "install-btn")
        self.btn.set_sensitive(True)
        self.spinner.stop()
        return False

    def _clicked(self, _btn):
        self.btn.set_sensitive(False)
        self.spinner.start()
        self.on_action(self, self.app, getattr(self, "installed", False))


class SoluxStore(Gtk.Window):
    def __init__(self):
        super().__init__(title="Solux Store")
        self.set_default_size(1080, 720)
        self.set_icon_name("solux-store")
        self.catalog = load_catalog()

        self._apply_css()

        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(root)

        # ----- Sidebar -----
        sidebar = Gtk.ScrolledWindow()
        sidebar.set_size_request(240, -1)
        sidebar.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        self.listbox.get_style_context().add_class("sidebar")
        self.listbox.connect("row-selected", self._on_category_selected)
        sidebar.add(self.listbox)
        root.pack_start(sidebar, False, False, 0)

        header = Gtk.Label(label="  SOLUX STORE")
        header.set_xalign(0)
        header.get_style_context().add_class("section-title")
        hrow = Gtk.ListBoxRow()
        hrow.set_selectable(False)
        hrow.add(header)
        self.listbox.add(hrow)

        for cat in self.catalog["categories"]:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(spacing=8)
            box.pack_start(Gtk.Image.new_from_icon_name(cat.get("icon", "folder"), Gtk.IconSize.MENU), False, False, 0)
            box.pack_start(Gtk.Label(label=cat["name"], xalign=0), True, True, 0)
            row.add(box)
            row.category = cat
            self.listbox.add(row)

        # ----- Main area -----
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main.set_margin_top(16); main.set_margin_bottom(16)
        main.set_margin_start(16); main.set_margin_end(16)
        root.pack_start(main, True, True, 0)

        # Search
        self.search = Gtk.SearchEntry()
        self.search.get_style_context().add_class("search-entry")
        self.search.set_placeholder_text("Buscar entre miles de aplicaciones...")
        self.search.connect("search-changed", self._on_search)
        main.pack_start(self.search, False, False, 0)

        self.scroller = Gtk.ScrolledWindow()
        self.scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.scroller.add(self.content)
        main.pack_start(self.scroller, True, True, 0)

        # Status bar
        self.status = Gtk.Label(label="Listo.", xalign=0)
        self.status.get_style_context().add_class("app-desc")
        main.pack_start(self.status, False, False, 0)

        self.show_all()
        # Select first category
        first = self.listbox.get_row_at_index(1)
        if first:
            self.listbox.select_row(first)

    def _apply_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _clear_content(self):
        for child in self.content.get_children():
            self.content.remove(child)

    def _hero(self, title, subtitle):
        hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        hero.get_style_context().add_class("hero")
        t = Gtk.Label(label=title, xalign=0)
        t.get_style_context().add_class("hero-title")
        s = Gtk.Label(label=subtitle, xalign=0)
        s.get_style_context().add_class("hero-sub")
        s.set_line_wrap(True)
        hero.pack_start(t, False, False, 0)
        hero.pack_start(s, False, False, 0)
        return hero

    def _on_category_selected(self, _lb, row):
        if row is None or not hasattr(row, "category"):
            return
        self.search.set_text("")
        cat = row.category
        self._clear_content()
        self.content.pack_start(
            self._hero(cat["name"], cat.get("description", "")), False, False, 0)

        if "subcategories" in cat:
            for sub in cat["subcategories"]:
                lbl = Gtk.Label(label=sub["name"], xalign=0)
                lbl.get_style_context().add_class("subsection-title")
                self.content.pack_start(lbl, False, False, 0)
                for app in sub["apps"]:
                    self.content.pack_start(AppCard(app, self._do_action), False, False, 0)
        else:
            for app in cat.get("apps", []):
                self.content.pack_start(AppCard(app, self._do_action), False, False, 0)

        self.content.show_all()

    def _iter_all_apps(self):
        for cat in self.catalog["categories"]:
            if "subcategories" in cat:
                for sub in cat["subcategories"]:
                    for app in sub["apps"]:
                        yield app
            for app in cat.get("apps", []):
                yield app

    def _on_search(self, entry):
        query = entry.get_text().strip().lower()
        if not query:
            sel = self.listbox.get_selected_row()
            if sel:
                self._on_category_selected(None, sel)
            return
        self._clear_content()
        self.content.pack_start(
            self._hero("Resultados de búsqueda", f'Coincidencias para "{query}"'), False, False, 0)
        count = 0
        for app in self._iter_all_apps():
            if query in app["name"].lower() or query in app.get("desc", "").lower():
                self.content.pack_start(AppCard(app, self._do_action), False, False, 0)
                count += 1
        if count == 0:
            self.content.pack_start(Gtk.Label(label="Sin resultados."), False, False, 0)
        self.content.show_all()

    def _do_action(self, card, app, installed):
        cmd = remove_cmd(app) if installed else install_cmd(app)
        verb = "Desinstalando" if installed else "Instalando"
        self.status.set_text(f"{verb} {app['name']}...")

        def worker():
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True)
                ok = proc.returncode == 0
                msg = f"{app['name']}: {'hecho' if ok else 'error'}"
            except Exception as exc:  # noqa: BLE001
                msg = f"{app['name']}: {exc}"
            GLib.idle_add(self.status.set_text, msg)
            GLib.idle_add(card.refresh_state)
        threading.Thread(target=worker, daemon=True).start()


def main():
    if not shutil.which("pkexec"):
        print("Advertencia: pkexec no encontrado; la instalación necesitará privilegios.")
    win = SoluxStore()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()


if __name__ == "__main__":
    main()
