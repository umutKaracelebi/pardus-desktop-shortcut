#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pardus-desktop-shortcut — Nautilus Extension
Nautilus dosya yöneticisinde sağ-tık menüsüne "Masaüstüne Ekle" seçeneği ekler.

Kurulum yeri: /usr/share/nautilus-python/extensions/

Copyright (C) 2026 Umut Karacelebi
License: GPL-3.0
"""

import os
import sys

# Core kütüphaneyi yükle
sys.path.insert(0, "/usr/share/pardus/desktop-shortcut")

from gi import require_version

try:
    require_version("Nautilus", "4.0")
except ValueError:
    require_version("Nautilus", "3.0")

require_version("Gtk", "3.0")
require_version("GObject", "2.0")

from gi.repository import Nautilus, GObject, Gtk, Gio

try:
    from desktop_shortcut import DesktopShortcut
except ImportError:
    # Geliştirme ortamında alternatif yol
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from desktop_shortcut import DesktopShortcut


class DesktopShortcutExtension(GObject.GObject, Nautilus.MenuProvider):
    """
    Nautilus sağ-tık menüsüne "Masaüstüne Ekle" seçeneği ekleyen extension.

    Şu durumlarda menü öğesi görünür:
      - Bir veya daha fazla .desktop dosyası seçildiğinde
      - /usr/share/applications/ veya benzer dizinlerde gezinirken
    """

    def __init__(self):
        super().__init__()
        self.shortcut = DesktopShortcut()

    def get_file_items(self, *args):
        """Dosya(lar) seçildiğinde çağrılır — sağ-tık menüsü."""
        # Nautilus 4.0 ve 3.0 API uyumu
        files = args[-1]

        if not files:
            return []

        # Sadece .desktop dosyaları için göster
        desktop_files = []
        for f in files:
            if f.get_uri_scheme() != "file":
                continue
            filepath = f.get_location().get_path()
            if filepath and filepath.endswith(".desktop"):
                desktop_files.append(f)

        if not desktop_files:
            return []

        # Tek dosya: zaten masaüstündeyse "Kaldır" göster
        if len(desktop_files) == 1:
            filepath = desktop_files[0].get_location().get_path()
            filename = os.path.basename(filepath)

            if self.shortcut.is_on_desktop(filename):
                item = Nautilus.MenuItem(
                    name="PardusDesktopShortcut::RemoveFromDesktop",
                    label="Masaüstünden Kaldır",
                    tip="Bu uygulamanın masaüstü kısayolunu kaldır",
                    icon="edit-delete-symbolic",
                )
                item.connect("activate", self._on_remove_activated, desktop_files)
                return [item]

        # "Masaüstüne Ekle" menü öğesi
        item = Nautilus.MenuItem(
            name="PardusDesktopShortcut::AddToDesktop",
            label="Masaüstüne Ekle",
            tip="Bu uygulamayı masaüstüne kısayol olarak ekle",
            icon="list-add-symbolic",
        )
        item.connect("activate", self._on_add_activated, desktop_files)

        return [item]

    def get_background_items(self, *args):
        """Arka plana (boş alana) sağ tıklandığında — şimdilik boş."""
        return []

    # ------------------------------------------------------------------
    # Masaüstüne ekleme callback'i
    # ------------------------------------------------------------------
    def _on_add_activated(self, menu_item, files):
        """Kullanıcı "Masaüstüne Ekle" seçeneğine tıkladığında çağrılır."""
        success_count = 0
        error_messages = []

        for f in files:
            filepath = f.get_location().get_path()
            if not filepath:
                continue

            ok, result = self.shortcut.copy_to_desktop(filepath, overwrite=False)
            if ok:
                success_count += 1
            else:
                error_messages.append(result)

        # Sonuç bildirimi
        if success_count > 0 and not error_messages:
            self._show_notification(
                "Masaüstüne Eklendi",
                "{} uygulama masaüstüne eklendi.".format(success_count)
                if success_count > 1
                else "Uygulama masaüstüne eklendi.",
            )
        elif error_messages:
            self._show_notification(
                "Uyarı",
                "\n".join(error_messages),
            )

    # ------------------------------------------------------------------
    # Masaüstünden kaldırma callback'i
    # ------------------------------------------------------------------
    def _on_remove_activated(self, menu_item, files):
        """Kullanıcı "Masaüstünden Kaldır" seçeneğine tıkladığında çağrılır."""
        for f in files:
            filepath = f.get_location().get_path()
            if not filepath:
                continue
            filename = os.path.basename(filepath)
            self.shortcut.remove_from_desktop(filename)

        self._show_notification(
            "Masaüstünden Kaldırıldı",
            "Kısayol masaüstünden kaldırıldı.",
        )

    # ------------------------------------------------------------------
    # Bildirim gösterme
    # ------------------------------------------------------------------
    @staticmethod
    def _show_notification(title, body):
        """Basit bir masaüstü bildirimi göster."""
        try:
            app = Gio.Application.get_default()
            if app:
                notification = Gio.Notification.new(title)
                notification.set_body(body)
                app.send_notification(None, notification)
            else:
                # Fallback: notify-send kullan
                import subprocess
                subprocess.Popen(
                    ["notify-send", "--app-name=Pardus Masaüstü Kısayolu",
                     title, body],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception:
            pass
