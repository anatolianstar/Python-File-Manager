"""
Modüler Dosya Organizatörü - Ana Program
Tüm modülleri bir araya getiren ana dosya
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os

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
        # Ana pencere oluştur
        self.root = tk.Tk()
        
        # Modülleri başlat
        self.initialize_modules()
        
        # Modüller arası bağlantıları kur
        self.setup_connections()
        
        # Bağlantıları test et
        self.test_connections()
        
        # Başlangıç ayarları
        self.setup_initial_state()
    
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
            
            print("✅ Tüm modüller başarıyla yüklendi!")
            
        except Exception as e:
            messagebox.showerror("Başlatma Hatası", f"Modüller yüklenirken hata: {e}")
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
        
        print("✅ Modül bağlantıları kuruldu!")
    
    def rebind_buttons(self):
        """Butonları yeniden bağla - GUI oluşturulduktan sonra"""
        print("🔧 Butonlar yeniden bağlanıyor...")
        
        # Ana butonları bul ve yeniden bağla
        for widget in self.gui_manager.root.winfo_children():
            self._rebind_widget_recursive(widget)
        
        print("✅ Butonlar yeniden bağlandı!")
    
    def rebind_events(self):
        """Event binding'leri yeniden yap"""
        print("🔧 Event binding'ler yeniden bağlanıyor...")
        
        # Target tree event'lerini temizle ve yeniden bağla
        target_tree = self.gui_manager.target_tree
        
        # Eski binding'leri temizle
        target_tree.unbind('<Double-1>')
        target_tree.unbind('<Button-3>')
        target_tree.unbind('<Delete>')
        target_tree.unbind('<Control-c>')
        target_tree.unbind('<Control-x>')
        target_tree.unbind('<Control-v>')
        target_tree.unbind('<F2>')
        target_tree.unbind('<F5>')
        target_tree.unbind('<BackSpace>')
        target_tree.unbind('<Return>')
        
        # Yeni binding'leri ekle
        target_tree.bind('<Double-1>', self.file_operations.on_target_double_click)
        target_tree.bind('<Button-3>', self.file_operations.show_context_menu)
        
        # Klavye kısayollarını da yeniden bağla
        target_tree.bind('<Delete>', lambda e: self.file_operations.delete_selected())
        target_tree.bind('<Control-c>', lambda e: self.file_operations.copy_selected())
        target_tree.bind('<Control-x>', lambda e: self.file_operations.cut_selected())
        target_tree.bind('<Control-v>', lambda e: self.file_operations.paste_selected())
        target_tree.bind('<F2>', lambda e: self.file_operations.rename_selected())
        target_tree.bind('<F5>', lambda e: self.file_operations.refresh_target())
        target_tree.bind('<BackSpace>', lambda e: self.file_operations.go_up())
        target_tree.bind('<Return>', lambda e: self.file_operations.open_selected())
        
        print("✅ Event binding'ler yeniden bağlandı!")
    
    def _rebind_widget_recursive(self, widget):
        """Widget'ları recursive olarak tara ve butonları yeniden bağla"""
        try:
            # Eğer bu bir Button ise
            if isinstance(widget, ttk.Button):
                button_text = widget.cget('text')
                
                # Buton metnine göre doğru metodu bağla
                if button_text == "Seç":
                    widget.configure(command=self.file_operations.select_source_folder)
                elif button_text == "Değiştir":
                    widget.configure(command=self.file_operations.select_target_folder)
                elif button_text == "◀ Geri":
                    widget.configure(command=self.file_operations.go_back)
                elif button_text == "▲ Üst Klasör":
                    widget.configure(command=self.file_operations.go_up)
                elif button_text == "🏠 Ana Klasör":
                    widget.configure(command=self.file_operations.go_home)
                elif button_text == "Git":
                    widget.configure(command=self.file_operations.navigate_to_path)
                elif button_text == "🔄 Yenile":
                    widget.configure(command=self.file_operations.refresh_target)
                elif button_text == "🗑️ Sil":
                    widget.configure(command=self.file_operations.delete_selected)
                elif button_text == "📋 Kopyala":
                    widget.configure(command=self.file_operations.copy_selected)
                elif button_text == "✂️ Kes":
                    widget.configure(command=self.file_operations.cut_selected)
                elif button_text == "📁 Yapıştır":
                    widget.configure(command=self.file_operations.paste_selected)
                elif button_text == "➕ Yeni Klasör":
                    widget.configure(command=self.file_operations.create_folder)
                elif button_text == "🔓 Aç":
                    widget.configure(command=self.file_operations.open_selected)
                elif button_text == "Dosyaları Tara":
                    widget.configure(command=self.scan_engine.scan_files)
                elif button_text == "🔍 Hedef Disk Analizi":
                    widget.configure(command=self.reporting.analyze_target_disk)
                elif button_text == "Organizasyonu Başlat":
                    widget.configure(command=self.start_organization)
                
            
            # Alt widget'ları da kontrol et
            for child in widget.winfo_children():
                self._rebind_widget_recursive(child)
                
        except Exception as e:
            # Hata olursa sessizce devam et
            pass
    
    def test_connections(self):
        """Bağlantıları test et ve doğrula"""
        print("🔍 Bağlantı testi yapılıyor...")
        
        # Test: select_source_folder bağlantısı
        if self.gui_manager.select_source_folder == self.file_operations.select_source_folder:
            print("✅ select_source_folder bağlantısı doğru")
        else:
            print("❌ select_source_folder bağlantısı yanlış!")
            # Zorla düzelt
            self.gui_manager.select_source_folder = self.file_operations.select_source_folder
            print("🔧 select_source_folder bağlantısı düzeltildi")
        
        # Test: select_target_folder bağlantısı
        if self.gui_manager.select_target_folder == self.file_operations.select_target_folder:
            print("✅ select_target_folder bağlantısı doğru")
        else:
            print("❌ select_target_folder bağlantısı yanlış!")
            # Zorla düzelt
            self.gui_manager.select_target_folder = self.file_operations.select_target_folder
            print("🔧 select_target_folder bağlantısı düzeltildi")
        
        # Test: scan_files bağlantısı
        if self.gui_manager.scan_files == self.scan_engine.scan_files:
            print("✅ scan_files bağlantısı doğru")
        else:
            print("❌ scan_files bağlantısı yanlış!")
            # Zorla düzelt
            self.gui_manager.scan_files = self.scan_engine.scan_files
            print("🔧 scan_files bağlantısı düzeltildi")
        
        print("✅ Bağlantı testi tamamlandı!")
    
    def setup_initial_state(self):
        """Başlangıç durumunu ayarla"""
        # Pencere başlığını güncelle
        self.root.title("Dosya Organizatörü - Modüler Versiyon v2.0")
        
        # Başlangıç mesajı
        self.gui_manager.status_var.set("Modüler dosya organizatörü hazır! Kaynak klasör seçerek başlayın.")
        
        # Klavye kısayolları
        self.setup_keyboard_shortcuts()
        
        print("✅ Başlangıç ayarları tamamlandı!")
    
    def setup_keyboard_shortcuts(self):
        """Klavye kısayollarını ayarla"""
        # Global kısayollar
        self.root.bind('<Control-o>', lambda e: self.file_operations.select_source_folder())
        self.root.bind('<Control-t>', lambda e: self.file_operations.select_target_folder())
        self.root.bind('<F5>', lambda e: self.file_operations.refresh_target())
        self.root.bind('<Control-s>', lambda e: self.scan_engine.scan_files())
        self.root.bind('<Control-r>', lambda e: self.reporting.analyze_target_disk())
        
        # File manager kısayolları
        self.root.bind('<Control-c>', lambda e: self.file_operations.copy_selected())
        self.root.bind('<Control-x>', lambda e: self.file_operations.cut_selected())
        self.root.bind('<Control-v>', lambda e: self.file_operations.paste_selected())
        # Delete tuşu sadece target_tree için bağlı olacak, global değil
        self.root.bind('<F2>', lambda e: self.file_operations.rename_selected())
        
        # Çıkış
        self.root.bind('<Control-q>', lambda e: self.quit_application())
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
    
    def start_organization(self):
        """Organizasyon işlemini başlat - birden fazla modül koordinasyonu"""
        # Önce kontroller
        if not self.gui_manager.source_var.get():
            messagebox.showwarning("Uyarı", "Önce kaynak klasör seçin!")
            return
        
        if not self.gui_manager.target_var.get():
            messagebox.showwarning("Uyarı", "Önce hedef klasör seçin!")
            return
        
        if not self.scan_engine.all_scanned_files:
            messagebox.showwarning("Uyarı", "Önce dosyaları tarayın!")
            return
        
        # Onay al
        unique_count = len(self.scan_engine.unique_files)
        duplicate_count = len(self.scan_engine.duplicate_files)
        
        message = f"""Organizasyon başlatılacak:

📊 İstatistikler:
• {unique_count} unique dosya kopyalanacak
• {duplicate_count} duplikat dosya var
• Hedef: {self.gui_manager.target_var.get()}

Devam etmek istediğinizden emin misiniz?"""
        
        if not messagebox.askyesno("Organizasyon Onayı", message):
            return
        
        # Organizasyon thread'ini başlat
        import threading
        org_thread = threading.Thread(target=self._organization_thread, daemon=True)
        org_thread.start()
    
    def _organization_thread(self):
        """Organizasyon thread'i"""
        try:
            # Progress başlat
            self.gui_manager.progress_var.set(0)
            self.gui_manager.status_var.set("Organizasyon başlatılıyor...")
            
            # Time estimation başlat
            self.gui_manager.start_time_estimation()
            
            # Organizasyonu gerçekleştir
            self._perform_organization()
            
        except Exception as e:
            self.root.after(0, lambda: self.gui_manager.status_var.set(f"❌ Organizasyon hatası: {e}"))
            print(f"Organizasyon hatası: {e}")
        finally:
            # Progress sıfırla
            self.root.after(0, lambda: self.gui_manager.progress_var.set(0))
            # Time estimation durdur
            self.root.after(0, lambda: self.gui_manager.stop_time_estimation())
    
    def _perform_organization(self):
        """Organizasyon işlemini gerçekleştir - Ana programdan optimize edildi"""
        import shutil
        import time
        
        target_base = self.gui_manager.target_var.get()
        total_files = len(self.scan_engine.unique_files)
        copied_files = 0
        skipped_files = 0
        error_files = 0
        
        # Duplikat işlem seçeneği
        duplicate_action = self.gui_manager.duplicate_action.get()
        
        # Önce mevcut klasörlerdeki dosyaları işle
        if hasattr(self.scan_engine, 'existing_folder_files'):
            for folder_path, files in self.scan_engine.existing_folder_files.items():
                print(f"📁 Mevcut klasöre dosya kopyalanıyor: {folder_path}")
                
                # Eğer folder_path tam yol değilse, hedef klasörle birleştir
                if not os.path.isabs(folder_path):
                    full_folder_path = os.path.join(target_base, folder_path)
                else:
                    full_folder_path = folder_path
                
                print(f"📂 Tam klasör yolu: {full_folder_path}")
                
                for file_info in files:
                    try:
                        # Hedef dosya yolu
                        target_file = os.path.join(full_folder_path, file_info['name'])
                        
                        # Gelişmiş duplikat kontrolü
                        if os.path.exists(target_file):
                            if duplicate_action == "skip":
                                skipped_files += 1
                                continue
                            elif duplicate_action == "ask":
                                # UI thread'inde sor
                                result = self._ask_duplicate_action(file_info['name'])
                                if result == "skip":
                                    skipped_files += 1
                                    continue
                                elif result == "skip_all":
                                    duplicate_action = "skip"
                                    skipped_files += 1
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
                            print(f"✅ Mevcut klasöre kopyalandı: {file_info['name']} -> {full_folder_path}")
                        else:
                            error_files += 1
                            print(f"❌ Mevcut klasör kopyalama hatası: {file_info['name']} - {message}")
                    
                    except Exception as e:
                        error_files += 1
                        print(f"❌ Mevcut klasör dosya hatası: {file_info['name']} - {e}")
        
        # Sonra yeni klasör yapısındaki dosyaları işle
        for i, file_info in enumerate(self.scan_engine.unique_files):
            try:
                # Progress güncelle
                progress = (i + 1) / total_files * 100
                self.root.after(0, lambda p=progress: self.gui_manager.progress_var.set(p))
                
                # Time estimation güncelle
                self.root.after(0, lambda p=progress, processed=i+1, total=total_files: 
                               self.gui_manager.update_time_estimation(p, processed, total))
                
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
                    # Klasör kopyalama
                    source_folder = file_info['path']
                    target_folder = os.path.join(target_base, "Klasörler", "Alt Klasörler", file_info['name'])
                    
                    # Hedef klasör varsa duplikat kontrolü
                    if os.path.exists(target_folder):
                        if duplicate_action == "skip":
                            skipped_files += 1
                            continue
                        elif duplicate_action == "ask":
                            result = self._ask_duplicate_action(file_info['name'])
                            if result == "skip":
                                skipped_files += 1
                                continue
                            elif result == "skip_all":
                                duplicate_action = "skip"
                                skipped_files += 1
                                continue
                            elif result == "copy_all":
                                duplicate_action = "copy"
                        
                        # Aynı isimde klasör varsa numara ekle
                        counter = 1
                        base_name = file_info['name']
                        while os.path.exists(target_folder):
                            new_name = f"{base_name}_{counter}"
                            target_folder = os.path.join(target_base, "Klasörler", "Alt Klasörler", new_name)
                            counter += 1
                    
                    # Klasörü komple kopyala
                    try:
                        shutil.copytree(source_folder, target_folder, dirs_exist_ok=False)
                        copied_files += 1
                        print(f"✅ Klasör kopyalandı: {file_info['name']}")
                    except Exception as e:
                        error_files += 1
                        print(f"❌ Klasör kopyalama hatası: {file_info['name']} - {e}")
                
                else:
                    # Normal dosya kopyalama
                    # Kategori ve hedef yolu belirle
                    category, category_info = self.file_operations.get_file_category(file_info['path'])
                    
                    # Hedef klasör yapısı
                    main_folder = os.path.join(target_base, category_info['folder'])
                    
                    extension = file_info['extension']
                    if extension in category_info['subfolders']:
                        subfolder = category_info['subfolders'][extension]
                    else:
                        subfolder = extension.replace('.', '').upper() if extension else 'Uzantisiz'
                    
                    target_folder = os.path.join(main_folder, subfolder)
                    
                    # Klasörleri oluştur
                    os.makedirs(target_folder, exist_ok=True)
                    
                    # Hedef dosya yolu
                    target_file = os.path.join(target_folder, file_info['name'])
                    
                    # Duplikat kontrolü
                    if os.path.exists(target_file):
                        if duplicate_action == "skip":
                            skipped_files += 1
                            continue
                        elif duplicate_action == "ask":
                            # UI thread'inde sor
                            result = self._ask_duplicate_action(file_info['name'])
                            if result == "skip":
                                skipped_files += 1
                                continue
                            elif result == "skip_all":
                                duplicate_action = "skip"
                                skipped_files += 1
                                continue
                            elif result == "copy_all":
                                duplicate_action = "copy"
                        
                        # Aynı isimde dosya varsa numara ekle
                        counter = 1
                        base_name, ext = os.path.splitext(file_info['name'])
                        while os.path.exists(target_file):
                            new_name = f"{base_name}_{counter}{ext}"
                            target_file = os.path.join(target_folder, new_name)
                            counter += 1
                    
                    # Optimize edilmiş kopyalama
                    success, message = self.file_operations.copy_file_optimized(file_info['path'], target_file)
                    
                    if success:
                        copied_files += 1
                    else:
                        error_files += 1
                        print(f"Kopyalama hatası: {file_info['name']} - {message}")
                
                # Status güncelle
                self.root.after(0, lambda cf=copied_files, sf=skipped_files, ef=error_files: 
                               self.gui_manager.status_var.set(f"Kopyalanan: {cf}, Atlanan: {sf}, Hata: {ef}"))
                
                # UI donmasını önle
                if i % 10 == 0:
                    time.sleep(0.001)
                
            except Exception as e:
                error_files += 1
                print(f"Dosya işleme hatası: {file_info['path']} - {e}")
                continue
        
        # Son güncelleme
        self.root.after(0, lambda: self.gui_manager.status_var.set(
            f"✅ Organizasyon tamamlandı! Kopyalanan: {copied_files}, Atlanan: {skipped_files}, Hata: {error_files}"))
    
    def _ask_duplicate_action(self, filename, duplicate_count=1):
        """Duplikat dosya için kullanıcıdan onay al - Ana programdan alındı"""
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
        
        msg_text = f"Duplikat dosya bulundu:\n\n📄 {filename}"
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
            self.gui_manager.duplicate_action.set("skip")
            dialog.destroy()
            
        def on_copy_all():
            result["action"] = "copy_all"
            self.gui_manager.duplicate_action.set("copy")
            dialog.destroy()
        
        ttk.Button(button_frame, text="🚫 Bu dosyayı atla", command=on_skip).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📋 Bu dosyayı kopyala", command=on_copy).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🚫 Tümünü atla", command=on_skip_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📋 Tümünü kopyala", command=on_copy_all).pack(side=tk.LEFT)
        
        # Dialog'u bekle
        dialog.wait_window()
        
        return result["action"]
    
    def quit_application(self):
        """Uygulamayı kapat"""
        # Ayarları kaydet
        self.file_operations.save_settings()
        
        # Çalışan thread'leri durdur
        if hasattr(self.scan_engine, 'stop_scan'):
            self.scan_engine.stop_scan()
        
        # Pencereyi kapat
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Uygulamayı çalıştır"""
        try:
            print("🚀 Modüler Dosya Organizatörü başlatılıyor...")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n⏹️ Uygulama kullanıcı tarafından durduruldu")
        except Exception as e:
            print(f"❌ Uygulama hatası: {e}")
        finally:
            print("👋 Uygulama kapatıldı")

def main():
    """Ana fonksiyon"""
    try:
        # Uygulama örneği oluştur ve çalıştır
        app = ModularFileManager()
        app.run()
        
    except Exception as e:
        print(f"Kritik hata: {e}")
        messagebox.showerror("Kritik Hata", f"Uygulama başlatılamadı: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 