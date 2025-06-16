@echo off
chcp 65001 >nul
echo.
echo 🚀 Python File Manager v3.0 - EXE Builder
echo ==========================================
echo.

echo 📋 Sistem kontrolleri yapılıyor...
echo.

REM Python kontrolü
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python bulunamadı!
    echo 📥 Python indirin: https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python kurulu
echo.

echo 📦 PyInstaller kuruluyor...
pip install pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PyInstaller kurulumu başarısız
    echo 💡 Manuel kurulum: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo ✅ PyInstaller hazır
echo.

echo 🧹 Eski build dosyaları temizleniyor...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "main_modular.spec" del "main_modular.spec"
echo ✅ Temizlik tamamlandı
echo.

echo 🔨 .exe dosyası oluşturuluyor...
echo ⏳ Bu işlem 2-5 dakika sürebilir, lütfen bekleyin...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name="Python-File-Manager" ^
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
    --collect-all=tkinter ^
    --noconsole ^
    --clean ^
    main_modular.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Build başarısız!
    echo 📋 Hata detayları için MANUAL_EXE_BUILD.md dosyasına bakın
    echo.
    pause
    exit /b 1
)

echo.
echo 🎉 BUILD BAŞARILI!
echo ==================
echo.

if exist "dist\Python-File-Manager.exe" (
    for %%I in ("dist\Python-File-Manager.exe") do (
        set /a size=%%~zI/1024/1024
    )
    echo ✅ .exe dosyası oluşturuldu
    echo 📂 Konum: %CD%\dist\Python-File-Manager.exe
    echo 📏 Boyut: Yaklaşık !size! MB
    echo.
    
    REM Dil dosyalarını kopyala
    if exist "languages" (
        if not exist "dist\languages" (
            xcopy "languages" "dist\languages" /E /I /Q >nul
            echo 🌍 Dil dosyaları kopyalandı
        )
    )
    
    REM README kopyala
    if exist "README.md" (
        copy "README.md" "dist\README.md" >nul
        echo 📄 README.md kopyalandı
    )
    
    echo.
    echo 🎯 KULLANIM:
    echo   • dist\Python-File-Manager.exe dosyasını çalıştırın
    echo   • Tüm dist klasörünü istediğiniz yere kopyalayabilirsiniz
    echo   • Python kurulu olmayan bilgisayarlarda da çalışır
    echo.
    
    echo 🔍 Test etmek ister misiniz? (E/H)
    set /p test_choice=Seçim: 
    if /i "!test_choice!"=="E" (
        echo 🚀 Program başlatılıyor...
        start "" "dist\Python-File-Manager.exe"
    )
    
) else (
    echo ❌ .exe dosyası oluşturulamadı
    echo 📋 MANUAL_EXE_BUILD.md dosyasındaki talimatları takip edin
)

echo.
echo 📦 Build tamamlandı!
pause 