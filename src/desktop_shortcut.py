#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pardus-desktop-shortcut — Core Library
Masaüstüne .desktop kısayolu ekleme kütüphanesi.

Copyright (C) 2026 Umut Karacelebi
License: GPL-3.0
"""

import os
import shutil
import subprocess
import configparser
import locale
import gettext

# i18n setup
APP_NAME = "pardus-desktop-shortcut"
LOCALE_DIR = "/usr/share/locale"

try:
    gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
    gettext.textdomain(APP_NAME)
    _ = gettext.gettext
except Exception:
    def _(msg):
        return msg


class DesktopShortcut:
    """Masaüstüne .desktop dosyası kısayolu oluşturma/kopyalama sınıfı."""

    # Sistem genelindeki .desktop dosya dizinleri
    SYSTEM_APP_DIRS = [
        "/usr/share/applications",
        "/usr/local/share/applications",
    ]

    def __init__(self):
        self.desktop_dir = self._resolve_desktop_dir()
        self.user_app_dir = os.path.join(
            os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")),
            "applications",
        )

    # ------------------------------------------------------------------
    # Masaüstü dizinini bulma
    # ------------------------------------------------------------------
    @staticmethod
    def _resolve_desktop_dir():
        """
        Kullanıcının masaüstü dizinini bul.
        Öncelik sırası:
          1. xdg-user-dir DESKTOP komutu
          2. XDG_DESKTOP_DIR (user-dirs.dirs)
          3. ~/Desktop
          4. ~/Masaüstü  (Türkçe Pardus varsayılanı)
          5. $HOME (son çare)
        """
        # 1. xdg-user-dir komutu
        try:
            result = subprocess.run(
                ["xdg-user-dir", "DESKTOP"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                if path and os.path.isdir(path):
                    return path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # 2. user-dirs.dirs dosyası
        home = os.path.expanduser("~")
        user_dirs = os.path.join(
            os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config")),
            "user-dirs.dirs",
        )
        if os.path.isfile(user_dirs):
            try:
                with open(user_dirs, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("XDG_DESKTOP_DIR"):
                            value = line.split("=", 1)[1].strip().strip('"')
                            value = value.replace("$HOME", home)
                            if os.path.isdir(value):
                                return value
            except OSError:
                pass

        # 3-4. Bilinen dizin isimleri
        for candidate in ("Desktop", "Masaüstü", "desktop"):
            path = os.path.join(home, candidate)
            if os.path.isdir(path):
                return path

        # 5. Son çare
        return home

    # ------------------------------------------------------------------
    # .desktop dosyasını masaüstüne kopyala
    # ------------------------------------------------------------------
    def copy_to_desktop(self, source_path, overwrite=False):
        """
        Bir .desktop dosyasını masaüstüne kopyala ve güvenilir olarak işaretle.

        Args:
            source_path: Kaynak .desktop dosyasının tam yolu
            overwrite: Mevcut dosyanın üzerine yaz

        Returns:
            (bool, str): (başarı, hedef_yol veya hata mesajı)
        """
        if not os.path.isfile(source_path):
            return False, _("{} dosyası bulunamadı.").format(source_path)

        if not source_path.endswith(".desktop"):
            return False, _("Sadece .desktop dosyaları desteklenmektedir.")

        filename = os.path.basename(source_path)
        dest_path = os.path.join(self.desktop_dir, filename)

        if os.path.exists(dest_path) and not overwrite:
            return False, _("{} zaten masaüstünde mevcut.").format(filename)

        try:
            # Masaüstü dizini yoksa oluştur
            os.makedirs(self.desktop_dir, exist_ok=True)

            # Kopyala
            shutil.copy2(source_path, dest_path)

            # Güvenilir olarak işaretle (GNOME "Allow Launching")
            self._mark_as_trusted(dest_path)

            return True, dest_path

        except OSError as e:
            return False, _("Kopyalama hatası: {}").format(str(e))

    # ------------------------------------------------------------------
    # Sıfırdan .desktop dosyası oluştur
    # ------------------------------------------------------------------
    def create_desktop_entry(self, name, exec_path, icon="", comment="",
                             categories="Application;", terminal=False,
                             overwrite=False):
        """
        Masaüstünde yeni bir .desktop dosyası oluştur.

        Args:
            name: Uygulama adı
            exec_path: Çalıştırılacak komut
            icon: İkon adı veya yolu
            comment: Açıklama
            categories: Kategoriler (noktalı virgülle ayrılmış)
            terminal: Terminalde çalışsın mı
            overwrite: Üzerine yaz

        Returns:
            (bool, str): (başarı, hedef_yol veya hata mesajı)
        """
        if not name or not name.strip():
            return False, _("Uygulama adı boş olamaz.")

        if not exec_path or not exec_path.strip():
            return False, _("Çalıştırılacak komut boş olamaz.")

        # Güvenli dosya adı
        safe_name = name.replace(" ", "_").replace("/", "_")
        filename = "{}.desktop".format(safe_name)
        dest_path = os.path.join(self.desktop_dir, filename)

        if os.path.exists(dest_path) and not overwrite:
            return False, _("{} zaten masaüstünde mevcut.").format(filename)

        try:
            os.makedirs(self.desktop_dir, exist_ok=True)

            content = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name={name}\n"
                "Exec={exec_path}\n"
                "Icon={icon}\n"
                "Comment={comment}\n"
                "Categories={categories}\n"
                "Terminal={terminal}\n"
                "StartupNotify=true\n"
            ).format(
                name=name,
                exec_path=exec_path,
                icon=icon,
                comment=comment,
                categories=categories,
                terminal="true" if terminal else "false",
            )

            with open(dest_path, "w") as f:
                f.write(content)

            self._mark_as_trusted(dest_path)

            return True, dest_path

        except OSError as e:
            return False, _("Oluşturma hatası: {}").format(str(e))

    # ------------------------------------------------------------------
    # GNOME "Allow Launching" — güvenilir işaretleme
    # ------------------------------------------------------------------
    @staticmethod
    def _mark_as_trusted(desktop_file_path):
        """
        .desktop dosyasını GNOME'da güvenilir olarak işaretle.
        Bu işlem iki adımda yapılır:
          1. gio set metadata::trusted true
          2. chmod +x
        """
        # 1. metadata::trusted ayarla
        try:
            subprocess.run(
                ["gio", "set", desktop_file_path, "metadata::trusted", "true"],
                capture_output=True, timeout=5,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # 2. Çalıştırılabilir yap
        try:
            os.chmod(desktop_file_path, 0o755)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Yüklü uygulamaları listele
    # ------------------------------------------------------------------
    def list_installed_apps(self):
        """
        Sistemde yüklü .desktop dosyalarını listele.

        Returns:
            list[dict]: Her biri {name, exec, icon, path} içeren sözlük listesi
        """
        apps = []
        search_dirs = self.SYSTEM_APP_DIRS + [self.user_app_dir]

        for app_dir in search_dirs:
            if not os.path.isdir(app_dir):
                continue

            for filename in sorted(os.listdir(app_dir)):
                if not filename.endswith(".desktop"):
                    continue

                filepath = os.path.join(app_dir, filename)
                info = self._parse_desktop_file(filepath)
                if info:
                    apps.append(info)

        return apps

    # ------------------------------------------------------------------
    # .desktop dosyasını oku ve bilgileri çıkar
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_desktop_file(filepath):
        """
        Bir .desktop dosyasını oku ve temel bilgileri döndür.

        Returns:
            dict veya None
        """
        try:
            config = configparser.ConfigParser(interpolation=None)
            config.read(filepath, encoding="utf-8")

            if "Desktop Entry" not in config:
                return None

            entry = config["Desktop Entry"]

            # NoDisplay veya Hidden uygulamaları atla
            if entry.get("NoDisplay", "false").lower() == "true":
                return None
            if entry.get("Hidden", "false").lower() == "true":
                return None

            entry_type = entry.get("Type", "Application")
            if entry_type != "Application":
                return None

            return {
                "name": entry.get("Name", os.path.basename(filepath)),
                "exec": entry.get("Exec", ""),
                "icon": entry.get("Icon", ""),
                "comment": entry.get("Comment", ""),
                "path": filepath,
                "filename": os.path.basename(filepath),
            }

        except (configparser.Error, OSError):
            return None

    # ------------------------------------------------------------------
    # Masaüstünde .desktop kısayolu var mı kontrol et
    # ------------------------------------------------------------------
    def is_on_desktop(self, desktop_filename):
        """Belirtilen .desktop dosyasının masaüstünde olup olmadığını kontrol et."""
        return os.path.exists(os.path.join(self.desktop_dir, desktop_filename))

    # ------------------------------------------------------------------
    # Masaüstünden kısayol kaldır
    # ------------------------------------------------------------------
    def remove_from_desktop(self, desktop_filename):
        """
        Masaüstünden bir .desktop kısayolunu kaldır.

        Returns:
            (bool, str): (başarı, mesaj)
        """
        dest_path = os.path.join(self.desktop_dir, desktop_filename)
        if not os.path.exists(dest_path):
            return False, _("{} masaüstünde bulunamadı.").format(desktop_filename)

        try:
            os.remove(dest_path)
            return True, _("{} masaüstünden kaldırıldı.").format(desktop_filename)
        except OSError as e:
            return False, _("Kaldırma hatası: {}").format(str(e))

    # ------------------------------------------------------------------
    # Bir uygulama adıyla .desktop dosyasını bul
    # ------------------------------------------------------------------
    def find_desktop_file(self, app_name):
        """
        Uygulama adı veya .desktop dosya adı ile sisteme yüklü
        .desktop dosyasını bul.

        Args:
            app_name: "firefox", "firefox.desktop" veya tam yol

        Returns:
            str veya None: .desktop dosyasının tam yolu
        """
        # Tam yol verilmişse direkt kontrol
        if os.path.isfile(app_name):
            return app_name

        # .desktop uzantısı ekle
        if not app_name.endswith(".desktop"):
            app_name = app_name + ".desktop"

        # Arama dizinlerinde bul
        search_dirs = self.SYSTEM_APP_DIRS + [self.user_app_dir]
        for app_dir in search_dirs:
            filepath = os.path.join(app_dir, app_name)
            if os.path.isfile(filepath):
                return filepath

        return None
