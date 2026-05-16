# Pardus Desktop Shortcut

*(Türkçe için lütfen [README.md](README.md) dosyasına bakınız)*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Debian Package](https://img.shields.io/badge/Debian-Package-red.svg)]()
[![GNOME 48 ESM](https://img.shields.io/badge/GNOME-48_ESM-brightgreen.svg)]()

**Developed by the İnoTürk team for the 2026 Teknofest Pardus Bug Catching and Suggestion Competition — Suggestion/Bug Category.**

An official integration tool that allows you to easily add applications, files, and folders to the desktop as a shortcut on the GNOME desktop environment via right-click. Works natively on Pardus and other Debian-based GNOME distributions. Fully supports i18n localization for over 100 languages.

## Problem
The GNOME desktop environment does not natively support creating application shortcuts on the desktop via drag-and-drop. Users have to manually copy `.desktop` files to the desktop directory, make them executable, and manually mark them as "Allow Launching" / "Trusted". Additionally, there is no practical way to simply right-click and send any document or folder to the desktop as a symbolic link.

## Solution
This tool provides **3 different integration points**:
1. **📁 Nautilus (Files) Right-Click Menu:** When you right-click on any file, folder, or `.desktop` application, an **"Add to Desktop"** option appears.
2. **🔲 GNOME App Menu (Activities):** When you right-click on any application icon in the GNOME Activities → Applications grid, an **"Add to Desktop"** option appears. (GNOME 45-48 ESM compatible)
3. **💻 Command Line Interface (CLI):** Manage your desktop items easily via terminal commands.

## Installation

### Via Debian/Pardus Package (.deb)
Download the `.deb` file from the Releases section and install it via terminal:
```bash
sudo dpkg -i pardus-desktop-shortcut_1.0.0-1_all.deb
sudo apt-get install -f
```
*(Note: Nautilus integration becomes active immediately. For the GNOME Shell extension, simply log out and log back in after installation).*

### Manual Installation
```bash
# Core library
sudo mkdir -p /usr/share/pardus/desktop-shortcut
sudo cp src/desktop_shortcut.py /usr/share/pardus/desktop-shortcut/

# CLI tool
sudo cp src/pardus-desktop-shortcut-cli /usr/bin/pardus-desktop-shortcut
sudo chmod +x /usr/bin/pardus-desktop-shortcut

# Nautilus extension
sudo cp nautilus/pardus-desktop-shortcut.py /usr/share/nautilus-python/extensions/

# GNOME Shell extension
sudo mkdir -p /usr/share/gnome-shell/extensions/pardus-desktop-shortcut@pardus.org.tr/
sudo cp gnome-shell-extension/* /usr/share/gnome-shell/extensions/pardus-desktop-shortcut@pardus.org.tr/

# Restart Nautilus
nautilus -q

# Enable GNOME Shell extension
gnome-extensions enable pardus-desktop-shortcut@pardus.org.tr
```

## Dependencies
- `python3` (>= 3.6)
- `python3-gi` (GTK/GObject introspection)
- `python3-nautilus` (Nautilus Python extension support)
- `gnome-shell` (GNOME Shell extension support)

## License
GPL-3.0 — See the [LICENSE](LICENSE) file.