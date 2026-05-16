# Pardus Masaüstü Kısayol Aracı (Pardus Desktop Shortcut)

*(For English, please see [README-en.md](README-en.md))*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Debian Package](https://img.shields.io/badge/Debian-Package-red.svg)]()
[![GNOME 48 ESM](https://img.shields.io/badge/GNOME-48_ESM-brightgreen.svg)]()

**2026 Teknofest Pardus Hata Yakalama ve Öneri Yarışması — Öneri/Hata Kategorisi için İnoTürk takımı tarafından geliştirilmiştir.**

GNOME masaüstünde uygulamaları, dosyaları ve klasörleri kolayca masaüstüne kısayol olarak eklemeyi sağlayan resmi nitelikli entegrasyon aracı. Pardus ve diğer Debian tabanlı GNOME dağıtımlarında çalışır. 100'den fazla dil için i18n altyapısı içerir.

## Problem
GNOME masaüstünde sürükle-bırak ile uygulama kısayolu oluşturma desteği bulunmamaktadır. Kullanıcıların `.desktop` dosyalarını manuel olarak kopyalayıp, çalıştırılabilir hale getirip, "Allow Launching" (Güvenilir) işaretlemesi gerekmektedir. Aynı şekilde herhangi bir belge veya klasörü masaüstüne kısayol olarak gönderme pratikliği yoktur.

## Çözüm
Bu araç **3 farklı entegrasyon noktası** sunar:
1. **📁 Nautilus (Dosyalar) Sağ-Tık Menüsü:** Herhangi bir dosyaya, klasöre veya `.desktop` uygulamasına sağ tıkladığınızda **"Masaüstüne Ekle"** seçeneği görünür.
2. **🔲 GNOME Uygulama Menüsü (Activities):** GNOME Activities (Etkinlikler) → Uygulamalar bölümünde herhangi bir uygulama ikonuna sağ tıkladığınızda **"Masaüstüne Ekle"** seçeneği görünür. (GNOME 45-48 ESM uyumlu)
3. **💻 Komut Satırı Aracı (CLI):** Terminal üzerinden komutlarla masaüstü yönetimi yapabilirsiniz.

## Kurulum

### Debian/Pardus Paketi ile (.deb)
Release bölümünden `.deb` dosyasını indirip terminalde kurabilirsiniz:
```bash
sudo dpkg -i pardus-desktop-shortcut_1.0.0-1_all.deb
sudo apt-get install -f
```
*(Not: Dosyalar uygulamasındaki entegrasyon anında aktif olur, GNOME Shell eklentisi için kurulum sonrası oturumu kapatıp açmanız yeterlidir).*

### Manuel Kurulum
```bash
# Core kütüphane
sudo mkdir -p /usr/share/pardus/desktop-shortcut
sudo cp src/desktop_shortcut.py /usr/share/pardus/desktop-shortcut/

# CLI aracı
sudo cp src/pardus-desktop-shortcut-cli /usr/bin/pardus-desktop-shortcut
sudo chmod +x /usr/bin/pardus-desktop-shortcut

# Nautilus extension
sudo cp nautilus/pardus-desktop-shortcut.py /usr/share/nautilus-python/extensions/

# GNOME Shell extension
sudo mkdir -p /usr/share/gnome-shell/extensions/pardus-desktop-shortcut@pardus.org.tr/
sudo cp gnome-shell-extension/* /usr/share/gnome-shell/extensions/pardus-desktop-shortcut@pardus.org.tr/

# Nautilus'u yeniden başlat
nautilus -q

# GNOME Shell extension'ı etkinleştir
gnome-extensions enable pardus-desktop-shortcut@pardus.org.tr
```

## Bağımlılıklar
- `python3` (>= 3.6)
- `python3-gi` (GTK/GObject introspection)
- `python3-nautilus` (Nautilus Python extension desteği)
- `gnome-shell` (GNOME Shell extension desteği)

## Lisans
GPL-3.0 — [LICENSE](LICENSE) dosyasına bakınız.