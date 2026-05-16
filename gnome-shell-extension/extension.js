/**
 * pardus-desktop-shortcut — GNOME Shell Extension
 *
 * GNOME uygulama menüsünde (Activities → Uygulamalar) uygulamalara
 * sağ tıklandığında "Masaüstüne Ekle" seçeneği ekler.
 *
 * Copyright (C) 2026 Umut Karacelebi
 * License: GPL-3.0
 */

'use strict';

const { Gio, GLib, Shell, St, Clutter } = imports.gi;
const Main = imports.ui.main;
const PopupMenu = imports.ui.popupMenu;
const AppDisplay = imports.ui.appDisplay;

const DESKTOP_SHORTCUT_SCRIPT = '/usr/share/pardus/desktop-shortcut/desktop_shortcut_helper.sh';

class PardusDesktopShortcutExtension {
    constructor() {
        this._appDisplayPatched = false;
        this._originalPopupMenu = null;
    }

    /**
     * Kullanıcının masaüstü dizinini bul.
     * xdg-user-dir komutu veya bilinen dizin isimlerini dener.
     */
    _getDesktopDir() {
        try {
            let [ok, stdout] = GLib.spawn_command_line_sync('xdg-user-dir DESKTOP');
            if (ok && stdout) {
                let dir = imports.byteArray.toString(stdout).trim();
                if (dir && GLib.file_test(dir, GLib.FileTest.IS_DIR)) {
                    return dir;
                }
            }
        } catch (e) {
            // xdg-user-dir mevcut değil
        }

        let home = GLib.get_home_dir();
        let candidates = ['Desktop', 'Masaüstü', 'desktop'];
        for (let c of candidates) {
            let path = GLib.build_filenamev([home, c]);
            if (GLib.file_test(path, GLib.FileTest.IS_DIR)) {
                return path;
            }
        }

        return home;
    }

    /**
     * .desktop dosyasını masaüstüne kopyala ve güvenilir olarak işaretle.
     */
    _copyToDesktop(appId) {
        let desktopDir = this._getDesktopDir();

        // .desktop dosyasının kaynak yolunu bul
        let sourcePath = null;
        let searchDirs = [
            '/usr/share/applications',
            '/usr/local/share/applications',
            GLib.build_filenamev([GLib.get_home_dir(), '.local', 'share', 'applications']),
        ];

        for (let dir of searchDirs) {
            let candidate = GLib.build_filenamev([dir, appId]);
            if (GLib.file_test(candidate, GLib.FileTest.EXISTS)) {
                sourcePath = candidate;
                break;
            }
        }

        if (!sourcePath) {
            Main.notify(
                'Pardus Masaüstü Kısayolu',
                `${appId} dosyası bulunamadı.`
            );
            return;
        }

        let destPath = GLib.build_filenamev([desktopDir, appId]);

        // Zaten masaüstündeyse bildir
        if (GLib.file_test(destPath, GLib.FileTest.EXISTS)) {
            Main.notify(
                'Pardus Masaüstü Kısayolu',
                'Bu uygulama zaten masaüstünde mevcut.'
            );
            return;
        }

        try {
            // Dosyayı kopyala
            let sourceFile = Gio.File.new_for_path(sourcePath);
            let destFile = Gio.File.new_for_path(destPath);
            sourceFile.copy(destFile, Gio.FileCopyFlags.NONE, null, null);

            // chmod +x
            GLib.spawn_command_line_sync(`chmod +x "${destPath}"`);

            // gio set metadata::trusted true
            GLib.spawn_command_line_sync(
                `gio set "${destPath}" metadata::trusted true`
            );

            Main.notify(
                'Pardus Masaüstü Kısayolu',
                'Uygulama masaüstüne eklendi.'
            );

        } catch (e) {
            Main.notify(
                'Pardus Masaüstü Kısayolu',
                `Hata: ${e.message}`
            );
        }
    }

    /**
     * .desktop kısayolunu masaüstünden kaldır.
     */
    _removeFromDesktop(appId) {
        let desktopDir = this._getDesktopDir();
        let destPath = GLib.build_filenamev([desktopDir, appId]);

        if (!GLib.file_test(destPath, GLib.FileTest.EXISTS)) {
            return;
        }

        try {
            let file = Gio.File.new_for_path(destPath);
            file.delete(null);

            Main.notify(
                'Pardus Masaüstü Kısayolu',
                'Kısayol masaüstünden kaldırıldı.'
            );
        } catch (e) {
            Main.notify(
                'Pardus Masaüstü Kısayolu',
                `Kaldırma hatası: ${e.message}`
            );
        }
    }

    /**
     * Uygulama ikonunun popup menüsüne "Masaüstüne Ekle" seçeneği ekle.
     */
    _patchAppIcon(appIcon) {
        if (!appIcon || !appIcon._menu) {
            return;
        }

        let menu = appIcon._menu;
        let app = appIcon.app;

        if (!app) {
            return;
        }

        let appId = app.get_id();
        if (!appId) {
            return;
        }

        // Zaten eklenmiş mi kontrol et
        if (menu._pardusDesktopShortcutAdded) {
            return;
        }

        // Ayırıcı
        let separator = new PopupMenu.PopupSeparatorMenuItem();
        menu.addMenuItem(separator);

        // Masaüstünde var mı kontrol et
        let desktopDir = this._getDesktopDir();
        let destPath = GLib.build_filenamev([desktopDir, appId]);
        let isOnDesktop = GLib.file_test(destPath, GLib.FileTest.EXISTS);

        if (isOnDesktop) {
            // "Masaüstünden Kaldır" seçeneği
            let removeItem = new PopupMenu.PopupMenuItem('Masaüstünden Kaldır');
            removeItem.connect('activate', () => {
                this._removeFromDesktop(appId);
            });
            menu.addMenuItem(removeItem);
        } else {
            // "Masaüstüne Ekle" seçeneği
            let addItem = new PopupMenu.PopupMenuItem('Masaüstüne Ekle');
            addItem.connect('activate', () => {
                this._copyToDesktop(appId);
            });
            menu.addMenuItem(addItem);
        }

        menu._pardusDesktopShortcutAdded = true;
    }

    /**
     * AppIcon sınıfını yamalayarak popup menüyü genişlet.
     */
    _patchAppDisplay() {
        if (this._appDisplayPatched) {
            return;
        }

        let self = this;

        // AppIcon'un popupMenu metodunu yakala
        this._originalPopupMenu = AppDisplay.AppIcon.prototype.popupMenu;

        AppDisplay.AppIcon.prototype.popupMenu = function(side) {
            // Önce orijinal menüyü oluştur
            if (self._originalPopupMenu) {
                self._originalPopupMenu.call(this, side);
            }
            // Sonra Pardus kısayol seçeneğini ekle
            self._patchAppIcon(this);
        };

        this._appDisplayPatched = true;
    }

    /**
     * Yamaları geri al.
     */
    _unpatchAppDisplay() {
        if (!this._appDisplayPatched) {
            return;
        }

        if (this._originalPopupMenu) {
            AppDisplay.AppIcon.prototype.popupMenu = this._originalPopupMenu;
            this._originalPopupMenu = null;
        }

        this._appDisplayPatched = false;
    }

    enable() {
        this._patchAppDisplay();
    }

    disable() {
        this._unpatchAppDisplay();
    }
}

function init() {
    return new PardusDesktopShortcutExtension();
}
