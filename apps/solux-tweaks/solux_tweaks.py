#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solux Tweaks — Ajustes rápidos de Solux OS
© 2026 Pollocrudo Company. Licencia GPLv3.

Panel ligero (GTK3) para adaptar el equilibrio entre comodidad diaria y seguridad, y
para aplicar retoques habituales sin abrir un terminal. Une los dos usos de Solux OS:
escritorio cómodo (como cualquier distro) y estación de seguridad (como Kali).

Dos "perfiles" de uso:
  • Modo Diario     — usabilidad primero (firewall activo pero permisivo saliente).
  • Modo Seguridad  — máximo blindaje (bloqueos estrictos, servicios sensibles apagados).

Las acciones con privilegios usan pkexec; las de usuario se aplican directamente.
"""

import os
import shutil
import subprocess
import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

CSS = b"""
window { background-color: #0D0D1A; color: #F1F5F9; }
.title { font-size: 22px; font-weight: 800; color: #F97316; }
.subtitle { color: #94A3B8; }
.card { background-color: #15152A; border: 1px solid #2A2A4A; border-radius: 12px; padding: 16px; }
.card-title { font-size: 15px; font-weight: 700; color: #3B82F6; }
.mode-daily { background: linear-gradient(#FBBF24, #F97316); color: #0D0D1A; font-weight: 800; border-radius: 10px; border: none; padding: 12px; }
.mode-secure { background: linear-gradient(#3B82F6, #22D3EE); color: #0D0D1A; font-weight: 800; border-radius: 10px; border: none; padding: 12px; }
.desc { color: #94A3B8; }
.status { font-family: 'JetBrains Mono', monospace; color: #22D3EE; font-size: 12px; }
"""


def run(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except FileNotFoundError:
        return 127, "no disponible"
    except Exception as exc:  # noqa: BLE001
        return 1, str(exc)


class Tweaks(Gtk.Window):
    def __init__(self):
        super().__init__(title="Solux Tweaks")
        self.set_default_size(620, 720)
        self.set_icon_name("preferences-system")
        self._css()

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(scroller)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_top(20); box.set_margin_bottom(20)
        box.set_margin_start(22); box.set_margin_end(22)
        scroller.add(box)

        title = Gtk.Label(label="Solux Tweaks", xalign=0); title.get_style_context().add_class("title")
        sub = Gtk.Label(label="Equilibra comodidad y seguridad, y aplica retoques rápidos.", xalign=0)
        sub.get_style_context().add_class("subtitle")
        box.pack_start(title, False, False, 0)
        box.pack_start(sub, False, False, 0)

        self.status = Gtk.Label(label="", xalign=0)
        self.status.get_style_context().add_class("status")
        self.status.set_line_wrap(True)

        # --- Perfiles de uso ---
        modes = self._card(box, "Perfil de uso")
        row = Gtk.Box(spacing=12, homogeneous=True)
        daily = Gtk.Button(label="Modo Diario")
        daily.get_style_context().add_class("mode-daily")
        daily.connect("clicked", lambda _b: self._apply_mode("daily"))
        secure = Gtk.Button(label="Modo Seguridad")
        secure.get_style_context().add_class("mode-secure")
        secure.connect("clicked", lambda _b: self._apply_mode("secure"))
        row.pack_start(daily, True, True, 0)
        row.pack_start(secure, True, True, 0)
        modes.pack_start(row, False, False, 0)
        modes.pack_start(Gtk.Label(
            label="Diario: firewall permisivo saliente, cómodo. "
                  "Seguridad: bloqueo estricto y servicios sensibles apagados.",
            xalign=0, wrap=True), False, False, 0)

        # --- Retoques rápidos (interruptores) ---
        toggles = self._card(box, "Retoques rápidos")
        self._switch(toggles, "Firewall (UFW) activo",
                     check=lambda: run(["systemctl", "is-active", "--quiet", "ufw"])[0] == 0,
                     on=["pkexec", "ufw", "--force", "enable"],
                     off=["pkexec", "ufw", "disable"])
        self._switch(toggles, "Modo no molestar (silenciar notificaciones)",
                     check=lambda: os.path.exists(os.path.expanduser("~/.config/solux/dnd")),
                     on=self._dnd_on, off=self._dnd_off, user=True)
        self._switch(toggles, "Aleatorización de MAC al conectar",
                     check=lambda: os.path.exists("/etc/NetworkManager/conf.d/00-macrandomize.conf"),
                     on=None, off=None, readonly=True)

        # --- Mantenimiento ---
        maint = self._card(box, "Mantenimiento")
        self._action(maint, "Actualizar el sistema", ["pkexec", "apt-get", "update"])
        self._action(maint, "Limpiar paquetes huérfanos", ["pkexec", "apt-get", "autoremove", "-y"])
        self._action(maint, "Vaciar caché de APT", ["pkexec", "apt-get", "clean"])
        self._action(maint, "Liberar espacio (journald 100M)",
                     ["pkexec", "journalctl", "--vacuum-size=100M"])

        # --- Apariencia ---
        appearance = self._card(box, "Apariencia")
        wall = Gtk.Button(label="Cambiar fondo de pantalla")
        wall.connect("clicked", lambda _b: self._launch("nitrogen") or self._launch("xfdesktop-settings"))
        appearance.pack_start(wall, False, False, 0)
        settings = Gtk.Button(label="Abrir ajustes de XFCE")
        settings.connect("clicked", lambda _b: self._launch("xfce4-settings-manager"))
        appearance.pack_start(settings, False, False, 0)

        box.pack_start(self.status, False, False, 0)

    # ---- infra ----
    def _css(self):
        prov = Gtk.CssProvider(); prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _card(self, parent, title):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.get_style_context().add_class("card")
        lbl = Gtk.Label(label=title, xalign=0); lbl.get_style_context().add_class("card-title")
        card.pack_start(lbl, False, False, 0)
        parent.pack_start(card, False, False, 0)
        return card

    def _set_status(self, text):
        GLib.idle_add(self.status.set_text, text)

    def _switch(self, card, label, check, on, off, user=False, readonly=False):
        row = Gtk.Box(spacing=10)
        row.pack_start(Gtk.Label(label=label, xalign=0), True, True, 0)
        sw = Gtk.Switch()
        sw.set_sensitive(not readonly)
        row.pack_end(sw, False, False, 0)
        card.pack_start(row, False, False, 0)

        def load():
            state = bool(check())
            GLib.idle_add(_set, state)

        def _set(state):
            sw.set_active(state)
            if not readonly:
                sw.connect("notify::active", toggled)
            return False

        def toggled(switch, _p):
            want = switch.get_active()
            cmd = on if want else off
            if cmd is None:
                return
            self._set_status(f"Aplicando: {label}...")

            def worker():
                if callable(cmd):
                    cmd()
                    rc, out = 0, "hecho"
                else:
                    rc, out = run(cmd)
                self._set_status(f"{label}: {'ok' if rc == 0 else out}")
            threading.Thread(target=worker, daemon=True).start()

        threading.Thread(target=load, daemon=True).start()

    def _action(self, card, label, cmd):
        btn = Gtk.Button(label=label)
        btn.connect("clicked", lambda _b: self._run_async(label, cmd))
        card.pack_start(btn, False, False, 0)

    def _run_async(self, label, cmd):
        self._set_status(f"{label}...")
        def worker():
            rc, out = run(cmd, timeout=180)
            self._set_status(f"{label}: {'ok' if rc == 0 else out[-400:]}")
        threading.Thread(target=worker, daemon=True).start()

    def _apply_mode(self, mode):
        if mode == "daily":
            cmds = [
                ["pkexec", "ufw", "default", "allow", "outgoing"],
                ["pkexec", "ufw", "--force", "enable"],
            ]
            self._set_status("Modo Diario aplicado: firewall activo, salida permitida.")
        else:
            cmds = [
                ["pkexec", "ufw", "default", "deny", "incoming"],
                ["pkexec", "ufw", "--force", "enable"],
                ["pkexec", "systemctl", "restart", "fail2ban"],
            ]
            self._set_status("Modo Seguridad aplicado: bloqueo estricto de entrada.")

        def worker():
            for c in cmds:
                run(c)
        threading.Thread(target=worker, daemon=True).start()

    def _dnd_on(self):
        os.makedirs(os.path.expanduser("~/.config/solux"), exist_ok=True)
        open(os.path.expanduser("~/.config/solux/dnd"), "w").close()
        run(["xfconf-query", "-c", "xfce4-notifyd", "-p", "/do-not-disturb", "-s", "true", "--create", "-t", "bool"])

    def _dnd_off(self):
        p = os.path.expanduser("~/.config/solux/dnd")
        if os.path.exists(p):
            os.remove(p)
        run(["xfconf-query", "-c", "xfce4-notifyd", "-p", "/do-not-disturb", "-s", "false"])

    def _launch(self, cmd):
        if shutil.which(cmd):
            subprocess.Popen([cmd])
            return True
        return False


def main():
    win = Tweaks()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
