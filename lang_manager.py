#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Multi-Language Manager
Çok dilli destek için basit ve etkili sistem
"""

import json
import os
from pathlib import Path

class LanguageManager:
    """Dil yönetim sistemi"""
    
    def __init__(self, default_language='tr'):
        self.current_language = default_language
        self.languages = {}
        self.fallback_language = 'en'  # Ana dil yoksa İngilizce kullan
        
        # Dil klasörünü oluştur
        self.lang_dir = Path(__file__).parent / 'languages'
        self.lang_dir.mkdir(exist_ok=True)
        
        # Dil dosyalarını yükle
        self.load_languages()
        
        # Ayarları yükle
        self.load_settings()
    
    def load_languages(self):
        """Tüm dil dosyalarını yükle"""
        try:
            for lang_file in self.lang_dir.glob('*.json'):
                lang_code = lang_file.stem
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.languages[lang_code] = json.load(f)
                print(f"✅ Dil yüklendi: {lang_code}")
        except Exception as e:
            print(f"❌ Dil yükleme hatası: {e}")
    
    def get_text(self, key, **kwargs):
        """Metni al (anahtar kelime ile)"""
        # Önce mevcut dili dene
        text = self._get_text_from_language(self.current_language, key)
        
        # Bulamazsa fallback dili dene
        if text is None and self.current_language != self.fallback_language:
            text = self._get_text_from_language(self.fallback_language, key)
        
        # Hala bulamazsa anahtar kelimeyi döndür
        if text is None:
            text = f"[{key}]"
        
        # Parametre varsa yerleştir
        if kwargs:
            try:
                return text.format(**kwargs)
            except:
                return text
        
        return text
    
    def _get_text_from_language(self, lang_code, key):
        """Belirli bir dilden metin al"""
        if lang_code not in self.languages:
            return None
        
        # Nested key desteği (menu.file.open gibi)
        keys = key.split('.')
        current = self.languages[lang_code]
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return None
    
    def set_language(self, lang_code):
        """Dili değiştir"""
        if lang_code in self.languages:
            self.current_language = lang_code
            self.save_settings()
            print(f"🌍 Dil değiştirildi: {lang_code}")
            return True
        else:
            print(f"❌ Dil bulunamadı: {lang_code}")
            return False
    
    def get_available_languages(self):
        """Kullanılabilir dilleri döndür"""
        return list(self.languages.keys())
    
    def create_language_file(self, lang_code, sample_texts=None):
        """Yeni dil dosyası oluştur"""
        if sample_texts is None:
            sample_texts = self._get_sample_texts()
        
        lang_file = self.lang_dir / f"{lang_code}.json"
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(sample_texts, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dil dosyası oluşturuldu: {lang_file}")
    
    def _get_sample_texts(self):
        """Örnek metin yapısı"""
        return {
            "app": {
                "title": "Dosya Organizatörü",
                "version": "v2.0"
            },
            "menu": {
                "file": {
                    "select_source": "Kaynak Klasör Seç",
                    "select_target": "Hedef Klasör Seç",
                    "exit": "Çıkış"
                },
                "operations": {
                    "copy": "Kopyala",
                    "cut": "Kes", 
                    "paste": "Yapıştır",
                    "delete": "Sil",
                    "rename": "Yeniden Adlandır"
                }
            },
            "buttons": {
                "scan": "Dosyaları Tara",
                "organize": "Organizasyonu Başlat",
                "cancel": "İptal",
                "ok": "Tamam",
                "back": "Geri",
                "up": "Üst Klasör",
                "refresh": "Yenile"
            },
            "messages": {
                "scan_complete": "Tarama tamamlandı! {count} dosya bulundu",
                "organization_complete": "Organizasyon tamamlandı!",
                "error": "Hata: {error}",
                "warning": "Uyarı: {message}",
                "confirm_delete": "{item} silinsin mi?",
                "folder_exists": "Klasör zaten mevcut. İçerikleri birleştir?",
                "no_files_selected": "Dosya seçilmedi!"
            },
            "dialogs": {
                "folder_conflict": {
                    "title": "Klasör Çakışması",
                    "message": "'{folder}' klasörü zaten mevcut!",
                    "merge": "İçerikleri Birleştir",
                    "rename": "Yeni İsimle Oluştur",
                    "cancel": "İptal"
                },
                "file_conflict": {
                    "title": "Dosya Çakışması", 
                    "message": "'{file}' dosyası zaten mevcut!",
                    "overwrite": "Üstüne Yaz",
                    "skip": "Atla",
                    "overwrite_all": "Tümünü Yaz",
                    "skip_all": "Tümünü Atla"
                }
            }
        }
    
    def load_settings(self):
        """Ayarları yükle"""
        settings_file = Path(__file__).parent / 'language_settings.json'
        try:
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_language = settings.get('language', self.current_language)
        except Exception as e:
            print(f"⚠️ Dil ayarları yüklenemedi: {e}")
    
    def save_settings(self):
        """Ayarları kaydet"""
        settings_file = Path(__file__).parent / 'language_settings.json'
        try:
            settings = {
                'language': self.current_language
            }
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Dil ayarları kaydedilemedi: {e}")

# Global language manager instance
lang_manager = LanguageManager()

# Helper functions for easy access
def t(key, **kwargs):
    """Kısa metin alma fonksiyonu"""
    return lang_manager.get_text(key, **kwargs)

def set_language(lang_code):
    """Dil değiştirme fonksiyonu"""
    return lang_manager.set_language(lang_code)

def get_languages():
    """Kullanılabilir dilleri al"""
    return lang_manager.get_available_languages()

# Başlangıçta dil dosyalarını oluştur (yoksa)
if __name__ == "__main__":
    # Türkçe dil dosyası oluştur
    if not (lang_manager.lang_dir / 'tr.json').exists():
        lang_manager.create_language_file('tr')
    
    # İngilizce dil dosyası oluştur
    if not (lang_manager.lang_dir / 'en.json').exists():
        english_texts = {
            "app": {
                "title": "File Organizer",
                "version": "v2.0"
            },
            "menu": {
                "file": {
                    "select_source": "Select Source Folder",
                    "select_target": "Select Target Folder", 
                    "exit": "Exit"
                },
                "operations": {
                    "copy": "Copy",
                    "cut": "Cut",
                    "paste": "Paste", 
                    "delete": "Delete",
                    "rename": "Rename"
                }
            },
            "buttons": {
                "scan": "Scan Files",
                "organize": "Start Organization",
                "cancel": "Cancel",
                "ok": "OK",
                "back": "Back",
                "up": "Up Folder",
                "refresh": "Refresh"
            },
            "messages": {
                "scan_complete": "Scan completed! {count} files found",
                "organization_complete": "Organization completed!",
                "error": "Error: {error}",
                "warning": "Warning: {message}",
                "confirm_delete": "Delete {item}?",
                "folder_exists": "Folder already exists. Merge contents?",
                "no_files_selected": "No files selected!"
            },
            "dialogs": {
                "folder_conflict": {
                    "title": "Folder Conflict",
                    "message": "'{folder}' folder already exists!",
                    "merge": "Merge Contents",
                    "rename": "Create with New Name",
                    "cancel": "Cancel"
                },
                "file_conflict": {
                    "title": "File Conflict",
                    "message": "'{file}' file already exists!",
                    "overwrite": "Overwrite",
                    "skip": "Skip",
                    "overwrite_all": "Overwrite All",
                    "skip_all": "Skip All"
                }
            }
        }
        lang_manager.create_language_file('en', english_texts)
    
    print("🌍 Dil sistemi hazır!")
    print(f"📁 Dil dosyaları: {lang_manager.lang_dir}")
    print(f"🌐 Mevcut diller: {lang_manager.get_available_languages()}") 