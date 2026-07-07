#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solux Welcome — Asistente de bienvenida de Solux OS
© 2026 Pollocrudo Company. Licencia GPLv3.

Se abre en el primer arranque para guiar la configuración inicial: presentación del
sistema, primeros pasos de seguridad, accesos directos a las apps propias y enlaces
útiles. Ofrece un interruptor para no volver a mostrarlo.
"""

import os
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

AUTOSTART_FLAG = os.path.expanduser("~/.config/solux/welcome-disabled")

CSS = b"""
window { background-color: #0D0D1A; color: #F1F5F9; }
.hero { background: linear-gradient(120deg, #F97316, #3B82F6); padding: 28px; border-radius: 0; }
.hero-title { font-size: 30px; font-weight: 800; color: #0D0D1A; }
.hero-sub { font-size: 15px; color: #0D0D1A; }
.card { background-color: #15152A; border: 1px solid #2A2A4A; border-radius: 12px; padding: 18px; }
.card:hover { border-color: #F97316; }
.card-title { font-size: 16px; font-weight: 700; color: #F97316; }
.card-desc { color: #94A3B8; }
.link-btn { background: #1E1E38; color: #22D3EE; border-radius: 8px; border: 1px solid #2A2A4A; padding: 6px 12px; }
.foot { color: #64748B; font-size: 12px; }
"""

CARDS = [
    ("security-high", "Revisa tu seguridad",
     "Abre el Centro de Seguridad para verificar firewall, antivirus e integridad.",
     "solux-security-center"),
    ("system-software-install", "Instala aplicaciones",
     "Explora miles de apps open source y el arsenal de Kali en la Solux Store.",
     "solux-store"),
    ("preferences-desktop", "Personaliza el escritorio",
     "Cambia fondos, temas y paneles a tu gusto desde los ajustes de XFCE.",
     "xfce4-settings-manager"),
    ("system-software-update", "Mantén el sistema al día",
     "Solux OS aplica actualizaciones de seguridad automáticamente. Puedes forzarlas.",
     None),
]


class Welcome(Gtk.Window):
    def __init__(self):
        super().__init__(title="Bienvenido a Solux OS")
        self.set_default_size(760, 620)
        self.set_icon_name("solux-welcome")
        self.set_position(Gtk.WindowPosition.CENTER)
        self._css()

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)

        # Hero
        hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hero.get_style_context().add_class("hero")
        t = Gtk.Label(label="Bienvenido a Solux OS", xalign=0)
        t.get_style_context().add_class("hero-title")
        s = Gtk.Label(label="Seguridad que renace contigo — 1.0 \"Phoenix\"", xalign=0)
        s.get_style_context().add_class("hero-sub")
        hero.pack_start(t, False, False, 0)
        hero.pack_start(s, False, False, 0)
        outer.pack_start(hero, False, False, 0)

        # Cards grid
        grid = Gtk.FlowBox()
        grid.set_valign(Gtk.Align.START)
        grid.set_max_children_per_line(2)
        grid.set_selection_mode(Gtk.SelectionMode.NONE)
        grid.set_row_spacing(14); grid.set_column_spacing(14)
        grid.set_margin_top(20); grid.set_margin_bottom(10)
        grid.set_margin_start(20); grid.set_margin_end(20)
        for icon, title, desc, launch in CARDS:
            grid.add(self._card(icon, title, desc, launch))
        outer.pack_start(grid, True, True, 0)

        # Footer
        foot = Gtk.Box(spacing=10)
        foot.set_margin_start(20); foot.set_margin_end(20); foot.set_margin_bottom(16)
        self.chk = Gtk.CheckButton(label="No mostrar esto al iniciar")
        self.chk.set_active(os.path.exists(AUTOSTART_FLAG))
        self.chk.connect("toggled", self._toggle_autostart)
        foot.pack_start(self.chk, True, True, 0)

        docs = Gtk.Button(label="Documentación")
        docs.get_style_context().add_class("link-btn")
        docs.connect("clicked", lambda _b: self._open_url("https://pollocrudo.example/solux-os/docs"))
        foot.pack_end(docs, False, False, 0)

        close = Gtk.Button(label="Empezar")
        close.get_style_context().add_class("link-btn")
        close.connect("clicked", lambda _b: self.close())
        foot.pack_end(close, False, False, 0)
        outer.pack_start(foot, False, False, 0)

        credit = Gtk.Label(label="© 2026 Pollocrudo Company — Solux OS", xalign=0.5)
        credit.get_style_context().add_class("foot")
        credit.set_margin_bottom(10)
        outer.pack_start(credit, False, False, 0)

    def _css(self):
        prov = Gtk.CssProvider(); prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _card(self, icon, title, desc, launch):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.get_style_context().add_class("card")
        card.set_size_request(330, -1)
        img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DND)
        head = Gtk.Box(spacing=10)
        head.pack_start(img, False, False, 0)
        lbl = Gtk.Label(label=title, xalign=0); lbl.get_style_context().add_class("card-title")
        head.pack_start(lbl, True, True, 0)
        card.pack_start(head, False, False, 0)
        d = Gtk.Label(label=desc, xalign=0, wrap=True); d.get_style_context().add_class("card-desc")
        card.pack_start(d, False, False, 0)
        if launch:
            btn = Gtk.Button(label="Abrir")
            btn.get_style_context().add_class("link-btn")
            btn.connect("clicked", lambda _b, cmd=launch: self._launch(cmd))
            box = Gtk.Box(); box.pack_end(btn, False, False, 0)
            card.pack_start(box, False, False, 0)
        return card

    def _launch(self, cmd):
        try:
            subprocess.Popen([cmd])
        except FileNotFoundError:
            dlg = Gtk.MessageDialog(
                transient_for=self, modal=True, message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=f"'{cmd}' no está disponible en este entorno.")
            dlg.run(); dlg.destroy()

    def _open_url(self, url):
        try:
            subprocess.Popen(["xdg-open", url])
        except FileNotFoundError:
            pass

    def _toggle_autostart(self, chk):
        os.makedirs(os.path.dirname(AUTOSTART_FLAG), exist_ok=True)
        if chk.get_active():
            open(AUTOSTART_FLAG, "w").close()
        elif os.path.exists(AUTOSTART_FLAG):
            os.remove(AUTOSTART_FLAG)


def main():
    win = Welcome()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
