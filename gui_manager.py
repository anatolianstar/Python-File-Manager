"""
GUI Manager Module
Ana GUI yapısını ve pencere yönetimini içerir
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from pathlib import Path

# Multi-language support
from lang_manager import t, set_language, get_languages, lang_manager
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
        self.status_var = tk.StringVar(value=t('status.ready'))
        
        # Time estimation variables
        self.time_estimation_var = tk.StringVar(value="")
        self.operation_start_time = None
        self.last_progress_time = None
        self.estimated_total_time = None
        
        # Multi-language StringVars for dynamic text updates
        self.ui_texts = {
            'source_label': tk.StringVar(value=t('menu.file.select_source')),
            'target_label': tk.StringVar(value=t('menu.file.select_target')),
            'location_label': tk.StringVar(value=t('labels.location') + ":"),
            'scan_mode_label': tk.StringVar(value=t('labels.scan_mode')),
        }
        
        # Tab başlıkları için değişkenler
        self.tab_references = {}
        
        # Widget references for dynamic updates
        self.ui_widgets = {}
        
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
        self.ui_widgets['source_label'] = ttk.Label(top_frame, textvariable=self.ui_texts['source_label'])
        self.ui_widgets['source_label'].grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(top_frame, textvariable=self.source_var, width=50).grid(row=0, column=1, padx=(0, 5))
        self.ui_widgets['select_btn'] = ttk.Button(top_frame, text=t('buttons.select'), command=self.select_source_folder)
        self.ui_widgets['select_btn'].grid(row=0, column=2)
        
        # Target SSD seçimi
        self.ui_widgets['target_label'] = ttk.Label(top_frame, textvariable=self.ui_texts['target_label'])
        self.ui_widgets['target_label'].grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Entry(top_frame, textvariable=self.target_var, width=50).grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        self.ui_widgets['change_btn'] = ttk.Button(top_frame, text=t('buttons.change'), command=self.select_target_folder)
        self.ui_widgets['change_btn'].grid(row=1, column=2, pady=(5, 0))
        
        # Alt klasör tarama seçeneği
        self.setup_scan_options(top_frame)
        
    def setup_scan_options(self, parent):
        """Tarama seçenekleri"""
        scan_frame = ttk.Frame(parent)
        scan_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        self.ui_widgets['scan_mode_label'] = ttk.Label(scan_frame, textvariable=self.ui_texts['scan_mode_label'])
        self.ui_widgets['scan_mode_label'].pack(side=tk.LEFT, padx=(0, 10))
        
        # Seçenek 1: Tüm alt klasörleri tara
        self.ui_widgets['scan_all_radio'] = ttk.Radiobutton(scan_frame, text=t('scan_options.scan_all'), 
                       variable=self.scan_mode, value="all")
        self.ui_widgets['scan_all_radio'].pack(side=tk.LEFT, padx=(0, 15))
        
        # Seçenek 2: Klasörleri komple kopyala
        self.ui_widgets['scan_none_radio'] = ttk.Radiobutton(scan_frame, text=t('scan_options.copy_folders'), 
                       variable=self.scan_mode, value="none")
        self.ui_widgets['scan_none_radio'].pack(side=tk.LEFT, padx=(0, 15))
        
        # Seçenek 3: Sadece dosyaları tara (YENİ)
        self.ui_widgets['scan_files_radio'] = ttk.Radiobutton(scan_frame, text=t('scan_options.files_only'), 
                       variable=self.scan_mode, value="files_only")
        self.ui_widgets['scan_files_radio'].pack(side=tk.LEFT)
        
        # Hatırlatma mesajı
        reminder_frame = ttk.Frame(parent)
        reminder_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        self.ui_widgets['reminder_label'] = ttk.Label(reminder_frame, text=t('scan_options.reminder'), 
                                 foreground="blue", font=('Arial', 8, 'italic'))
        self.ui_widgets['reminder_label'].pack(side=tk.LEFT, padx=(20, 0))
        
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
        self.ui_widgets['target_panel'] = ttk.LabelFrame(parent, text=t('panels.target_manager'))
        self.ui_widgets['target_panel'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        left_frame = self.ui_widgets['target_panel']
        
        # Navigasyon kontrolleri
        nav_frame = ttk.Frame(left_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        self.ui_widgets['back_btn'] = ttk.Button(nav_frame, text="◀ " + t('buttons.back'), command=self.go_back)
        self.ui_widgets['back_btn'].pack(side=tk.LEFT, padx=(0, 5))
        self.ui_widgets['up_btn'] = ttk.Button(nav_frame, text="▲ " + t('buttons.up'), command=self.go_up)
        self.ui_widgets['up_btn'].pack(side=tk.LEFT, padx=(0, 5))
        self.ui_widgets['home_btn'] = ttk.Button(nav_frame, text="🏠 " + t('buttons.home'), command=self.go_home)
        self.ui_widgets['home_btn'].pack(side=tk.LEFT, padx=(0, 5))
        
        # Yol gösterge çubuğu
        path_frame = ttk.Frame(left_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        self.ui_widgets['location_label'] = ttk.Label(path_frame, textvariable=self.ui_texts['location_label'])
        self.ui_widgets['location_label'].pack(side=tk.LEFT)
        self.path_entry = ttk.Entry(path_frame, textvariable=self.current_path_var, font=('Consolas', 9))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.path_entry.bind('<Return>', self.navigate_to_path)
        self.ui_widgets['go_btn'] = ttk.Button(path_frame, text=t('buttons.go'), command=self.navigate_to_path)
        self.ui_widgets['go_btn'].pack(side=tk.RIGHT)

        # File manager kontrolleri
        target_controls = ttk.Frame(left_frame)
        target_controls.pack(fill=tk.X, padx=5, pady=5)
        
        self.ui_widgets['refresh_btn'] = ttk.Button(target_controls, text="🔄 " + t('buttons.refresh'), command=self.refresh_target)
        self.ui_widgets['refresh_btn'].pack(side=tk.LEFT, padx=(0, 5))
        self.ui_widgets['delete_btn'] = ttk.Button(target_controls, text="🗑️ " + t('buttons.delete'), command=self.delete_selected)
        self.ui_widgets['delete_btn'].pack(side=tk.LEFT, padx=(0, 5))
        self.ui_widgets['copy_btn'] = ttk.Button(target_controls, text="📋 " + t('buttons.copy'), command=self.copy_selected)
        self.ui_widgets['copy_btn'].pack(side=tk.LEFT, padx=(0, 5))
        self.ui_widgets['cut_btn'] = ttk.Button(target_controls, text="✂️ " + t('buttons.cut'), command=self.cut_selected)
        self.ui_widgets['cut_btn'].pack(side=tk.LEFT, padx=(0, 5))
        self.ui_widgets['paste_btn'] = ttk.Button(target_controls, text="📁 " + t('buttons.paste'), command=self.paste_selected)
        self.ui_widgets['paste_btn'].pack(side=tk.LEFT, padx=(0, 5))
        self.ui_widgets['new_folder_btn'] = ttk.Button(target_controls, text="➕ " + t('buttons.new_folder'), command=self.create_folder)
        self.ui_widgets['new_folder_btn'].pack(side=tk.LEFT, padx=(0, 5))
        
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
        # StringVar'ları güncelle
        self.ui_texts['source_label'].set(t('menu.file.select_source'))
        self.ui_texts['target_label'].set(t('menu.file.select_target'))
        self.ui_texts['location_label'].set(t('labels.location') + ":")
        self.ui_texts['scan_mode_label'].set(t('labels.scan_mode'))
        
        # LabelFrame'i güncelle (config ile)
        if 'target_panel' in self.ui_widgets:
            self.ui_widgets['target_panel'].config(text=t('panels.target_manager'))
        
        # Button metinlerini güncelle
        if 'select_btn' in self.ui_widgets:
            self.ui_widgets['select_btn'].config(text=t('buttons.select'))
        if 'change_btn' in self.ui_widgets:
            self.ui_widgets['change_btn'].config(text=t('buttons.change'))
        if 'back_btn' in self.ui_widgets:
            self.ui_widgets['back_btn'].config(text="◀ " + t('buttons.back'))
        if 'up_btn' in self.ui_widgets:
            self.ui_widgets['up_btn'].config(text="▲ " + t('buttons.up'))
        if 'home_btn' in self.ui_widgets:
            self.ui_widgets['home_btn'].config(text="🏠 " + t('buttons.home'))
        if 'go_btn' in self.ui_widgets:
            self.ui_widgets['go_btn'].config(text=t('buttons.go'))
        if 'refresh_btn' in self.ui_widgets:
            self.ui_widgets['refresh_btn'].config(text="🔄 " + t('buttons.refresh'))
        if 'delete_btn' in self.ui_widgets:
            self.ui_widgets['delete_btn'].config(text="🗑️ " + t('buttons.delete'))
        if 'copy_btn' in self.ui_widgets:
            self.ui_widgets['copy_btn'].config(text="📋 " + t('buttons.copy'))
        if 'cut_btn' in self.ui_widgets:
            self.ui_widgets['cut_btn'].config(text="✂️ " + t('buttons.cut'))
        if 'paste_btn' in self.ui_widgets:
            self.ui_widgets['paste_btn'].config(text="📁 " + t('buttons.paste'))
        if 'new_folder_btn' in self.ui_widgets:
            self.ui_widgets['new_folder_btn'].config(text="➕ " + t('buttons.new_folder'))
        
        # Tree headings güncelle
        if hasattr(self, 'target_tree'):
            self.target_tree.heading('#0', text='📁 ' + t('labels.file_folder_name'))
            self.target_tree.heading('size', text='📏 ' + t('labels.size'))
            self.target_tree.heading('type', text='🏷️ ' + t('labels.type'))
            self.target_tree.heading('modified', text='📅 ' + t('labels.modified'))
        
        # Status güncelle
        if (self.status_var.get() == t('status.ready') or 
            self.status_var.get() == "Hazır" or self.status_var.get() == "Ready"):
            self.status_var.set(t('status.ready'))
        
        # Scan options güncelle
        if 'scan_all_radio' in self.ui_widgets:
            self.ui_widgets['scan_all_radio'].config(text=t('scan_options.scan_all'))
        if 'scan_none_radio' in self.ui_widgets:
            self.ui_widgets['scan_none_radio'].config(text=t('scan_options.copy_folders'))
        if 'scan_files_radio' in self.ui_widgets:
            self.ui_widgets['scan_files_radio'].config(text=t('scan_options.files_only'))
        if 'reminder_label' in self.ui_widgets:
            self.ui_widgets['reminder_label'].config(text=t('scan_options.reminder'))
        
        # Bottom panel butonları güncelle
        if 'scan_btn' in self.ui_widgets:
            self.ui_widgets['scan_btn'].config(text=t('buttons.scan'))
        if 'analyze_btn' in self.ui_widgets:
            self.ui_widgets['analyze_btn'].config(text=t('buttons.analyze'))
        if 'organize_btn' in self.ui_widgets:
            self.ui_widgets['organize_btn'].config(text=t('buttons.organize'))
        
        # Duplicate tab güncellemeleri
        if hasattr(self, 'duplicate_tree'):
            self.duplicate_tree.heading('#0', text=t('duplicates.groups'))
            self.duplicate_tree.heading('path', text=t('labels.file_path'))
            self.duplicate_tree.heading('size', text=t('duplicates.size'))
            self.duplicate_tree.heading('hash', text=t('duplicates.hash'))
        
        # Duplicate control güncellemeleri
        if 'dup_control_label' in self.ui_widgets:
            self.ui_widgets['dup_control_label'].config(text=t('duplicates.control_label'))
        if 'dup_name_check' in self.ui_widgets:
            self.ui_widgets['dup_name_check'].config(text=t('duplicates.name'))
        if 'dup_size_check' in self.ui_widgets:
            self.ui_widgets['dup_size_check'].config(text=t('duplicates.size'))
        if 'dup_hash_check' in self.ui_widgets:
            self.ui_widgets['dup_hash_check'].config(text=t('duplicates.hash'))
        if 'dup_action_label' in self.ui_widgets:
            self.ui_widgets['dup_action_label'].config(text=t('duplicates.action_label'))
        if 'dup_ask_radio' in self.ui_widgets:
            self.ui_widgets['dup_ask_radio'].config(text=t('duplicates.ask'))
        if 'dup_skip_radio' in self.ui_widgets:
            self.ui_widgets['dup_skip_radio'].config(text=t('duplicates.skip'))
        if 'dup_copy_radio' in self.ui_widgets:
            self.ui_widgets['dup_copy_radio'].config(text=t('duplicates.copy'))
        
        # Preview tab güncellemeleri
        if hasattr(self, 'preview_tree'):
            self.preview_tree.heading('#0', text=t('labels.folder_structure'))
            self.preview_tree.heading('count', text=t('labels.file_count'))
        
        # Source tab güncellemeleri
        if hasattr(self, 'source_tree'):
            self.source_tree.heading('#0', text=t('source_tab.file_name'))
            self.source_tree.heading('size', text=t('source_tab.size'))
            self.source_tree.heading('type', text=t('source_tab.type'))
        
        # Panel başlıkları güncelle
        if 'target_panel' in self.ui_widgets:
            self.ui_widgets['target_panel'].config(text=t('panels.target_manager'))
        if 'source_panel' in self.ui_widgets:
            self.ui_widgets['source_panel'].config(text=t('panels.source_organization'))
        
        # Tab başlıklarını güncelle
        if hasattr(self, 'notebook'):
            try:
                # Tüm tab başlıklarını güncelle
                for i in range(self.notebook.index("end")):
                    tab_text = self.notebook.tab(i, "text")
                    if "Kaynak" in tab_text or "Source" in tab_text:
                        self.notebook.tab(i, text=t('source_tab.title'))
                    elif "Önizleme" in tab_text or "Preview" in tab_text:
                        self.notebook.tab(i, text=t('tabs.preview'))
                    elif "Duplikat" in tab_text or "Duplicate" in tab_text:
                        self.notebook.tab(i, text=t('tabs.duplicates'))
            except Exception as e:
                print(f"Tab başlığı güncelleme hatası: {e}")
        
    def setup_target_tree_events(self):
        """Target tree event bindings - Bu event'ler main_modular.py'de bağlanacak"""
        # Event bindings main_modular.py rebind_events() fonksiyonunda yapılıyor
        # Bu fonksiyon artık gerekli değil
        pass
    
    def setup_source_panel(self, parent):
        """Sağ panel - Kaynak dosyalar ve organizasyon"""
        self.ui_widgets['source_panel'] = ttk.LabelFrame(parent, text=t('panels.source_organization'))
        self.ui_widgets['source_panel'].pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        right_frame = self.ui_widgets['source_panel']
        
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
        self.notebook.add(source_tab, text=t('source_tab.title'))
        
        self.source_tree = ttk.Treeview(source_tab, columns=('size', 'type'), show='tree headings')
        self.source_tree.heading('#0', text=t('source_tab.file_name'))
        self.source_tree.heading('size', text=t('source_tab.size'))
        self.source_tree.heading('type', text=t('source_tab.type'))
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
        self.notebook.add(preview_tab, text=t('tabs.preview'))
        
        self.preview_tree = ttk.Treeview(preview_tab, columns=('count',), show='tree headings')
        self.preview_tree.heading('#0', text=t('labels.folder_structure'))
        self.preview_tree.heading('count', text=t('labels.file_count'))
        self.preview_tree.column('#0', width=250)
        self.preview_tree.column('count', width=100)
        
        preview_scrollbar = ttk.Scrollbar(preview_tab, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_duplicate_tab(self):
        """Duplikat dosyalar tab"""
        duplicate_tab = ttk.Frame(self.notebook)
        self.notebook.add(duplicate_tab, text=t('tabs.duplicates'))
        
        # Duplikat kontrol seçenekleri
        self.setup_duplicate_controls(duplicate_tab)
        
        # Duplikat tree
        self.setup_duplicate_tree(duplicate_tab)
        
    def setup_duplicate_controls(self, parent):
        """Duplikat kontrol seçenekleri"""
        # Duplikat kontrol seçenekleri
        dup_controls = ttk.Frame(parent)
        dup_controls.pack(fill=tk.X, padx=5, pady=5)
        
        self.ui_widgets['dup_control_label'] = ttk.Label(dup_controls, text=t('duplicates.control_label'))
        self.ui_widgets['dup_control_label'].pack(side=tk.LEFT)
        self.ui_widgets['dup_name_check'] = ttk.Checkbutton(dup_controls, text=t('duplicates.name'), variable=self.duplicate_check_name)
        self.ui_widgets['dup_name_check'].pack(side=tk.LEFT, padx=(10, 5))
        self.ui_widgets['dup_size_check'] = ttk.Checkbutton(dup_controls, text=t('duplicates.size'), variable=self.duplicate_check_size)
        self.ui_widgets['dup_size_check'].pack(side=tk.LEFT, padx=5)
        self.ui_widgets['dup_hash_check'] = ttk.Checkbutton(dup_controls, text=t('duplicates.hash'), variable=self.duplicate_check_hash)
        self.ui_widgets['dup_hash_check'].pack(side=tk.LEFT, padx=5)
        
        # Duplikat işlem seçenekleri
        dup_action_frame = ttk.Frame(parent)
        dup_action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.ui_widgets['dup_action_label'] = ttk.Label(dup_action_frame, text=t('duplicates.action_label'))
        self.ui_widgets['dup_action_label'].pack(side=tk.LEFT)
        self.ui_widgets['dup_ask_radio'] = ttk.Radiobutton(dup_action_frame, text=t('duplicates.ask'), 
                       variable=self.duplicate_action, value="ask")
        self.ui_widgets['dup_ask_radio'].pack(side=tk.LEFT, padx=(10, 5))
        self.ui_widgets['dup_skip_radio'] = ttk.Radiobutton(dup_action_frame, text=t('duplicates.skip'), 
                       variable=self.duplicate_action, value="skip")
        self.ui_widgets['dup_skip_radio'].pack(side=tk.LEFT, padx=5)
        self.ui_widgets['dup_copy_radio'] = ttk.Radiobutton(dup_action_frame, text=t('duplicates.copy'), 
                       variable=self.duplicate_action, value="copy")
        self.ui_widgets['dup_copy_radio'].pack(side=tk.LEFT, padx=5)
        
    def setup_duplicate_tree(self, parent):
        """Duplikat dosyalar tree"""
        self.duplicate_tree = ttk.Treeview(parent, columns=('path', 'size', 'hash'), show='tree headings')
        self.duplicate_tree.heading('#0', text=t('duplicates.groups'))
        self.duplicate_tree.heading('path', text=t('labels.file_path'))
        self.duplicate_tree.heading('size', text=t('duplicates.size'))
        self.duplicate_tree.heading('hash', text=t('duplicates.hash'))
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
        
        self.ui_widgets['scan_btn'] = ttk.Button(button_frame, text=t('buttons.scan'), command=self.scan_files)
        self.ui_widgets['scan_btn'].pack(side=tk.LEFT, padx=(0, 5))
        self.ui_widgets['analyze_btn'] = ttk.Button(button_frame, text=t('buttons.analyze'), command=self.analyze_target_disk)
        self.ui_widgets['analyze_btn'].pack(side=tk.LEFT, padx=(0, 5))
        self.ui_widgets['organize_btn'] = ttk.Button(button_frame, text=t('buttons.organize'), command=self.start_organization)
        self.ui_widgets['organize_btn'].pack(side=tk.LEFT, padx=(0, 5))
        
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
        from lang_manager import t
        
        if not self.operation_start_time or current_progress <= 0:
            return
        
        current_time = time.time()
        elapsed_time = current_time - self.operation_start_time
        
        # Progress yüzdesi 0-100 arası
        if current_progress >= 100:
            self.time_estimation_var.set(f"✅ {t('time.completed')}")
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
                    self.time_estimation_var.set(f"⏱️ {t('time.remaining')}: {time_str} ({remaining_items} {t('time.files')})")
                else:
                    self.time_estimation_var.set(f"⏱️ {t('time.remaining')}: {time_str}")
            else:
                self.time_estimation_var.set(f"⏱️ {t('time.calculating')}")
    
    def format_time(self, seconds):
        """Süreyi okunabilir formata çevir"""
        from lang_manager import t
        
        if seconds < 60:
            return f"{int(seconds)} {t('time.seconds')}"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}{t('time.minutes_short')} {secs}{t('time.seconds_short')}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}{t('time.hours_short')} {minutes}{t('time.minutes_short')}"
    
    def stop_time_estimation(self):
        """Zaman tahminini durdur"""
        self.operation_start_time = None
        self.last_progress_time = None
        self.estimated_total_time = None
        self.time_estimation_var.set("") 