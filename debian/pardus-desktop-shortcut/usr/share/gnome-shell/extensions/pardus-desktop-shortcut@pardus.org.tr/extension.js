/**
 * pardus-desktop-shortcut — GNOME Shell Extension
 *
 * GNOME uygulama menüsünde (Activities → Uygulamalar) uygulamalara
 * sağ tıklandığında "Masaüstüne Ekle" seçeneği ekler.
 *
 * Copyright (C) 2026 Umut Karacelebi
 * License: GPL-3.0
 */

import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import * as AppDisplay from 'resource:///org/gnome/shell/ui/appDisplay.js';

import * as Gettext from 'gettext';
const _ = Gettext.domain('pardus-desktop-shortcut').gettext;

export default class PardusDesktopShortcutExtension {
    constructor() {
        this._appDisplayPatched = false;
        this._originalPopupMenu = null;
    }

    /**
     * Kullanıcının masaüstü dizinini bul.
     */
    _getDesktopDir() {
        try {
            let [ok, stdout] = GLib.spawn_command_line_sync('xdg-user-dir DESKTOP');
            if (ok && stdout) {
                let dir = new TextDecoder().decode(stdout).trim();
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
            Main.notify(_('Pardus Desktop Shortcut'), _('{} not found.').replace('{}', appId));
            return;
        }

        let destPath = GLib.build_filenamev([desktopDir, appId]);

        if (GLib.file_test(destPath, GLib.FileTest.EXISTS)) {
            Main.notify(_('Pardus Desktop Shortcut'), _('This application is already on the desktop.'));
            return;
        }

        try {
            let sourceFile = Gio.File.new_for_path(sourcePath);
            let destFile = Gio.File.new_for_path(destPath);
            sourceFile.copy(destFile, Gio.FileCopyFlags.NONE, null, null);

            GLib.spawn_command_line_sync(`chmod +x "${destPath}"`);
            GLib.spawn_command_line_sync(`gio set "${destPath}" metadata::trusted true`);

            Main.notify(_('Pardus Desktop Shortcut'), _('Application added to desktop.'));

        } catch (e) {
            Main.notify(_('Pardus Desktop Shortcut'), _('Error: ') + e.message);
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
            Main.notify(_('Pardus Desktop Shortcut'), _('Shortcut removed from desktop.'));
        } catch (e) {
            Main.notify(_('Pardus Desktop Shortcut'), _('Removal error: {}').replace('{}', e.message));
        }
    }

    /**
     * Uygulama ikonunun popup menüsüne seçenek ekle.
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

        if (menu._pardusDesktopShortcutAdded) {
            return;
        }

        let separator = new PopupMenu.PopupSeparatorMenuItem();
        menu.addMenuItem(separator);

        let desktopDir = this._getDesktopDir();
        let destPath = GLib.build_filenamev([desktopDir, appId]);
        let isOnDesktop = GLib.file_test(destPath, GLib.FileTest.EXISTS);

        if (isOnDesktop) {
            let removeItem = new PopupMenu.PopupMenuItem(_('Remove from Desktop'));
            removeItem.connect('activate', () => {
                this._removeFromDesktop(appId);
            });
            menu.addMenuItem(removeItem);
        } else {
            let addItem = new PopupMenu.PopupMenuItem(_('Add to Desktop'));
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
        this._originalPopupMenu = AppDisplay.AppIcon.prototype.popupMenu;

        AppDisplay.AppIcon.prototype.popupMenu = function(side) {
            if (self._originalPopupMenu) {
                self._originalPopupMenu.call(this, side);
            }
            self._patchAppIcon(this);
        };

        this._appDisplayPatched = true;
    }

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
