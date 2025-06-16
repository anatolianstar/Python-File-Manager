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
import time
import hashlib

# Multi-language support
from lang_manager import t, set_language, get_languages, lang_manager
from language_switcher import LanguageSwitcher

# Modülleri import et
try:
    from gui_manager import GUIManager
    from file_operations import FileOperations
    from scan_engine import ScanEngine
    from reporting import ReportingManager
    from duplicate_image_finder import DuplicateImageFinder
    from duplicate_file_finder import DuplicateFileFinder
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
            
            # İşlem durdurma kontrolü için değişkenler
            self.operation_cancelled = False
            self.current_operation_thread = None
            self.operation_type = None  # "scan" veya "organize"
            
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
            
            # Scan engine'e main referansı ver (buton kontrolü için)
            self.scan_engine.main_app = self
            
            # 4. Reporting Manager - Raporlama
            self.reporting = ReportingManager(self.gui_manager, self.file_operations, self.scan_engine)
            
            # 5. Duplicate Image Finder - Tek klasör duplikat bulucu
            self.duplicate_finder = DuplicateImageFinder(self.root)
            
            # 6. Duplicate File Finder - Tek klasör dosya duplikat bulucu
            self.duplicate_file_finder = DuplicateFileFinder(self.root)
            
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
        self.gui_manager.scan_files = self.start_scan
        
        # Reporting bağlantıları
        self.gui_manager.analyze_target_disk = self.reporting.analyze_target_disk

        # Duplicate Image Finder bağlantısı
        self.gui_manager.open_duplicate_finder = self.duplicate_finder.open_window
        
        # Duplicate File Finder bağlantısı
        self.gui_manager.open_duplicate_file_finder = self.duplicate_file_finder.open_window

        # Organizasyon işlemi - bu özel bir durum, birden fazla modül kullanır
        self.gui_manager.start_organization = self.start_organization
        
        # İşlem durdurma
        self.gui_manager.stop_operation = self.stop_operation
        
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
            if 'stop_btn' in widgets:
                widgets['stop_btn'].configure(command=self.stop_operation)
                
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
            
            # Duplicate Image Finder butonu
            if 'duplicate_finder_btn' in widgets:
                widgets['duplicate_finder_btn'].configure(command=self.duplicate_finder.open_window)
            
            # Duplicate File Finder butonu
            if 'duplicate_file_finder_btn' in widgets:
                widgets['duplicate_file_finder_btn'].configure(command=self.duplicate_file_finder.open_window)
    
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
            
            # İlk durumda stop butonu deaktif
            if 'stop_btn' in widgets:
                widgets['stop_btn'].configure(state='disabled')
        
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
    
    def stop_operation(self):
        """Çalışan işlemi durdur"""
        try:
            # İşlem iptal bayrağını set et
            self.operation_cancelled = True
            
            # Hangi işlem çalışıyorsa onu durdur
            if self.operation_type == "scan":
                self.scan_engine.stop_scanning = True
            elif self.operation_type == "organize":
                # Organizasyon zaten self.operation_cancelled kontrolü yapıyor
                pass
            
            # UI güncelle
            if hasattr(self.gui_manager, 'ui_widgets'):
                widgets = self.gui_manager.ui_widgets
                if 'stop_btn' in widgets:
                    widgets['stop_btn'].configure(state='disabled', text="⏹️ Durduruluyor...")
            
            # Progress ve time estimation durdur
            self.gui_manager.stop_time_estimation()
            
            # Kullanıcıya bilgi ver
            def show_stop_message():
                operation_name = "Tarama" if self.operation_type == "scan" else "Organizasyon"
                messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), 
                                  f"{operation_name} durduruldu. Mevcut işlem tamamlandıktan sonra duracak.")
                
                # Butonları normale döndür
                self._reset_buttons_after_operation()
            
            # UI thread'inde mesaj göster
            self.root.after(100, show_stop_message)
            
        except Exception as e:
            print(f"Stop operation error: {e}")

    def start_scan(self):
        """Tarama işlemini başlat - Thread-safe"""
        # İptal bayrağını sıfırla
        self.operation_cancelled = False
        self.operation_type = "scan"
        
        # Butonları deaktif et
        if hasattr(self.gui_manager, 'ui_widgets'):
            widgets = self.gui_manager.ui_widgets
            if 'organize_btn' in widgets:
                widgets['organize_btn'].configure(state='disabled')
            if 'scan_btn' in widgets:
                widgets['scan_btn'].configure(state='disabled')
            if 'stop_btn' in widgets:
                widgets['stop_btn'].configure(state='normal')
        
        # Scan engine'e stop kontrolü ekle
        self.scan_engine.stop_scanning = False
        
        # Tarama başlat
        self.scan_engine.scan_files()

    def start_organization(self):
        """Organizasyon işlemini başlat - Thread-safe"""
        import threading
        
        # İptal bayrağını sıfırla
        self.operation_cancelled = False
        self.operation_type = "organize"
        
        # Butonları deaktif et
        if hasattr(self.gui_manager, 'ui_widgets'):
            widgets = self.gui_manager.ui_widgets
            if 'organize_btn' in widgets:
                widgets['organize_btn'].configure(state='disabled')
            if 'scan_btn' in widgets:
                widgets['scan_btn'].configure(state='disabled')
            if 'stop_btn' in widgets:
                widgets['stop_btn'].configure(state='normal')
        
        # Progress bar'ı sıfırla
        self.gui_manager.progress_var.set(0)
        
        # Thread'de organizasyon başlat
        try:
            organization_thread = threading.Thread(target=self._organization_thread, daemon=True)
            self.current_operation_thread = organization_thread
            organization_thread.start()
        except Exception as e:
            messagebox.showerror("Hata", f"Organizasyon başlatılamadı: {e}")
            # Butonları yeniden aktif et
            self._reset_buttons_after_operation()
    
    def _reset_buttons_after_operation(self):
        """İşlem sonrası butonları normale döndür"""
        if hasattr(self.gui_manager, 'ui_widgets'):
            widgets = self.gui_manager.ui_widgets
            if 'organize_btn' in widgets:
                widgets['organize_btn'].configure(state='normal')
            if 'scan_btn' in widgets:
                widgets['scan_btn'].configure(state='normal')
            if 'stop_btn' in widgets:
                widgets['stop_btn'].configure(state='disabled')

    def _organization_thread(self):
        """Organizasyon thread'i - Ana thread'den ayrı çalışır"""
        try:
            self._perform_organization()
        except Exception as e:
            # Hata durumunda UI'yi güncelle
            def error_update():
                messagebox.showerror("Organizasyon Hatası", f"Organizasyon sırasında hata oluştu: {e}")
                self._reset_buttons_after_operation()
            
            self.root.after(0, error_update)
    
    def _count_total_items_for_organization(self):
        """Organize edilecek toplam öğe sayısını hesapla - Organization structure'dan"""
        total_count = 0
        
        # Organization structure'daki tüm dosyaları say
        if hasattr(self.scan_engine, 'organization_structure'):
            for main_folder, subfolders in self.scan_engine.organization_structure.items():
                for subfolder, files in subfolders.items():
                    total_count += len(files)
        
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
            moved_files = 0  # Taşınan dosya sayısı
            duplicates_moved = 0  # Duplikat dosya sayısı
            empty_folders_moved = 0  # Boş klasör sayısı
            likely_duplicates_moved = 0  # Muhtemel duplikat sayısı
            
            # Duplikat işlem seçeneği
            duplicate_action = self.gui_manager.duplicate_action.get()
            
            # Organizasyon modu seçeneği - Yeni eklendi
            operation_mode = self.gui_manager.operation_mode.get()  # "copy" veya "move"
            
            # Duplicate Files klasörü oluştur
            duplicate_files_folder = os.path.join(target_base, "Duplicate Files")
            os.makedirs(duplicate_files_folder, exist_ok=True)
            
            # Likely Duplicates klasörü oluştur
            likely_duplicates_folder = os.path.join(target_base, "Likely Duplicates")
            os.makedirs(likely_duplicates_folder, exist_ok=True)
            
            # TARAMA SONUÇLARINI KULLAN: Organizasyon yapısından direkt taşı
            # Artık existing_folder_files ve unique_files ayrımı yok - hepsi organization_structure'da
            
            for main_folder, subfolders in self.scan_engine.organization_structure.items():
                # İptal kontrolü
                if self.operation_cancelled:
                    def cancelled_update():
                        messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), 
                                           "Organizasyon kullanıcı tarafından durduruldu.")
                        self._reset_buttons_after_operation()
                    self.root.after(0, cancelled_update)
                    return
                
                # ÖZEL DURUM: Duplicate Files ve Likely Duplicates klasörleri
                # Bu klasörler zaten doğru organize edilmiş, sadece dosyaları taşı
                if main_folder in ["Duplicate Files", "Likely Duplicates"]:
                    print(f"🔄 {main_folder} klasörü işleniyor...")
                    
                    # Ana klasörü oluştur
                    main_folder_path = os.path.join(target_base, main_folder)
                    os.makedirs(main_folder_path, exist_ok=True)
                    
                    for subfolder, files in subfolders.items():
                        # İptal kontrolü
                        if self.operation_cancelled:
                            def cancelled_update():
                                messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), 
                                                   "Organizasyon kullanıcı tarafından durduruldu.")
                                self._reset_buttons_after_operation()
                            self.root.after(0, cancelled_update)
                            return
                        
                        # Hedef klasör yolu
                        if subfolder:
                            target_folder_path = os.path.join(main_folder_path, subfolder)
                        else:
                            target_folder_path = main_folder_path
                        
                        # Hedef klasörü oluştur
                        os.makedirs(target_folder_path, exist_ok=True)
                        
                        # Bu klasördeki tüm dosyaları işle
                        for file_info in files:
                            # İptal kontrolü - her dosya için
                            if self.operation_cancelled:
                                def cancelled_update():
                                    messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), 
                                                       "Organizasyon kullanıcı tarafından durduruldu.")
                                    self._reset_buttons_after_operation()
                                self.root.after(0, cancelled_update)
                                return
                            
                            try:
                                # Hedef dosya yolu
                                target_file = os.path.join(target_folder_path, file_info['name'])
                                
                                # Self-copy kontrolü
                                if os.path.normpath(file_info['path']) == os.path.normpath(target_file):
                                    skipped_files += 1
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
                                    continue
                                
                                # Aynı isimde dosya varsa numara ekle (duplikat klasöründe bile)
                                if os.path.exists(target_file):
                                    counter = 1
                                    is_folder = file_info.get('is_folder', False)
                                    
                                    if is_folder:
                                        # Klasör için uzantısız işlem
                                        base_name = file_info['name']
                                        while os.path.exists(target_file):
                                            new_name = f"{base_name}_{counter}"
                                            target_file = os.path.join(target_folder_path, new_name)
                                            counter += 1
                                    else:
                                        # Dosya için uzantılı işlem
                                        base_name, ext = os.path.splitext(file_info['name'])
                                        while os.path.exists(target_file):
                                            new_name = f"{base_name}_{counter}{ext}"
                                            target_file = os.path.join(target_folder_path, new_name)
                                            counter += 1
                                    
                                    print(f"🔢 {main_folder} içinde dosya numaralandırıldı: {file_info['name']} -> {os.path.basename(target_file)}")
                                
                                # Dosya/klasör türüne göre kopyala veya taşı
                                is_folder = file_info.get('is_folder', False)
                                
                                if operation_mode == "move":
                                    if is_folder:
                                        # Klasör taşıma için shutil.move kullan
                                        try:
                                            import shutil
                                            shutil.move(file_info['path'], target_file)
                                            moved_files += 1
                                            success = True
                                            if main_folder == "Duplicate Files":
                                                duplicates_moved += 1
                                            elif main_folder == "Likely Duplicates":
                                                likely_duplicates_moved += 1
                                            print(f"📁 {main_folder} klasörü taşındı: {file_info['name']} -> {target_file}")
                                        except Exception as e:
                                            error_files += 1
                                            success = False
                                            print(f"⚠️ {main_folder} klasör taşıma hatası: {file_info['name']} - {e}")
                                    else:
                                        # Normal dosya taşıma
                                        success, message = self.file_operations.move_file_optimized(file_info['path'], target_file)
                                        if success:
                                            moved_files += 1
                                            if main_folder == "Duplicate Files":
                                                duplicates_moved += 1
                                            elif main_folder == "Likely Duplicates":
                                                likely_duplicates_moved += 1
                                            print(f"📄 {main_folder} dosyası taşındı: {file_info['name']}")
                                        else:
                                            error_files += 1
                                            print(f"⚠️ {main_folder} dosya taşıma hatası: {file_info['name']} - {message}")
                                else:  # copy mode
                                    if is_folder:
                                        # Klasör kopyalama için shutil.copytree kullan
                                        try:
                                            import shutil
                                            shutil.copytree(file_info['path'], target_file)
                                            copied_files += 1
                                            success = True
                                            if main_folder == "Duplicate Files":
                                                duplicates_moved += 1
                                            elif main_folder == "Likely Duplicates":
                                                likely_duplicates_moved += 1
                                            print(f"📁 {main_folder} klasörü kopyalandı: {file_info['name']} -> {target_file}")
                                        except Exception as e:
                                            error_files += 1
                                            success = False
                                            print(f"⚠️ {main_folder} klasör kopyalama hatası: {file_info['name']} - {e}")
                                    else:
                                        # Normal dosya kopyalama
                                        success, message = self.file_operations.copy_file_optimized(file_info['path'], target_file)
                                        if success:
                                            copied_files += 1
                                            if main_folder == "Duplicate Files":
                                                duplicates_moved += 1
                                            elif main_folder == "Likely Duplicates":
                                                likely_duplicates_moved += 1
                                            print(f"📄 {main_folder} dosyası kopyalandı: {file_info['name']}")
                                        else:
                                            error_files += 1
                                            print(f"⚠️ {main_folder} dosya kopyalama hatası: {file_info['name']} - {message}")
                                
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
                                print(f"⚠️ {main_folder} dosya işleme hatası: {e}")
                                
                                # Progress güncelle (hata durumunda da)
                                progress = (processed_items / total_items) * 100
                                def update_progress():
                                    self.gui_manager.progress_var.set(progress)
                                self.root.after(0, update_progress)
                    
                    # Bu klasör işlendi, bir sonrakine geç
                    continue
                
                # NORMAL KLASÖRLER: Duplicate Files ve Likely Duplicates dışındaki tüm klasörler
                print(f"🔄 Normal klasör işleniyor: {main_folder}")
                
                # Ana klasörü oluştur
                main_folder_path = os.path.join(target_base, main_folder)
                os.makedirs(main_folder_path, exist_ok=True)
                
                for subfolder, files in subfolders.items():
                    # İptal kontrolü
                    if self.operation_cancelled:
                        def cancelled_update():
                            messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), 
                                               "Organizasyon kullanıcı tarafından durduruldu.")
                            self._reset_buttons_after_operation()
                        self.root.after(0, cancelled_update)
                        return
                    
                    # Hedef klasör yolu
                    if subfolder:
                        target_folder_path = os.path.join(main_folder_path, subfolder)
                    else:
                        target_folder_path = main_folder_path
                    
                    # Hedef klasörü oluştur
                    os.makedirs(target_folder_path, exist_ok=True)
                    
                    # Bu klasördeki tüm dosyaları işle
                    for file_info in files:
                        # İptal kontrolü - her dosya için
                        if self.operation_cancelled:
                            def cancelled_update():
                                messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), 
                                                   "Organizasyon kullanıcı tarafından durduruldu.")
                                self._reset_buttons_after_operation()
                            self.root.after(0, cancelled_update)
                            return
                        
                        try:
                            # Hedef dosya yolu
                            target_file = os.path.join(target_folder_path, file_info['name'])
                            
                            # Self-copy kontrolü
                            if os.path.normpath(file_info['path']) == os.path.normpath(target_file):
                                skipped_files += 1
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
                                continue
                            
                            # ARTIK DUPLIKAT KONTROLÜ YOK - Çünkü duplikatlar zaten ayrı klasörlerde
                            # Sadece normal dosya/klasör işleme
                            
                            # Aynı isimde dosya/klasör varsa duplikat action'a göre işlem yap
                            if os.path.exists(target_file):
                                # Duplikat action kontrolü
                                if duplicate_action == "skip":
                                    # Skip - dosyayı atla
                                    skipped_files += 1
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
                                    
                                    print(f"⏭️ Dosya atlandı (zaten var): {file_info['name']}")
                                    continue
                                    
                                elif duplicate_action == "copy":
                                    # Copy with number - numara ekle
                                    counter = 1
                                    is_folder = file_info.get('is_folder', False)
                                    
                                    if is_folder:
                                        # Klasör için uzantısız işlem
                                        base_name = file_info['name']
                                        while os.path.exists(target_file):
                                            new_name = f"{base_name}_{counter}"
                                            target_file = os.path.join(target_folder_path, new_name)
                                            counter += 1
                                    else:
                                        # Dosya için uzantılı işlem
                                        base_name, ext = os.path.splitext(file_info['name'])
                                        while os.path.exists(target_file):
                                            new_name = f"{base_name}_{counter}{ext}"
                                            target_file = os.path.join(target_folder_path, new_name)
                                            counter += 1
                                    
                                    print(f"🔢 Dosya numaralandırıldı: {file_info['name']} -> {os.path.basename(target_file)}")
                                    
                                elif duplicate_action == "ask":
                                    # Ask each time - kullanıcıya sor
                                    action = self._ask_duplicate_action(file_info['name'])
                                    
                                    if action in ["skip", "skip_all"]:
                                        # Skip this file
                                        skipped_files += 1
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
                                        
                                        print(f"⏭️ Kullanıcı dosyayı atladı: {file_info['name']}")
                                        
                                        # Skip all seçildiyse duplicate_action'ı güncelle
                                        if action == "skip_all":
                                            duplicate_action = "skip"
                                            print("⏭️ Tüm duplikatlar atlanacak")
                                        
                                        continue
                                        
                                    elif action in ["copy", "copy_all"]:
                                        # Copy with number
                                        counter = 1
                                        is_folder = file_info.get('is_folder', False)
                                        
                                        if is_folder:
                                            # Klasör için uzantısız işlem
                                            base_name = file_info['name']
                                            while os.path.exists(target_file):
                                                new_name = f"{base_name}_{counter}"
                                                target_file = os.path.join(target_folder_path, new_name)
                                                counter += 1
                                        else:
                                            # Dosya için uzantılı işlem
                                            base_name, ext = os.path.splitext(file_info['name'])
                                            while os.path.exists(target_file):
                                                new_name = f"{base_name}_{counter}{ext}"
                                                target_file = os.path.join(target_folder_path, new_name)
                                                counter += 1
                                        
                                        print(f"🔢 Kullanıcı dosyayı numaralandırdı: {file_info['name']} -> {os.path.basename(target_file)}")
                                        
                                        # Copy all seçildiyse duplicate_action'ı güncelle
                                        if action == "copy_all":
                                            duplicate_action = "copy"
                                            print("🔢 Tüm duplikatlar numaralandırılacak")
                                else:
                                    # Varsayılan: numara ekle (eski davranış)
                                    counter = 1
                                    is_folder = file_info.get('is_folder', False)
                                    
                                    if is_folder:
                                        # Klasör için uzantısız işlem
                                        base_name = file_info['name']
                                        while os.path.exists(target_file):
                                            new_name = f"{base_name}_{counter}"
                                            target_file = os.path.join(target_folder_path, new_name)
                                            counter += 1
                                    else:
                                        # Dosya için uzantılı işlem
                                        base_name, ext = os.path.splitext(file_info['name'])
                                        while os.path.exists(target_file):
                                            new_name = f"{base_name}_{counter}{ext}"
                                            target_file = os.path.join(target_folder_path, new_name)
                                            counter += 1
                            
                            # Dosya/klasör türüne göre kopyala veya taşı
                            is_folder = file_info.get('is_folder', False)
                            
                            if operation_mode == "move":
                                if is_folder:
                                    # Klasör taşıma için shutil.move kullan
                                    try:
                                        import shutil
                                        shutil.move(file_info['path'], target_file)
                                        moved_files += 1
                                        success = True
                                        print(f"📁 Normal klasör taşındı: {file_info['name']} -> {target_file}")
                                    except Exception as e:
                                        error_files += 1
                                        success = False
                                        print(f"⚠️ Normal klasör taşıma hatası: {file_info['name']} - {e}")
                                else:
                                    # Normal dosya taşıma
                                    success, message = self.file_operations.move_file_optimized(file_info['path'], target_file)
                                    if success:
                                        moved_files += 1
                                        print(f"📄 Normal dosya taşındı: {file_info['name']}")
                                    else:
                                        error_files += 1
                                        print(f"⚠️ Normal dosya taşıma hatası: {file_info['name']} - {message}")
                            else:  # copy mode
                                if is_folder:
                                    # Klasör kopyalama için shutil.copytree kullan
                                    try:
                                        import shutil
                                        shutil.copytree(file_info['path'], target_file)
                                        copied_files += 1
                                        success = True
                                        print(f"📁 Normal klasör kopyalandı: {file_info['name']} -> {target_file}")
                                    except Exception as e:
                                        error_files += 1
                                        success = False
                                        print(f"⚠️ Normal klasör kopyalama hatası: {file_info['name']} - {e}")
                                else:
                                    # Normal dosya kopyalama
                                    success, message = self.file_operations.copy_file_optimized(file_info['path'], target_file)
                                    if success:
                                        copied_files += 1
                                        print(f"📄 Normal dosya kopyalandı: {file_info['name']}")
                                    else:
                                        error_files += 1
                                        print(f"⚠️ Normal dosya kopyalama hatası: {file_info['name']} - {message}")
                            
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
                            print(f"⚠️ Normal klasör işleme hatası: {e}")
                            
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
                if operation_mode == "move":
                    message += f"{lang_manager.get_text('messages.moved')}: {moved_files}\n"
                    message += f"{lang_manager.get_text('messages.copied')}: {copied_files}\n"
                else:
                    message += f"{lang_manager.get_text('messages.copied')}: {copied_files}\n"
                message += f"{lang_manager.get_text('messages.skipped')}: {skipped_files}\n"
                message += f"{lang_manager.get_text('messages.errors')}: {error_files}\n"
                
                # Duplikat ve boş klasör bilgileri
                if duplicates_moved > 0:
                    message += f"{lang_manager.get_text('messages.duplicates_moved')}: {duplicates_moved}\n"
                if likely_duplicates_moved > 0:
                    message += f"Muhtemel Duplikatlar Taşındı: {likely_duplicates_moved}\n"
                if empty_folders_moved > 0:
                    message += f"{lang_manager.get_text('messages.empty_folders_moved')}: {empty_folders_moved}"
                
                messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), message)
                
                # Butonları yeniden aktif et
                self._reset_buttons_after_operation()
            
            # Boş klasörleri temizle
            if operation_mode == "move":
                empty_folders_moved += self._cleanup_empty_folders(self.file_operations.source_path, duplicate_files_folder)
            
            self.root.after(0, final_update)
                    
        except Exception as e:
            # Kritik hata durumunda
            def error_update():
                # Time estimation durdur
                self.gui_manager.stop_time_estimation()
                
                messagebox.showerror(lang_manager.get_text('dialogs.error.title'), 
                                   lang_manager.get_text('messages.error', error=str(e)))
                self._reset_buttons_after_operation()
            
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
    
    def _cleanup_empty_folders(self, source_path, duplicate_files_folder):
        """Boş klasörleri Duplicate Files klasörüne taşı"""
        import time
        empty_folders_moved = 0
        
        try:
            # Kaynak klasörde boş klasörleri bul (bottom-up approach)
            for root, dirs, files in os.walk(source_path, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    
                    # Klasör boş mu kontrol et
                    if self._is_folder_empty(dir_path):
                        try:
                            # Boş klasörü Duplicate Files'a taşı
                            timestamp = int(time.time())
                            empty_folder_name = f"empty_folder_{timestamp}_{dir_name}"
                            target_path = os.path.join(duplicate_files_folder, empty_folder_name)
                            
                            # Klasörü taşı
                            shutil.move(dir_path, target_path)
                            empty_folders_moved += 1
                            print(f"📁 Boş klasör taşındı: {dir_name} -> Duplicate Files/{empty_folder_name}")
                            
                        except Exception as e:
                            print(f"⚠️ Boş klasör taşıma hatası: {e}")
                            continue
            
            return empty_folders_moved
            
        except Exception as e:
            print(f"⚠️ Boş klasör temizleme hatası: {e}")
            return 0
    
    def _is_folder_empty(self, folder_path):
        """Klasörün tamamen boş olup olmadığını kontrol et"""
        try:
            # Klasör var mı kontrol et
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                return False
            
            # Klasör içeriğini kontrol et
            for root, dirs, files in os.walk(folder_path):
                # Herhangi bir dosya varsa boş değil
                if files:
                    return False
                
                # Alt klasörlerde dosya var mı kontrol et
                for subdir in dirs:
                    subdir_path = os.path.join(root, subdir)
                    if not self._is_folder_empty(subdir_path):
                        return False
            
            # Hiç dosya bulunamadıysa boş
            return True
            
        except Exception as e:
            print(f"⚠️ Klasör boşluk kontrolü hatası: {e}")
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

    def _calculate_file_hash(self, file_path, chunk_size=8192):
        """Dosya hash'ini hesapla"""
        try:
            hash_md5 = hashlib.md5()  # MD5 algoritması kullanılıyor
            with open(file_path, "rb") as f:  # Dosyayı binary modda aç
                for chunk in iter(lambda: f.read(chunk_size), b""):  # 8KB parçalar halinde oku
                    hash_md5.update(chunk)  # Her parçayı hash'e ekle
            return hash_md5.hexdigest()  # Hexadecimal string döndür
        except:
            return None  # Hata durumunda None döndür
    
    def _get_media_dimensions(self, file_path):
        """Media dosyasının boyutlarını al (resim/video)"""
        try:
            extension = os.path.splitext(file_path)[1].lower()
            
            # Resim dosyaları için
            if extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']:
                return self._get_image_dimensions(file_path)
            
            # Video dosyaları için
            elif extension in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']:
                return self._get_video_dimensions(file_path)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Media boyut alma hatası: {e}")
            return None
    
    def _get_image_dimensions(self, file_path):
        """Resim dosyasının boyutlarını al"""
        try:
            # PIL/Pillow kullanmadan basit JPEG/PNG header okuma
            with open(file_path, 'rb') as f:
                # JPEG için
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    return self._parse_jpeg_dimensions(f)
                # PNG için
                elif file_path.lower().endswith('.png'):
                    return self._parse_png_dimensions(f)
                # Diğer formatlar için basit yaklaşım
                else:
                    return None
        except:
            return None
    
    def _parse_jpeg_dimensions(self, f):
        """JPEG dosyasından boyutları oku"""
        try:
            f.seek(0)
            if f.read(2) != b'\xff\xd8':  # JPEG magic number
                return None
            
            while True:
                marker = f.read(2)
                if len(marker) != 2:
                    break
                    
                if marker[0] != 0xff:
                    break
                    
                # SOF (Start of Frame) marker'ları
                if marker[1] in [0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]:
                    f.read(3)  # Length + precision
                    height = int.from_bytes(f.read(2), 'big')
                    width = int.from_bytes(f.read(2), 'big')
                    return f"{width}x{height}"
                else:
                    # Segment length oku ve atla
                    length = int.from_bytes(f.read(2), 'big')
                    f.seek(length - 2, 1)
            
            return None
        except:
            return None
    
    def _parse_png_dimensions(self, f):
        """PNG dosyasından boyutları oku"""
        try:
            f.seek(0)
            if f.read(8) != b'\x89PNG\r\n\x1a\n':  # PNG signature
                return None
            
            # IHDR chunk'ı oku
            f.read(4)  # Chunk length
            if f.read(4) != b'IHDR':
                return None
                
            width = int.from_bytes(f.read(4), 'big')
            height = int.from_bytes(f.read(4), 'big')
            return f"{width}x{height}"
        except:
            return None
    
    def _get_video_dimensions(self, file_path):
        """Video dosyasının boyutlarını al (basit yaklaşım)"""
        try:
            # Video metadata okuma çok karmaşık, basit bir yaklaşım kullanıyoruz
            # Gerçek uygulamada ffprobe veya benzeri araçlar kullanılabilir
            
            # Dosya boyutuna göre tahmin (çok basit)
            file_size = os.path.getsize(file_path)
            
            # Yaygın video çözünürlükleri ve dosya boyutları
            if file_size < 50 * 1024 * 1024:  # 50MB altı
                return "720x480"  # SD
            elif file_size < 200 * 1024 * 1024:  # 200MB altı
                return "1280x720"  # HD
            elif file_size < 500 * 1024 * 1024:  # 500MB altı
                return "1920x1080"  # Full HD
            else:
                return "3840x2160"  # 4K
                
        except:
            return None


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