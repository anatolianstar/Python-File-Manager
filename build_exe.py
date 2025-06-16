#!/usr/bin/env python3
"""
Python File Manager - Executable Builder
PyInstaller ile .exe dosyası oluşturma scripti
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Gerekli bağımlılıkları kontrol et"""
    print("🔍 Bağımlılıklar kontrol ediliyor...")
    
    try:
        import PyInstaller
        print("✅ PyInstaller kurulu")
    except ImportError:
        print("❌ PyInstaller kurulu değil")
        print("📦 PyInstaller kuruluyor...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0"])
            print("✅ PyInstaller başarıyla kuruldu")
        except Exception as e:
            print(f"❌ PyInstaller kurulumu başarısız: {e}")
            return False
    
    return True

def prepare_build_directory():
    """Build dizinini hazırla"""
    print("📁 Build dizini hazırlanıyor...")
    
    # Eski build dosyalarını temizle
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("🗑️ Eski dist klasörü temizlendi")
    
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("🗑️ Eski build klasörü temizlendi")
    
    # Geçici spec dosyasını sil
    spec_file = "main_modular.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"🗑️ Eski {spec_file} silindi")

def create_exe():
    """PyInstaller ile .exe dosyası oluştur"""
    print("🔨 .exe dosyası oluşturuluyor...")
    
    # PyInstaller komut parametreleri
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Tek dosya olarak paketle
        "--windowed",                   # Console window gösterme
        "--name=Python-File-Manager",   # Exe dosya adı
        "--icon=icon.ico",              # İkon (varsa)
        "--add-data=languages;languages",  # Dil dosyaları
        "--add-data=*.json;.",          # JSON ayar dosyaları
        "--hidden-import=tkinter",      # Tkinter modülü
        "--hidden-import=threading",    # Threading modülü
        "--hidden-import=hashlib",      # Hashlib modülü
        "--hidden-import=shutil",       # Shutil modülü
        "--hidden-import=json",         # JSON modülü
        "--hidden-import=os",           # OS modülü
        "--hidden-import=sys",          # Sys modülü
        "--hidden-import=time",         # Time modülü
        "--hidden-import=pathlib",      # Pathlib modülü
        "--hidden-import=collections",  # Collections modülü
        "--hidden-import=traceback",    # Traceback modülü
        "--collect-all=tkinter",        # Tüm tkinter bileşenleri
        "--noconsole",                  # Console penceresi açma
        "--clean",                      # Temiz build
        "main_modular.py"               # Ana Python dosyası
    ]
    
    # İkon dosyası yoksa parametreyi kaldır
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
        print("⚠️ icon.ico bulunamadı, ikon olmadan devam ediliyor")
    
    try:
        print("⏳ PyInstaller çalıştırılıyor... (Bu işlem birkaç dakika sürebilir)")
        subprocess.check_call(cmd)
        print("✅ .exe dosyası başarıyla oluşturuldu!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller hatası: {e}")
        return False
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return False

def post_build_tasks():
    """Build sonrası görevler"""
    print("📦 Post-build görevleri...")
    
    exe_path = os.path.join("dist", "Python-File-Manager.exe")
    
    if os.path.exists(exe_path):
        # Dosya boyutunu kontrol et
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"📏 .exe dosya boyutu: {size_mb:.1f} MB")
        
        # Dil dosyalarını dist klasörüne kopyala
        if os.path.exists("languages"):
            dist_languages = os.path.join("dist", "languages")
            if not os.path.exists(dist_languages):
                shutil.copytree("languages", dist_languages)
                print("🌍 Dil dosyaları kopyalandı")
        
        # README dosyasını kopyala
        if os.path.exists("README.md"):
            shutil.copy("README.md", "dist/README.md")
            print("📄 README.md kopyalandı")
        
        # LICENSE dosyasını kopyala
        if os.path.exists("LICENSE"):
            shutil.copy("LICENSE", "dist/LICENSE")
            print("📜 LICENSE kopyalandı")
        
        print(f"🎉 Başarılı! .exe dosyası: {exe_path}")
        print(f"📂 Dist klasörü: {os.path.abspath('dist')}")
        
        return True
    else:
        print("❌ .exe dosyası oluşturulamadı")
        return False

def create_installer_script():
    """Kurulum scripti oluştur"""
    print("📦 Kurulum scripti oluşturuluyor...")
    
    installer_content = '''@echo off
echo 🚀 Python File Manager v3.0 Installer
echo.
echo Bu program dosyalarınızı organize etmenize yardımcı olur.
echo.
echo 📁 Kurulum dizini: %CD%
echo.
echo ✅ Kurulum tamamlanmıştır!
echo.
echo 🎯 Çalıştırmak için: Python-File-Manager.exe
echo.
pause
'''
    
    with open("dist/install.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)
    
    print("✅ install.bat oluşturuldu")

def main():
    """Ana build fonksiyonu"""
    print("🚀 Python File Manager .exe Builder")
    print("=" * 50)
    
    # Bağımlılıkları kontrol et
    if not check_dependencies():
        print("❌ Bağımlılık kontrolü başarısız")
        return False
    
    # Build dizinini hazırla
    prepare_build_directory()
    
    # .exe dosyası oluştur
    if not create_exe():
        print("❌ .exe oluşturma başarısız")
        return False
    
    # Post-build görevleri
    if not post_build_tasks():
        print("❌ Post-build görevleri başarısız")
        return False
    
    # Kurulum scripti oluştur
    create_installer_script()
    
    print("=" * 50)
    print("🎉 BUILD BAŞARILI!")
    print("📂 Dosyalar 'dist' klasöründe")
    print("🎯 Çalıştırmak için: dist/Python-File-Manager.exe")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            input("\n🎉 Build tamamlandı! Çıkmak için Enter tuşuna basın...")
        else:
            input("\n❌ Build başarısız! Çıkmak için Enter tuşuna basın...")
    except KeyboardInterrupt:
        print("\n\n⏹️ Build kullanıcı tarafından iptal edildi")
    except Exception as e:
        print(f"\n❌ Kritik hata: {e}")
        input("Çıkmak için Enter tuşuna basın...") 