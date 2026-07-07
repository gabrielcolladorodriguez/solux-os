#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solux Security Center — Centro de seguridad de Solux OS
© 2026 Pollocrudo Company. Licencia GPLv3.

Panel de control (GTK3) con 10 secciones que consultan y accionan las herramientas de
seguridad del sistema: estado general, firewall, antivirus, integridad de ficheros,
amenazas, red, privacidad, actualizaciones, sandbox y auditoría.

Las comprobaciones se ejecutan en hilos para no bloquear la interfaz. Las acciones que
requieren privilegios usan `pkexec`.
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
.sidebar { background-color: #15152A; }
.sidebar row { padding: 12px 16px; }
.sidebar row:selected { background-color: #F97316; color: #0D0D1A; }
.title { font-size: 22px; font-weight: 800; color: #F97316; }
.subtitle { color: #94A3B8; }
.card { background-color: #15152A; border: 1px solid #2A2A4A; border-radius: 12px; padding: 16px; }
.stat-ok { color: #22C55E; font-weight: 700; }
.stat-warn { color: #F59E0B; font-weight: 700; }
.stat-bad { color: #EF4444; font-weight: 700; }
.stat-num { font-size: 30px; font-weight: 800; color: #F1F5F9; }
.action-btn { background: linear-gradient(#FBBF24, #F97316); color: #0D0D1A; font-weight: 700; border-radius: 8px; border: none; padding: 8px 16px; }
.mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #94A3B8; }
"""


def run(cmd, timeout=20):
    """Ejecuta un comando y devuelve (rc, salida)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except FileNotFoundError:
        return 127, "comando no disponible"
    except subprocess.TimeoutExpired:
        return 124, "tiempo agotado"
    except Exception as exc:  # noqa: BLE001
        return 1, str(exc)


def service_active(name):
    rc, _ = run(["systemctl", "is-active", "--quiet", name], timeout=5)
    return rc == 0


class Section:
    """Descriptor de una sección del centro de seguridad."""

    def __init__(self, key, title, icon, subtitle, builder):
        self.key = key
        self.title = title
        self.icon = icon
        self.subtitle = subtitle
        self.builder = builder


class SecurityCenter(Gtk.Window):
    def __init__(self):
        super().__init__(title="Solux Security Center")
        self.set_default_size(1080, 720)
        self.set_icon_name("solux-security-center")
        self._apply_css()

        self.sections = [
            Section("estado", "Estado general", "security-high",
                    "Vista rápida de la postura de seguridad", self.page_status),
            Section("firewall", "Firewall", "network-wired",
                    "nftables y UFW", self.page_firewall),
            Section("antivirus", "Antivirus", "security-medium",
                    "ClamAV: escaneo de malware", self.page_antivirus),
            Section("integridad", "Integridad de ficheros", "document-properties",
                    "AIDE: detección de cambios", self.page_integrity),
            Section("amenazas", "Amenazas", "dialog-warning",
                    "rkhunter y Fail2ban", self.page_threats),
            Section("red", "Red", "network-transmit-receive",
                    "Puertos, conexiones y MAC", self.page_network),
            Section("privacidad", "Privacidad", "view-private",
                    "DNS, telemetría y navegador", self.page_privacy),
            Section("updates", "Actualizaciones", "system-software-update",
                    "Parches de seguridad", self.page_updates),
            Section("sandbox", "Sandbox", "application-x-executable",
                    "AppArmor y Firejail", self.page_sandbox),
            Section("auditoria", "Auditoría", "utilities-terminal",
                    "Lynis: hardening del sistema", self.page_audit),
        ]

        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(root)

        # Sidebar
        sb = Gtk.ScrolledWindow(); sb.set_size_request(250, -1)
        sb.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        self.listbox.get_style_context().add_class("sidebar")
        self.listbox.connect("row-selected", self._on_select)
        sb.add(self.listbox)
        root.pack_start(sb, False, False, 0)

        header = Gtk.Label(label="  SECURITY CENTER", xalign=0)
        header.get_style_context().add_class("title")
        hr = Gtk.ListBoxRow(); hr.set_selectable(False); hr.add(header)
        self.listbox.add(hr)

        for sec in self.sections:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(spacing=10)
            box.pack_start(Gtk.Image.new_from_icon_name(sec.icon, Gtk.IconSize.LARGE_TOOLBAR), False, False, 0)
            box.pack_start(Gtk.Label(label=sec.title, xalign=0), True, True, 0)
            row.add(box); row.section = sec
            self.listbox.add(row)

        # Content
        self.stack = Gtk.ScrolledWindow()
        self.stack.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        root.pack_start(self.stack, True, True, 0)
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.container.set_margin_top(20); self.container.set_margin_bottom(20)
        self.container.set_margin_start(24); self.container.set_margin_end(24)
        self.stack.add(self.container)

        self.show_all()
        self.listbox.select_row(self.listbox.get_row_at_index(1))

    # ---- infra ----
    def _apply_css(self):
        prov = Gtk.CssProvider(); prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _clear(self):
        for c in self.container.get_children():
            self.container.remove(c)

    def _on_select(self, _lb, row):
        if row is None or not hasattr(row, "section"):
            return
        self._clear()
        sec = row.section
        title = Gtk.Label(label=sec.title, xalign=0); title.get_style_context().add_class("title")
        sub = Gtk.Label(label=sec.subtitle, xalign=0); sub.get_style_context().add_class("subtitle")
        self.container.pack_start(title, False, False, 0)
        self.container.pack_start(sub, False, False, 0)
        sec.builder()
        self.container.show_all()

    def _card(self, title):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.get_style_context().add_class("card")
        if title:
            lbl = Gtk.Label(label=title, xalign=0)
            lbl.set_markup(f"<b>{GLib.markup_escape_text(title)}</b>")
            card.pack_start(lbl, False, False, 0)
        self.container.pack_start(card, False, False, 0)
        return card

    def _status_row(self, card, label, checker):
        """Añade una fila con estado asíncrono. checker() -> (texto, clase)."""
        row = Gtk.Box(spacing=10)
        name = Gtk.Label(label=label, xalign=0)
        value = Gtk.Label(label="Comprobando...", xalign=1)
        spinner = Gtk.Spinner(); spinner.start()
        row.pack_start(name, True, True, 0)
        row.pack_end(value, False, False, 0)
        row.pack_end(spinner, False, False, 0)
        card.pack_start(row, False, False, 0)

        def worker():
            text, css_class = checker()
            GLib.idle_add(_apply, text, css_class)

        def _apply(text, css_class):
            spinner.stop(); spinner.hide()
            value.set_text(text)
            ctx = value.get_style_context()
            for c in ("stat-ok", "stat-warn", "stat-bad"):
                ctx.remove_class(c)
            ctx.add_class(css_class)
            return False

        threading.Thread(target=worker, daemon=True).start()

    def _action_button(self, card, label, cmd, needs_terminal=False):
        btn = Gtk.Button(label=label)
        btn.get_style_context().add_class("action-btn")
        output = Gtk.Label(xalign=0); output.get_style_context().add_class("mono")
        output.set_line_wrap(True); output.set_selectable(True)

        def clicked(_b):
            btn.set_sensitive(False)
            output.set_text("Ejecutando...")

            def worker():
                if needs_terminal and shutil.which("xfce4-terminal"):
                    run(["xfce4-terminal", "-e", " ".join(cmd)], timeout=5)
                    res = "Abierto en una terminal."
                else:
                    rc, out = run(cmd, timeout=120)
                    res = out[-1500:] if out else f"(código {rc})"
                GLib.idle_add(_done, res)

            def _done(res):
                output.set_text(res); btn.set_sensitive(True); return False
            threading.Thread(target=worker, daemon=True).start()

        btn.connect("clicked", clicked)
        card.pack_start(btn, False, False, 0)
        card.pack_start(output, False, False, 0)

    # ---- pages ----
    def page_status(self):
        card = self._card("Resumen de protección")
        self._status_row(card, "AppArmor",
            lambda: (("Activo (enforce)", "stat-ok") if run(["aa-status", "--enabled"])[0] == 0
                     else ("Inactivo", "stat-bad")))
        self._status_row(card, "Firewall UFW",
            lambda: (("Activo", "stat-ok") if service_active("ufw") else ("Inactivo", "stat-bad")))
        self._status_row(card, "Fail2ban",
            lambda: (("Activo", "stat-ok") if service_active("fail2ban") else ("Inactivo", "stat-warn")))
        self._status_row(card, "Antivirus ClamAV",
            lambda: (("Instalado", "stat-ok") if shutil.which("clamscan") else ("No instalado", "stat-warn")))
        self._status_row(card, "Actualizaciones automáticas",
            lambda: (("Activas", "stat-ok") if service_active("unattended-upgrades") else ("Inactivas", "stat-warn")))

        tip = self._card("Consejo")
        tip.pack_start(Gtk.Label(
            label="Solux OS aplica hardening estricto por defecto. Revisa cada sección para "
                  "verificar y accionar las defensas del sistema.",
            xalign=0, wrap=True), False, False, 0)

    def page_firewall(self):
        card = self._card("Estado del firewall")
        self._status_row(card, "UFW",
            lambda: (("Activo", "stat-ok") if service_active("ufw") else ("Inactivo", "stat-bad")))
        self._status_row(card, "nftables",
            lambda: (("Cargado", "stat-ok") if service_active("nftables") else ("Sin reglas", "stat-warn")))
        actions = self._card("Acciones")
        self._action_button(actions, "Ver reglas UFW", ["pkexec", "ufw", "status", "verbose"])
        self._action_button(actions, "Ver ruleset nftables", ["pkexec", "nft", "list", "ruleset"])

    def page_antivirus(self):
        card = self._card("ClamAV")
        self._status_row(card, "Motor instalado",
            lambda: (("Sí", "stat-ok") if shutil.which("clamscan") else ("No", "stat-bad")))
        self._status_row(card, "Base de firmas (freshclam)",
            lambda: (("Servicio activo", "stat-ok") if service_active("clamav-freshclam") else ("Detenido", "stat-warn")))
        actions = self._card("Escanear")
        self._action_button(actions, "Actualizar firmas", ["pkexec", "freshclam"])
        self._action_button(actions, "Escanear /home (rápido)", ["clamscan", "-r", "-i", os.path.expanduser("~")])

    def page_integrity(self):
        card = self._card("AIDE — Integridad de ficheros")
        self._status_row(card, "AIDE instalado",
            lambda: (("Sí", "stat-ok") if shutil.which("aide") else ("No", "stat-bad")))
        self._status_row(card, "Base de datos",
            lambda: (("Presente", "stat-ok") if os.path.exists("/var/lib/aide/aide.db")
                     else ("No inicializada", "stat-warn")))
        actions = self._card("Acciones")
        self._action_button(actions, "Comprobar integridad ahora", ["pkexec", "aide", "--check"])
        self._action_button(actions, "Reconstruir base de datos", ["pkexec", "aideinit"])

    def page_threats(self):
        card = self._card("Detección de amenazas")
        self._status_row(card, "rkhunter (rootkits)",
            lambda: (("Instalado", "stat-ok") if shutil.which("rkhunter") else ("No", "stat-warn")))
        self._status_row(card, "Fail2ban",
            lambda: (("Activo", "stat-ok") if service_active("fail2ban") else ("Inactivo", "stat-warn")))
        actions = self._card("Acciones")
        self._action_button(actions, "Buscar rootkits", ["pkexec", "rkhunter", "--check", "--skip-keypress"])
        self._action_button(actions, "Ver cárceles de Fail2ban", ["pkexec", "fail2ban-client", "status"])

    def page_network(self):
        card = self._card("Estado de red")
        self._status_row(card, "Aleatorización de MAC",
            lambda: (("Configurada", "stat-ok")
                     if os.path.exists("/etc/NetworkManager/conf.d/00-macrandomize.conf")
                     else ("No configurada", "stat-warn")))
        actions = self._card("Inspección")
        self._action_button(actions, "Puertos a la escucha", ["ss", "-tulpn"])
        self._action_button(actions, "Conexiones activas", ["ss", "-tunap"])

    def page_privacy(self):
        card = self._card("Privacidad")
        self._status_row(card, "DNS cifrado (dnscrypt-proxy)",
            lambda: (("Activo", "stat-ok") if service_active("dnscrypt-proxy") else ("No activo", "stat-warn")))
        self._status_row(card, "Telemetría del sistema",
            lambda: ("Desactivada", "stat-ok"))
        self._status_row(card, "Firejail (sandbox navegador)",
            lambda: (("Disponible", "stat-ok") if shutil.which("firejail") else ("No instalado", "stat-warn")))
        note = self._card("Nota")
        note.pack_start(Gtk.Label(
            label="Solux OS no recopila datos de uso. El navegador arranca en un sandbox de "
                  "Firejail y el DNS puede cifrarse para evitar fugas.", xalign=0, wrap=True),
            False, False, 0)

    def page_updates(self):
        card = self._card("Actualizaciones de seguridad")
        self._status_row(card, "unattended-upgrades",
            lambda: (("Activo", "stat-ok") if service_active("unattended-upgrades") else ("Inactivo", "stat-warn")))
        actions = self._card("Acciones")
        self._action_button(actions, "Buscar actualizaciones", ["pkexec", "apt-get", "update"])
        self._action_button(actions, "Instalar actualizaciones de seguridad",
                            ["pkexec", "unattended-upgrade", "-d"])

    def page_sandbox(self):
        card = self._card("Aislamiento de aplicaciones")
        self._status_row(card, "AppArmor",
            lambda: (("Enforce", "stat-ok") if run(["aa-status", "--enabled"])[0] == 0 else ("Inactivo", "stat-bad")))
        self._status_row(card, "Firejail",
            lambda: (("Instalado", "stat-ok") if shutil.which("firejail") else ("No", "stat-warn")))
        actions = self._card("Acciones")
        self._action_button(actions, "Ver perfiles AppArmor", ["pkexec", "aa-status"])

    def page_audit(self):
        card = self._card("Auditoría de hardening (Lynis)")
        self._status_row(card, "Lynis",
            lambda: (("Instalado", "stat-ok") if shutil.which("lynis") else ("No instalado", "stat-warn")))
        actions = self._card("Ejecutar auditoría")
        self._action_button(actions, "Auditoría completa del sistema",
                            ["pkexec", "lynis", "audit", "system", "--quick"])


def main():
    win = SecurityCenter()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()


if __name__ == "__main__":
    main()
