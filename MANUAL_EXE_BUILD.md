# 🔨 Python File Manager - Manuel .exe Oluşturma Rehberi

## 📋 **Ön Koşullar**

### 1. Python Kurulumu Kontrolü
```cmd
python --version
```
Python 3.7+ olmalı. Yoksa indirin: https://python.org/downloads/

### 2. PyInstaller Kurulumu
```cmd
pip install pyinstaller
```

## 🚀 **Hızlı .exe Oluşturma**

### Temel Komut:
```cmd
pyinstaller --onefile --windowed --name="Python-File-Manager" main_modular.py
```

### Detaylı Komut:
```cmd
pyinstaller ^
    --onefile ^
    --windowed ^
    --name="Python-File-Manager" ^
    --add-data="languages;languages" ^
    --add-data="*.json;." ^
    --hidden-import=tkinter ^
    --hidden-import=threading ^
    --hidden-import=hashlib ^
    --hidden-import=shutil ^
    --noconsole ^
    --clean ^
    main_modular.py
```

## 📁 **Adım Adım Talimatlar**

### 1. Terminali Açın
- Windows: `Win+R` → `cmd` → Enter
- PowerShell: `Win+X` → `Windows PowerShell`

### 2. Proje Klasörüne Gidin
```cmd
cd "C:\Users\MOSAIC\PycharmProjects\Python-File-Manager-main"
```

### 3. PyInstaller'ı Kurun (İlk sefer)
```cmd
pip install pyinstaller
```

### 4. .exe Dosyası Oluşturun
```cmd
pyinstaller --onefile --windowed --name="Python-File-Manager" --add-data="languages;languages" main_modular.py
```

### 5. Sonucu Kontrol Edin
- `dist` klasörü oluşur
- `dist/Python-File-Manager.exe` dosyası orada olur

## 🔧 **PyInstaller Parametreleri**

| Parametre | Açıklama |
|-----------|----------|
| `--onefile` | Tek .exe dosyası oluştur |
| `--windowed` | Konsol penceresi gösterme |
| `--noconsole` | Arka plan konsolu gizle |
| `--name="isim"` | .exe dosya adını belirle |
| `--add-data="src;dest"` | Ek dosyaları dahil et |
| `--hidden-import=modul` | Gizli modülleri dahil et |
| `--clean` | Önceki build'i temizle |
| `--icon=icon.ico` | İkon dosyası ekle |

## 🌍 **Dil Dosyalarını Dahil Etme**

### Windows:
```cmd
--add-data="languages;languages"
```

### Linux/Mac:
```cmd
--add-data="languages:languages"
```

## 📦 **Tam Özellikli Build Komutu**

```cmd
pyinstaller ^
    --onefile ^
    --windowed ^
    --name="Python-File-Manager-v3.0" ^
    --add-data="languages;languages" ^
    --add-data="*.json;." ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=threading ^
    --hidden-import=hashlib ^
    --hidden-import=shutil ^
    --hidden-import=json ^
    --hidden-import=os ^
    --hidden-import=sys ^
    --hidden-import=time ^
    --hidden-import=pathlib ^
    --hidden-import=collections ^
    --hidden-import=traceback ^
    --collect-all=tkinter ^
    --noconsole ^
    --clean ^
    --distpath="./release" ^
    main_modular.py
```

## 🐛 **Sık Karşılaşılan Sorunlar**

### 1. **PyInstaller bulunamadı**
```cmd
pip install --upgrade pyinstaller
```

### 2. **Modül import hatası**
Her eksik modül için:
```cmd
--hidden-import=module_name
```

### 3. **Dosya bulunamadı hatası**
```cmd
--add-data="source_file;destination"
```

### 4. **Tkinter hatası**
```cmd
--collect-all=tkinter
```

### 5. **Büyük dosya boyutu**
- `--exclude-module=modulename` kullanın  
- Gereksiz modülleri çıkarın

## 📋 **Build Sonrası Kontrol Listesi**

- [ ] `dist` klasöründe .exe dosyası var mı?
- [ ] .exe dosyası çalışıyor mu?
- [ ] Dil değiştirme çalışıyor mu?
- [ ] Tüm özellikler aktif mi?
- [ ] Dosya boyutu kabul edilebilir mi?

## 📊 **Beklenen Dosya Boyutları**

- **Minimal build**: ~15-25 MB
- **Tam build**: ~50-80 MB
- **Tüm modüllerle**: ~100-150 MB

## 🎯 **Optimizasyon İpuçları**

### Dosya Boyutunu Küçültme:
```cmd
--exclude-module=matplotlib
--exclude-module=numpy
--exclude-module=pandas
```

### Hızlı Başlatma:
```cmd
--onedir  # Onefile yerine
```

### Debug Modu:
```cmd
--debug=all
--console  # Hata mesajları için
```

## 📁 **Alternatif Build Script'i**

`build.bat` dosyası oluşturun:

```batch
@echo off
echo 🚀 Python File Manager .exe Builder
echo ================================

echo 📦 PyInstaller kuruluyor...
pip install pyinstaller

echo 🔨 .exe dosyası oluşturuluyor...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name="Python-File-Manager" ^
    --add-data="languages;languages" ^
    --noconsole ^
    --clean ^
    main_modular.py

echo ✅ Tamamlandı!
echo 📂 Dosya: dist\Python-File-Manager.exe
pause
```

Çalıştırmak için:
```cmd
build.bat
```

## 🌟 **İleri Düzey Özellikler**

### Dijital İmza Ekleme:
```cmd
signtool sign /f certificate.pfx /p password dist\Python-File-Manager.exe
```

### Version Info Ekleme:
```cmd
--version-file=version.txt
```

### Splash Screen:
```cmd
--splash=splash.png
```

## 📞 **Yardım**

Build sorunları için:
1. `pyinstaller --help` komutu
2. Log dosyalarını kontrol edin
3. GitHub Issues: https://github.com/anatolianstar/Python-File-Manager/issues

---

**🎉 Başarılı build sonrası `dist` klasöründe .exe dosyanız hazır olacak!** 