#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILE MANAGER - Kapsamlı Dosya Yöneticisi
========================================

Bu uygulama, Python Tkinter kullanarak geliştirilmiş gelişmiş bir dosya yönetim sistemidir.
Ana amacı dosyaları kategorilere göre organize etme, duplikat tespiti ve kapsamlı dosya yönetimidir.

ANA ÖZELLİKLER:
==============
1. İki Panelli Arayüz:
   - Sol Panel: Kaynak dosya yöneticisi (navigasyon, sıralama, filtreleme)
   - Sağ Panel: Hedef organize yapısı

2. Gelişmiş Sol Panel:
   - Navigasyon butonları (Geri, Yukarı, Ana Sayfa)
   - Tıklanabilir yol çubuğu
   - Klavye kısayolları (Delete, Ctrl+C/X/V, F2, F5, Backspace)
   - Sağ tık context menüsü
   - Dosya özellikleri ve hash görüntüleme

3. Akıllı Filtreleme:
   - Gizli sistem dosyalarını filtreleme
   - Unix-style gizli dosyalar (. ile başlayan)
   - Geçici dosya filtreleme

4. Sütun Sıralama:
   - Tıklanabilir sütun başlıkları (↑↓)
   - Akıllı boyut, tarih, tür sıralaması
   - Klasörler öncelikli sıralama

5. Duplikat Tespit:
   - Ayrı "🔄 Duplikat Dosyalar" sekmesi
   - Çoklu tespit kriterleri (isim, boyut, hash)
   - Gerçek zamanlı tespit
   - Tree view ile gruplandırılmış gösterim

6. Organize Süreci:
   - Klasör yapısı doğrulama
   - Gerçek zamanlı duplikat kontrolü
   - Detaylı ilerleme raporlama
   - Kapsamlı tamamlama istatistikleri

KRİTİK ÇÖZÜMLER:
===============
- Duplikat Kontrolü: Hedef klasörde gerçek zamanlı kontrol sistemi
- Sıralama Kararlılığı: Intelligent parsing algoritmaları
- Performans: Threading ile UI responsive tutma

GELİŞTİRME TARİHÇESİ:
====================
v1.0: Temel dosya organize işlevi
v1.5: Sol panel geliştirme, klavye kısayolları
v2.0: Duplikat tespit sistemi, gerçek zamanlı kontrolü

CURSOR AI İLE DEVAM ETME:
========================
Bu projeye başka bilgisayarda devam etmek için:
1. README.md dosyasını referans gösterin
2. Bu file_manager.py dosyasını paylaşın
3. Spesifik ihtiyacınızı belirtin

Son güncellenme: Duplikat kontrolü optimizasyonu
Durum: Production Ready
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict
import threading
import json
import asyncio
from functools import lru_cache
import aiofiles
import logging
import unittest

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_manager.log'),
        logging.StreamHandler()
    ]
)

class FileOrganizer:
    """Dosya organizasyon mantığı"""
    pass  # Boş sınıflar tanımlanmış ama kullanılmamış

class FileScanner:
    """Dosya tarama"""
    pass

class UIManager:
    """Arayüz yönetimi"""
    pass

class ConfigManager:
    """Ayar yönetimi"""
    def __init__(self):
        self.config = self.load_config()
    
    def get_file_categories(self):
        return self.config.get('categories', DEFAULT_CATEGORIES)

class FileOperationObserver:
    def on_progress(self, progress):
        """UI güncelleme"""
        pass
        
    def on_complete(self, result):
        """Tamamlanma işlemi"""
        pass

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager - Dosya Organizatörü")
        self.root.geometry("1200x700")
        
        # Dosya kategorileri
        self.file_categories = {
            'images': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
                'folder': 'Resimler',
                'subfolders': {
                    '.jpg': 'JPG', '.jpeg': 'JPEG', '.png': 'PNG', 
                    '.gif': 'GIF', '.bmp': 'BMP', '.tiff': 'TIFF',
                    '.webp': 'WEBP', '.svg': 'SVG'
                }
            },
            'documents': {
                'extensions': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
                'folder': 'Belgeler',
                'subfolders': {
                    '.pdf': 'PDF', '.doc': 'Word', '.docx': 'Word',
                    '.txt': 'Metin', '.rtf': 'RTF'
                }
            },
            'spreadsheets': {
                'extensions': ['.xls', '.xlsx', '.csv'],
                'folder': 'Excel_Dosyalari',
                'subfolders': {
                    '.xls': 'Excel', '.xlsx': 'Excel', '.csv': 'CSV'
                }
            },
            'archives': {
                'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz'],
                'folder': 'Arsiv_Dosyalari',
                'subfolders': {
                    '.zip': 'ZIP', '.rar': 'RAR', '.7z': '7Z',
                    '.tar': 'TAR', '.gz': 'GZ'
                }
            },
            'programs': {
                'extensions': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.app'],
                'folder': 'Program_Dosyalari',
                'subfolders': {
                    '.exe': 'EXE', '.msi': 'MSI', '.deb': 'DEB',
                    '.rpm': 'RPM', '.dmg': 'DMG', '.app': 'APP'
                }
            },
            'notes': {
                'extensions': ['.note', '.md', '.odt'],
                'folder': 'Not_Dosyalari',
                'subfolders': {
                    '.note': 'Notes', '.md': 'Markdown', '.odt': 'ODT'
                }
            },
            'cad_files': {
                'extensions': ['.dxf', '.dwg', '.step', '.stp', '.iges', '.igs'],
                'folder': 'CAD_Dosyalari',
                'subfolders': {
                    '.dxf': 'DXF', '.dwg': 'DWG', '.step': 'STEP',
                    '.stp': 'STEP', '.iges': 'IGES', '.igs': 'IGES'
                }
            },
            'video_files': {
                'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
                'folder': 'Video_Dosyalari',
                'subfolders': {
                    '.mp4': 'MP4', '.avi': 'AVI', '.mkv': 'MKV',
                    '.mov': 'MOV', '.wmv': 'WMV', '.flv': 'FLV', '.webm': 'WEBM'
                }
            },
            'audio_files': {
                'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
                'folder': 'Ses_Dosyalari',
                'subfolders': {
                    '.mp3': 'MP3', '.wav': 'WAV', '.flac': 'FLAC',
                    '.aac': 'AAC', '.ogg': 'OGG', '.wma': 'WMA'
                }
            }
        }
        
        self.source_path = ""
        self.target_path = ""
        self.duplicate_files = []
        self.duplicate_groups = {}  # Duplikat dosya grupları {group_key: [file_paths]}
        self.unique_files = []  # Unique dosyalar (organize edilecek)
        self.config_file = "file_manager_config.json"
        self.current_target_dir = ""
        self.clipboard_files = []
        self.clipboard_operation = ""  # 'copy' or 'cut'
        self.navigation_history = []  # Geri gitme geçmişi
        self.history_index = -1
        self.sort_column = ""  # Hangi sütuna göre sıralandığı
        self.sort_reverse = False  # Sıralama yönü
        self.debug_mode = True  # Debug çıktıları için
        
        # Kaydedilmiş ayarları yükle
        self.load_settings()
        
        self.setup_ui()
        
        # İlk açılışta hedef klasörü yükle
        if self.target_path:
            self.current_target_dir = self.target_path
            self.refresh_target()
        
    def load_settings(self):
        """Kaydedilmiş ayarları yükle"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.target_path = config.get('last_target_path', '')
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
            
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            config = {
                'last_target_path': self.target_path
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
        
    def setup_ui(self):
        # Ana frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst panel - Klasör seçimi
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Source klasör seçimi
        ttk.Label(top_frame, text="Kaynak Klasör:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.source_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.source_var, width=50).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(top_frame, text="Seç", command=self.select_source_folder).grid(row=0, column=2)
        
        # Target SSD seçimi
        ttk.Label(top_frame, text="Hedef SSD:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.target_var = tk.StringVar(value=self.target_path)
        ttk.Entry(top_frame, textvariable=self.target_var, width=50).grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        ttk.Button(top_frame, text="Değiştir", command=self.select_target_folder).grid(row=1, column=2, pady=(5, 0))
        
        # Alt klasör tarama seçeneği
        scan_frame = ttk.Frame(top_frame)
        scan_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(scan_frame, text="Alt klasörleri tara:").pack(side=tk.LEFT, padx=(0, 10))
        self.scan_subfolders = tk.BooleanVar(value=True)
        ttk.Radiobutton(scan_frame, text="Evet - Tüm alt klasörleri tara", 
                       variable=self.scan_subfolders, value=True).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(scan_frame, text="Hayır - Sadece ana klasördeki dosyaları al", 
                       variable=self.scan_subfolders, value=False).pack(side=tk.LEFT)
        
        # Orta panel - İki pencere
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Sol panel - Hedef File Manager
        left_frame = ttk.LabelFrame(middle_frame, text="Hedef Klasör - File Manager")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Navigasyon kontrolleri
        nav_frame = ttk.Frame(left_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        ttk.Button(nav_frame, text="◀ Geri", command=self.go_back).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="▲ Üst Klasör", command=self.go_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="🏠 Ana Klasör", command=self.go_home).pack(side=tk.LEFT, padx=(0, 5))
        
        # Yol gösterge çubuğu
        path_frame = ttk.Frame(left_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        ttk.Label(path_frame, text="Konum:").pack(side=tk.LEFT)
        self.current_path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.current_path_var, font=('Consolas', 9))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.path_entry.bind('<Return>', self.navigate_to_path)
        ttk.Button(path_frame, text="Git", command=self.navigate_to_path).pack(side=tk.RIGHT)

        # File manager kontrolleri
        target_controls = ttk.Frame(left_frame)
        target_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(target_controls, text="🔄 Yenile", command=self.refresh_target).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="🗑️ Sil", command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="📋 Kopyala", command=self.copy_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="✂️ Kes", command=self.cut_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="📁 Yapıştır", command=self.paste_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="➕ Yeni Klasör", command=self.create_folder).pack(side=tk.LEFT, padx=(0, 5))
        
        # Hedef klasör ağacı
        target_frame = ttk.Frame(left_frame)
        target_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        self.target_tree = ttk.Treeview(target_frame, columns=('size', 'type', 'modified'), show='tree headings')
        self.target_tree.heading('#0', text='📁 Dosya/Klasör Adı', command=lambda: self.sort_tree('#0'))
        self.target_tree.heading('size', text='📏 Boyut', command=lambda: self.sort_tree('size'))
        self.target_tree.heading('type', text='🏷️ Tür', command=lambda: self.sort_tree('type'))
        self.target_tree.heading('modified', text='📅 Değiştirilme', command=lambda: self.sort_tree('modified'))
        self.target_tree.column('#0', width=250)
        self.target_tree.column('size', width=80)
        self.target_tree.column('type', width=80)
        self.target_tree.column('modified', width=120)
        
        target_scrollbar = ttk.Scrollbar(target_frame, orient=tk.VERTICAL, command=self.target_tree.yview)
        self.target_tree.configure(yscrollcommand=target_scrollbar.set)
        
        self.target_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        target_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Çift tıklama ve sağ tık menüsü
        self.target_tree.bind('<Double-1>', self.on_target_double_click)
        self.target_tree.bind('<Button-3>', self.show_context_menu)
        
        # Sürükleyip bırakma desteği
        self.setup_drag_drop()
        
        # Klavye kısayolları
        self.target_tree.bind('<Delete>', lambda e: self.delete_selected())
        self.target_tree.bind('<Control-c>', lambda e: self.copy_selected())
        self.target_tree.bind('<Control-x>', lambda e: self.cut_selected())
        self.target_tree.bind('<Control-v>', lambda e: self.paste_selected())
        self.target_tree.bind('<F2>', lambda e: self.rename_selected())
        self.target_tree.bind('<F5>', lambda e: self.refresh_target())
        self.target_tree.bind('<BackSpace>', lambda e: self.go_up())
        
        # Sağ panel - Kaynak Dosyalar ve Organizasyon
        right_frame = ttk.LabelFrame(middle_frame, text="Kaynak Dosyalar ve Organizasyon Önizleme")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Notebook için tab'lar
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Kaynak dosyalar
        source_tab = ttk.Frame(self.notebook)
        self.notebook.add(source_tab, text="Kaynak Dosyalar")
        
        self.source_tree = ttk.Treeview(source_tab, columns=('size', 'type'), show='tree headings')
        self.source_tree.heading('#0', text='Dosya Adı')
        self.source_tree.heading('size', text='Boyut')
        self.source_tree.heading('type', text='Tür')
        self.source_tree.column('#0', width=250)
        self.source_tree.column('size', width=80)
        self.source_tree.column('type', width=80)
        
        source_scrollbar = ttk.Scrollbar(source_tab, orient=tk.VERTICAL, command=self.source_tree.yview)
        self.source_tree.configure(yscrollcommand=source_scrollbar.set)
        
        self.source_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        source_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tab 2: Organizasyon önizleme
        preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(preview_tab, text="Organizasyon Önizleme")
        
        self.preview_tree = ttk.Treeview(preview_tab, columns=('count',), show='tree headings')
        self.preview_tree.heading('#0', text='Klasör Yapısı')
        self.preview_tree.heading('count', text='Dosya Sayısı')
        self.preview_tree.column('#0', width=250)
        self.preview_tree.column('count', width=100)
        
        preview_scrollbar = ttk.Scrollbar(preview_tab, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tab 3: Duplikat dosyalar
        duplicate_tab = ttk.Frame(self.notebook)
        self.notebook.add(duplicate_tab, text="🔄 Duplikat Dosyalar")
        
        # Duplikat kontrol seçenekleri
        dup_controls = ttk.Frame(duplicate_tab)
        dup_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dup_controls, text="Duplikat Kontrol:").pack(side=tk.LEFT)
        self.duplicate_check_name = tk.BooleanVar(value=True)
        self.duplicate_check_size = tk.BooleanVar(value=True)
        self.duplicate_check_hash = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(dup_controls, text="İsim", variable=self.duplicate_check_name).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Checkbutton(dup_controls, text="Boyut", variable=self.duplicate_check_size).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(dup_controls, text="Hash", variable=self.duplicate_check_hash).pack(side=tk.LEFT, padx=5)
        
        # Duplikat işlem seçenekleri
        dup_action_frame = ttk.Frame(duplicate_tab)
        dup_action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dup_action_frame, text="Duplikat dosyalar için:").pack(side=tk.LEFT)
        self.duplicate_action = tk.StringVar(value="ask")
        ttk.Radiobutton(dup_action_frame, text="Her seferinde sor", 
                       variable=self.duplicate_action, value="ask").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Radiobutton(dup_action_frame, text="Otomatik atla", 
                       variable=self.duplicate_action, value="skip").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(dup_action_frame, text="Otomatik kopyala", 
                       variable=self.duplicate_action, value="copy").pack(side=tk.LEFT, padx=5)
        
        self.duplicate_tree = ttk.Treeview(duplicate_tab, columns=('path', 'size', 'hash'), show='tree headings')
        self.duplicate_tree.heading('#0', text='🔄 Duplikat Dosya Grupları')
        self.duplicate_tree.heading('path', text='Dosya Yolu')
        self.duplicate_tree.heading('size', text='Boyut')
        self.duplicate_tree.heading('hash', text='Hash')
        self.duplicate_tree.column('#0', width=200)
        self.duplicate_tree.column('path', width=300)
        self.duplicate_tree.column('size', width=80)
        self.duplicate_tree.column('hash', width=120)
        
        duplicate_scrollbar = ttk.Scrollbar(duplicate_tab, orient=tk.VERTICAL, command=self.duplicate_tree.yview)
        self.duplicate_tree.configure(yscrollcommand=duplicate_scrollbar.set)
        
        self.duplicate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        duplicate_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Alt panel - Kontroller ve durum
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)
        
        # Butonlar
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame, text="Dosyaları Tara", command=self.scan_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔍 Hedef Disk Analizi", command=self.analyze_target_disk).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Organizasyonu Başlat", command=self.start_organization).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Duplikatları Göster", command=self.show_duplicates).pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Durum etiketi
        self.status_var = tk.StringVar(value="Hazır")
        ttk.Label(bottom_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
    def select_source_folder(self):
        folder = filedialog.askdirectory(title="Kaynak Klasörü Seçin")
        if folder:
            self.source_path = folder
            self.source_var.set(folder)
            
    def select_target_folder(self):
        initial_dir = self.target_path if self.target_path and os.path.exists(self.target_path) else None
        folder = filedialog.askdirectory(title="Hedef SSD'yi Seçin", initialdir=initial_dir)
        if folder:
            self.target_path = folder
            self.target_var.set(folder)
            self.current_target_dir = folder
            # Ayarları kaydet
            self.save_settings()
            # Hedef klasörü yenile
            self.refresh_target()
            
    @lru_cache(maxsize=1000)
    def get_file_hash(self, filepath):
        """Dosyanın MD5 hash'ini hesapla"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Hata: {e}")
            return None
            
    def get_file_category(self, file_path):
        """Dosyanın kategorisini belirle"""
        ext = Path(file_path).suffix.lower()
        for category, info in self.file_categories.items():
            if ext in info['extensions']:
                return category, info
        
        # Bilinmeyen dosya formatı için otomatik klasör oluştur
        if ext:
            # Uzantıyı temizle ve büyük harfe çevir
            clean_ext = ext.replace('.', '').upper()
            folder_name = f"{clean_ext}_Dosyalari"
            subfolder_name = clean_ext
            
            return 'unknown', {
                'folder': folder_name,
                'subfolders': {ext: subfolder_name}
            }
        else:
            # Uzantısız dosyalar
            return 'no_extension', {
                'folder': 'Uzantisiz_Dosyalar',
                'subfolders': {}
            }
            
    def get_file_category_info(self, category):
        """Kategori bilgisini al"""
        if category in self.file_categories:
            return category, self.file_categories[category]
        elif category == 'unknown':
            return category, {'folder': 'Bilinmeyen_Dosyalar', 'subfolders': {}}
        elif category == 'no_extension':
            return category, {'folder': 'Uzantisiz_Dosyalar', 'subfolders': {}}
        else:
                        return category, {'folder': 'Diger_Dosyalar', 'subfolders': {}}
    
    def add_to_history(self, path):
        """Geçmişe klasör ekle"""
        if path and path != self.current_target_dir:
            # Mevcut pozisyondan sonrasını temizle
            self.navigation_history = self.navigation_history[:self.history_index + 1]
            self.navigation_history.append(path)
            self.history_index = len(self.navigation_history) - 1
            
    def go_back(self):
        """Önceki klasöre git"""
        if self.history_index > 0:
            self.history_index -= 1
            new_path = self.navigation_history[self.history_index]
            if os.path.exists(new_path):
                self.current_target_dir = new_path
                self.refresh_target(add_to_history=False)
                
    def go_up(self):
        """Üst klasöre git"""
        if self.current_target_dir:
            parent_dir = os.path.dirname(self.current_target_dir)
            if parent_dir != self.current_target_dir and os.path.exists(parent_dir):
                self.add_to_history(self.current_target_dir)
                self.current_target_dir = parent_dir
                self.refresh_target(add_to_history=False)
                
    def go_home(self):
        """Ana hedef klasöre git"""
        if self.target_path and os.path.exists(self.target_path):
            self.add_to_history(self.current_target_dir)
            self.current_target_dir = self.target_path
            self.refresh_target(add_to_history=False)
            
    def navigate_to_path(self, event=None):
        """Belirtilen yola git"""
        path = self.current_path_var.get().strip()
        if path and os.path.exists(path) and os.path.isdir(path):
            self.add_to_history(self.current_target_dir)
            self.current_target_dir = path
            self.refresh_target(add_to_history=False)
        else:
            messagebox.showerror("Hata", "Geçersiz klasör yolu!")
            self.current_path_var.set(self.current_target_dir)

    def refresh_target(self, add_to_history=True):
        """Hedef klasörü yenile"""
        if not self.current_target_dir or not os.path.exists(self.current_target_dir):
            return
            
        # Yol çubuğunu güncelle
        self.current_path_var.set(self.current_target_dir)
        
        self.target_tree.delete(*self.target_tree.get_children())
        
        try:
            # Klasörleri ve dosyaları listele
            items = []
            for item in os.listdir(self.current_target_dir):
                # Gizli dosyaları atla
                item_path = os.path.join(self.current_target_dir, item)
                if self.is_hidden_file(item, item_path):
                    continue
                    
                item_path = os.path.join(self.current_target_dir, item)
                try:
                    if os.path.isdir(item_path):
                        # Klasör
                        items.append({
                            'name': item,
                            'path': item_path,
                            'type': 'Klasör',
                            'size': '',
                            'modified': self.get_modified_time(item_path),
                            'is_dir': True
                        })
                    else:
                        # Dosya
                        file_size = os.path.getsize(item_path)
                        items.append({
                            'name': item,
                            'path': item_path,
                            'type': 'Dosya',
                            'size': self.format_size(file_size),
                            'modified': self.get_modified_time(item_path),
                            'is_dir': False
                        })
                except Exception as e:
                    print(f"Hata: {e}")
                    continue
            
            # Önce klasörler, sonra dosyalar
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            
            # Tree'ye ekle
            for item in items:
                icon = "📁" if item['is_dir'] else "📄"
                self.target_tree.insert('', 'end', 
                                      text=f"{icon} {item['name']}", 
                                      values=(item['size'], item['type'], item['modified']),
                                      tags=('directory' if item['is_dir'] else 'file',))
            
            # Mevcut sıralama varsa uygula
            if self.sort_column:
                # Mevcut sıralama bilgisini koru
                current_reverse = self.sort_reverse
                current_column = self.sort_column
                
                # Sıralama uygula
                self.sort_column = ""  # Reset için
                self.sort_reverse = not current_reverse  # Ters çevir ki tekrar eski haline gelsin
                self.sort_tree(current_column)
                                      
        except Exception as e:
            print(f"Hata: {e}")
    
    def get_modified_time(self, file_path):
        """Dosya değiştirilme zamanını al"""
        try:
            import time
            timestamp = os.path.getmtime(file_path)
            return time.strftime('%d.%m.%Y %H:%M', time.localtime(timestamp))
        except Exception as e:
            print(f"Hata: {e}")
            return ""
    
    def is_hidden_file(self, filename, file_path=None):
        """Gizli dosya kontrolü"""
        # Dosya adı bazlı kontroller
        if filename.startswith('.'):  # Unix tarzı gizli dosyalar
            return True
        
        # Windows sistem dosyaları
        hidden_files = [
            'desktop.ini', 'thumbs.db', '$recycle.bin', 'system volume information',
            'pagefile.sys', 'hiberfil.sys', 'swapfile.sys', '.ds_store'
        ]
        
        if filename.lower() in hidden_files:
            return True
            
        # Geçici dosyalar
        if filename.startswith('~') or filename.endswith('.tmp'):
            return True
            
        # Windows gizli öznitelik kontrolü (eğer dosya yolu verilmişse)
        if file_path and os.path.exists(file_path):
            try:
                import stat
                # Windows'ta gizli dosya özniteliği kontrolü
                if hasattr(os, 'stat'):
                    stat_result = os.stat(file_path)
                    if hasattr(stat_result, 'st_file_attributes'):
                        if stat_result.st_file_attributes & 0x02:  # FILE_ATTRIBUTE_HIDDEN
                            return True
            except:
                pass
            
        return False

    def sort_tree(self, column):
        """Tree view sıralama"""
        # Sıralama yönünü belirle
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Sütun başlıklarını güncelle - ok işareti ekle
        self.update_column_headers()
        
        # Mevcut verileri al
        items = []
        for item in self.target_tree.get_children():
            item_data = self.target_tree.item(item)
            items.append((item, item_data))
        
        # Sıralama anahtarını belirle
        def sort_key(item_tuple):
            item, item_data = item_tuple
            
            if column == '#0':
                # Dosya adına göre sırala, önce klasörler
                text = item_data['text'].replace("📁 ", "").replace("📄 ", "")
                is_dir = "📁" in item_data['text']
                return (not is_dir, text.lower())
            
            elif column == 'size':
                # Boyuta göre sırala
                size_text = item_data['values'][0] if item_data['values'] else ""
                
                # Klasörleri en üstte tut
                is_dir = "📁" in item_data['text']
                if is_dir:
                    return -1 if not self.sort_reverse else float('inf')
                
                if size_text == "" or size_text == "Klasör":
                    return 0
                    
                # Boyut stringini sayıya çevir
                return self.parse_size_string(size_text)
            
            elif column == 'type':
                # Türe göre sırala
                return item_data['values'][1] if len(item_data['values']) > 1 else ""
            
            elif column == 'modified':
                # Tarihe göre sırala
                date_text = item_data['values'][2] if len(item_data['values']) > 2 else ""
                return self.parse_date_string(date_text)
            
            return ""
        
        # Sırala
        items.sort(key=sort_key, reverse=self.sort_reverse)
        
        # Tree'yi yeniden düzenle
        for index, (item, _) in enumerate(items):
            self.target_tree.move(item, '', index)
    
    def update_column_headers(self):
        """Sütun başlıklarını ok işareti ile güncelle"""
        # Tüm başlıkları temizle
        self.target_tree.heading('#0', text='📁 Dosya/Klasör Adı')
        self.target_tree.heading('size', text='📏 Boyut')
        self.target_tree.heading('type', text='🏷️ Tür')
        self.target_tree.heading('modified', text='📅 Değiştirilme')
        
        # Aktif sütuna ok ekle
        if self.sort_column:
            arrow = " ↓" if self.sort_reverse else " ↑"
            current_text = self.target_tree.heading(self.sort_column)['text']
            self.target_tree.heading(self.sort_column, text=current_text + arrow)
    
    def parse_size_string(self, size_str):
        """Boyut stringini sayıya çevir"""
        try:
            if not size_str or size_str == "Klasör" or size_str == "":
                return 0
            
            # Boyut birimlerini çevir (büyükten küçüğe sırayla kontrol et)
            units = [
                ('TB', 1024**4),
                ('GB', 1024**3), 
                ('MB', 1024**2),
                ('KB', 1024),
                ('B', 1)
            ]
            
            size_str = size_str.strip()
            
            for unit, multiplier in units:
                if size_str.endswith(unit):
                    # Sayısal kısmı al
                    number_part = size_str[:-len(unit)].strip()
                    try:
                        number = float(number_part)
                        return int(number * multiplier)
                    except ValueError:
                        continue
            
            # Hiçbir birim bulunamazsa raw number olarak dene
            try:
                return int(float(size_str))
            except:
                return 0
                
        except Exception:
            return 0
    
    def parse_date_string(self, date_str):
        """Tarih stringini sıralaması için çevir"""
        try:
            if not date_str:
                return ""
            
            # Tarih formatı: "dd.mm.yyyy hh:mm"
            from datetime import datetime
            return datetime.strptime(date_str, '%d.%m.%Y %H:%M')
        except:
            return ""

    def format_size(self, size_bytes):
        """Dosya boyutunu formatla"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def setup_drag_drop(self):
        """Sürükleyip bırakma özelliğini ayarla"""
        self.drag_data = {"item": None, "x": 0, "y": 0}
        
        # Sürükleme başlangıcı
        self.target_tree.bind('<Button-1>', self.on_drag_start)
        self.target_tree.bind('<B1-Motion>', self.on_drag_motion)
        self.target_tree.bind('<ButtonRelease-1>', self.on_drag_end)
        
    def on_drag_start(self, event):
        """Sürükleme başlangıcı"""
        item = self.target_tree.identify_row(event.y)
        if item:
            self.drag_data["item"] = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            # İlk sürükleme cursor'u
            self.target_tree.config(cursor="hand2")
            
    def on_drag_motion(self, event):
        """Sürükleme hareketi"""
        if self.drag_data["item"]:
            # Sürüklenen öğeyi vurgula
            self.target_tree.selection_set(self.drag_data["item"])
            
            # Cursor'ı taşıma ikonu yap
            self.target_tree.config(cursor="fleur")  # Taşıma cursor'u
            
            # Hedef kontrolü - eğer klasör üzerindeyse farklı cursor
            target_item = self.target_tree.identify_row(event.y)
            if target_item and target_item != self.drag_data["item"]:
                target_item_data = self.target_tree.item(target_item)
                target_name = target_item_data['text'].replace("📁 ", "").replace("📄 ", "")
                target_path = os.path.join(self.current_target_dir, target_name)
                
                if os.path.isdir(target_path):
                    self.target_tree.config(cursor="dotbox")  # Hedef klasör cursor'u
                else:
                    self.target_tree.config(cursor="X_cursor")  # Geçersiz hedef
            
    def on_drag_end(self, event):
        """Sürükleme bitişi"""
        if not self.drag_data["item"]:
            return
            
        # Hedef öğeyi bul
        target_item = self.target_tree.identify_row(event.y)
        
        if target_item and target_item != self.drag_data["item"]:
            source_item = self.target_tree.item(self.drag_data["item"])
            target_item_data = self.target_tree.item(target_item)
            
            source_name = source_item['text'].replace("📁 ", "").replace("📄 ", "")
            target_name = target_item_data['text'].replace("📁 ", "").replace("📄 ", "")
            
            source_path = os.path.join(self.current_target_dir, source_name)
            target_path = os.path.join(self.current_target_dir, target_name)
            
            # Hedef bir klasör mü kontrol et
            if os.path.isdir(target_path):
                self.move_file_to_folder(source_path, target_path)
        
        # Sürükleme verilerini temizle
        self.drag_data = {"item": None, "x": 0, "y": 0}
        
        # Cursor'ı normale döndür
        self.target_tree.config(cursor="")
        
    def move_file_to_folder(self, source_path, target_folder):
        """Dosyayı hedef klasöre taşı"""
        if messagebox.askyesno("Taşıma Onayı", 
                              f"'{os.path.basename(source_path)}' dosyasını '{os.path.basename(target_folder)}' klasörüne taşımak istiyor musunuz?"):
            try:
                file_name = os.path.basename(source_path)
                new_path = os.path.join(target_folder, file_name)
                
                # Aynı isimde dosya varsa numara ekle
                counter = 1
                base_name, ext = os.path.splitext(file_name)
                while os.path.exists(new_path):
                    new_name = f"{base_name}_{counter}{ext}"
                    new_path = os.path.join(target_folder, new_name)
                    counter += 1
                
                shutil.move(source_path, new_path)
                self.refresh_target()
                self.status_var.set(f"'{file_name}' taşındı.")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Taşıma hatası: {e}")

    def on_target_double_click(self, event):
        """Hedef ağaçta çift tıklama"""
        selection = self.target_tree.selection()
        if not selection:
            return
            
        item = self.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_target_dir, item_name)
        
        if os.path.isdir(item_path):
            # Klasöre gir
            self.add_to_history(self.current_target_dir)
            self.current_target_dir = item_path
            self.refresh_target(add_to_history=False)
        else:
            # Dosyayı aç
            try:
                os.startfile(item_path)
            except Exception as e:
                print(f"Hata: {e}")
                messagebox.showerror("Hata", "Dosya açılamadı!")
    
    def show_context_menu(self, event):
        """Sağ tık menüsü"""
        try:
            # Seçili öğeyi belirle
            item = self.target_tree.identify_row(event.y)
            if item:
                self.target_tree.selection_set(item)
                
            # Sağ tık menüsü oluştur
            context_menu = tk.Menu(self.root, tearoff=0)
            
            selection = self.target_tree.selection()
            
            if selection:
                # Dosya/klasör seçili
                context_menu.add_command(label="🔓 Aç", command=self.open_selected)
                context_menu.add_command(label="🔍 Dosya Konumunu Aç", command=self.open_file_location)
                context_menu.add_separator()
                context_menu.add_command(label="📋 Kopyala (Ctrl+C)", command=self.copy_selected)
                context_menu.add_command(label="✂️ Kes (Ctrl+X)", command=self.cut_selected)
                
                # Yapıştırma - pano doluysa aktif
                paste_state = tk.NORMAL if self.clipboard_files else tk.DISABLED
                context_menu.add_command(label="📁 Yapıştır (Ctrl+V)", command=self.paste_selected, state=paste_state)
                
                context_menu.add_separator()
                context_menu.add_command(label="🗑️ Sil (Del)", command=self.delete_selected)
                context_menu.add_command(label="✏️ Yeniden Adlandır (F2)", command=self.rename_selected)
                context_menu.add_separator()
                
                # Tek dosya seçiliyse ek seçenekler
                if len(selection) == 1:
                    item_data = self.target_tree.item(selection[0])
                    item_name = item_data['text'].replace("📁 ", "").replace("📄 ", "")
                    item_path = os.path.join(self.current_target_dir, item_name)
                    
                    if os.path.isfile(item_path):
                        context_menu.add_command(label="📊 Dosya Bilgileri", command=self.show_file_info)
                        context_menu.add_command(label="🔄 Dosya Hash", command=self.show_file_hash)
                    
                context_menu.add_command(label="📋 Özellikler", command=self.show_properties)
            else:
                # Boş alan
                context_menu.add_command(label="📁 Yapıştır (Ctrl+V)", command=self.paste_selected, 
                                       state=tk.NORMAL if self.clipboard_files else tk.DISABLED)
                context_menu.add_separator()
                context_menu.add_command(label="➕ Yeni Klasör", command=self.create_folder)
                context_menu.add_command(label="📄 Yeni Dosya", command=self.create_new_file)
                context_menu.add_separator()
                context_menu.add_command(label="🔄 Yenile (F5)", command=self.refresh_target)
                context_menu.add_separator()
                context_menu.add_command(label="📋 Klasör Özellikeri", command=self.show_folder_properties)
            
            # Menüyü göster
            context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Menü hatası: {e}")
    
    def delete_selected(self):
        """Seçili dosya/klasörü sil"""
        selection = self.target_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silinecek dosya/klasörü seçin!")
            return
            
        items_to_delete = []
        for item_id in selection:
            item = self.target_tree.item(item_id)
            item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
            item_path = os.path.join(self.current_target_dir, item_name)
            items_to_delete.append((item_name, item_path))
        
        # Onay iste
        if len(items_to_delete) == 1:
            message = f"'{items_to_delete[0][0]}' silinsin mi?"
        else:
            message = f"{len(items_to_delete)} öğe silinsin mi?"
            
        if messagebox.askyesno("Silme Onayı", message):
            for item_name, item_path in items_to_delete:
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                except Exception as e:
                    print(f"Hata: {e}")
                    messagebox.showerror("Hata", f"'{item_name}' silinirken hata: {e}")
            
            self.refresh_target()
    
    def copy_selected(self):
        """Seçili dosyaları kopyala"""
        selection = self.target_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen kopyalanacak dosya/klasörü seçin!")
            return
            
        self.clipboard_files = []
        for item_id in selection:
            item = self.target_tree.item(item_id)
            item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
            item_path = os.path.join(self.current_target_dir, item_name)
            self.clipboard_files.append(item_path)
        
        self.clipboard_operation = 'copy'
        self.status_var.set(f"{len(self.clipboard_files)} öğe kopyalandı.")
    
    def cut_selected(self):
        """Seçili dosyaları kes"""
        selection = self.target_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen kesilecek dosya/klasörü seçin!")
            return
            
        self.clipboard_files = []
        for item_id in selection:
            item = self.target_tree.item(item_id)
            item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
            item_path = os.path.join(self.current_target_dir, item_name)
            self.clipboard_files.append(item_path)
        
        self.clipboard_operation = 'cut'
        self.status_var.set(f"{len(self.clipboard_files)} öğe kesildi.")
    
    def paste_selected(self):
        """Panodaki dosyaları yapıştır"""
        if not self.clipboard_files:
            messagebox.showwarning("Uyarı", "Panoda dosya yok!")
            return
            
        for file_path in self.clipboard_files:
            try:
                file_name = os.path.basename(file_path)
                target_path = os.path.join(self.current_target_dir, file_name)
                
                # Aynı isimde dosya varsa numara ekle
                counter = 1
                base_name, ext = os.path.splitext(file_name)
                while os.path.exists(target_path):
                    new_name = f"{base_name}_{counter}{ext}"
                    target_path = os.path.join(self.current_target_dir, new_name)
                    counter += 1
                
                if self.clipboard_operation == 'copy':
                    if os.path.isdir(file_path):
                        shutil.copytree(file_path, target_path)
                    else:
                        shutil.copy2(file_path, target_path)
                elif self.clipboard_operation == 'cut':
                    shutil.move(file_path, target_path)
                    
            except Exception as e:
                print(f"Hata: {e}")
                messagebox.showerror("Hata", f"'{os.path.basename(file_path)}' yapıştırılırken hata: {e}")
        
        if self.clipboard_operation == 'cut':
            self.clipboard_files = []
            
        self.refresh_target()
        self.status_var.set("Yapıştırma tamamlandı.")
    
    def move_selected(self):
        """Seçili dosyaları taşı"""
        self.cut_selected()
    
    def create_folder(self):
        """Yeni klasör oluştur"""
        folder_name = tk.simpledialog.askstring("Yeni Klasör", "Klasör adı:")
        if folder_name:
            folder_path = os.path.join(self.current_target_dir, folder_name)
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.refresh_target()
                self.status_var.set(f"'{folder_name}' klasörü oluşturuldu.")
            except Exception as e:
                print(f"Hata: {e}")
                messagebox.showerror("Hata", f"Klasör oluşturulurken hata: {e}")
    
    def open_selected(self):
        """Seçili dosyayı aç"""
        selection = self.target_tree.selection()
        if not selection:
            return
            
        item = self.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_target_dir, item_name)
        
        try:
            os.startfile(item_path)
        except Exception as e:
            print(f"Hata: {e}")
            messagebox.showerror("Hata", "Dosya açılamadı!")
    
    def rename_selected(self):
        """Seçili dosyayı yeniden adlandır"""
        selection = self.target_tree.selection()
        if not selection:
            return
            
        item = self.target_tree.item(selection[0])
        old_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        
        new_name = tk.simpledialog.askstring("Yeniden Adlandır", "Yeni ad:", initialvalue=old_name)
        if new_name and new_name != old_name:
            old_path = os.path.join(self.current_target_dir, old_name)
            new_path = os.path.join(self.current_target_dir, new_name)
            
            try:
                os.rename(old_path, new_path)
                self.refresh_target()
                self.status_var.set(f"'{old_name}' -> '{new_name}' olarak yeniden adlandırıldı.")
            except Exception as e:
                print(f"Hata: {e}")
                messagebox.showerror("Hata", f"Yeniden adlandırma hatası: {e}")
    
    def open_file_location(self):
        """Dosya konumunu aç"""
        selection = self.target_tree.selection()
        if not selection:
            return
            
        item = self.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_target_dir, item_name)
        
        try:
            os.system(f'explorer /select,"{item_path}"')
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya konumu açılamadı: {e}")
            
    def show_file_info(self):
        """Detaylı dosya bilgilerini göster"""
        selection = self.target_tree.selection()
        if not selection:
            return
            
        item = self.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_target_dir, item_name)
        
        try:
            stat = os.stat(item_path)
            import time
            
            # Detaylı dosya bilgileri
            created = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(stat.st_ctime))
            modified = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(stat.st_mtime))
            accessed = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(stat.st_atime))
            
            info = f"""📄 DOSYA BİLGİLERİ
            
📝 Adı: {item_name}
📂 Yol: {item_path}
📏 Boyut: {self.format_size(stat.st_size)}
📅 Oluşturulma: {created}
✏️ Değiştirilme: {modified}
👁️ Son Erişim: {accessed}
🔧 İzinler: {oct(stat.st_mode)[-3:]}
            
🔍 Uzantı: {Path(item_path).suffix}
📊 Kategori: {self.get_file_category(item_path)[0]}"""
            
            messagebox.showinfo("Dosya Bilgileri", info)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya bilgileri alınırken hata: {e}")
            
    def show_file_hash(self):
        """Dosya hash değerini göster"""
        selection = self.target_tree.selection()
        if not selection:
            return
            
        item = self.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_target_dir, item_name)
        
        if not os.path.isfile(item_path):
            return
            
        def calculate_hash():
            try:
                file_hash = self.get_file_hash(item_path)
                if file_hash:
                    hash_info = f"""🔐 DOSYA HASH BİLGİSİ
                    
📄 Dosya: {item_name}
🔑 MD5 Hash: {file_hash}
📏 Boyut: {self.format_size(os.path.getsize(item_path))}
                    
💡 Bu hash değeri dosyanın benzersiz kimliğidir.
Aynı hash'e sahip dosyalar tamamen aynıdır."""
                    messagebox.showinfo("Dosya Hash", hash_info)
                else:
                    messagebox.showerror("Hata", "Hash hesaplanamadı!")
            except Exception as e:
                messagebox.showerror("Hata", f"Hash hesaplama hatası: {e}")
        
        # Hash hesaplama thread'de yapılır
        threading.Thread(target=calculate_hash, daemon=True).start()
        self.status_var.set("Hash hesaplanıyor...")
        
    def create_new_file(self):
        """Yeni dosya oluştur"""
        file_name = tk.simpledialog.askstring("Yeni Dosya", "Dosya adı (uzantı ile):")
        if file_name:
            file_path = os.path.join(self.current_target_dir, file_name)
            try:
                # Boş dosya oluştur
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                self.refresh_target()
                self.status_var.set(f"'{file_name}' dosyası oluşturuldu.")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya oluşturulurken hata: {e}")
                
    def show_folder_properties(self):
        """Klasör özelliklerini göster"""
        try:
            # Klasördeki dosya sayısını hesapla
            total_files = 0
            total_folders = 0
            total_size = 0
            
            for item in os.listdir(self.current_target_dir):
                item_path = os.path.join(self.current_target_dir, item)
                try:
                    if os.path.isdir(item_path):
                        total_folders += 1
                    else:
                        total_files += 1
                        total_size += os.path.getsize(item_path)
                except:
                    continue
            
            properties = f"""📁 KLASÖR BİLGİLERİ
            
📂 Klasör: {os.path.basename(self.current_target_dir)}
📍 Yol: {self.current_target_dir}
📄 Dosya Sayısı: {total_files}
📁 Klasör Sayısı: {total_folders}
📏 Toplam Boyut: {self.format_size(total_size)}
📅 Değiştirilme: {self.get_modified_time(self.current_target_dir)}"""
            
            messagebox.showinfo("Klasör Özellikleri", properties)
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör özellikleri alınırken hata: {e}")

    def show_properties(self):
        """Dosya özelliklerini göster"""
        selection = self.target_tree.selection()
        if not selection:
            return
            
        item = self.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_target_dir, item_name)
        
        try:
            stat = os.stat(item_path)
            size = self.format_size(stat.st_size) if os.path.isfile(item_path) else "Klasör"
            modified = self.get_modified_time(item_path)
            
            properties = f"""Dosya: {item_name}
Yol: {item_path}
Tür: {'Klasör' if os.path.isdir(item_path) else 'Dosya'}
Boyut: {size}
Değiştirilme: {modified}"""
            
            messagebox.showinfo("Özellikler", properties)
        except Exception as e:
            print(f"Hata: {e}")
            messagebox.showerror("Hata", f"Özellikler alınırken hata: {e}")
         
    def scan_files(self):
        """Dosyaları tara ve UI'yi güncelle"""
        self._prepare_scan()
        self._scan_source_files()
        # _detect_duplicates zaten _scan_source_files içinde çağrılıyor
        # _update_ui fonksiyonu gerekli değil, tüm UI güncellemeleri zaten yapılıyor
    
    def _prepare_scan(self):
        self.status_var.set("Dosyalar taranıyor...")
        self.source_tree.delete(*self.source_tree.get_children())
        self.preview_tree.delete(*self.preview_tree.get_children())
        self.duplicate_tree.delete(*self.duplicate_tree.get_children())
        
        file_stats = defaultdict(lambda: defaultdict(int))
        total_files = 0
        processed_files = 0
        self.all_scanned_files = []  # Tüm taranan dosyalar - instance variable olarak tanımla
        
        # Alt klasör tarama seçeneğine göre dosyaları listele
        if self.scan_subfolders.get():
            # Tüm alt klasörleri tara - önce dosya sayısını hesapla
            for root, dirs, files in os.walk(self.source_path):
                # Gizli dosyaları çıkar
                filtered_files = [f for f in files if not self.is_hidden_file(f, os.path.join(root, f))]
                total_files += len(filtered_files)
            
            # Dosyaları tara ve işle
            for root, dirs, files in os.walk(self.source_path):
                for file in files:
                    # Gizli dosyaları atla
                    file_path = os.path.join(root, file)
                    if self.is_hidden_file(file, file_path):
                        continue
                    try:
                        file_size = os.path.getsize(file_path)
                        category, cat_info = self.get_file_category(file_path)
                        
                        # Dosyayı listeye ekle
                        self.all_scanned_files.append(file_path)
                        
                        # Source tree'ye ekle
                        rel_path = os.path.relpath(file_path, self.source_path)
                        self.source_tree.insert('', 'end', text=rel_path, 
                                             values=(self.format_size(file_size), category))
                        
                        # İstatistikleri güncelle
                        file_stats[category]['count'] += 1
                        file_stats[category]['size'] += file_size
                        
                        processed_files += 1
                        if total_files > 0:
                            progress = (processed_files / total_files) * 100
                            self.progress_var.set(progress)
                        
                        # UI güncellemesi için bekle
                        if processed_files % 10 == 0:  # Her 10 dosyada bir UI güncelle
                            self.root.update_idletasks()
                            
                    except Exception as e:
                        print(f"Hata: {file_path} - {e}")
        else:
            # Sadece ana klasördeki dosyaları al
            try:
                all_files = [f for f in os.listdir(self.source_path) 
                            if os.path.isfile(os.path.join(self.source_path, f))]
                # Gizli dosyaları filtrele
                files = [f for f in all_files if not self.is_hidden_file(f, os.path.join(self.source_path, f))]
                total_files = len(files)
            except:
                files = []
                total_files = 0
            
            # Ana klasördeki dosyaları tara
            for file in files:
                file_path = os.path.join(self.source_path, file)
                try:
                    file_size = os.path.getsize(file_path)
                    category, cat_info = self.get_file_category(file_path)
                    
                    # Dosyayı listeye ekle
                    self.all_scanned_files.append(file_path)
                    
                    # Source tree'ye ekle
                    rel_path = os.path.relpath(file_path, self.source_path)
                    self.source_tree.insert('', 'end', text=rel_path, 
                                         values=(self.format_size(file_size), category))
                    
                    # İstatistikleri güncelle
                    file_stats[category]['count'] += 1
                    file_stats[category]['size'] += file_size
                    
                    processed_files += 1
                    if total_files > 0:
                        progress = (processed_files / total_files) * 100
                        self.progress_var.set(progress)
                    
                    # UI güncellemesi için bekle
                    if processed_files % 5 == 0:  # Her 5 dosyada bir UI güncelle
                        self.root.update_idletasks()
                        
                except Exception as e:
                    print(f"Hata: {file_path} - {e}")
        
        # Dosya uzantılarına göre detaylı istatistik topla
        extension_stats = defaultdict(int)
        category_extension_map = defaultdict(set)
        
        # Tüm dosyaları tekrar tara ve uzantı bazında say
        if self.scan_subfolders.get():
            # Alt klasörlü tarama
            for root, dirs, files in os.walk(self.source_path):
                for file in files:
                    # Gizli dosyaları atla
                    file_path = os.path.join(root, file)
                    if self.is_hidden_file(file, file_path):
                        continue
                    try:
                        file_ext = Path(file_path).suffix.lower()
                        category, cat_info = self.get_file_category(file_path)
                        
                        extension_stats[file_ext] += 1
                        category_extension_map[category].add(file_ext)
                    except Exception as e:
                        print(f"Hata: {file_path} - {e}")
        else:
            # Sadece ana klasör tarama
            try:
                all_files = [f for f in os.listdir(self.source_path) 
                            if os.path.isfile(os.path.join(self.source_path, f))]
                files = [f for f in all_files if not self.is_hidden_file(f, os.path.join(self.source_path, f))]
                
                for file in files:
                    file_path = os.path.join(self.source_path, file)
                    try:
                        file_ext = Path(file_path).suffix.lower()
                        category, cat_info = self.get_file_category(file_path)
                        
                        extension_stats[file_ext] += 1
                        category_extension_map[category].add(file_ext)
                    except Exception as e:
                        print(f"Hata: {file_path} - {e}")
            except Exception as e:
                print(f"Klasör okuma hatası: {e}")
        
        # Organizasyon önizleme tree'sini güncelle
        for category, stats in file_stats.items():
            category, cat_info = self.get_file_category_info(category)
            folder_name = cat_info['folder']
            
            # Ana klasör ekle
            parent_item = self.preview_tree.insert('', 'end', text=folder_name, 
                                                 values=(f"{stats['count']} dosya"))
            
            # Bu kategoride bulunan uzantıları göster
            found_extensions = category_extension_map.get(category, set())
            
            if found_extensions:
                for ext in sorted(found_extensions):
                    if ext:  # Boş uzantı değilse
                        # Alt klasör adını belirle
                        if 'subfolders' in cat_info and ext in cat_info['subfolders']:
                            subfolder_name = cat_info['subfolders'][ext]
                        else:
                            # Bilinmeyen uzantı için otomatik isim
                            subfolder_name = ext.replace('.', '').upper()
                        
                        # Bu uzantıdaki dosya sayısı
                        ext_count = extension_stats[ext]
                        
                        self.preview_tree.insert(parent_item, 'end', text=f"└─ {subfolder_name}", 
                                               values=(f"{ext_count} dosya"))
                    else:
                        # Uzantısız dosyalar
                        ext_count = extension_stats[ext]
                        if ext_count > 0:
                            self.preview_tree.insert(parent_item, 'end', text="└─ Uzantısız", 
                                                   values=(f"{ext_count} dosya"))
        
        # Tarama tamamlandı - duplikat kontrolü _scan_source_files'da yapılacak
        self.status_var.set(f"Dosya tarama tamamlandı. {len(self.all_scanned_files)} dosya bulundu.")
        self.progress_var.set(100)
        
    def _scan_source_files(self):
        """Kaynak dosyaları tara ve duplikat kontrolü yap - düzeltilmiş versiyon"""
        
        # Eğer all_scanned_files tanımlanmamışsa, boş liste ile başla
        if not hasattr(self, 'all_scanned_files'):
            self.all_scanned_files = []
            
        # Duplikat kontrol işlemi
        self.status_var.set("Duplikat dosyalar kontrol ediliyor...")
        self.progress_var.set(90)
        
        # SADECE KAYNAK DOSYALARI ile duplikat kontrolü yap
        source_files_only = self.all_scanned_files.copy()
        
        if self.debug_mode:
            print(f"🔍 Kaynak dosyalar duplikat kontrolü: {len(source_files_only)} dosya")
        
        # Kaynak dosyalar arasında duplikat tespiti
        self.find_duplicates_advanced(source_files_only)
        
        # Hedef klasörde aynı dosyalar var mı kontrol et (ayrı sayım)
        target_duplicate_count = 0
        if self.target_path and os.path.exists(self.target_path):
            target_files = []
            for root, dirs, files in os.walk(self.target_path):
                for file in files:
                    if not self.is_hidden_file(file):
                        target_files.append(os.path.join(root, file))
            
            if self.debug_mode:
                print(f"🔍 Hedef klasör dosyaları: {len(target_files)} dosya")
            
            # Kaynak dosyalarla hedef dosyaları karşılaştır
            for source_file in source_files_only:
                source_name = os.path.basename(source_file).lower()
                source_size = 0
                try:
                    source_size = os.path.getsize(source_file)
                except:
                    continue
                    
                for target_file in target_files:
                    target_name = os.path.basename(target_file).lower()
                    target_size = 0
                    try:
                        target_size = os.path.getsize(target_file)
                    except:
                        continue
                    
                    # Basit karşılaştırma: isim + boyut
                    if source_name == target_name and source_size == target_size:
                        target_duplicate_count += 1
                        break
        
        # Duplikat tree'sini doldur
        self.populate_duplicate_tree()
        
        # İstatistikleri DOĞRU hesapla
        total_source_files = len(self.all_scanned_files)
        
        # Kaynak dosyalar arasındaki duplikatlar
        source_duplicate_count = 0
        for group_files in self.duplicate_groups.values():
            # Her gruptan sadece kaynak dosyaları say
            source_files_in_group = [f for f in group_files if f in self.all_scanned_files]
            if len(source_files_in_group) > 1:
                source_duplicate_count += len(source_files_in_group)
        
        # Benzersiz dosya sayısı = Toplam - Duplikatlar
        unique_count = total_source_files - source_duplicate_count
        
        # Toplam duplikat = Kaynak duplikatlar + Hedef duplikatlar
        total_duplicate_count = source_duplicate_count + target_duplicate_count
        
        scan_mode = "tüm alt klasörler dahil" if self.scan_subfolders.get() else "sadece ana klasör"
        
        # Doğru istatistikleri göster
        status_text = f"Tarama tamamlandı. {total_source_files} dosya | {unique_count} benzersiz | {source_duplicate_count} kaynak duplikat"
        if target_duplicate_count > 0:
            status_text += f" | {target_duplicate_count} hedef duplikat"
        status_text += f" ({scan_mode})"
        
        self.status_var.set(status_text)
        self.progress_var.set(0)
        
        if self.debug_mode:
            print(f"📊 DOĞRU İSTATİSTİKLER:")
            print(f"   Toplam kaynak dosya: {total_source_files}")
            print(f"   Benzersiz dosya: {unique_count}")
            print(f"   Kaynak duplikat: {source_duplicate_count}")
            print(f"   Hedef duplikat: {target_duplicate_count}")
            print(f"   Duplikat grup sayısı: {len(self.duplicate_groups)}")
        
        # unique_files listesini doğru oluştur
        all_duplicate_files = set()
        for group_files in self.duplicate_groups.values():
            for file_path in group_files:
                if file_path in self.all_scanned_files:
                    all_duplicate_files.add(file_path)
        
        self.unique_files = [f for f in self.all_scanned_files if f not in all_duplicate_files]
        
        if self.debug_mode:
            print(f"   Unique files listesi: {len(self.unique_files)} dosya")
    
    def _detect_duplicates(self):
        """Gelişmiş duplikat dosya tespiti"""
        if self.debug_mode:
            print(f"🔍 Duplikat kontrol başlıyor: {len(self.all_scanned_files)} dosya")
            print(f"Kontrol seçenekleri - İsim: {self.duplicate_check_name.get()}, Boyut: {self.duplicate_check_size.get()}, Hash: {self.duplicate_check_hash.get()}")
        
        duplicate_groups = defaultdict(list)
        unique_files = []
        
        # Duplikat kontrol seçeneklerine göre key oluştur
        def get_duplicate_key(file_path):
            key_parts = []
            
            # En az bir kontrol seçeneği aktif olmalı
            if not (self.duplicate_check_name.get() or self.duplicate_check_size.get() or self.duplicate_check_hash.get()):
                # Hiçbiri seçili değilse, default olarak isim + boyut kullan
                self.duplicate_check_name.set(True)
                self.duplicate_check_size.set(True)
            
            if self.duplicate_check_name.get():
                # Dosya adı (uzantısız, küçük harf)
                filename = os.path.splitext(os.path.basename(file_path))[0].lower()
                key_parts.append(('name', filename))
            
            if self.duplicate_check_size.get():
                # Dosya boyutu
                try:
                    file_size = os.path.getsize(file_path)
                    key_parts.append(('size', file_size))
                except Exception as e:
                    if self.debug_mode:
                        print(f"Boyut hatası {file_path}: {e}")
                    key_parts.append(('size', -1))  # -1 = hata
            
            if self.duplicate_check_hash.get():
                # Dosya hash'i (yavaş)
                file_hash = self.get_file_hash(file_path)
                key_parts.append(('hash', file_hash if file_hash else 'HASH_ERROR'))
            
            # Uzantı her zaman dahil
            ext = os.path.splitext(file_path)[1].lower()
            key_parts.append(('ext', ext))
            
            return tuple(key_parts)
        
        # Dosyaları grupla
        processed = 0
        for file_path in self.all_scanned_files:
            try:
                if not os.path.exists(file_path):
                    if self.debug_mode:
                        print(f"⚠️ Dosya bulunamadı: {file_path}")
                    continue
                
                key = get_duplicate_key(file_path)
                duplicate_groups[key].append(file_path)
                processed += 1
                
                # Her 100 dosyada bir rapor
                if processed % 100 == 0 and self.debug_mode:
                    print(f"İşlenen: {processed}/{len(self.all_scanned_files)}")
                    
            except Exception as e:
                print(f"❌ Duplikat kontrol hatası {file_path}: {e}")
                unique_files.append(file_path)
        
        if self.debug_mode:
            print(f"✅ Gruplama tamamlandı: {len(duplicate_groups)} grup")
        
        # Duplikat grupları ve unique dosyaları ayır
        self.duplicate_groups = {}
        group_id = 1
        
        for key, files in duplicate_groups.items():
            if len(files) > 1:
                # Duplikat grup bulundu
                group_name = f"Grup {group_id}"
                self.duplicate_groups[group_name] = files
                if self.debug_mode:
                    print(f"🔄 {group_name}: {len(files)} dosya - {[os.path.basename(f) for f in files[:2]]}{'...' if len(files) > 2 else ''}")
                group_id += 1
            else:
                # Unique dosya
                unique_files.extend(files)
        
        self.unique_files = unique_files
        
        if self.debug_mode:
            print(f"📊 Sonuç: {len(self.duplicate_groups)} duplikat grup, {len(unique_files)} benzersiz dosya")
        
        # Eski format için duplikat listesi
        duplicates = []
        for files in self.duplicate_groups.values():
            duplicates.extend(files)
            
        return duplicates
    
    def find_duplicates_advanced(self, file_list):
        """Gelişmiş duplikat dosya tespiti"""
        if self.debug_mode:
            print(f"🔍 Duplikat kontrol başlıyor: {len(file_list)} dosya")
            print(f"Kontrol seçenekleri - İsim: {self.duplicate_check_name.get()}, Boyut: {self.duplicate_check_size.get()}, Hash: {self.duplicate_check_hash.get()}")
        
        duplicate_groups = defaultdict(list)
        unique_files = []
        
        # Duplikat kontrol seçeneklerine göre key oluştur
        def get_duplicate_key(file_path):
            key_parts = []
            
            # En az bir kontrol seçeneği aktif olmalı
            if not (self.duplicate_check_name.get() or self.duplicate_check_size.get() or self.duplicate_check_hash.get()):
                # Hiçbiri seçili değilse, default olarak isim + boyut kullan
                self.duplicate_check_name.set(True)
                self.duplicate_check_size.set(True)
            
            if self.duplicate_check_name.get():
                # Dosya adı (uzantısız, küçük harf)
                filename = os.path.splitext(os.path.basename(file_path))[0].lower()
                key_parts.append(('name', filename))
            
            if self.duplicate_check_size.get():
                # Dosya boyutu
                try:
                    file_size = os.path.getsize(file_path)
                    key_parts.append(('size', file_size))
                except Exception as e:
                    if self.debug_mode:
                        print(f"Boyut hatası {file_path}: {e}")
                    key_parts.append(('size', -1))  # -1 = hata
            
            if self.duplicate_check_hash.get():
                # Dosya hash'i (yavaş)
                file_hash = self.get_file_hash(file_path)
                key_parts.append(('hash', file_hash if file_hash else 'HASH_ERROR'))
            
            # Uzantı her zaman dahil
            ext = os.path.splitext(file_path)[1].lower()
            key_parts.append(('ext', ext))
            
            return tuple(key_parts)
        
        # Dosyaları grupla
        processed = 0
        for file_path in file_list:
            try:
                if not os.path.exists(file_path):
                    if self.debug_mode:
                        print(f"⚠️ Dosya bulunamadı: {file_path}")
                    continue
                
                key = get_duplicate_key(file_path)
                duplicate_groups[key].append(file_path)
                processed += 1
                
                # Her 100 dosyada bir rapor
                if processed % 100 == 0 and self.debug_mode:
                    print(f"İşlenen: {processed}/{len(file_list)}")
                    
            except Exception as e:
                print(f"❌ Duplikat kontrol hatası {file_path}: {e}")
                unique_files.append(file_path)
        
        if self.debug_mode:
            print(f"✅ Gruplama tamamlandı: {len(duplicate_groups)} grup")
        
        # Duplikat grupları ve unique dosyaları ayır
        self.duplicate_groups = {}
        group_id = 1
        
        for key, files in duplicate_groups.items():
            if len(files) > 1:
                # Duplikat grup bulundu
                group_name = f"Grup {group_id}"
                self.duplicate_groups[group_name] = files
                if self.debug_mode:
                    print(f"🔄 {group_name}: {len(files)} dosya - {[os.path.basename(f) for f in files[:2]]}{'...' if len(files) > 2 else ''}")
                group_id += 1
            else:
                # Unique dosya
                unique_files.extend(files)
        
        self.unique_files = unique_files
        
        if self.debug_mode:
            print(f"📊 Sonuç: {len(self.duplicate_groups)} duplikat grup, {len(unique_files)} benzersiz dosya")
        
        # Eski format için duplikat listesi
        duplicates = []
        for files in self.duplicate_groups.values():
            duplicates.extend(files)
            
        return duplicates
    
    def find_duplicates(self, file_list):
        """Eski duplikat fonksiyonu - geriye uyumluluk için"""
        return self.find_duplicates_advanced(file_list)
    
    def populate_duplicate_tree(self):
        """Duplikat tree'sini doldur"""
        self.duplicate_tree.delete(*self.duplicate_tree.get_children())
        
        if not self.duplicate_groups:
            # Duplikat yok mesajı
            self.duplicate_tree.insert('', 'end', text="✅ Duplikat dosya bulunamadı!", 
                                     values=("", "", ""))
            return
        
        for group_name, files in self.duplicate_groups.items():
            # Grup başlığı
            group_icon = "🔄"
            group_text = f"{group_icon} {group_name} ({len(files)} dosya)"
            group_item = self.duplicate_tree.insert('', 'end', text=group_text, 
                                                  values=("", "", ""))
            
            # Grup dosyaları
            for i, file_path in enumerate(files):
                try:
                    file_size = os.path.getsize(file_path)
                    file_hash = ""
                    
                    # Hash hesaplama sadece gerekli ise
                    if self.duplicate_check_hash.get():
                        file_hash = self.get_file_hash(file_path) or "Hesaplanamadı"
                    
                    # Dosya ikonu
                    file_icon = "📄" if i == 0 else "📄"  # İlk dosya orijinal sayılabilir
                    
                    # Relative path hesaplama - farklı disk sürücüleri için güvenli
                    try:
                        if self.source_path and os.path.exists(self.source_path):
                            # Aynı disk sürücüsünde mi kontrol et
                            source_drive = os.path.splitdrive(self.source_path)[0]
                            file_drive = os.path.splitdrive(file_path)[0]
                            
                            if source_drive.lower() == file_drive.lower():
                                rel_path = os.path.relpath(file_path, self.source_path)
                            else:
                                # Farklı disk sürücüleri - sadece dosya adını göster
                                rel_path = f"[{file_drive}] {os.path.basename(file_path)}"
                        else:
                            rel_path = os.path.basename(file_path)
                    except (ValueError, OSError):
                        # Hata durumunda sadece dosya adını göster
                        rel_path = os.path.basename(file_path)
                    
                    self.duplicate_tree.insert(group_item, 'end', 
                                             text=f"  {file_icon} {os.path.basename(file_path)}", 
                                             values=(rel_path, self.format_size(file_size), file_hash[:16] + "..." if len(file_hash) > 16 else file_hash))
                except Exception as e:
                    print(f"Duplikat tree hatası: {file_path} - {e}")
            
            # Grubu genişlet
            self.duplicate_tree.item(group_item, open=True)
        
    def verify_and_fix_target_structure(self):
        """Hedef klasör yapısını kontrol et ve gerekirse düzelt"""
        try:
            # Tüm kategori klasörlerini listele
            expected_folders = set()
            for category, cat_info in self.file_categories.items():
                expected_folders.add(cat_info['folder'])
            
            # Duplikat klasörünü de ekle
            expected_folders.add("Duplikat_Dosyalar")
            
            # Mevcut klasörleri tara
            current_folders = {}  # folder_name -> current_path
            
            def scan_for_folders(root_path, depth=0):
                """Klasörleri recursively tara"""
                if depth > 3:  # Çok derinlere inme
                    return
                    
                try:
                    for item in os.listdir(root_path):
                        if self.is_hidden_file(item):
                            continue
                            
                        item_path = os.path.join(root_path, item)
                        if os.path.isdir(item_path):
                            # Beklenen klasörlerden biri mi?
                            if item in expected_folders:
                                current_folders[item] = item_path
                            
                            # Alt klasörleri de tara
                            scan_for_folders(item_path, depth + 1)
                except:
                    pass
            
            # Hedef klasörü tara
            scan_for_folders(self.target_path)
            
            # Yanlış yerde olan klasörleri düzelt
            moved_folders = []
            
            for folder_name in expected_folders:
                if folder_name in current_folders:
                    current_path = current_folders[folder_name]
                    expected_path = os.path.join(self.target_path, folder_name)
                    
                    # Eğer yanlış yerdeyse taşı
                    if current_path != expected_path:
                        try:
                            # Hedef konumda zaten var mı kontrol et
                            if os.path.exists(expected_path):
                                # Mevcut içeriği birleştir
                                self.merge_folders(current_path, expected_path)
                                # Eski klasörü sil
                                shutil.rmtree(current_path)
                            else:
                                # Doğrudan taşı
                                shutil.move(current_path, expected_path)
                            
                            moved_folders.append(f"{folder_name}: {current_path} → {expected_path}")
                        except Exception as e:
                            print(f"Klasör taşıma hatası {folder_name}: {e}")
                else:
                    # Klasör yok, oluştur
                    folder_path = os.path.join(self.target_path, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
            
            # Kullanıcıya rapor ver
            if moved_folders:
                report = "Aşağıdaki klasörler düzeltildi:\n\n" + "\n".join(moved_folders)
                messagebox.showinfo("Klasör Yapısı Düzeltildi", report)
                
            self.status_var.set("Klasör yapısı kontrol edildi.")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör yapısı kontrolü sırasında hata: {e}")
    
    def merge_folders(self, source_folder, target_folder):
        """İki klasörü birleştir"""
        try:
            for item in os.listdir(source_folder):
                if self.is_hidden_file(item):
                    continue
                    
                source_item = os.path.join(source_folder, item)
                target_item = os.path.join(target_folder, item)
                
                if os.path.isdir(source_item):
                    # Alt klasör
                    if os.path.exists(target_item):
                        # Recursive birleştir
                        self.merge_folders(source_item, target_item)
                    else:
                        # Taşı
                        shutil.move(source_item, target_item)
                else:
                    # Dosya
                    if os.path.exists(target_item):
                        # Aynı isimde dosya var, numara ekle
                        counter = 1
                        name, ext = os.path.splitext(item)
                        while os.path.exists(target_item):
                            new_name = f"{name}_{counter}{ext}"
                            target_item = os.path.join(target_folder, new_name)
                            counter += 1
                    
                    shutil.move(source_item, target_item)
                    
        except Exception as e:
            print(f"Klasör birleştirme hatası: {e}")
    
    def find_and_move_category_folder(self, folder_name):
        """Kategori klasörünü ara ve doğru konuma taşı"""
        try:
            # Hedef klasör içinde arama yap
            for root, dirs, files in os.walk(self.target_path):
                if folder_name in dirs:
                    found_path = os.path.join(root, folder_name)
                    expected_path = os.path.join(self.target_path, folder_name)
                    
                    # Eğer yanlış konumdaysa taşı
                    if found_path != expected_path:
                        try:
                            if os.path.exists(expected_path):
                                # Hedefte zaten var, birleştir
                                self.merge_folders(found_path, expected_path)
                                shutil.rmtree(found_path)
                            else:
                                # Doğrudan taşı
                                shutil.move(found_path, expected_path)
                            
                            self.status_var.set(f"'{folder_name}' klasörü düzeltildi.")
                            return expected_path
                        except Exception as e:
                            print(f"Klasör taşıma hatası: {e}")
                            return None
                    else:
                        return found_path
            
            return None
        except Exception as e:
            print(f"Klasör arama hatası: {e}")
            return None
    
    def is_file_locked(self, file_path):
        """Dosyanın kilitli olup olmadığını kontrol et"""
        try:
            with open(file_path, 'rb') as f:
                pass
            return False
        except (PermissionError, OSError, IOError):
            return True
    
    def copy_file_optimized(self, source_path, target_path):
        """Optimize edilmiş dosya kopyalama"""
        try:
            # Küçük dosyalar için normal copy
            file_size = os.path.getsize(source_path)
            
            if file_size < 1024 * 1024:  # 1MB'den küçük
                shutil.copy2(source_path, target_path)
            else:
                # Büyük dosyalar için chunk-based copy
                self.copy_file_chunked(source_path, target_path)
                
        except Exception as e:
            # Fallback to normal copy
            shutil.copy2(source_path, target_path)
    
    def copy_file_chunked(self, source_path, target_path):
        """Büyük dosyalar için chunk-based kopyalama"""
        chunk_size = 1024 * 1024  # 1MB chunks
        
        with open(source_path, 'rb') as src:
            with open(target_path, 'wb') as dst:
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
        
        # Metadata'yı kopyala
        shutil.copystat(source_path, target_path)
         
    def start_organization(self):
        if not self.source_path or not self.target_path:
            messagebox.showerror("Hata", "Lütfen kaynak ve hedef klasörleri seçin!")
            return
        
        # Kullanıcıya onay sor
        confirm_msg = """Organizasyon işlemi başlatılacak:

✓ Hedef klasör yapısı kontrol edilecek ve düzeltilecek
✓ Yanlış konumdaki kategori klasörleri taşınacak  
✓ Dosyalar kategorilerine göre organize edilecek
✓ Duplikat dosyalar ayrı klasöre konulacak

Devam etmek istiyor musunuz?"""
        
        if not messagebox.askyesno("Organizasyon Onayı", confirm_msg):
            return
            
        def organize_thread():
            try:
                self.status_var.set("Hedef klasör yapısı kontrol ediliyor...")
                
                # Hedef klasör yapısını kontrol et ve düzelt
                self.verify_and_fix_target_structure()
                
                self.status_var.set("Dosyalar organize ediliyor...")
                
                # Önceden taranan dosyaları kullan
                if not hasattr(self, 'unique_files') or not self.unique_files:
                    self.root.after(0, lambda: messagebox.showerror("Hata", "Önce dosyaları tarayın!"))
                    return
                
                if self.debug_mode:
                    print(f"📁 Kaynak dosyalar: {len(self.unique_files)} dosya")
                
                # Duplikatları kontrol et (tarama sırasında zaten yapıldı)
                source_duplicates = []
                for group_files in self.duplicate_groups.values():
                    for file_path in group_files:
                        if file_path in self.unique_files:  # Kaynak dosyalarda var
                            source_duplicates.append(file_path)
                            if self.debug_mode:
                                print(f"🔄 Duplikat bulundu: {os.path.basename(file_path)}")
                
                # Organize edilecek dosyalar (unique - duplikatlar)
                all_files = [f for f in self.unique_files if f not in source_duplicates]
                self.duplicate_files = source_duplicates
                self.target_duplicates_count = 0  # Hedef klasörde bulunan duplikat sayısı
                
                if self.debug_mode:
                    print(f"📊 Organize edilecek: {len(all_files)} dosya, Duplikat atlanan: {len(source_duplicates)} dosya")
                
                total_files = len(all_files)
                processed_files = 0
                failed_files = 0
                skipped_files = 0
                
                # Duplikat klasörünü oluştur
                duplicate_folder = os.path.join(self.target_path, "Duplikat_Dosyalar")
                os.makedirs(duplicate_folder, exist_ok=True)
                
                # Batch işleme için
                batch_size = 50
                current_batch = 0
                
                for i, file_path in enumerate(all_files):
                    try:
                        # Dosya hala mevcut mu kontrol et
                        if not os.path.exists(file_path):
                            skipped_files += 1
                            continue
                            
                        # Dosya kilitli mi kontrol et
                        if self.is_file_locked(file_path):
                            if self.debug_mode:
                                print(f"⚠️ Dosya kilitli, atlanıyor: {file_path}")
                            skipped_files += 1
                            continue
                        
                        category, cat_info = self.get_file_category(file_path)
                        file_ext = Path(file_path).suffix.lower()
                        
                        # Hedef klasör yapısını oluştur - önce doğru konumda olduğundan emin ol
                        main_folder = os.path.join(self.target_path, cat_info['folder'])
                        
                        # Ana klasörün doğru konumda olduğunu kontrol et
                        if not os.path.exists(main_folder):
                            # Belki başka yerde taşınmış, ara ve düzelt
                            found_folder = self.find_and_move_category_folder(cat_info['folder'])
                            if found_folder:
                                main_folder = found_folder
                            else:
                                os.makedirs(main_folder, exist_ok=True)
                        
                        # Alt klasör varsa oluştur
                        if 'subfolders' in cat_info and file_ext in cat_info['subfolders']:
                            sub_folder = cat_info['subfolders'][file_ext]
                            target_folder = os.path.join(main_folder, sub_folder)
                        else:
                            target_folder = main_folder
                        
                        os.makedirs(target_folder, exist_ok=True)
                        
                        # Dosya adını hazırla
                        file_name = os.path.basename(file_path)
                        target_file_path = os.path.join(target_folder, file_name)
                        
                        # Hedef klasörde aynı dosya var mı kontrol et (hızlı kontrol)
                        is_duplicate_in_target = False
                        
                        if os.path.exists(target_file_path):
                            # Önce boyut karşılaştırması (hızlı)
                            try:
                                source_size = os.path.getsize(file_path)
                                target_size = os.path.getsize(target_file_path)
                                
                                if source_size == target_size:
                                    # Hash karşılaştırması sadece gerekli ise (yavaş)  
                                    if self.duplicate_check_hash.get():
                                        source_hash = self.get_file_hash(file_path)
                                        target_hash = self.get_file_hash(target_file_path)
                                        is_duplicate_in_target = (source_hash == target_hash)
                                    else:
                                        # Dosya adı + boyut karşılaştırması (hızlı)
                                        source_name = os.path.basename(file_path).lower()
                                        target_name = os.path.basename(target_file_path).lower()
                                        is_duplicate_in_target = (source_name == target_name)
                            except OSError:
                                # Dosya erişim hatası, devam et
                                pass
                                    
                            if self.debug_mode and is_duplicate_in_target:
                                print(f"🔄 Hedef klasörde aynı dosya tespit edildi: {file_name}")
                        
                        # Duplikat kontrolü - önce genel duplikat listesi, sonra hedef klasör kontrolü
                        if file_path in self.duplicate_files or is_duplicate_in_target:
                            # Kullanıcıdan onay al
                            duplicate_action = None
                            
                            # UI thread'de onay al
                            def get_user_choice():
                                nonlocal duplicate_action
                                duplicate_action = self.ask_duplicate_action(file_name)
                            
                            self.root.after(0, get_user_choice)
                            
                            # Kullanıcı cevabını bekle
                            while duplicate_action is None:
                                import time
                                time.sleep(0.1)
                            
                            if duplicate_action in ["skip", "skip_all"]:
                                # Dosyayı atla
                                skipped_files += 1
                                if self.debug_mode:
                                    print(f"🚫 Duplikat atlandı: {file_name}")
                                continue
                            elif duplicate_action in ["copy", "copy_all"]:
                                # Duplikat klasörüne koy
                                target_file_path = os.path.join(duplicate_folder, file_name)
                                
                                # Aynı isimde dosya varsa numara ekle
                                counter = 1
                                base_name, ext = os.path.splitext(file_name)
                                while os.path.exists(target_file_path):
                                    new_name = f"{base_name}_{counter}{ext}"
                                    target_file_path = os.path.join(duplicate_folder, new_name)
                                    counter += 1
                                    
                                if is_duplicate_in_target:
                                    self.target_duplicates_count += 1
                                    
                                if self.debug_mode:
                                    if is_duplicate_in_target:
                                        print(f"🔄 Hedef klasörde duplikat bulundu: {file_name} -> {target_folder}")
                                    else:
                                        print(f"🔄 Genel duplikat listesinde: {file_name}")
                        else:
                            # Normal dosya için aynı isim kontrolü
                            counter = 1
                            base_name, ext = os.path.splitext(file_name)
                            while os.path.exists(target_file_path):
                                new_name = f"{base_name}_{counter}{ext}"
                                target_file_path = os.path.join(target_folder, new_name)
                                counter += 1
                        
                        # Dosyayı kopyala - optimized copy
                        self.copy_file_optimized(file_path, target_file_path)
                        
                        if self.debug_mode:
                            print(f"✅ Kopyalandı: {file_name} -> {os.path.relpath(target_file_path, self.target_path)}")
                        
                        processed_files += 1
                        
                        # Progress güncelleme - her 10 dosyada bir
                        if processed_files % 10 == 0 or processed_files == total_files:
                            progress = (processed_files / total_files) * 100
                            self.root.after(0, lambda p=progress: self.progress_var.set(p))
                            
                            # Status güncelleme
                            status_text = f"İşleniyor: {processed_files}/{total_files} dosya ({progress:.1f}%)"
                            self.root.after(0, lambda s=status_text: self.status_var.set(s))
                        
                        # Batch işleme - UI donmasını önle
                        current_batch += 1
                        if current_batch >= batch_size:
                            current_batch = 0
                            self.root.after(0, lambda: self.root.update_idletasks())
                            import time
                            time.sleep(0.01)  # Kısa pause
                        
                    except Exception as e:
                        failed_files += 1
                        error_msg = f"❌ Hata: {file_path} - {str(e)}"
                        print(error_msg)
                        
                        # Kritik hata mı kontrol et
                        if "Permission denied" in str(e) or "Access is denied" in str(e):
                            print(f"⚠️ İzin hatası, devam ediliyor: {file_path}")
                        elif "No space left" in str(e):
                            self.root.after(0, lambda: messagebox.showerror("Kritik Hata", "Hedef diskte yer kalmadı!"))
                            break
                        elif failed_files > 10:
                            # Çok fazla hata varsa kullanıcıya sor
                            if not messagebox.askyesno("Çok Fazla Hata", f"{failed_files} dosya kopyalanamadı. Devam etmek istiyor musunuz?"):
                                break
                
                # Final statistics
                total_duplicates = len(self.duplicate_files) + self.target_duplicates_count
                success_rate = (processed_files / total_files * 100) if total_files > 0 else 0
                
                final_status = f"Tamamlandı! {processed_files} başarılı, {failed_files} hata, {skipped_files} atlandı"
                self.root.after(0, lambda s=final_status: self.status_var.set(s))
                self.root.after(0, lambda: self.progress_var.set(0))
                
                # Detaylı rapor
                report = f"""📊 ORGANIZASYON RAPORU

✅ Başarıyla organize edilen: {processed_files} dosya
❌ Hata ile karşılaşılan: {failed_files} dosya  
⏭️ Atlanan dosyalar: {skipped_files} dosya
🔄 Duplikat olarak atlanan: {total_duplicates} dosya
   • Kaynak klasörde duplikat: {len(self.duplicate_files)} dosya
   • Hedef klasörde zaten mevcut: {self.target_duplicates_count} dosya
📈 Başarı oranı: {success_rate:.1f}%

📈 Kategori dağılımı:"""
                
                # Kategori istatistikleri ekle
                category_stats = defaultdict(int)
                for file_path in all_files[:processed_files]:  # Sadece işlenen dosyalar
                    try:
                        category, _ = self.get_file_category(file_path)
                        category_stats[category] += 1
                    except:
                        pass
                
                for category, count in sorted(category_stats.items()):
                    report += f"\n  • {category}: {count} dosya"
                
                self.root.after(0, lambda r=report: messagebox.showinfo("Organizasyon Tamamlandı", r))
                
            except Exception as e:
                error_msg = f"Kritik hata: {str(e)}"
                print(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Kritik Hata", error_msg))
            finally:
                # Her durumda progress bar'ı sıfırla
                self.root.after(0, lambda: self.progress_var.set(0))
            
        threading.Thread(target=organize_thread, daemon=True).start()
        
    def show_duplicates(self):
        if not self.duplicate_files:
            messagebox.showinfo("Bilgi", "Henüz duplikat dosya taraması yapılmadı.")
            return
            
        # Duplikat dosyaları gösteren yeni pencere
        dup_window = tk.Toplevel(self.root)
        dup_window.title("Duplikat Dosyalar")
        dup_window.geometry("600x400")
        
        dup_tree = ttk.Treeview(dup_window, columns=('size',), show='tree headings')
        dup_tree.heading('#0', text='Dosya Yolu')
        dup_tree.heading('size', text='Boyut')
        dup_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for file_path in self.duplicate_files:
            try:
                file_size = os.path.getsize(file_path)
                dup_tree.insert('', 'end', text=file_path, values=(f"{file_size:,} bytes"))
            except Exception as e:
                print(f"Hata: {e}")

    def load_files_on_demand(self, start_index, count):
        """Dosyaları ihtiyaç halinde yükle"""
        pass

    def update_ui_batch(self, items):
        """UI güncellemelerini toplu yap"""
        for item in items:
            # TODO: Implement tree insertion
            pass
        self.root.update_idletasks()

    async def scan_files_async(self):
        """Gerçek async implementasyon"""
        tasks = []
        for file_path in all_scanned_files:
            tasks.append(self.process_file_async(file_path))
        await asyncio.gather(*tasks)

    def ask_duplicate_action(self, file_name, duplicate_count=1):
        """Duplikat dosya için kullanıcıdan onay al"""
        if self.duplicate_action.get() == "skip":
            return "skip"
        elif self.duplicate_action.get() == "copy":
            return "copy"
        else:  # ask
            # Özel dialog oluştur
            dialog = tk.Toplevel(self.root)
            dialog.title("Duplikat Dosya Bulundu")
            dialog.geometry("500x200")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Dialog'u merkeze yerleştir
            dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
            
            result = {"action": "skip"}  # Default
            
            # İçerik
            main_frame = ttk.Frame(dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Uyarı ikonu ve mesaj
            msg_frame = ttk.Frame(main_frame)
            msg_frame.pack(fill=tk.X, pady=(0, 20))
            
            ttk.Label(msg_frame, text="⚠️", font=("Arial", 24)).pack(side=tk.LEFT, padx=(0, 10))
            
            msg_text = f"Duplikat dosya bulundu:\n\n📄 {file_name}"
            if duplicate_count > 1:
                msg_text += f"\n\n🔄 Toplam {duplicate_count} duplikat dosya var."
            
            ttk.Label(msg_frame, text=msg_text, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Seçenekler
            option_frame = ttk.Frame(main_frame)
            option_frame.pack(fill=tk.X, pady=(0, 20))
            
            ttk.Label(option_frame, text="Ne yapmak istiyorsunuz?", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            # Butonlar
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            def on_skip():
                result["action"] = "skip"
                dialog.destroy()
                
            def on_copy():
                result["action"] = "copy"
                dialog.destroy()
                
            def on_skip_all():
                result["action"] = "skip_all"
                self.duplicate_action.set("skip")
                dialog.destroy()
                
            def on_copy_all():
                result["action"] = "copy_all"
                self.duplicate_action.set("copy")
                dialog.destroy()
            
            ttk.Button(button_frame, text="🚫 Bu dosyayı atla", command=on_skip).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="📋 Bu dosyayı kopyala", command=on_copy).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="🚫 Tümünü atla", command=on_skip_all).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="📋 Tümünü kopyala", command=on_copy_all).pack(side=tk.LEFT)
            
            # Dialog'u bekle
            dialog.wait_window()
            
            return result["action"]

    def analyze_target_disk(self):
        """Hedef disk analizi - ne var, ne yapılacak detaylı rapor"""
        if not self.target_path or not os.path.exists(self.target_path):
            messagebox.showwarning("Uyarı", "Önce hedef klasör seçin!")
            return
            
        if not hasattr(self, 'all_scanned_files') or not self.all_scanned_files:
            messagebox.showwarning("Uyarı", "Önce kaynak dosyaları tarayın!")
            return
        
        # Hedef disk analizi
        self.status_var.set("Hedef disk analiz ediliyor...")
        
        # Hedef diskteki mevcut dosyaları tara
        target_files = {}  # category -> files
        target_file_paths = []
        
        for root, dirs, files in os.walk(self.target_path):
            for file in files:
                if self.is_hidden_file(file):
                    continue
                    
                file_path = os.path.join(root, file)
                target_file_paths.append(file_path)
                
                # Kategorisini belirle
                category, cat_info = self.get_file_category(file_path)
                if category not in target_files:
                    target_files[category] = []
                target_files[category].append(file_path)
        
        # Kaynak dosyaları kategorilere ayır
        source_files = {}  # category -> files
        for file_path in self.all_scanned_files:
            category, cat_info = self.get_file_category(file_path)
            if category not in source_files:
                source_files[category] = []
            source_files[category].append(file_path)
        
        # Karşılaştırma analizi
        analysis_report = []
        analysis_report.append("🔍 HEDEF DİSK ANALİZ RAPORU")
        analysis_report.append("=" * 50)
        analysis_report.append("")
        
        # Genel istatistikler
        total_target_files = len(target_file_paths)
        total_source_files = len(self.all_scanned_files)
        
        analysis_report.append(f"📊 GENEL İSTATİSTİKLER:")
        analysis_report.append(f"   Hedef diskte mevcut: {total_target_files} dosya")
        analysis_report.append(f"   Kaynak klasörde: {total_source_files} dosya")
        analysis_report.append("")
        
        # Kategori bazında analiz
        all_categories = set(source_files.keys()) | set(target_files.keys())
        
        will_be_copied = 0
        will_be_skipped = 0
        already_exists = 0
        
        for category in sorted(all_categories):
            source_count = len(source_files.get(category, []))
            target_count = len(target_files.get(category, []))
            
            analysis_report.append(f"📁 {category.upper()}:")
            analysis_report.append(f"   Hedefte mevcut: {target_count} dosya")
            analysis_report.append(f"   Kaynakta: {source_count} dosya")
            
            if source_count > 0:
                # Bu kategorideki dosyalar için duplikat kontrolü
                source_files_in_category = source_files.get(category, [])
                target_files_in_category = target_files.get(category, [])
                
                duplicates_found = 0
                new_files = 0
                
                for source_file in source_files_in_category:
                    source_name = os.path.basename(source_file).lower()
                    source_size = 0
                    try:
                        source_size = os.path.getsize(source_file)
                    except:
                        continue
                    
                    is_duplicate = False
                    for target_file in target_files_in_category:
                        target_name = os.path.basename(target_file).lower()
                        target_size = 0
                        try:
                            target_size = os.path.getsize(target_file)
                        except:
                            continue
                        
                        if source_name == target_name and source_size == target_size:
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        duplicates_found += 1
                    else:
                        new_files += 1
                
                analysis_report.append(f"   → Yeni eklenecek: {new_files} dosya")
                analysis_report.append(f"   → Zaten var (duplikat): {duplicates_found} dosya")
                
                will_be_copied += new_files
                will_be_skipped += duplicates_found
                already_exists += duplicates_found
            
            analysis_report.append("")
        
        # Özet
        analysis_report.append("📋 ORGANIZE İŞLEMİ ÖZETİ:")
        analysis_report.append(f"   ✅ Kopyalanacak: {will_be_copied} dosya")
        analysis_report.append(f"   🔄 Duplikat (atlanacak/sorulacak): {will_be_skipped} dosya")
        analysis_report.append(f"   📁 Hedefte zaten var: {already_exists} dosya")
        analysis_report.append("")
        
        # Disk alanı tahmini
        total_size_to_copy = 0
        for file_path in self.all_scanned_files:
            try:
                # Sadece kopyalanacak dosyaları say (basit kontrol)
                source_name = os.path.basename(file_path).lower()
                source_size = os.path.getsize(file_path)
                
                is_duplicate = False
                for target_file in target_file_paths:
                    target_name = os.path.basename(target_file).lower()
                    try:
                        target_size = os.path.getsize(target_file)
                        if source_name == target_name and source_size == target_size:
                            is_duplicate = True
                            break
                    except:
                        continue
                
                if not is_duplicate:
                    total_size_to_copy += source_size
            except:
                continue
        
        analysis_report.append(f"💾 DISK ALANI TAHMİNİ:")
        analysis_report.append(f"   Kopyalanacak toplam boyut: {self.format_size(total_size_to_copy)}")
        
        # Hedef disk boş alanı kontrolü
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.target_path)
            analysis_report.append(f"   Hedef diskte boş alan: {self.format_size(free)}")
            
            if total_size_to_copy > free:
                analysis_report.append("   ⚠️ UYARI: Yeterli disk alanı yok!")
            else:
                analysis_report.append("   ✅ Yeterli disk alanı var")
        except:
            analysis_report.append("   Disk alanı kontrol edilemedi")
        
        # Raporu göster
        report_text = "\n".join(analysis_report)
        
        # Yeni pencerede göster
        report_window = tk.Toplevel(self.root)
        report_window.title("Hedef Disk Analiz Raporu")
        report_window.geometry("800x600")
        
        # Text widget
        text_frame = ttk.Frame(report_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, report_text)
        text_widget.config(state=tk.DISABLED)
        
        # Butonlar
        button_frame = ttk.Frame(report_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Raporu Kaydet", 
                  command=lambda: self.save_report(report_text)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Kapat", 
                  command=report_window.destroy).pack(side=tk.RIGHT)
        
        self.status_var.set("Hedef disk analizi tamamlandı.")
        
        if self.debug_mode:
            print("📊 Hedef disk analizi tamamlandı")
            print(f"   Kopyalanacak: {will_be_copied} dosya")
            print(f"   Duplikat: {will_be_skipped} dosya")

    def save_report(self, report_text):
        """Raporu dosyaya kaydet"""
        try:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Raporu Kaydet"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                messagebox.showinfo("Başarılı", f"Rapor kaydedildi:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor kaydedilemedi: {e}")

def main():
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop()

if __name__ == "__main__":
    main() 