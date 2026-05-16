# Pardus Desktop Shortcut / Pardus Masaüstü Kısayol Aracı

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Debian Package](https://img.shields.io/badge/Debian-Package-red.svg)]()
[![GNOME 48 ESM](https://img.shields.io/badge/GNOME-48_ESM-brightgreen.svg)]()

*(English description follows below)*

**2026 Teknofest Pardus Hata Yakalama ve Öneri Yarışması — Öneri/Hata Kategorisi için İnoTürk takımı tarafından geliştirilmiştir.**

GNOME masaüstünde uygulamaları, dosyaları ve klasörleri kolayca masaüstüne kısayol olarak eklemeyi sağlayan resmi nitelikli entegrasyon aracı. Pardus ve diğer Debian tabanlı GNOME dağıtımlarında çalışır. 100'den fazla dil için i18n altyapısı içerir.

## Problem (TR)
GNOME masaüstünde sürükle-bırak ile uygulama kısayolu oluşturma desteği bulunmamaktadır. Kullanıcıların `.desktop` dosyalarını manuel olarak kopyalayıp, çalıştırılabilir hale getirip, "Allow Launching" (Güvenilir) işaretlemesi gerekmektedir. Aynı şekilde herhangi bir belge veya klasörü masaüstüne kısayol olarak gönderme pratikliği yoktur.

## Çözüm (TR)
Bu araç **3 farklı entegrasyon noktası** sunar:
1. **📁 Nautilus (Dosyalar) Sağ-Tık Menüsü:** Herhangi bir dosyaya, klasöre veya `.desktop` uygulamasına sağ tıkladığınızda **"Masaüstüne Ekle"** seçeneği görünür.
2. **🔲 GNOME Uygulama Menüsü (Activities):** GNOME Activities (Etkinlikler) → Uygulamalar bölümünde herhangi bir uygulama ikonuna sağ tıkladığınızda **"Masaüstüne Ekle"** seçeneği görünür. (GNOME 45-48 ESM uyumlu)
3. **💻 Komut Satırı Aracı (CLI):** Terminal üzerinden komutlarla masaüstü yönetimi yapabilirsiniz.

## Kurulum (TR)
**Debian/Pardus Paketi ile (.deb):**
Release bölümünden `.deb` dosyasını indirip terminalde kurabilirsiniz:
```bash
sudo dpkg -i pardus-desktop-shortcut_1.0.0-1_all.deb
```
*(Not: Dosyalar uygulamasındaki entegrasyon anında aktif olur, GNOME Shell eklentisi için kurulum sonrası oturumu kapatıp açmanız yeterlidir).*

---

# English Description

**Developed by the İnoTürk team for the 2026 Teknofest Pardus Bug Catching and Suggestion Competition — Suggestion/Bug Category.**

An official integration tool that allows you to easily add applications, files, and folders to the desktop as a shortcut on the GNOME desktop environment. Works natively on Pardus and other Debian-based GNOME distributions. Fully supports i18n localization for over 100 languages.

## Problem (EN)
The GNOME desktop environment does not natively support creating application shortcuts on the desktop via drag-and-drop. Users have to manually copy `.desktop` files to the desktop directory, make them executable, and manually mark them as "Allow Launching" / "Trusted". Additionally, there is no practical way to simply right-click and send any document or folder to the desktop as a symbolic link.

## Solution (EN)
This tool provides **3 different integration points**:
1. **📁 Nautilus (Files) Right-Click Menu:** When you right-click on any file, folder, or `.desktop` application, an **"Add to Desktop"** option appears.
2. **🔲 GNOME App Menu (Activities):** When you right-click on any application icon in the GNOME Activities → Applications grid, an **"Add to Desktop"** option appears. (GNOME 45-48 ESM compatible)
3. **💻 Command Line Interface (CLI):** Manage your desktop items easily via terminal commands.

## Installation (EN)
**Via Debian/Pardus Package (.deb):**
Download the `.deb` file from the Releases section and install it via terminal:
```bash
sudo dpkg -i pardus-desktop-shortcut_1.0.0-1_all.deb
```
*(Note: Nautilus integration becomes active immediately. For the GNOME Shell extension, simply log out and log back in after installation).*

---

## Bağımlılıklar / Dependencies
- `python3` (>= 3.6)
- `python3-gi` (GTK/GObject introspection)
- `python3-nautilus` (Nautilus Python extension support)
- `gnome-shell` (GNOME Shell extension support)

## Lisans / License
GPL-3.0 — See the [LICENSE](LICENSE) file.

## İletişim / Contact
- GitHub: [@umutKaracelebi](https://github.com/umutKaracelebi)
- Pardus Topluluk (Community): [forum.pardus.org.tr](https://forum.pardus.org.tr)
