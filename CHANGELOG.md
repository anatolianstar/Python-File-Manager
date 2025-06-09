# 📝 Changelog - Python File Manager

Tüm önemli değişiklikler bu dosyada belgelenmiştir.

Format [Keep a Changelog](https://keepachangelog.com/tr/1.0.0/) tabanlıdır,
ve bu proje [Semantic Versioning](https://semver.org/lang/tr/) kullanır.

## [3.0.0] - 2024-12-19

### 🎉 **Yeni Özellikler**

#### 🌍 **Multi-Language Support**
- **Dinamik dil sistemi** eklendi (`lang_manager.py`)
- **JSON-based i18n** - Kolay çeviri yönetimi
- **Otomatik fallback** - Eksik çevirilerde İngilizce göster
- **GUI dil seçici** - Gerçek zamanlı dil değişimi
- **Türkçe ve İngilizce** tam destek

#### 🧠 **Smart Category Learning**
- **Kullanıcı davranış öğrenme** sistemi
- **Dosya taşıma tercihlerini** hatırlama
- **JSON-based hafıza** (`~/.file_manager_learned_categories.json`)
- **Otomatik kategori önerileri** öğrenilen tercihlere göre

#### 🔄 **Advanced Folder Merging**
- **Akıllı klasör birleştirme** sistemi
- **Çakışma çözüm diyalogları** (merge/rename/cancel)
- **Dosya çakışması yönetimi** (skip/overwrite seçenekleri)
- **Global işlem modları** (skip all/overwrite all)

#### 🛡️ **Secure File Operations**
- **Multi-stage verification** - Kopyala→Doğrula→Sil→Onayla
- **Dosya kaybı koruması** - Güvenli taşıma sistemi
- **Hash verification** - Dosya bütünlüğü kontrolü
- **Detaylı progress tracking** - İşlem durumu takibi

### 🔧 **Geliştirmeler**

#### 📂 **Kategori Sistemi**
- **40+ yeni dosya uzantısı** eklendi
- **CAD/3D dosya** desteği (STL, OBJ, 3MF, STEP, IGES)
- **Font dosyaları** kategorisi (TTF, OTF, WOFF)
- **Kod dosyaları** genişletildi (GO, RUST, KOTLIN)
- **Modern görüntü formatları** (WebP, AVIF, HEIC)

#### 🎨 **GUI Geliştirmeleri**
- **Language switcher widget** eklendi
- **Çakışma diyalogları** modern tasarım
- **Progress bar** iyileştirmeleri
- **Emoji destekli** mesaj sistemi
- **Responsive layout** düzenlemeleri

#### ⚡ **Performans**
- **Threading** optimizasyonları
- **Memory usage** iyileştirmeleri  
- **File scanning** hızlandırma
- **Async operations** için hazırlık

### 🐛 **Hata Düzeltmeleri**
- **Folder merge** sırasında dosya kaybı sorunu
- **Unicode karakterler** ile dosya adları
- **Long path support** Windows'ta
- **Memory leak** thread işlemlerinde
- **GUI freezing** büyük dosya işlemlerinde

### 🗑️ **Kaldırılan Özellikler**
- Eski **hardcoded strings** tamamen kaldırıldı
- **Duplicate code** temizlendi
- **Legacy functions** modernize edildi

---

## [2.0.0] - 2024-12-15

### 🎉 **Yeni Özellikler**
- **Modular architecture** - Kod tabanı 5 modüle ayrıldı
- **Advanced reporting** - Detaylı işlem raporları
- **Duplicate detection** - MD5 hash tabanlı
- **Enhanced file operations** - Güvenli taşıma sistemi
- **Category learning** - Temel öğrenme sistemi

### 🔧 **Geliştirmeler**
- **GUI modernizasyonu** - Tkinter ttk widgets
- **Better error handling** - Comprehensive exception handling
- **Logging system** - Debug ve info level logging
- **Configuration management** - JSON tabanlı ayarlar

### 🐛 **Hata Düzeltmeleri**
- **File permission** hataları
- **Path encoding** sorunları
- **Memory optimization** büyük dosyalar için

---

## [1.0.0] - 2024-12-01

### 🚀 **İlk Sürüm**
- **Temel dosya organizasyonu** - Kategori tabanlı düzenleme
- **Basit GUI arayüzü** - Tkinter tabanlı
- **File categorization** - 15+ kategori desteği
- **Drag & drop** - Temel sürükle bırak
- **Progress tracking** - Basit ilerleme göstergesi

### 📂 **Desteklenen Kategoriler**
- Resim dosyaları (JPG, PNG, GIF)
- Video dosyaları (MP4, AVI, MKV)
- Ses dosyaları (MP3, WAV, FLAC)
- Belge dosyaları (PDF, DOCX, TXT)
- Arşiv dosyaları (ZIP, RAR, 7Z)

---

## 🚀 **Gelecek Planları**

### v3.1.0 (Planlanan)
- [ ] **More languages** - Almanca, Fransızca
- [ ] **Themes support** - Dark/Light mode
- [ ] **Plugin system** - Genişletilecek mimari
- [ ] **Cloud integration** - Google Drive, Dropbox

### v4.0.0 (Uzun vadeli)
- [ ] **Machine learning** - Gelişmiş kategori öğrenme
- [ ] **Web interface** - Browser tabanlı yönetim
- [ ] **Mobile companion** - Mobil uygulama
- [ ] **Real-time sync** - Çoklu cihaz senkronizasyonu

---

## 📊 **İstatistikler**

| Versiyon | Satır Sayısı | Dosya Sayısı | Özellik Sayısı |
|----------|--------------|--------------|----------------|
| v1.0.0   | ~800         | 1            | 5              |
| v2.0.0   | ~1,500       | 5            | 15             |
| v3.0.0   | ~2,300       | 7            | 25+            |

---

## ⚠️ **Breaking Changes**

### v3.0.0
- **API değişiklikleri**: Tüm string literals `t()` fonksiyonu ile değiştirildi
- **Config format**: Yeni JSON tabanlı dil ayarları
- **File structure**: Yeni `languages/` klasör yapısı

### v2.0.0  
- **Module structure**: Tek dosyadan çoklu modül yapısına geçiş
- **Function names**: CamelCase'den snake_case'e geçiş
- **Config location**: Ayar dosyaları yeni konumda

---

**📅 Son güncelleme**: 2024-12-19  
**🔗 Repository**: [GitHub Link]  
**👤 Geliştirici**: [Your Name] 