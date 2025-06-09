"""
GUI Manager Module
Ana GUI yapısını ve pencere yönetimini içerir
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from pathlib import Path

# Multi-language support
from lang_manager import t, set_language, get_languages
from language_switcher import LanguageSwitcher

class GUIManager:
    def __init__(self, root):
        self.root = root
        self.setup_main_window()
        self.setup_variables()
        self.setup_ui()
        
    def setup_main_window(self):
        """Ana pencere ayarları"""
        self.root.title(t('app.title'))
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        
        # Icon ayarla (varsa)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def setup_variables(self):
        """UI değişkenlerini tanımla"""
        # Klasör yolları
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.current_path_var = tk.StringVar()
        
        # Tarama seçenekleri
        self.scan_subfolders = tk.BooleanVar(value=True)
        
        # Yeni tarama modu değişkeni: "all", "none", "files_only"
        self.scan_mode = tk.StringVar(value="all")
        
        # Duplikat kontrol seçenekleri
        self.duplicate_check_name = tk.BooleanVar(value=True)
        self.duplicate_check_size = tk.BooleanVar(value=True)
        self.duplicate_check_hash = tk.BooleanVar(value=False)
        self.duplicate_action = tk.StringVar(value="ask")
        
        # Progress ve status
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Hazır")
        
        # Time estimation variables
        self.time_estimation_var = tk.StringVar(value="")
        self.operation_start_time = None
        self.last_progress_time = None
        self.estimated_total_time = None
        
    def setup_ui(self):
        """Ana UI bileşenlerini oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst panel - Klasör seçimi
        self.setup_folder_selection(main_frame)
        
        # Orta panel - İki pencere
        self.setup_main_panels(main_frame)
        
        # Alt panel - Kontroller ve durum
        self.setup_bottom_panel(main_frame)
        
    def setup_folder_selection(self, parent):
        """Klasör seçim paneli"""
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Language switcher - sağ üst köşe
        lang_frame = ttk.Frame(top_frame)
        lang_frame.grid(row=0, column=3, sticky=tk.E, padx=(10, 0))
        
        self.language_switcher = LanguageSwitcher(lang_frame, self.on_language_change)
        self.language_switcher.pack()
        
        # Source klasör seçimi
        ttk.Label(top_frame, text=t('menu.file.select_source')).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(top_frame, textvariable=self.source_var, width=50).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(top_frame, text=t('buttons.select'), command=self.select_source_folder).grid(row=0, column=2)
        
        # Target SSD seçimi
        ttk.Label(top_frame, text=t('menu.file.select_target')).grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Entry(top_frame, textvariable=self.target_var, width=50).grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        ttk.Button(top_frame, text=t('buttons.change'), command=self.select_target_folder).grid(row=1, column=2, pady=(5, 0))
        
        # Alt klasör tarama seçeneği
        self.setup_scan_options(top_frame)
        
    def setup_scan_options(self, parent):
        """Tarama seçenekleri"""
        scan_frame = ttk.Frame(parent)
        scan_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(scan_frame, text="Alt klasör tarama modu:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Seçenek 1: Tüm alt klasörleri tara
        ttk.Radiobutton(scan_frame, text="✅ Tüm alt klasörleri tara (dosyaları kategorilere ayır)", 
                       variable=self.scan_mode, value="all").pack(side=tk.LEFT, padx=(0, 15))
        
        # Seçenek 2: Klasörleri komple kopyala
        ttk.Radiobutton(scan_frame, text="📁 Klasörleri komple kopyala (klasör yapısını koru)", 
                       variable=self.scan_mode, value="none").pack(side=tk.LEFT, padx=(0, 15))
        
        # Seçenek 3: Sadece dosyaları tara (YENİ)
        ttk.Radiobutton(scan_frame, text="📄 Sadece dosyaları tara (alt klasörleri görmezden gel)", 
                       variable=self.scan_mode, value="files_only").pack(side=tk.LEFT)
        
        # Hatırlatma mesajı
        reminder_frame = ttk.Frame(parent)
        reminder_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        reminder_text = ("💡 HATIRLATMA: \n"
                        "• 'Tüm alt klasörleri tara': Tüm dosyaları kategorilere ayırır\n"
                        "• 'Klasörleri komple kopyala': Klasör yapısını korur\n"
                        "• 'Sadece dosyaları tara': Alt klasörlerdeki dosyaları görmezden gelir, sadece ana klasördeki dosyaları işler")
        
        reminder_label = ttk.Label(reminder_frame, text=reminder_text, 
                                 foreground="blue", font=('Arial', 8, 'italic'))
        reminder_label.pack(side=tk.LEFT, padx=(20, 0))
        
    def setup_main_panels(self, parent):
        """Ana paneller - sol ve sağ"""
        middle_frame = ttk.Frame(parent)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Sol panel - Hedef File Manager
        self.setup_target_panel(middle_frame)
        
        # Sağ panel - Kaynak Dosyalar ve Organizasyon
        self.setup_source_panel(middle_frame)
        
    def setup_target_panel(self, parent):
        """Sol panel - Hedef klasör file manager"""
        left_frame = ttk.LabelFrame(parent, text="Hedef Klasör - File Manager")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Navigasyon kontrolleri
        nav_frame = ttk.Frame(left_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        ttk.Button(nav_frame, text="◀ " + t('buttons.back'), command=self.go_back).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="▲ " + t('buttons.up'), command=self.go_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="🏠 " + t('buttons.home'), command=self.go_home).pack(side=tk.LEFT, padx=(0, 5))
        
        # Yol gösterge çubuğu
        path_frame = ttk.Frame(left_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        ttk.Label(path_frame, text=t('labels.location') + ":").pack(side=tk.LEFT)
        self.path_entry = ttk.Entry(path_frame, textvariable=self.current_path_var, font=('Consolas', 9))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.path_entry.bind('<Return>', self.navigate_to_path)
        ttk.Button(path_frame, text=t('buttons.go'), command=self.navigate_to_path).pack(side=tk.RIGHT)

        # File manager kontrolleri
        target_controls = ttk.Frame(left_frame)
        target_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(target_controls, text="🔄 " + t('buttons.refresh'), command=self.refresh_target).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="🗑️ " + t('buttons.delete'), command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="📋 " + t('buttons.copy'), command=self.copy_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="✂️ " + t('buttons.cut'), command=self.cut_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="📁 " + t('buttons.paste'), command=self.paste_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="➕ " + t('buttons.new_folder'), command=self.create_folder).pack(side=tk.LEFT, padx=(0, 5))
        
        # Hedef klasör ağacı
        self.setup_target_tree(left_frame)
        
    def setup_target_tree(self, parent):
        """Hedef klasör tree widget"""
        target_frame = ttk.Frame(parent)
        target_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        self.target_tree = ttk.Treeview(target_frame, columns=('size', 'type', 'modified'), show='tree headings')
        self.target_tree.heading('#0', text='📁 ' + t('labels.file_folder_name'), command=lambda: self.sort_tree('#0'))
        self.target_tree.heading('size', text='📏 ' + t('labels.size'), command=lambda: self.sort_tree('size'))
        self.target_tree.heading('type', text='🏷️ ' + t('labels.type'), command=lambda: self.sort_tree('type'))
        self.target_tree.heading('modified', text='📅 ' + t('labels.modified'), command=lambda: self.sort_tree('modified'))
        self.target_tree.column('#0', width=250)
        self.target_tree.column('size', width=80)
        self.target_tree.column('type', width=80)
        self.target_tree.column('modified', width=120)
        
        target_scrollbar = ttk.Scrollbar(target_frame, orient=tk.VERTICAL, command=self.target_tree.yview)
        self.target_tree.configure(yscrollcommand=target_scrollbar.set)
        
        self.target_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        target_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Event bindings
        self.setup_target_tree_events()
    
    def on_language_change(self, lang_code):
        """Dil değiştirildiğinde tüm UI'ı güncelle"""
        # Ana pencere başlığını güncelle
        self.root.title(t('app.title'))
        
        # Tüm widget'ları yeniden yükle
        self.refresh_ui_texts()
        
    def refresh_ui_texts(self):
        """Tüm UI metinlerini yenile"""
        # Ana widget'ları güncelleme gelecek sürümlerde geliştirilecek
        pass
        
    def setup_target_tree_events(self):
        """Target tree event bindings"""
        # Çift tıklama ve sağ tık menüsü
        self.target_tree.bind('<Double-1>', self.on_target_double_click)
        self.target_tree.bind('<Button-3>', self.show_context_menu)
        
        # Klavye kısayolları - target_tree'ye özel
        self.target_tree.bind('<Delete>', lambda e: self.delete_selected())
        self.target_tree.bind('<Control-c>', lambda e: self.copy_selected())
        self.target_tree.bind('<Control-x>', lambda e: self.cut_selected())
        self.target_tree.bind('<Control-v>', lambda e: self.paste_selected())
        self.target_tree.bind('<F2>', lambda e: self.rename_selected())
        self.target_tree.bind('<F5>', lambda e: self.refresh_target())
        self.target_tree.bind('<BackSpace>', lambda e: self.go_up())
        self.target_tree.bind('<Return>', lambda e: self.open_selected())
        
    def setup_source_panel(self, parent):
        """Sağ panel - Kaynak dosyalar ve organizasyon"""
        right_frame = ttk.LabelFrame(parent, text="Kaynak Dosyalar ve Organizasyon Önizleme")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Notebook için tab'lar
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Kaynak dosyalar
        self.setup_source_tab()
        
        # Tab 2: Organizasyon önizleme
        self.setup_preview_tab()
        
        # Tab 3: Duplikat dosyalar
        self.setup_duplicate_tab()
        
    def setup_source_tab(self):
        """Kaynak dosyalar tab"""
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
        
    def setup_preview_tab(self):
        """Organizasyon önizleme tab"""
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
        
    def setup_duplicate_tab(self):
        """Duplikat dosyalar tab"""
        duplicate_tab = ttk.Frame(self.notebook)
        self.notebook.add(duplicate_tab, text="🔄 Duplikat Dosyalar")
        
        # Duplikat kontrol seçenekleri
        self.setup_duplicate_controls(duplicate_tab)
        
        # Duplikat tree
        self.setup_duplicate_tree(duplicate_tab)
        
    def setup_duplicate_controls(self, parent):
        """Duplikat kontrol seçenekleri"""
        # Duplikat kontrol seçenekleri
        dup_controls = ttk.Frame(parent)
        dup_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dup_controls, text="Duplikat Kontrol:").pack(side=tk.LEFT)
        ttk.Checkbutton(dup_controls, text="İsim", variable=self.duplicate_check_name).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Checkbutton(dup_controls, text="Boyut", variable=self.duplicate_check_size).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(dup_controls, text="Hash", variable=self.duplicate_check_hash).pack(side=tk.LEFT, padx=5)
        
        # Duplikat işlem seçenekleri
        dup_action_frame = ttk.Frame(parent)
        dup_action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dup_action_frame, text="Duplikat dosyalar için:").pack(side=tk.LEFT)
        ttk.Radiobutton(dup_action_frame, text="Her seferinde sor", 
                       variable=self.duplicate_action, value="ask").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Radiobutton(dup_action_frame, text="Otomatik atla", 
                       variable=self.duplicate_action, value="skip").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(dup_action_frame, text="Numara ekleyerek taşı", 
                       variable=self.duplicate_action, value="copy").pack(side=tk.LEFT, padx=5)
        
    def setup_duplicate_tree(self, parent):
        """Duplikat dosyalar tree"""
        self.duplicate_tree = ttk.Treeview(parent, columns=('path', 'size', 'hash'), show='tree headings')
        self.duplicate_tree.heading('#0', text='🔄 Duplikat Dosya Grupları')
        self.duplicate_tree.heading('path', text='Dosya Yolu')
        self.duplicate_tree.heading('size', text='Boyut')
        self.duplicate_tree.heading('hash', text='Hash')
        self.duplicate_tree.column('#0', width=200)
        self.duplicate_tree.column('path', width=300)
        self.duplicate_tree.column('size', width=80)
        self.duplicate_tree.column('hash', width=120)
        
        duplicate_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.duplicate_tree.yview)
        self.duplicate_tree.configure(yscrollcommand=duplicate_scrollbar.set)
        
        self.duplicate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        duplicate_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_bottom_panel(self, parent):
        """Alt panel - butonlar, progress, status"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=tk.X)
        
        # Butonlar
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame, text="Dosyaları Tara", command=self.scan_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔍 Hedef Disk Analizi", command=self.analyze_target_disk).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Organizasyonu Başlat", command=self.start_organization).pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Time estimation label
        time_frame = ttk.Frame(bottom_frame)
        time_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.time_label = ttk.Label(time_frame, textvariable=self.time_estimation_var, 
                                   font=('Arial', 9), foreground='blue')
        self.time_label.pack(side=tk.RIGHT)
        
        # Durum etiketi
        status_label = ttk.Label(bottom_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X)
        
    # Placeholder metodlar - main_modular.py'de gerçek metodlarla değiştirilecek
    # Placeholder metodlar - main_modular.py'de rebind_buttons() ile değiştirilecek
    def select_source_folder(self):
        """Kaynak klasör seçimi - file_operations modülünden çağrılacak"""
        pass
        
    def select_target_folder(self):
        """Hedef klasör seçimi - file_operations modülünden çağrılacak"""
        pass
        
    def go_back(self):
        """Geri git - file_operations modülünden çağrılacak"""
        pass
        
    def go_up(self):
        """Üst klasör - file_operations modülünden çağrılacak"""
        pass
        
    def go_home(self):
        """Ana klasör - file_operations modülünden çağrılacak"""
        pass
        
    def navigate_to_path(self, event=None):
        """Yola git - file_operations modülünden çağrılacak"""
        pass
        
    def refresh_target(self):
        """Hedef klasörü yenile - file_operations modülünden çağrılacak"""
        pass
        
    def delete_selected(self):
        """Seçili dosyaları sil - file_operations modülünden çağrılacak"""
        pass
        
    def copy_selected(self):
        """Seçili dosyaları kopyala - file_operations modülünden çağrılacak"""
        pass
        
    def cut_selected(self):
        """Seçili dosyaları kes - file_operations modülünden çağrılacak"""
        pass
        
    def paste_selected(self):
        """Dosyaları yapıştır - file_operations modülünden çağrılacak"""
        pass
        
    def create_folder(self):
        """Yeni klasör oluştur - file_operations modülünden çağrılacak"""
        pass
        
    def sort_tree(self, column):
        """Tree sıralama - file_operations modülünden çağrılacak"""
        pass
        
    def on_target_double_click(self, event):
        """Çift tıklama - file_operations modülünden çağrılacak"""
        pass
        
    def show_context_menu(self, event):
        """Sağ tık menüsü - file_operations modülünden çağrılacak"""
        pass
        
    def rename_selected(self):
        """Dosya adını değiştir - file_operations modülünden çağrılacak"""
        pass
        
    def open_selected(self):
        """Dosya/klasör aç - file_operations modülünden çağrılacak"""
        pass
        
    def scan_files(self):
        """Dosya tarama - scan_engine modülünden çağrılacak"""
        pass
        
    def analyze_target_disk(self):
        """Hedef disk analizi - reporting modülünden çağrılacak"""
        pass
        
    def start_organization(self):
        """Organizasyon başlat - file_operations modülünden çağrılacak"""
        pass
        

        
    def start_time_estimation(self):
        """Zaman tahmini başlat"""
        import time
        self.operation_start_time = time.time()
        self.last_progress_time = time.time()
        self.estimated_total_time = None
        self.time_estimation_var.set("")
    
    def update_time_estimation(self, current_progress, processed_items=None, total_items=None):
        """Zaman tahminini güncelle"""
        import time
        
        if not self.operation_start_time or current_progress <= 0:
            return
        
        current_time = time.time()
        elapsed_time = current_time - self.operation_start_time
        
        # Progress yüzdesi 0-100 arası
        if current_progress >= 100:
            self.time_estimation_var.set("✅ Tamamlandı!")
            return
        
        # Kalan süreyi hesapla
        if current_progress > 0:
            estimated_total_time = elapsed_time * (100 / current_progress)
            remaining_time = estimated_total_time - elapsed_time
            
            if remaining_time > 0:
                # Zamanı formatla
                time_str = self.format_time(remaining_time)
                
                # Ek bilgi varsa ekle
                if processed_items and total_items:
                    remaining_items = total_items - processed_items
                    self.time_estimation_var.set(f"⏱️ Kalan süre: {time_str} ({remaining_items} dosya)")
                else:
                    self.time_estimation_var.set(f"⏱️ Kalan süre: {time_str}")
            else:
                self.time_estimation_var.set("⏱️ Hesaplanıyor...")
    
    def format_time(self, seconds):
        """Süreyi okunabilir formata çevir"""
        if seconds < 60:
            return f"{int(seconds)} saniye"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}dk {secs}sn"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}sa {minutes}dk"
    
    def stop_time_estimation(self):
        """Zaman tahminini durdur"""
        self.operation_start_time = None
        self.last_progress_time = None
        self.estimated_total_time = None
        self.time_estimation_var.set("") 