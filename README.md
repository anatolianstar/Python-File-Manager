# 🗂️ Advanced Python File Manager v3.0

[![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)

**Gelişmiş, modüler ve çok dilli dosya yönetim sistemi**

## 🚀 **Versiyon 3.0 - Yeni Özellikler**

### 🌍 **Multi-Language Support**
- **Dinamik dil değiştirme** - Program açıkken dil değiştir
- **JSON-based i18n** - Kolay çeviri sistemi
- **Otomatik fallback** - Eksik çeviri koruması
- **GUI dil seçici** - Tek tıkla dil değişimi

### 🧠 **Smart Category Learning**
- **Kullanıcı davranışlarını öğrenme** - Dosya taşıma tercihlerini hatırlama
- **Otomatik kategori önerisi** - Öğrenilen tercihlere göre organizasyon
- **JSON-based hafıza** - Öğrenilen bilgilerin kalıcı saklanması

### 🔄 **Advanced Folder Merging**
- **Akıllı klasör birleştirme** - Aynı isimli klasörleri otomatik birleştir
- **Çakışma çözümü** - Dosya ve klasör çakışmalarını yönet
- **Global işlem modları** - Tümünü atla/yaz seçenekleri

### 🛡️ **Secure File Operations**
- **Multi-stage verification** - Kopyala→Doğrula→Sil→Onayla
- **Dosya kaybı koruması** - Güvenli taşıma sistemi
- **Detaylı progress tracking** - İşlem durumu takibi

## 📦 **Kurulum**

### Gereksinimler
```bash
Python 3.7+
tkinter (genellikle Python ile birlikte gelir)
```

### Kurulum Adımları
```bash
# Repository'yi klonla
git clone https://github.com/USERNAME/Python-File-Manager.git
cd Python-File-Manager

# Programı çalıştır
python main_modular.py
```

## 🎯 **Kullanım**

### Temel İşlemler
1. **Kaynak klasör seç** - Organize edilecek dosyalar
2. **Hedef klasör seç** - Dosyaların organize edileceği yer
3. **Dosyaları tara** - Kategori analizi
4. **Organizasyonu başlat** - Otomatik düzenleme

### Dil Değiştirme
```python
from lang_manager import set_language, t

# Dil değiştir
set_language('en')  # English
set_language('tr')  # Türkçe

# Metin al
button_text = t('buttons.scan')
```

## 🏗️ **Proje Yapısı**

```
File-Manager/
├── 📁 Core System
│   ├── main_modular.py          # Ana program
│   ├── file_operations.py       # Dosya işlemleri
│   ├── scan_engine.py          # Tarama motoru
│   ├── gui_manager.py          # GUI yönetimi
│   └── reporting.py            # Raporlama
├── 📁 Multi-Language
│   ├── lang_manager.py         # Dil yönetimi
│   ├── language_switcher.py    # GUI dil seçici
│   └── languages/              # Dil dosyaları
│       ├── tr.json            # Türkçe
│       └── en.json            # English
└── 📁 Settings
    ├── language_settings.json  # Dil tercihleri
    └── learned_categories.json # Öğrenilen kategoriler
```

## 🔧 **Özellikler**

### 📂 **Dosya Kategorileri**
- **Görüntüler**: JPG, PNG, GIF, BMP, TIFF, WebP
- **Videolar**: MP4, AVI, MKV, MOV, WMV, FLV
- **Sesler**: MP3, WAV, FLAC, AAC, OGG
- **Belgeler**: PDF, DOCX, XLSX, PPTX, TXT
- **Kod Dosyaları**: PY, JS, HTML, CSS, JSON
- **3D/CAD**: STL, OBJ, 3MF, STEP, IGES
- **Arşivler**: ZIP, RAR, 7Z, TAR, GZ

### 🎨 **GUI Özellikleri**
- **Modern arayüz** - Tkinter tabanlı
- **Drag & Drop** - Dosya sürükle bırak
- **Progress bar** - İşlem durumu
- **Dil seçici** - Dinamik dil değişimi
- **Çakışma diyalogları** - Kullanıcı tercihi

### 🧠 **Akıllı Özellikler**
- **Kategori öğrenme** - Kullanıcı davranışlarını analiz
- **Otomatik öneriler** - Öğrenilen tercihlere göre
- **Hata toleransı** - Güvenli dosya işlemleri
- **Esnek konfigürasyon** - JSON tabanlı ayarlar

## 🌐 **Desteklenen Diller**

| Dil | Kod | Durum |
|-----|-----|-------|
| 🇹🇷 Türkçe | `tr` | ✅ Tam destek |
| 🇺🇸 English | `en` | ✅ Tam destek |
| 🇩🇪 Deutsch | `de` | 🚧 Planlanan |
| 🇫🇷 Français | `fr` | 🚧 Planlanan |

## 🔄 **Versiyon Geçmişi**

### v3.0 (2024)
- ✨ Multi-language support
- 🧠 Smart category learning
- 🔄 Advanced folder merging
- 🛡️ Secure file operations
- 🎨 Modern GUI improvements

### v2.0 (2024)
- 📂 Modular architecture
- 🏗️ Enhanced file operations
- 📊 Advanced reporting
- 🎯 Better categorization

### v1.0 (2024)
- 🚀 Initial release
- 📁 Basic file organization
- 🖥️ Simple GUI interface

## 🤝 **Katkıda Bulunma**

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📝 **Yeni Dil Ekleme**

```python
# Yeni dil dosyası oluştur
from lang_manager import lang_manager

# Almanca dil dosyası oluştur
german_texts = {
    "app": {"title": "Datei-Organizer"},
    "buttons": {"scan": "Dateien scannen"}
    # ... diğer çeviriler
}

lang_manager.create_language_file('de', german_texts)
```

## 🐛 **Bilinen Sorunlar**

- Windows'ta uzun dosya yolu sınırlaması
- Çok büyük dosyalarda (>2GB) yavaşlama
- Bazı özel karakterlerde encoding sorunu

## 📄 **Lisans**

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 **Destek**

- 🐛 **Bug Report**: GitHub Issues
- 💡 **Feature Request**: GitHub Discussions
- 📧 **İletişim**: GitHub Profile

---

**⭐ Projeyi beğendiyseniz yıldız verin!**

Made with ❤️ by [Your Name]
