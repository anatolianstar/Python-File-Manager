#!/usr/bin/env python3
"""
Python File Manager - Executable Builder
PyInstaller ile .exe dosyası oluşturma scripti
"""

import os
import sys
import subprocess
import shutil

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
    for folder in ["dist", "build"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🗑️ Eski {folder} klasörü temizlendi")
    
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
        "--add-data=languages;languages",  # Dil dosyaları
        "--add-data=*.json;.",          # JSON ayar dosyaları
        "--hidden-import=tkinter",      # Tkinter modülü
        "--hidden-import=threading",    # Threading modülü
        "--collect-all=tkinter",        # Tüm tkinter bileşenleri
        "--clean",                      # Temiz build
        "main_modular.py"               # Ana Python dosyası
    ]
    
    # İkon dosyası varsa ekle
    if os.path.exists("icon.ico"):
        cmd.insert(-1, "--icon=icon.ico")
    else:
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
        
        # Dokümantasyon dosyalarını kopyala
        docs = ["README.md", "LICENSE"]
        for doc in docs:
            if os.path.exists(doc):
                shutil.copy(doc, f"dist/{doc}")
                print(f"📄 {doc} kopyalandı")
        
        print(f"🎉 Başarılı! .exe dosyası: {exe_path}")
        print(f"📂 Dist klasörü: {os.path.abspath('dist')}")
        
        return True
    else:
        print("❌ .exe dosyası oluşturulamadı")
        return False

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