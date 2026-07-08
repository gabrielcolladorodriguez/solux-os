#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solux Notes — Notas rápidas de Solux OS
© 2026 Pollocrudo Company. Licencia GPLv3.

Aplicación de notas ligera (Python 3 + GTK 3). Guarda notas en Markdown plano en
~/.local/share/solux-notes/, con lista lateral, búsqueda y autoguardado. Sin nube, sin
cuentas, sin telemetría — tus notas son tuyas y viven en tu disco.
"""

import os
import re
import time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

NOTES_DIR = os.path.expanduser("~/.local/share/solux-notes")

CSS = b"""
window { background-color: #0D0D1A; color: #F1F5F9; }
.sidebar { background-color: #15152A; }
.sidebar list { background: transparent; }
.note-row { padding: 10px 12px; border-bottom: 1px solid #2A2A4A; }
.note-row:selected { background: #F97316; color: #0D0D1A; }
.note-title { font-weight: 700; }
.note-preview { color: #94A3B8; font-size: 11px; }
.search { background: #0D0D1A; border: 1px solid #2A2A4A; border-radius: 8px; padding: 6px 10px; }
textview, textview text { background-color: #0D0D1A; color: #F1F5F9; font-family: 'JetBrains Mono', monospace; font-size: 13px; }
.toolbtn { background: #1E1E38; color: #FBBF24; border: 1px solid #2A2A4A; border-radius: 8px; }
.toolbtn:hover { border-color: #F97316; }
headerbar { background: linear-gradient(#1E1E38,#15152A); }
.brand { color: #F97316; font-weight: 800; }
"""


def slugify(text):
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s]+", "-", s) or "nota"


class SoluxNotes(Gtk.Window):
    def __init__(self):
        super().__init__(title="Solux Notes")
        self.set_default_size(940, 640)
        self.set_icon_name("solux-notes")
        os.makedirs(NOTES_DIR, exist_ok=True)
        self.current = None
        self._save_timer = None
        self._css()

        hb = Gtk.HeaderBar(show_close_button=True, title="Solux Notes")
        self.set_titlebar(hb)
        brand = Gtk.Label(); brand.set_markup('<span foreground="#F97316" weight="800">📝 Solux Notes</span>')
        hb.pack_start(brand)
        newb = Gtk.Button.new_from_icon_name("document-new-symbolic", Gtk.IconSize.BUTTON)
        newb.get_style_context().add_class("toolbtn")
        newb.connect("clicked", lambda _b: self.new_note())
        hb.pack_start(newb)
        delb = Gtk.Button.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
        delb.get_style_context().add_class("toolbtn")
        delb.connect("clicked", lambda _b: self.delete_note())
        hb.pack_end(delb)

        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(root)

        # Sidebar
        side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        side.set_size_request(280, -1)
        side.get_style_context().add_class("sidebar")
        self.search = Gtk.SearchEntry()
        self.search.get_style_context().add_class("search")
        self.search.set_margin_top(8); self.search.set_margin_start(8); self.search.set_margin_end(8); self.search.set_margin_bottom(4)
        self.search.connect("search-changed", lambda _e: self.refresh_list())
        side.pack_start(self.search, False, False, 0)
        sc = Gtk.ScrolledWindow(); sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-selected", self.on_select)
        sc.add(self.listbox)
        side.pack_start(sc, True, True, 0)
        root.pack_start(side, False, False, 0)

        # Editor
        ed = Gtk.ScrolledWindow(); ed.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.text = Gtk.TextView()
        self.text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text.set_left_margin(16); self.text.set_right_margin(16)
        self.text.set_top_margin(12); self.text.set_bottom_margin(12)
        self.buffer = self.text.get_buffer()
        self.buffer.connect("changed", self.on_change)
        ed.add(self.text)
        root.pack_start(ed, True, True, 0)

        self.refresh_list()
        if self.listbox.get_row_at_index(0):
            self.listbox.select_row(self.listbox.get_row_at_index(0))
        else:
            self.new_note()

    def _css(self):
        p = Gtk.CssProvider(); p.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _notes(self):
        items = []
        for fn in os.listdir(NOTES_DIR):
            if fn.endswith(".md"):
                path = os.path.join(NOTES_DIR, fn)
                try:
                    with open(path, encoding="utf-8") as fh:
                        content = fh.read()
                except OSError:
                    continue
                items.append((path, content, os.path.getmtime(path)))
        items.sort(key=lambda x: x[2], reverse=True)
        return items

    def refresh_list(self):
        query = self.search.get_text().strip().lower()
        for c in self.listbox.get_children():
            self.listbox.remove(c)
        for path, content, _mt in self._notes():
            if query and query not in content.lower():
                continue
            title = content.strip().splitlines()[0] if content.strip() else "(sin título)"
            preview = " ".join(content.strip().splitlines()[1:])[:50]
            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("note-row")
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            t = Gtk.Label(label=title[:36], xalign=0); t.get_style_context().add_class("note-title")
            p = Gtk.Label(label=preview, xalign=0); p.get_style_context().add_class("note-preview")
            box.pack_start(t, False, False, 0); box.pack_start(p, False, False, 0)
            row.add(box); row.path = path
            self.listbox.add(row)
        self.listbox.show_all()

    def on_select(self, _lb, row):
        if row is None or not hasattr(row, "path"):
            return
        self.current = row.path
        try:
            with open(row.path, encoding="utf-8") as fh:
                content = fh.read()
        except OSError:
            content = ""
        self.buffer.handler_block_by_func(self.on_change)
        self.buffer.set_text(content)
        self.buffer.handler_unblock_by_func(self.on_change)

    def new_note(self):
        path = os.path.join(NOTES_DIR, f"nota-{int(time.time())}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("Nueva nota\n\n")
        self.current = path
        self.refresh_list()
        self.buffer.set_text("Nueva nota\n\n")
        self.text.grab_focus()

    def delete_note(self):
        if self.current and os.path.exists(self.current):
            os.remove(self.current)
            self.current = None
            self.buffer.set_text("")
            self.refresh_list()

    def on_change(self, _buf):
        if self._save_timer:
            GLib.source_remove(self._save_timer)
        self._save_timer = GLib.timeout_add(600, self._save)

    def _save(self):
        self._save_timer = None
        if not self.current:
            return False
        start, end = self.buffer.get_bounds()
        text = self.buffer.get_text(start, end, True)
        try:
            with open(self.current, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError:
            pass
        # Actualiza el título en la lista sin perder el foco
        row = self.listbox.get_selected_row()
        if row:
            box = row.get_child()
            labels = box.get_children()
            if labels:
                first = text.strip().splitlines()[0] if text.strip() else "(sin título)"
                labels[0].set_text(first[:36])
        return False


def main():
    win = SoluxNotes()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
