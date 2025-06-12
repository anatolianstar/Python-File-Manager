# 🗂️ Akıllı Dublicate Kontrollü Dosya Dağıtım Programı

[🇬🇧 English](README_EN.md) | 🇹🇷 Türkçe

**Gelişmiş dosya organizasyon ve dağıtım aracı** - Dosyalarınızı akıllı kategorizasyon ve dublicate kontrolü ile otomatik olarak organize eder.

## 🌟 Program Özellikleri

### 🧠 Akıllı Kategorizasyon Sistemi
- **Otomatik dosya sınıflandırması**: 15+ farklı kategori (resim, video, audio, doküman, program dosyaları vb.)
- **Öğrenen sistem**: Kullanıcı tercihlerini hatırlar ve öğrenir
- **Hedef odaklı kategorizasyon**: Belirli klasör yapılarına göre özelleşen kategoriler
- **Esnek kategori yönetimi**: Yeni kategoriler ekleyebilme ve mevcut kategorileri düzenleyebilme

### 🔍 Dublicate Kontrolü ve Güvenlik
- **MD5 hash tabanlı dublicate kontrolü**: Aynı içeriğe sahip dosyaları tespit eder
- **Güvenli kopyalama**: Dosya bütünlüğünü korur
- **Çakışma önleme**: Aynı isimli farklı dosyalar otomatik olarak yeniden adlandırılır
- **Hata toleransı**: Başarısız operasyonlar sistemi durdurmaz

### ⚡ Performans ve Kullanıcı Deneyimi
- **Paralel işlemler**: Çoklu thread desteği ile hızlı kopyalama
- **Gerçek zamanlı ilerleme takibi**: Tüm alt klasörler dahil doğru ilerleme gösterimi
- **Detaylı operasyon raporları**: Başarılı, atlanan ve başarısız operasyonların detayları
- **Kullanıcı dostu arayüz**: Türkçe menü ve mesajlar
- **Geniş dosya format desteği**: 100+ dosya uzantısı desteği

### 📁 Klasör İşlemleri
- **Derin klasör yapısı desteği**: Alt klasörler dahil tam organizasyon
- **Klasör birleştirme**: Aynı kategorideki klasörler otomatik birleştirilir
- **Yapı koruma**: Önemli klasör yapıları korunur
- **Seçici organizasyon**: Belirli dosya türlerini organize etme seçeneği

## 🛠️ Kurulum

### Gereksinimler
- Python 3.7 veya üzeri
- tkinter (genellikle Python ile birlikte gelir)
- threading, shutil, hashlib (standart kütüphaneler)

### Kurulum Adımları
1. **Projeyi indirin:**
   ```bash
   git clone https://github.com/[YOUR_USERNAME]/Python-File-Manager.git
   cd Python-File-Manager
   ```

2. **Programı çalıştırın:**
   ```bash
   python main_modular.py
   ```

## 🚀 Kullanım Kılavuzu

### Ana Özellikler

#### 1. 📋 Dosya Tarama ve Seçim
- **Klasör seçimi**: Organize edilecek kaynak klasörünü seçin
- **Dosya filtreleme**: Belirli dosya türlerini seçerek organize edin
- **Önizleme**: Hangi dosyaların nereye gideceğini önceden görün

#### 2. 🎯 Hedef Klasör Ayarları
- **Hedef konumu seçin**: Dosyaların organize edileceği klasörü belirleyin
- **Kategori yapısı**: Otomatik oluşturulan kategori klasörlerini önizleyin
- **Özelleştirilmiş organizasyon**: İhtiyaçlarınıza göre kategori ayarları

#### 3. ⚙️ Organize İşlemi
- **Tek tıkla organizasyon**: "Organize Et" butonuna basın
- **İlerleme takibi**: Gerçek zamanlı ilerleme çubuğu ve detay bilgileri
- **Hata yönetimi**: Başarısız işlemler otomatik olarak raporlanır

#### 4. 📊 Sonuç Raporları
- **Detaylı istatistikler**: Kopyalanan, atlanan ve başarısız dosya sayıları
- **Kategori dağılımı**: Hangi kategoriye kaç dosya yerleştirildiği
- **Hata analizi**: Başarısız operasyonların sebepleri

### Gelişmiş Özellikler

#### 🎓 Öğrenen Sistem
Program, kullanıcı tercihlerini öğrenir ve gelecekteki organizasyonlarda bu bilgileri kullanır:
- Manuel kategori atamalarını hatırlar
- Sık kullanılan klasör yapılarını tanır
- Dosya türü tercihleri kaydedilir

#### 🔄 Dublicate Yönetimi
- **Akıllı dublicate tespiti**: Aynı içeriğe sahip dosyalar tespit edilir
- **Esnek dublicate işleme**: Atla, yeniden adlandır veya üzerine yaz seçenekleri
- **Güvenli işlemler**: Orijinal dosyalar korunur

#### 📁 Kategori Yönetimi
```
📁 Organize Edilmiş Dosyalar/
├── 🖼️ Resim Dosyaları/
│   ├── .jpg, .png, .gif, .bmp, .svg
├── 🎥 Video Dosyaları/
│   ├── .mp4, .avi, .mkv, .mov, .wmv
├── 🎵 Audio Dosyaları/
│   ├── .mp3, .wav, .flac, .aac, .ogg
├── 📄 Doküman Dosyaları/
│   ├── .pdf, .doc, .docx, .txt, .xls
├── 💾 Program Dosyaları/
│   ├── .exe, .msi, .deb, .rpm, .dmg
├── 🗜️ Sıkıştırılmış Dosyalar/
│   ├── .zip, .rar, .7z, .tar, .gz
├── 🛠️ CAD & 3D Dosyaları/
│   ├── .dwg, .step, .stl, .obj, .blend
├── 💻 Kod Dosyaları/
│   ├── .py, .js, .html, .css, .java
├── 🔤 Font Dosyaları/
│   ├── .ttf, .otf, .woff, .woff2
└── 📦 Yazılım Paketleri/
    ├── Kurulum dosyaları ve klasörleri
```

## 🔧 Teknik Detaylar

### Sistem Mimarisi
- **Modüler tasarım**: Her özellik ayrı modül olarak geliştirilmiş
- **Thread güvenliği**: Paralel işlemler için güvenli thread yönetimi
- **Bellek optimizasyonu**: Büyük dosya işlemleri için verimli bellek kullanımı
- **Hata kurtarma**: Sistem çökmelerini önleyen kapsamlı hata yönetimi

### Performans Özellikleri
- **Paralel kopyalama**: Çoklu dosya aynı anda işlenir
- **Akıllı önbellekleme**: Sık kullanılan bilgiler önbelleğe alınır
- **Progresif yükleme**: Büyük klasör yapıları kademeli olarak işlenir
- **Kaynak yönetimi**: CPU ve bellek kullanımı optimize edilmiştir

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak istiyorsanız:

1. **Fork yapın** ve kendi branch'inizi oluşturun
2. **Özellik geliştirin** veya bug düzeltmesi yapın
3. **Test edin** - değişikliklerinizi kapsamlı olarak test edin
4. **Pull request gönderin** - detaylı açıklama ile birlikte

### Geliştirme Rehberi
- Kod standartlarına uyun (PEP 8)
- Docstring'leri eksiksiz yazın
- Unit test'ler ekleyin
- Türkçe yorum satırları kullanın

## 📝 Lisans

Bu proje MIT lisansı altında dağıtılmaktadır. Detaylar için `LICENSE` dosyasına bakınız.

## 🐛 Hata Bildirimi

Hata bulursanız veya öneriniz varsa:
- **GitHub Issues** bölümünü kullanın
- **Detaylı açıklama** ekleyin
- **Hata tekrarlanabilir adımlar** belirtin
- **Sistem bilgilerinizi** paylaşın

## 📚 Sık Sorulan Sorular

**Q: Program hangi işletim sistemlerinde çalışır?**
A: Windows, macOS ve Linux'te çalışır. Python 3.7+ gereklidir.

**Q: Büyük dosyalar işlenebilir mi?**
A: Evet, program büyük dosyaları verimli şekilde işler. Bellek kullanımı optimize edilmiştir.

**Q: Kategori ayarları özelleştirilebilir mi?**
A: Evet, hem mevcut kategoriler düzenlenebilir hem de yeni kategoriler eklenebilir.

**Q: Dublicate dosyalar nasıl tespit edilir?**
A: MD5 hash algoritması kullanılarak dosya içerikleri karşılaştırılır.

**Q: Orijinal dosyalar güvende mi?**
A: Evet, program sadece kopyalama yapar, orijinal dosyaları silmez.

---

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**

📧 **İletişim**: [GitHub Issues](https://github.com/[YOUR_USERNAME]/Python-File-Manager/issues)
🐛 **Bug Report**: [Hata Bildirimi](https://github.com/[YOUR_USERNAME]/Python-File-Manager/issues/new)
💡 **Feature Request**: [Özellik Önerisi](https://github.com/[YOUR_USERNAME]/Python-File-Manager/issues/new)
