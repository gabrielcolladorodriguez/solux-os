#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solux Browser — Navegador de Solux OS
© 2026 Pollocrudo Company. Licencia GPLv3.

Navegador con pestañas construido sobre WebKit2GTK (el mismo motor libre que usan
GNOME Web o Epiphany). El motor de render es WebKit (open source); la aplicación, la
marca, la interfaz y las funciones son propias de Solux OS.

Características:
  • Pestañas, navegación (atrás/adelante/recargar), barra de direcciones inteligente.
  • Búsqueda con DuckDuckGo (privacidad) si no escribes una URL.
  • Modo privado (ventana efímera, sin historial ni cookies persistentes).
  • DNT activado, sin telemetría, tema oscuro Solux.
"""

import sys
import gi

gi.require_version("Gtk", "3.0")
try:
    gi.require_version("WebKit2", "4.1")
except ValueError:  # respaldo para sistemas con 4.0
    gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, Gdk, WebKit2, GLib, Pango  # noqa: E402

HOME_URL = "https://duckduckgo.com/"
SEARCH = "https://duckduckgo.com/?q=%s"

CSS = b"""
window { background-color: #0D0D1A; }
headerbar, .titlebar { background: linear-gradient(#1E1E38, #15152A); border-bottom: 1px solid #2A2A4A; }
.nav-btn { background: #1E1E38; color: #F1F5F9; border: 1px solid #2A2A4A; border-radius: 8px; min-width: 32px; min-height: 30px; }
.nav-btn:hover { border-color: #F97316; }
.url-entry { background: #0D0D1A; color: #F1F5F9; border: 1px solid #2A2A4A; border-radius: 16px; padding: 4px 14px; caret-color: #F97316; }
.url-entry:focus { border-color: #F97316; box-shadow: 0 0 0 2px rgba(249,115,22,.3); }
.brand { color: #F97316; font-weight: 800; padding: 0 8px; }
.priv { color: #22D3EE; font-weight: 700; }
notebook header { background: #15152A; }
notebook tab { background: #15152A; color: #94A3B8; padding: 4px 8px; border: none; }
notebook tab:checked { color: #F97316; box-shadow: inset 0 -3px #F97316; }
.newtab { background: #1E1E38; color: #FBBF24; border-radius: 8px; }
"""


class Tab(Gtk.Box):
    def __init__(self, browser, url=None, ephemeral=False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.browser = browser
        if ephemeral:
            ctx = WebKit2.WebContext.new_ephemeral()
            self.webview = WebKit2.WebView.new_with_context(ctx)
        else:
            self.webview = WebKit2.WebView()

        settings = self.webview.get_settings()
        settings.set_enable_developer_extras(True)
        settings.set_property("enable-dns-prefetching", False)
        try:
            settings.set_property("enable-do-not-track", True)
        except TypeError:
            pass
        settings.set_user_agent_with_application_details("SoluxBrowser", "1.0")

        self.webview.connect("notify::title", self._on_title)
        self.webview.connect("notify::estimated-load-progress", self._on_progress)
        self.webview.connect("notify::uri", self._on_uri)
        self.pack_start(self.webview, True, True, 0)

        # Pestaña con título + botón cerrar
        self.label = Gtk.Label(label="Nueva pestaña")
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_max_width_chars(18)
        self.tab_widget = Gtk.Box(spacing=6)
        self.tab_widget.pack_start(self.label, True, True, 0)
        close = Gtk.Button.new_from_icon_name("window-close", Gtk.IconSize.MENU)
        close.set_relief(Gtk.ReliefStyle.NONE)
        close.connect("clicked", lambda _b: self.browser.close_tab(self))
        self.tab_widget.pack_end(close, False, False, 0)
        self.tab_widget.show_all()

        self.webview.load_uri(url or HOME_URL)

    def _on_title(self, *_):
        t = self.webview.get_title() or "Solux"
        self.label.set_text(t)
        if self.browser.current_tab() is self:
            self.browser.set_title(f"{t} — Solux Browser")

    def _on_uri(self, *_):
        if self.browser.current_tab() is self:
            self.browser.url_entry.set_text(self.webview.get_uri() or "")

    def _on_progress(self, *_):
        if self.browser.current_tab() is self:
            p = self.webview.get_estimated_load_progress()
            self.browser.url_entry.set_progress_fraction(0 if p >= 1.0 else p)


class SoluxBrowser(Gtk.Window):
    def __init__(self, ephemeral=False):
        super().__init__(title="Solux Browser")
        self.set_default_size(1180, 760)
        self.set_icon_name("solux-browser")
        self.ephemeral = ephemeral
        self._css()

        # Header
        hb = Gtk.HeaderBar(show_close_button=True)
        self.set_titlebar(hb)

        brand = Gtk.Label()
        brand.set_markup('<span foreground="#F97316" weight="800">☀ Solux</span>')
        hb.pack_start(brand)

        for icon, cb in [("go-previous-symbolic", self.go_back),
                         ("go-next-symbolic", self.go_forward),
                         ("view-refresh-symbolic", self.reload)]:
            b = Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
            b.get_style_context().add_class("nav-btn")
            b.connect("clicked", cb)
            hb.pack_start(b)

        self.url_entry = Gtk.Entry()
        self.url_entry.get_style_context().add_class("url-entry")
        self.url_entry.set_placeholder_text("Busca en DuckDuckGo o escribe una dirección…")
        self.url_entry.set_width_chars(60)
        self.url_entry.connect("activate", self.on_go)
        hb.set_custom_title(self.url_entry)

        newt = Gtk.Button.new_from_icon_name("tab-new-symbolic", Gtk.IconSize.BUTTON)
        newt.get_style_context().add_class("newtab")
        newt.connect("clicked", lambda _b: self.new_tab())
        hb.pack_end(newt)

        if ephemeral:
            priv = Gtk.Label()
            priv.set_markup('<span foreground="#22D3EE" weight="700">Privado</span>')
            hb.pack_end(priv)

        menu_btn = Gtk.MenuButton()
        menu_btn.set_image(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
        menu_btn.get_style_context().add_class("nav-btn")
        menu_btn.set_popover(self._menu())
        hb.pack_end(menu_btn)

        # Notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.connect("switch-page", self._on_switch)
        self.add(self.notebook)

        self.new_tab()

    def _css(self):
        p = Gtk.CssProvider(); p.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _menu(self):
        pop = Gtk.Popover()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_top(8); box.set_margin_bottom(8)
        box.set_margin_start(8); box.set_margin_end(8)
        for label, cb in [
            ("Nueva pestaña", lambda _b: self.new_tab()),
            ("Nueva ventana privada", lambda _b: SoluxBrowser(ephemeral=True).show_all()),
            ("Inicio", lambda _b: self._load(HOME_URL)),
            ("Solux Store", lambda _b: self._launch("solux-store")),
            ("Centro de Seguridad", lambda _b: self._launch("solux-security-center")),
        ]:
            btn = Gtk.ModelButton(text=label)
            btn.connect("clicked", cb)
            box.pack_start(btn, False, False, 0)
        box.show_all()
        pop.add(box)
        return pop

    # --- tabs ---
    def new_tab(self, url=None):
        tab = Tab(self, url=url, ephemeral=self.ephemeral)
        idx = self.notebook.append_page(tab, tab.tab_widget)
        self.notebook.set_tab_reorderable(tab, True)
        self.show_all()
        self.notebook.set_current_page(idx)
        self.url_entry.grab_focus()
        return tab

    def close_tab(self, tab):
        if self.notebook.get_n_pages() <= 1:
            self.close()
            return
        self.notebook.remove_page(self.notebook.page_num(tab))

    def current_tab(self):
        pg = self.notebook.get_current_page()
        return self.notebook.get_nth_page(pg) if pg >= 0 else None

    def _on_switch(self, _nb, page, _num):
        GLib.idle_add(self.url_entry.set_text, page.webview.get_uri() or "")

    # --- navigation ---
    def on_go(self, _entry):
        text = self.url_entry.get_text().strip()
        if not text:
            return
        if " " in text or "." not in text:
            uri = SEARCH % GLib.uri_escape_string(text, None, True)
        elif "://" not in text:
            uri = "https://" + text
        else:
            uri = text
        self._load(uri)

    def _load(self, uri):
        t = self.current_tab()
        if t:
            t.webview.load_uri(uri)

    def go_back(self, _b):
        t = self.current_tab()
        if t and t.webview.can_go_back():
            t.webview.go_back()

    def go_forward(self, _b):
        t = self.current_tab()
        if t and t.webview.can_go_forward():
            t.webview.go_forward()

    def reload(self, _b):
        t = self.current_tab()
        if t:
            t.webview.reload()

    def _launch(self, cmd):
        import shutil, subprocess
        if shutil.which(cmd):
            subprocess.Popen([cmd])


def main():
    ephemeral = "--private" in sys.argv or "-p" in sys.argv
    win = SoluxBrowser(ephemeral=ephemeral)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
