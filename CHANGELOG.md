# Changelog

Tüm önemli değişiklikler bu dosyada belgelenecektir.

## [1.1.0] - 2024-12-XX - Çeviri Sistemi Entegrasyonu

### Eklenen Özellikler
- 🌐 **Tam Çeviri Sistemi Entegrasyonu**: Tüm modüller artık çeviri sistemini destekliyor
- 🔍 **Duplicate Finder Çeviri Desteği**: Image ve File Duplicate Finder modülleri tam çeviri desteği
- 🔄 **Dinamik Dil Değiştirme**: Uygulama çalışırken dil değiştirme özelliği
- 📝 **Genişletilmiş Çeviri Dosyaları**: Tüm UI elementleri için kapsamlı çeviri desteği

### Düzeltilen Hatalar
- 🐛 Layout manager çakışması düzeltildi (grid/pack karışımı)
- 🔧 Duplicate finder modüllerinde eksik metodlar eklendi
- ⚡ UI thread güvenliği iyileştirildi
- 🎯 Çeviri anahtarları standardize edildi

### Teknik İyileştirmeler
- 📦 Modüler çeviri sistemi mimarisi
- 🔗 Tüm modüller arası çeviri bağlantıları
- 🛡️ Thread-safe çeviri güncellemeleri
- 📊 Çeviri kapsama analizi

## [1.0.0] - 2024-01-XX - İlk Sürüm

### Eklenen Özellikler
- 🧠 Akıllı dosya kategorizasyon sistemi
- 🔍 MD5 hash tabanlı dublicate kontrolü
- ⚡ Çoklu thread desteği ile hızlı dosya işlemleri
- 📊 Detaylı operasyon raporları
- 🌐 Çoklu dil desteği (Türkçe/İngilizce)
- 📁 Derin klasör yapısı desteği
- 🎓 Öğrenen sistem - kullanıcı tercihlerini hatırlama
- 🛠️ Gelişmiş dosya yöneticisi özellikleri
- 🔄 Dublicate dosya yönetimi (atla/kopyala/birleştir)
- 📈 Gerçek zamanlı ilerleme takibi

### Modüler Yapı
- `main_modular.py` - Ana uygulama koordinatörü
- `gui_manager.py` - Kullanıcı arayüzü yönetimi
- `file_operations.py` - Dosya işlemleri
- `scan_engine.py` - Dosya tarama ve analiz motoru
- `reporting.py` - Raporlama sistemi
- `lang_manager.py` - Çoklu dil desteği
- `language_switcher.py` - Dil değiştirici widget
- `duplicate_image_finder.py` - Resim dublicate bulucu
- `duplicate_file_finder.py` - Dosya dublicate bulucu

### Desteklenen Dosya Kategorileri
- 🖼️ Resim Dosyaları (jpg, png, gif, bmp, svg, etc.)
- 🎥 Video Dosyaları (mp4, avi, mkv, mov, wmv, etc.)
- 🎵 Audio Dosyaları (mp3, wav, flac, aac, ogg, etc.)
- 📄 Doküman Dosyaları (pdf, doc, docx, txt, xls, etc.)
- 💾 Program Dosyaları (exe, msi, deb, rpm, dmg, etc.)
- 🗜️ Sıkıştırılmış Dosyalar (zip, rar, 7z, tar, gz, etc.)
- 🛠️ CAD & 3D Dosyaları (dwg, step, stl, obj, blend, etc.)
- 💻 Kod Dosyaları (py, js, html, css, java, etc.)
- 🔤 Font Dosyaları (ttf, otf, woff, woff2, etc.)
- 📦 Yazılım Paketleri ve klasörleri

### Teknik Özellikler
- Python 3.7+ desteği
- Tkinter tabanlı modern arayüz
- Thread-safe operasyonlar
- Bellek optimizasyonu
- Kapsamlı hata yönetimi
- Configurable ayarlar
- Otomatik backup sistemi 