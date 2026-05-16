# pardus-desktop-shortcut

GNOME masaüstünde uygulamaları kolayca masaüstüne eklemeyi sağlayan araç.

Pardus ve diğer Debian tabanlı GNOME dağıtımlarında çalışır.

## Problem

GNOME masaüstünde sürükle-bırak ile uygulama kısayolu oluşturma desteği bulunmamaktadır. Kullanıcıların `.desktop` dosyalarını manuel olarak kopyalayıp, çalıştırılabilir hale getirip, "Allow Launching" işaretlemesi gerekmektedir.

## Çözüm

Bu araç **3 farklı entegrasyon noktası** sunar:

### 1. 📁 Nautilus Sağ-Tık Menüsü

Nautilus (Dosyalar) uygulamasında herhangi bir `.desktop` dosyasına sağ tıkladığınızda **"Masaüstüne Ekle"** seçeneği görünür.

### 2. 🔲 GNOME Uygulama Menüsü

GNOME Activities (Etkinlikler) → Uygulamalar bölümünde herhangi bir uygulama ikonuna sağ tıkladığınızda **"Masaüstüne Ekle"** seçeneği görünür.

### 3. 💻 Komut Satırı Aracı

```bash
# Bir uygulamayı masaüstüne ekle
pardus-desktop-shortcut --add firefox

# Tam yol ile ekle
pardus-desktop-shortcut --add /usr/share/applications/firefox.desktop

# Sıfırdan oluştur
pardus-desktop-shortcut --create --name "Uygulamam" --exec "/usr/bin/app" --icon "app-icon"

# Masaüstünden kaldır
pardus-desktop-shortcut --remove firefox.desktop

# Yüklü uygulamaları listele
pardus-desktop-shortcut --list
```

## Kurulum

### Debian/Pardus Paketi ile

```bash
# .deb paketi oluştur
dpkg-buildpackage -us -uc -b

# Paketi yükle
sudo dpkg -i ../pardus-desktop-shortcut_1.0.0-1_all.deb

# Bağımlılıkları tamamla
sudo apt-get install -f
```

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

## Dosya Yapısı

```
pardus-desktop-shortcut/
├── debian/                          # Debian paketleme
│   ├── control                      # Paket meta verileri
│   ├── rules                        # Derleme kuralları
│   ├── changelog                    # Sürüm geçmişi
│   ├── copyright                    # Lisans bilgisi
│   ├── install                      # Dosya kurulum eşlemeleri
│   └── source/format
├── src/
│   ├── desktop_shortcut.py          # Core Python kütüphanesi
│   └── pardus-desktop-shortcut-cli  # Komut satırı aracı
├── nautilus/
│   └── pardus-desktop-shortcut.py   # Nautilus sağ-tık extension
├── gnome-shell-extension/
│   ├── extension.js                 # GNOME Shell extension
│   └── metadata.json                # Extension meta verileri
├── README.md
└── LICENSE                          # GPL-3.0
```

## Nasıl Çalışır?

1. Seçilen `.desktop` dosyası kullanıcının masaüstü dizinine kopyalanır
2. `chmod +x` ile çalıştırılabilir hale getirilir
3. `gio set metadata::trusted true` ile GNOME'da "Allow Launching" otomatik olarak işaretlenir
4. Masaüstü dizini XDG standardına göre belirlenir (`$XDG_DESKTOP_DIR`, `~/Desktop`, `~/Masaüstü`)

## Katkıda Bulunma

1. Bu repoyu fork'layın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: yeni özellik'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

## Lisans

GPL-3.0 — [LICENSE](LICENSE) dosyasına bakınız.

## İletişim

- GitHub: [@umutKaracelebi](https://github.com/umutKaracelebi)
- Pardus Topluluk: [forum.pardus.org.tr](https://forum.pardus.org.tr)
