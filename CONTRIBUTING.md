# 🤝 Python File Manager'a Katkıda Bulunma Rehberi

Python File Manager projesine katkıda bulunduğunuz için teşekkürler! 🎉

## 📋 Katkı Türleri

### 🐛 Bug Raporları
- GitHub Issues kullanarak bug raporu açın
- Hatayı açık şekilde tarif edin
- Adım adım tekrar etme talimatları verin
- Ekran görüntüleri ekleyin (varsa)
- Sistem bilgilerinizi paylaşın (OS, Python versiyonu)

### ✨ Özellik Önerileri
- Yeni özellik için Issue açın
- Özelliğin ne işe yarayacağını açıklayın
- Mümkünse mockup veya örnek görseller ekleyin
- Teknik detayları tartışın

### 🌍 Çeviri Katkıları
- `languages/` klasöründeki dil dosyalarını güncelleyin
- Yeni dil desteği eklemek için:
  1. `languages/` klasörüne yeni JSON dosyası ekleyin
  2. `lang_manager.py` dosyasını güncelleyin
  3. Test edin ve pull request gönderin

### 💻 Kod Katkıları
- Fork yapın ve yeni branch oluşturun
- Kod standartlarına uyun (PEP 8)
- Docstring'leri eksiksiz yazın
- Test edin
- Pull request gönderin

## 🔧 Geliştirme Ortamı Kurulumu

### 1. Repository'yi Fork Edin
```bash
# GitHub'da fork yapın, sonra clone edin
git clone https://github.com/YOUR_USERNAME/Python-File-Manager.git
cd Python-File-Manager
```

### 2. Development Branch Oluşturun
```bash
git checkout -b feature/your-feature-name
# veya
git checkout -b bugfix/bug-description
```

### 3. Değişiklikleri Yapın
- Kodunuzu yazın
- Testlerinizi yapın
- Commit'lerinizi yapın

### 4. Pull Request Gönderin
```bash
git push origin feature/your-feature-name
```
GitHub'da pull request oluşturun.

## 📝 Kod Standartları

### Python Style Guide
- **PEP 8** standartlarına uyun
- **4 space** indentation kullanın
- **Turkish comments** yazın (kod içi yorumlar)
- **English docstrings** yazın (fonksiyon dokümantasyonu için)

### Örnek Kod Formatı
```python
def process_files(source_path, target_path, file_types=None):
    """
    Process files from source to target directory.
    
    Args:
        source_path (str): Source directory path
        target_path (str): Target directory path
        file_types (list, optional): File extensions to process
    
    Returns:
        dict: Processing results with counts
    """
    # Kaynak klasör kontrolü yap
    if not os.path.exists(source_path):
        raise ValueError("Kaynak klasör bulunamadı")
    
    # İşlem başlat
    results = {"success": 0, "failed": 0}
    return results
```

### Commit Message Format
```
<type>: <description>

Types:
- feat: Yeni özellik
- fix: Bug düzeltmesi
- docs: Dokümantasyon
- style: Kod formatı
- refactor: Kod refactor
- test: Test ekleme
- chore: Yapılandırma değişiklikleri
```

## 🧪 Test Etme

### Manuel Test Adımları
1. **Program Başlatma**: `python main_modular.py`
2. **Klasör Seçimi**: Kaynak ve hedef klasör seçin
3. **Dosya Tarama**: Scan butonunu test edin
4. **Organizasyon**: Organize butonunu test edin
5. **Dil Değişimi**: Dil değiştirme özelliğini test edin

### Test Checklist
- [ ] Program başlıyor mu?
- [ ] Tüm butonlar çalışıyor mu?
- [ ] Hata mesajları doğru mu?
- [ ] Dil değişimi çalışıyor mu?
- [ ] Dosya işlemleri güvenli mi?

## 🚀 Pull Request Süreci

### 1. PR Öncesi Kontrol
- [ ] Kod PEP 8 standartlarına uygun
- [ ] Tüm testler geçiyor
- [ ] Dokümantasyon güncellendi
- [ ] CHANGELOG.md güncellendi (önemli değişiklikler için)

### 2. PR Template
```markdown
## Değişiklik Türü
- [ ] Bug düzeltmesi
- [ ] Yeni özellik
- [ ] Dokümantasyon güncellemesi
- [ ] Performans iyileştirmesi

## Açıklama
Değişikliğinizi kısaca açıklayın...

## Test Edildi Mi?
- [ ] Manuel test yapıldı
- [ ] Farklı işletim sistemlerinde test edildi

## Screenshots
Ekran görüntüleri ekleyin (varsa)
```

### 3. Code Review
- Maintainer'lar kodunuzu inceleyecek
- Gerekirse değişiklik isteyebilirler
- Onaylandıktan sonra merge edilecek

## 🏷️ Issue Labels

- `bug` - Hata raporu
- `enhancement` - Yeni özellik
- `documentation` - Dokümantasyon
- `good first issue` - Yeni katkıcılar için
- `help wanted` - Yardım gerekiyor
- `translation` - Çeviri ile ilgili
- `priority-high` - Yüksek öncelik
- `priority-low` - Düşük öncelik

## 🌟 Katkıcı Rehberi

### İlk Katkınız mı?
1. "good first issue" etiketli issue'lara bakın
2. Küçük bir düzeltme ile başlayın
3. Pull request sürecini öğrenin
4. Community ile etkileşime geçin

### Büyük Değişiklikler
- Büyük özellikler için önce Issue açın
- Teknik detayları tartışın
- Implementation planı yapın
- Adım adım geliştirin

## 📞 İletişim

### GitHub
- **Issues**: https://github.com/anatolianstar/Python-File-Manager/issues
- **Discussions**: Genel konuşmalar için

### Soru Sorma
- Issue açmaktan çekinmeyin
- "question" etiketi kullanın
- Açık ve detaylı sorular sorun

## 🎉 Teşekkürler

Her katkınız değerlidir! Projeyi geliştirmek için zaman ayırdığınız için teşekkürler.

### Hall of Fame
Katkıda bulunanlar:
- [@anatolianstar] - Project maintainer
- Katkınızı buraya ekleyelim! 🌟

---

**📚 Daha fazla bilgi için GITHUB_SETUP.md dosyasına bakın.** 