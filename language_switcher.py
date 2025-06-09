#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Language Switcher Widget
GUI'de dinamik dil değiştirme için widget
"""

import tkinter as tk
from tkinter import ttk
from lang_manager import lang_manager, t, set_language, get_languages

class LanguageSwitcher:
    """Dil değiştirme widget'ı"""
    
    def __init__(self, parent, on_language_change=None):
        self.parent = parent
        self.on_language_change = on_language_change
        
        # Dil frame oluştur
        self.frame = ttk.Frame(parent)
        
        # Dil etiketi
        self.label = ttk.Label(self.frame, text="🌍")
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Dil combobox
        self.combo = ttk.Combobox(self.frame, width=8)
        self.combo.pack(side=tk.LEFT)
        
        # Dil seçeneklerini yükle
        self.update_languages()
        
        # Event bağla
        self.combo.bind('<<ComboboxSelected>>', self.on_language_selected)
        
    def update_languages(self):
        """Mevcut dilleri güncelle"""
        languages = get_languages()
        language_names = {
            'tr': 'Türkçe',
            'en': 'English',
            'de': 'Deutsch',
            'fr': 'Français',
            'es': 'Español'
        }
        
        # Combobox değerlerini ayarla
        display_languages = []
        for lang in languages:
            display_name = language_names.get(lang, lang.upper())
            display_languages.append(f"{lang} - {display_name}")
        
        self.combo['values'] = display_languages
        
        # Mevcut dili seç
        current_lang = lang_manager.current_language
        for i, lang in enumerate(languages):
            if lang == current_lang:
                self.combo.current(i)
                break
    
    def on_language_selected(self, event=None):
        """Dil seçildiğinde çağrılır"""
        selection = self.combo.get()
        if selection:
            # Dil kodunu çıkar (tr - Türkçe -> tr)
            lang_code = selection.split(' - ')[0]
            
            # Dili değiştir
            if set_language(lang_code):
                # Callback çağır
                if self.on_language_change:
                    self.on_language_change(lang_code)
    
    def pack(self, **kwargs):
        """Frame'i pack et"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Frame'i grid et"""
        self.frame.grid(**kwargs)

def demo():
    """Dil switcher demo"""
    root = tk.Tk()
    root.title("Language Switcher Demo")
    root.geometry("400x300")
    
    # Başlık
    title_var = tk.StringVar()
    title_label = ttk.Label(root, textvariable=title_var, font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    # Örnek butonlar
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=20)
    
    scan_var = tk.StringVar()
    scan_button = ttk.Button(button_frame, textvariable=scan_var)
    scan_button.pack(side=tk.LEFT, padx=10)
    
    organize_var = tk.StringVar()
    organize_button = ttk.Button(button_frame, textvariable=organize_var)
    organize_button.pack(side=tk.LEFT, padx=10)
    
    # Örnek mesaj
    message_var = tk.StringVar()
    message_label = ttk.Label(root, textvariable=message_var)
    message_label.pack(pady=20)
    
    def update_texts():
        """Metinleri güncelle"""
        title_var.set(t('app.title'))
        scan_var.set(t('buttons.scan'))
        organize_var.set(t('buttons.organize'))
        message_var.set(t('messages.scan_complete', count=150))
    
    def on_language_change(lang_code):
        """Dil değiştiğinde çağrılır"""
        update_texts()
        print(f"Dil değiştirildi: {lang_code}")
    
    # Dil switcher
    lang_switcher = LanguageSwitcher(root, on_language_change)
    lang_switcher.pack(pady=10)
    
    # İlk metinleri yükle
    update_texts()
    
    root.mainloop()

if __name__ == "__main__":
    demo() 