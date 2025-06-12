"""
Modüler Dosya Organizatörü - Ana Program
Tüm modülleri bir araya getiren ana dosya
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import shutil
import traceback

# Multi-language support
from lang_manager import t, set_language, get_languages, lang_manager
from language_switcher import LanguageSwitcher

# Modülleri import et
try:
    from gui_manager import GUIManager
    from file_operations import FileOperations
    from scan_engine import ScanEngine
    from reporting import ReportingManager
except ImportError as e:
    print(f"Modül import hatası: {e}")
    print("Tüm modül dosyalarının aynı klasörde olduğundan emin olun!")
    sys.exit(1)

class ModularFileManager:
    """Ana uygulama sınıfı - tüm modülleri koordine eder"""
    
    def __init__(self):
        try:
            # Ana pencere oluştur
            self.root = tk.Tk()
            
            # Hata yakalama sistemi kur
            self.setup_error_handling()
            
            # Modülleri başlat
            self.initialize_modules()
            
            # Modüller arası bağlantıları kur
            self.setup_connections()
            
            # Bağlantıları test et
            self.test_connections()
            
            # Başlangıç ayarları
            self.setup_initial_state()
            
        except Exception as e:
            messagebox.showerror("Kritik Hata", f"Program başlatılamadı: {e}")
            sys.exit(1)
    
    def setup_error_handling(self):
        """Hata yakalama sistemi kur"""
        # Tkinter hata yakalama
        def handle_tk_error(exc, val, tb):
            error_msg = f"Tkinter Hatası: {val}"
            try:
                messagebox.showerror("Tkinter Hatası", error_msg)
            except:
                pass
        
        # Python genel hata yakalama
        def handle_python_error(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            error_msg = f"Python Hatası: {exc_value}"
            try:
                messagebox.showerror("Python Hatası", error_msg)
            except:
                pass
        
        # Error handler'ları ata
        self.root.report_callback_exception = handle_tk_error
        sys.excepthook = handle_python_error
    
    def initialize_modules(self):
        """Tüm modülleri başlat"""
        try:
            # 1. GUI Manager - Ana arayüz
            self.gui_manager = GUIManager(self.root)
            
            # 2. File Operations - Dosya işlemleri
            self.file_operations = FileOperations(self.gui_manager)
            
            # 3. Scan Engine - Tarama motoru
            self.scan_engine = ScanEngine(self.gui_manager, self.file_operations)
            
            # 4. Reporting Manager - Raporlama
            self.reporting = ReportingManager(self.gui_manager, self.file_operations, self.scan_engine)
            
        except Exception as e:
            error_msg = f"Modül başlatma hatası: {e}"
            messagebox.showerror("Modül Hatası", error_msg)
            sys.exit(1)
    
    def setup_connections(self):
        """Modüller arası bağlantıları kur"""
        # GUI Manager'daki placeholder metodları gerçek metodlarla değiştir
        
        # File Operations bağlantıları
        self.gui_manager.select_source_folder = self.file_operations.select_source_folder
        self.gui_manager.select_target_folder = self.file_operations.select_target_folder
        self.gui_manager.go_back = self.file_operations.go_back
        self.gui_manager.go_up = self.file_operations.go_up
        self.gui_manager.go_home = self.file_operations.go_home
        self.gui_manager.navigate_to_path = self.file_operations.navigate_to_path
        self.gui_manager.refresh_target = self.file_operations.refresh_target
        self.gui_manager.delete_selected = self.file_operations.delete_selected
        self.gui_manager.copy_selected = self.file_operations.copy_selected
        self.gui_manager.cut_selected = self.file_operations.cut_selected
        self.gui_manager.paste_selected = self.file_operations.paste_selected
        self.gui_manager.create_folder = self.file_operations.create_folder
        self.gui_manager.sort_tree = self.file_operations.sort_tree
        self.gui_manager.on_target_double_click = self.file_operations.on_target_double_click
        self.gui_manager.show_context_menu = self.file_operations.show_context_menu
        self.gui_manager.rename_selected = self.file_operations.rename_selected
        self.gui_manager.open_selected = self.file_operations.open_selected
        
        # Scan Engine bağlantıları
        self.gui_manager.scan_files = self.scan_engine.scan_files
        
        # Reporting bağlantıları
        self.gui_manager.analyze_target_disk = self.reporting.analyze_target_disk

        # Organizasyon işlemi - bu özel bir durum, birden fazla modül kullanır
        self.gui_manager.start_organization = self.start_organization
        
        # Butonları yeniden bağla
        self.rebind_buttons()
        
        # Event binding'leri yeniden yap
        self.rebind_events()
    
    def rebind_buttons(self):
        """Butonları yeniden bağla - GUI oluşturulduktan sonra"""
        # GUI Manager'daki widget referanslarını kullan
        if hasattr(self.gui_manager, 'ui_widgets'):
            widgets = self.gui_manager.ui_widgets
            
            # Ana butonları bağla
            if 'select_btn' in widgets:
                widgets['select_btn'].configure(command=self.file_operations.select_source_folder)
            if 'change_btn' in widgets:
                widgets['change_btn'].configure(command=self.file_operations.select_target_folder)
            if 'scan_btn' in widgets:
                widgets['scan_btn'].configure(command=self.scan_engine.scan_files)
            if 'analyze_btn' in widgets:
                widgets['analyze_btn'].configure(command=self.reporting.analyze_target_disk)
            if 'organize_btn' in widgets:
                widgets['organize_btn'].configure(command=self.start_organization)
                
            # File manager butonlarını bağla
            if 'back_btn' in widgets:
                widgets['back_btn'].configure(command=self.file_operations.go_back)
            if 'up_btn' in widgets:
                widgets['up_btn'].configure(command=self.file_operations.go_up)
            if 'home_btn' in widgets:
                widgets['home_btn'].configure(command=self.file_operations.go_home)
            if 'go_btn' in widgets:
                widgets['go_btn'].configure(command=self.file_operations.navigate_to_path)
            if 'refresh_btn' in widgets:
                widgets['refresh_btn'].configure(command=self.file_operations.refresh_target)
            if 'delete_btn' in widgets:
                widgets['delete_btn'].configure(command=self.file_operations.delete_selected)
            if 'copy_btn' in widgets:
                widgets['copy_btn'].configure(command=self.file_operations.copy_selected)
            if 'cut_btn' in widgets:
                widgets['cut_btn'].configure(command=self.file_operations.cut_selected)
            if 'paste_btn' in widgets:
                widgets['paste_btn'].configure(command=self.file_operations.paste_selected)
            if 'folder_btn' in widgets:
                widgets['folder_btn'].configure(command=self.file_operations.create_folder)
    
    def rebind_events(self):
        """Event binding'leri yeniden yap"""
        # Target tree event'leri - doğrudan gui_manager'dan erişim
        if hasattr(self.gui_manager, 'target_tree'):
            self.gui_manager.target_tree.bind("<Double-1>", self.file_operations.on_target_double_click)
            self.gui_manager.target_tree.bind("<Button-3>", self.file_operations.show_context_menu)
            
            # TreeView column sorting
            for col in ["#0", "size", "type", "modified"]:
                self.gui_manager.target_tree.heading(col, command=lambda c=col: self.file_operations.sort_tree(c))
            
            # Keyboard shortcuts for target tree
            self.gui_manager.target_tree.bind('<Delete>', lambda e: self.file_operations.delete_selected())
            self.gui_manager.target_tree.bind('<Control-c>', lambda e: self.file_operations.copy_selected())
            self.gui_manager.target_tree.bind('<Control-x>', lambda e: self.file_operations.cut_selected())
            self.gui_manager.target_tree.bind('<Control-v>', lambda e: self.file_operations.paste_selected())
            self.gui_manager.target_tree.bind('<F2>', lambda e: self.file_operations.rename_selected())
            self.gui_manager.target_tree.bind('<F5>', lambda e: self.file_operations.refresh_target())
            self.gui_manager.target_tree.bind('<BackSpace>', lambda e: self.file_operations.go_up())
            self.gui_manager.target_tree.bind('<Return>', lambda e: self.file_operations.open_selected())
        
        # Path entry event'i
        if hasattr(self.gui_manager, 'path_entry'):
            self.gui_manager.path_entry.bind("<Return>", lambda e: self.file_operations.navigate_to_path())
            
        print("✅ Event bindings yeniden bağlandı")
    
    def test_connections(self):
        """Modül bağlantılarını test et"""
        # Test gerekli metodların var olduğunu
        required_methods = [
            'select_source_folder', 'select_target_folder', 'scan_files', 
            'start_organization', 'analyze_target_disk'
        ]
        
        for method_name in required_methods:
            if not hasattr(self.gui_manager, method_name):
                raise Exception(f"Gerekli metod bulunamadı: {method_name}")
            
            method = getattr(self.gui_manager, method_name)
            if not callable(method):
                raise Exception(f"Metod çağırılabilir değil: {method_name}")
    
    def setup_initial_state(self):
        """Başlangıç durumunu ayarla"""
        # GUI elemanlarının başlangıç durumları
        if hasattr(self.gui_manager, 'ui_widgets'):
            widgets = self.gui_manager.ui_widgets
            
            # İlk durumda organize butonu deaktif
            if 'organize_btn' in widgets:
                widgets['organize_btn'].configure(state='disabled')
        
        # Klavye kısayollarını kur
        self.setup_keyboard_shortcuts()
    
    def setup_keyboard_shortcuts(self):
        """Klavye kısayollarını ayarla"""
        # Ctrl+O - Organize
        self.root.bind('<Control-o>', lambda e: self.start_organization())
        # Ctrl+S - Scan
        self.root.bind('<Control-s>', lambda e: self.scan_engine.scan_files())
        # Ctrl+Q - Quit
        self.root.bind('<Control-q>', lambda e: self.quit_application())
        # F5 - Refresh
        self.root.bind('<F5>', lambda e: self.file_operations.refresh_target())
        # Delete - Delete selected
        self.root.bind('<Delete>', lambda e: self.file_operations.delete_selected())
        # Ctrl+C - Copy
        self.root.bind('<Control-c>', lambda e: self.file_operations.copy_selected())
        # Ctrl+V - Paste  
        self.root.bind('<Control-v>', lambda e: self.file_operations.paste_selected())
        # Ctrl+X - Cut
        self.root.bind('<Control-x>', lambda e: self.file_operations.cut_selected())
    
    def start_organization(self):
        """Organizasyon işlemini başlat - Thread-safe"""
        import threading
        
        # Butonları deaktif et
        if hasattr(self.gui_manager, 'ui_widgets'):
            widgets = self.gui_manager.ui_widgets
            if 'organize_btn' in widgets:
                widgets['organize_btn'].configure(state='disabled')
            if 'scan_btn' in widgets:
                widgets['scan_btn'].configure(state='disabled')
        
        # Progress bar'ı sıfırla
        self.gui_manager.progress_var.set(0)
        
        # Thread'de organizasyon başlat
        try:
            organization_thread = threading.Thread(target=self._organization_thread, daemon=True)
            organization_thread.start()
        except Exception as e:
            messagebox.showerror("Hata", f"Organizasyon başlatılamadı: {e}")
            # Butonları yeniden aktif et
            if hasattr(self.gui_manager, 'ui_widgets'):
                widgets = self.gui_manager.ui_widgets
                if 'organize_btn' in widgets:
                    widgets['organize_btn'].configure(state='normal')
                if 'scan_btn' in widgets:
                    widgets['scan_btn'].configure(state='normal')
    
    def _organization_thread(self):
        """Organizasyon thread'i - Ana thread'den ayrı çalışır"""
        try:
            self._perform_organization()
        except Exception as e:
            # Hata durumunda UI'yi güncelle
            def error_update():
                messagebox.showerror("Organizasyon Hatası", f"Organizasyon sırasında hata oluştu: {e}")
                if hasattr(self.gui_manager, 'ui_widgets'):
                    widgets = self.gui_manager.ui_widgets
                    if 'organize_btn' in widgets:
                        widgets['organize_btn'].configure(state='normal')
                    if 'scan_btn' in widgets:
                        widgets['scan_btn'].configure(state='normal')
            
            self.root.after(0, error_update)
    
    def _count_total_items_for_organization(self):
        """Organize edilecek toplam öğe sayısını hesapla - Gerçek rakamlar"""
        total_count = 0
        
        # Mevcut klasörlerdeki dosyaları say
        if hasattr(self.scan_engine, 'existing_folder_files'):
            for files in self.scan_engine.existing_folder_files.values():
                total_count += len(files)
        
        # Yeni yapıdaki unique dosyaları ve klasörleri say
        if hasattr(self.scan_engine, 'unique_files'):
            for file_info in self.scan_engine.unique_files:
                if file_info.get('is_folder', False):
                    # Klasörler için içerideki öğeleri de say
                    try:
                        folder_path = file_info['path']
                        if os.path.exists(folder_path):
                            for root, dirs, files in os.walk(folder_path):
                                total_count += len(dirs) + len(files)
                    except:
                        total_count += 1  # Klasör erişilemezse sadece kendisini say
                else:
                    total_count += 1
        
        return total_count

    def _perform_organization(self):
        """Organizasyon işlemini gerçekleştir - Ana programdan optimize edildi"""
        import time
        
        try:
            target_base = self.gui_manager.target_var.get()
            
            # Time estimation başlat
            self.gui_manager.start_time_estimation()
            
            # Gerçek toplam öğe sayısını hesapla
            total_items = self._count_total_items_for_organization()
            
            copied_files = 0
            skipped_files = 0
            error_files = 0
            processed_items = 0
            
            # Duplikat işlem seçeneği
            duplicate_action = self.gui_manager.duplicate_action.get()
            
            # Önce mevcut klasörlerdeki dosyaları işle
            if hasattr(self.scan_engine, 'existing_folder_files'):
                for folder_path, files in self.scan_engine.existing_folder_files.items():
                    
                    # Yol kontrolünü iyileştir
                    if os.path.isabs(folder_path):
                        full_folder_path = folder_path
                    else:
                        full_folder_path = os.path.join(target_base, folder_path)
                    
                    # Klasör var mı kontrol et
                    if not os.path.exists(full_folder_path):
                        try:
                            os.makedirs(full_folder_path, exist_ok=True)
                        except Exception as e:
                            continue
                    
                    for file_info in files:
                        try:
                            # Hedef dosya yolu
                            target_file = os.path.join(full_folder_path, file_info['name'])
                            
                            # Aynı dosya mı kontrol et (self-copy engellemesi)
                            if os.path.normpath(file_info['path']) == os.path.normpath(target_file):
                                skipped_files += 1
                                processed_items += 1
                                
                                # Progress güncelle (skip durumunda da)
                                progress = (processed_items / total_items) * 100
                                def update_progress():
                                    self.gui_manager.progress_var.set(progress)
                                self.root.after(0, update_progress)
                                
                                # Time estimation güncelle
                                def update_time():
                                    self.gui_manager.update_time_estimation(progress, processed_items, total_items)
                                self.root.after(0, update_time)
                                continue
                            
                            # Gelişmiş duplikat kontrolü - hash bazlı kontrol
                            duplicate_found = False
                            if os.path.exists(target_file):
                                # Skip mode'da hızlı kontrol
                                if duplicate_action == "skip":
                                    # Sadece dosya boyutu kontrolü (çok hızlı)
                                    try:
                                        source_size = os.path.getsize(file_info['path'])
                                        target_size = os.path.getsize(target_file)
                                        duplicate_found = (source_size == target_size)
                                    except:
                                        duplicate_found = True  # Hata durumunda güvenli tarafta ol
                                else:
                                    # Diğer modlarda tam kontrol
                                    if self.file_operations._files_are_identical(file_info['path'], target_file):
                                        duplicate_found = True
                            
                            if duplicate_found:
                                if duplicate_action == "skip":
                                    skipped_files += 1
                                    processed_items += 1
                                    
                                    # Progress güncelle (skip durumunda da)
                                    progress = (processed_items / total_items) * 100
                                    def update_progress():
                                        self.gui_manager.progress_var.set(progress)
                                    self.root.after(0, update_progress)
                                    
                                    # Time estimation güncelle
                                    def update_time():
                                        self.gui_manager.update_time_estimation(progress, processed_items, total_items)
                                    self.root.after(0, update_time)
                                    continue
                                elif duplicate_action == "ask":
                                    # UI thread'inde sor
                                    result = self._ask_duplicate_action(file_info['name'])
                                    if result == "skip":
                                        skipped_files += 1
                                        processed_items += 1
                                        
                                        # Progress güncelle (skip durumunda da)
                                        progress = (processed_items / total_items) * 100
                                        def update_progress():
                                            self.gui_manager.progress_var.set(progress)
                                        self.root.after(0, update_progress)
                                        
                                        continue
                                    elif result == "skip_all":
                                        duplicate_action = "skip"
                                        skipped_files += 1
                                        processed_items += 1
                                        
                                        # Progress güncelle (skip durumunda da)
                                        progress = (processed_items / total_items) * 100
                                        def update_progress():
                                            self.gui_manager.progress_var.set(progress)
                                        self.root.after(0, update_progress)
                                        
                                        continue
                                    elif result == "copy_all":
                                        duplicate_action = "copy"
                                
                                # Aynı isimde dosya varsa numara ekle
                                if duplicate_action == "copy":
                                    counter = 1
                                    base_name, ext = os.path.splitext(file_info['name'])
                                    while os.path.exists(target_file):
                                        new_name = f"{base_name}_{counter}{ext}"
                                        target_file = os.path.join(full_folder_path, new_name)
                                        counter += 1
                            
                            # Dosyayı kopyala
                            success, message = self.file_operations.copy_file_optimized(file_info['path'], target_file)
                            
                            if success:
                                copied_files += 1
                                processed_items += 1
                            else:
                                error_files += 1
                                processed_items += 1
                            
                            # Progress güncelle
                            progress = (processed_items / total_items) * 100
                            def update_progress():
                                self.gui_manager.progress_var.set(progress)
                            self.root.after(0, update_progress)
                            
                            # Time estimation güncelle
                            def update_time():
                                self.gui_manager.update_time_estimation(progress, processed_items, total_items)
                            self.root.after(0, update_time)
                        
                        except Exception as e:
                            error_files += 1
                            processed_items += 1
                            
                            # Progress güncelle (hata durumunda da)
                            progress = (processed_items / total_items) * 100
                            def update_progress():
                                self.gui_manager.progress_var.set(progress)
                            self.root.after(0, update_progress)
            
            # Sonra yeni klasör yapısındaki dosyaları işle
            for i, file_info in enumerate(self.scan_engine.unique_files):
                try:
                    # Eğer bu dosya mevcut klasörlerde işlendiyse atla
                    if hasattr(self.scan_engine, 'existing_folder_files'):
                        skip_file = False
                        for folder_files in self.scan_engine.existing_folder_files.values():
                            if file_info in folder_files:
                                skip_file = True
                                break
                        if skip_file:
                            continue
                    
                    # Klasör mü kontrol et
                    if file_info.get('is_folder', False):
                        # Klasör kopyalama - "Yazılım Paketleri" kategorisine koy
                        source_folder = file_info['path']
                        target_folder = os.path.join(target_base, "Yazılım Paketleri", file_info['name'])
                        
                        # Parent klasörleri oluştur
                        parent_folder = os.path.dirname(target_folder)
                        os.makedirs(parent_folder, exist_ok=True)
                        
                        # Hedef klasör varsa duplikat kontrolü
                        if os.path.exists(target_folder):
                            if duplicate_action == "skip":
                                skipped_files += 1
                                # Klasör skip edilirken içindeki öğe sayısını hesapla
                                folder_item_count = 0
                                try:
                                    for root, dirs, files in os.walk(source_folder):
                                        folder_item_count += len(dirs) + len(files)
                                except:
                                    folder_item_count = 1
                                
                                processed_items += folder_item_count
                                
                                # Progress güncelle
                                progress = (processed_items / total_items) * 100
                                def update_progress():
                                    self.gui_manager.progress_var.set(progress)
                                self.root.after(0, update_progress)
                                
                                continue
                            else:
                                # Klasörü birleştir (merge)
                                try:
                                    merge_result = self._merge_folders(source_folder, target_folder)
                                    
                                    if merge_result:
                                        copied_files += 1
                                        # İçerik sayısını hesapla
                                        folder_item_count = 0
                                        try:
                                            for root, dirs, files in os.walk(source_folder):
                                                folder_item_count += len(dirs) + len(files)
                                        except:
                                            folder_item_count = 1
                                        
                                        processed_items += folder_item_count
                                    else:
                                        error_files += 1
                                        processed_items += 1
                                        
                                except Exception as merge_error:
                                    error_files += 1
                                    processed_items += 1
                        else:
                            # Yeni klasör kopyalama
                            try:
                                shutil.copytree(source_folder, target_folder)
                                copied_files += 1
                                
                                # İçerik sayısını hesapla
                                folder_item_count = 0
                                try:
                                    for root, dirs, files in os.walk(source_folder):
                                        folder_item_count += len(dirs) + len(files)
                                except:
                                    folder_item_count = 1
                                
                                processed_items += folder_item_count
                                
                            except Exception as e:
                                error_files += 1
                                processed_items += 1
                        
                        # Progress güncelle
                        progress = (processed_items / total_items) * 100
                        def update_progress():
                            self.gui_manager.progress_var.set(progress)
                        self.root.after(0, update_progress)
                        
                        # Time estimation güncelle
                        def update_time():
                            self.gui_manager.update_time_estimation(progress, processed_items, total_items)
                        self.root.after(0, update_time)
                        
                    else:
                        # Normal dosya işleme - Scan Engine'in organization_structure'ını kullan
                        # file_info'dan kategori çıkarmak yerine organizasyon yapısından al
                        file_found = False
                        for main_folder, subfolders in self.scan_engine.organization_structure.items():
                            for subfolder, files in subfolders.items():
                                if file_info in files:
                                    # Dosya bulundu, doğru kategori klasörünü oluştur
                                    if subfolder:
                                        target_folder = os.path.join(target_base, main_folder, subfolder)
                                    else:
                                        target_folder = os.path.join(target_base, main_folder)
                                    
                                    # Kategori klasörünü oluştur
                                    os.makedirs(target_folder, exist_ok=True)
                                    
                                    # Hedef dosya yolu
                                    target_file = os.path.join(target_folder, file_info['name'])
                                    file_found = True
                                    break
                            if file_found:
                                break
                        
                        if not file_found:
                            # Fallback: file_info'dan kategori al veya Other Files'a koy
                            category = file_info.get('category', 'Other Files')
                            target_folder = os.path.join(target_base, category)
                            os.makedirs(target_folder, exist_ok=True)
                            target_file = os.path.join(target_folder, file_info['name'])
                        
                        # Duplikat kontrolü - hash bazlı kontrol
                        duplicate_found = False
                        if os.path.exists(target_file):
                            # Skip mode'da hızlı kontrol
                            if duplicate_action == "skip":
                                # Sadece dosya boyutu kontrolü (çok hızlı)
                                try:
                                    source_size = os.path.getsize(file_info['path'])
                                    target_size = os.path.getsize(target_file)
                                    duplicate_found = (source_size == target_size)
                                except:
                                    duplicate_found = True  # Hata durumunda güvenli tarafta ol
                            else:
                                # Diğer modlarda tam kontrol
                                if self.file_operations._files_are_identical(file_info['path'], target_file):
                                    duplicate_found = True
                        
                        if duplicate_found:
                            if duplicate_action == "skip":
                                skipped_files += 1
                            elif duplicate_action == "ask":
                                result = self._ask_duplicate_action(file_info['name'])
                                if result == "skip":
                                    skipped_files += 1
                                elif result == "skip_all":
                                    duplicate_action = "skip"
                                    skipped_files += 1
                                elif result == "copy_all":
                                    duplicate_action = "copy"
                            
                            # Aynı isimde dosya varsa numara ekle
                            if duplicate_action == "copy":
                                counter = 1
                                base_name, ext = os.path.splitext(file_info['name'])
                                while os.path.exists(target_file):
                                    new_name = f"{base_name}_{counter}{ext}"
                                    target_file = os.path.join(target_folder, new_name)
                                    counter += 1
                        
                        # Dosyayı kopyala (duplicate skip durumu hariç)
                        if not (duplicate_found and duplicate_action == "skip"):
                            success, message = self.file_operations.copy_file_optimized(file_info['path'], target_file)
                            
                            if success:
                                copied_files += 1
                            else:
                                error_files += 1
                        
                        processed_items += 1
                        
                        # Progress güncelle
                        progress = (processed_items / total_items) * 100
                        def update_progress():
                            self.gui_manager.progress_var.set(progress)
                        self.root.after(0, update_progress)
                        
                        # Time estimation güncelle
                        def update_time():
                            self.gui_manager.update_time_estimation(progress, processed_items, total_items)
                        self.root.after(0, update_time)
                
                except Exception as e:
                    error_files += 1
                    processed_items += 1
                    
                    # Progress güncelle (hata durumunda da)
                    progress = (processed_items / total_items) * 100
                    def update_progress():
                        self.gui_manager.progress_var.set(progress)
                    self.root.after(0, update_progress)
            
            # İşlem tamamlandığında UI'yi güncelle
            def final_update():
                self.gui_manager.progress_var.set(100)
                
                # Time estimation durdur
                self.gui_manager.stop_time_estimation()
                
                # Rapor mesajını çeviri sistemi ile oluştur
                message = f"{lang_manager.get_text('messages.organization_complete')}\n"
                message += f"{lang_manager.get_text('messages.copied')}: {copied_files}\n"
                message += f"{lang_manager.get_text('messages.skipped')}: {skipped_files}\n"
                message += f"{lang_manager.get_text('messages.errors')}: {error_files}"
                
                messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), message)
                
                # Butonları yeniden aktif et
                if hasattr(self.gui_manager, 'ui_widgets'):
                    widgets = self.gui_manager.ui_widgets
                    if 'organize_btn' in widgets:
                        widgets['organize_btn'].configure(state='normal')
                    if 'scan_btn' in widgets:
                        widgets['scan_btn'].configure(state='normal')
            
            self.root.after(0, final_update)
                    
        except Exception as e:
            # Kritik hata durumunda
            def error_update():
                # Time estimation durdur
                self.gui_manager.stop_time_estimation()
                
                messagebox.showerror(lang_manager.get_text('dialogs.error.title'), 
                                   lang_manager.get_text('messages.error', error=str(e)))
                if hasattr(self.gui_manager, 'ui_widgets'):
                    widgets = self.gui_manager.ui_widgets
                    if 'organize_btn' in widgets:
                        widgets['organize_btn'].configure(state='normal')
                    if 'scan_btn' in widgets:
                        widgets['scan_btn'].configure(state='normal')
            
            self.root.after(0, error_update)

    def _ask_duplicate_action(self, filename):
        """Duplikat dosya için kullanıcıya sor"""
        result = [None]  # Referans liste
        
        # Dialog oluştur
        dialog = tk.Toplevel(self.root)
        dialog.title(lang_manager.get_text('dialogs.duplicate_found.title'))
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Merkeze hizala
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Mesaj
        msg_text = f"'{filename}' {lang_manager.get_text('dialogs.duplicate_found.message')}\n{lang_manager.get_text('dialogs.duplicate_found.question')}"
        msg_label = tk.Label(dialog, text=msg_text, 
                            justify=tk.CENTER, wraplength=350)
        msg_label.pack(pady=20)
        
        # Butonlar frame
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        # Buton fonksiyonları
        def on_skip():
            result[0] = "skip"
            dialog.destroy()
        
        def on_copy():
            result[0] = "copy"
            dialog.destroy()
        
        def on_skip_all():
            result[0] = "skip_all"
            dialog.destroy()
            
        def on_copy_all():
            result[0] = "copy_all" 
            dialog.destroy()
        
        # Butonlar
        tk.Button(btn_frame, text=lang_manager.get_text('dialogs.duplicate_found.skip_this'), command=on_skip, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=lang_manager.get_text('dialogs.duplicate_found.copy_this'), command=on_copy, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=lang_manager.get_text('dialogs.duplicate_found.skip_all'), command=on_skip_all, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=lang_manager.get_text('dialogs.duplicate_found.copy_all'), command=on_copy_all, width=12).pack(side=tk.LEFT, padx=5)
        
        # Dialog'u bekle
        self.root.wait_window(dialog)
        
        return result[0] or "skip"
    
    def _merge_folders(self, source_folder, target_folder):
        """İki klasörü birleştir"""
        try:
            if not os.path.exists(source_folder):
                return False
            
            # Hedef klasör yoksa oluştur
            if not os.path.exists(target_folder):
                os.makedirs(target_folder, exist_ok=True)
            
            # Kaynak klasördeki tüm öğeleri hedef klasöre kopyala
            for item in os.listdir(source_folder):
                source_item = os.path.join(source_folder, item)
                target_item = os.path.join(target_folder, item)
                
                if os.path.isdir(source_item):
                    # Alt klasör ise recursive merge
                    if os.path.exists(target_item):
                        self._merge_folders(source_item, target_item)
                    else:
                        shutil.copytree(source_item, target_item)
                else:
                    # Dosya ise kopyala (varsa üzerine yaz)
                    try:
                        shutil.copy2(source_item, target_item)
                    except Exception as e:
                        continue
            
            return True
            
        except Exception as e:
            return False
    
    def quit_application(self):
        """Uygulamayı güvenli şekilde kapat"""
        try:
            # Kullanıcıya onay sor
            if messagebox.askyesno(lang_manager.get_text('dialogs.exit.title'), lang_manager.get_text('dialogs.exit.message')):
                # Öğrenilmiş kategorileri kaydet
                if hasattr(self, 'file_operations'):
                    try:
                        self.file_operations.save_learned_categories()
                    except Exception as e:
                        pass
                
                # Pencereyi kapat
                self.root.quit()
                self.root.destroy()
                
        except Exception as e:
            # Kritik hata durumunda zorla çık
            try:
                self.root.quit()
                self.root.destroy()
            except:
                sys.exit(1)
    
    def run(self):
        """Ana döngüyü başlat"""
        try:
            # Pencere kapanma olayını yakala
            self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
            
            # Ana döngü
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("Kritik Hata", f"Program çalıştırılamadı: {e}")


if __name__ == "__main__":
    try:
        # Ana uygulama örneği oluştur
        app = ModularFileManager()
        
        # Uygulamayı çalıştır
        app.run()
        
    except Exception as e:
        print(f"Kritik hata: {e}")
        if 'messagebox' in globals():
            try:
                messagebox.showerror("Kritik Hata", f"Program başlatılamadı: {e}")
            except:
                pass
        sys.exit(1) 