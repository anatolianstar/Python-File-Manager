"""
Duplicate Image Finder - Tek Klasör İçi Duplikat Resim Bulucu
Sadece tek bir klasör içindeki duplikat resimleri bulur ve organize eder
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib
import shutil
from collections import defaultdict
import threading
from lang_manager import lang_manager

class DuplicateImageFinder:
    """Tek klasör içindeki duplikat resimleri bulan araç"""
    
    def __init__(self, parent_root):
        self.parent_root = parent_root
        self.window = None
        self.selected_folder = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar()
        self.is_scanning = False
        self.scan_thread = None
        self.stop_scanning = False
        self.is_moving = False
        
        # Desteklenen resim formatları
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        
        # Sonuçlar
        self.duplicate_groups = {}
        self.total_files = 0
        self.duplicate_files = 0
        self.space_saved = 0
        
    def open_window(self):
        """Duplikat resim bulucu penceresini aç"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent_root)
        self.window.title(lang_manager.get_text('duplicate_finder.image_title'))
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Pencereyi merkeze hizala
        self.window.transient(self.parent_root)
        self.center_window()
        
        # UI oluştur
        self.create_ui()
        
        # Pencere kapanma olayı
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
    def center_window(self):
        """Pencereyi ekranın merkezine hizala"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
        
    def create_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Başlık
        title_label = ttk.Label(main_frame, text=lang_manager.get_text('duplicate_finder.image_title'), 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Klasör seçimi
        ttk.Label(main_frame, text=lang_manager.get_text('duplicate_finder.select_folder')).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.selected_folder, 
                                     state="readonly")
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_btn = ttk.Button(folder_frame, text=lang_manager.get_text('duplicate_finder.browse'), 
                                    command=self.select_folder)
        self.browse_btn.grid(row=0, column=1)
        
        # Kontrol butonları
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.scan_btn = ttk.Button(button_frame, text=lang_manager.get_text('duplicate_finder.start_scan'), 
                                  command=self.start_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text=lang_manager.get_text('duplicate_finder.stop'), 
                                  command=self.stop_operation, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.move_btn = ttk.Button(button_frame, text=lang_manager.get_text('duplicate_finder.move_duplicates'), 
                                  command=self.move_duplicates, state="disabled")
        self.move_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text=lang_manager.get_text('duplicate_finder.clear_results'), 
                                   command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Sonuçlar listesi
        results_frame = ttk.LabelFrame(main_frame, text=lang_manager.get_text('duplicate_finder.duplicate_groups'), padding="5")
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ("size", "count", "files")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="tree headings")
        
        # Column headings
        self.results_tree.heading("#0", text=lang_manager.get_text('duplicate_finder.group'))
        self.results_tree.heading("size", text=lang_manager.get_text('duplicate_finder.file_size'))
        self.results_tree.heading("count", text=lang_manager.get_text('duplicate_finder.count'))
        self.results_tree.heading("files", text=lang_manager.get_text('duplicate_finder.files'))
        
        # Column widths
        self.results_tree.column("#0", width=100)
        self.results_tree.column("size", width=100)
        self.results_tree.column("count", width=80)
        self.results_tree.column("files", width=400)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", 
                                   command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient="horizontal", 
                                   command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, 
                                   xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # İstatistikler
        stats_frame = ttk.LabelFrame(main_frame, text=lang_manager.get_text('duplicate_finder.statistics'), padding="5")
        stats_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text=lang_manager.get_text('duplicate_finder.no_scan_performed'))
        self.stats_label.pack()
        
        # Başlangıç durumu
        self.status_var.set(lang_manager.get_text('duplicate_finder.ready_to_scan'))
        
    def select_folder(self):
        """Taranacak klasörü seç"""
        folder = filedialog.askdirectory(title=lang_manager.get_text('duplicate_finder.select_folder'))
        if folder:
            self.selected_folder.set(folder)
            self.clear_results()
            
    def start_scan(self):
        """Duplikat tarama işlemini başlat"""
        if not self.selected_folder.get():
            messagebox.showwarning(lang_manager.get_text('duplicate_finder.warning'), 
                                 lang_manager.get_text('duplicate_finder.select_folder_first'))
            return
        
        if not os.path.exists(self.selected_folder.get()):
            messagebox.showerror(lang_manager.get_text('duplicate_finder.error'), 
                               lang_manager.get_text('duplicate_finder.folder_not_exist'))
            return
        
        # UI durumunu güncelle
        self.is_scanning = True
        self.stop_scanning = False
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.move_btn.configure(state="disabled")
        
        # Progress sıfırla
        self.progress_var.set(0)
        self.status_var.set(lang_manager.get_text('duplicate_finder.starting_scan'))
        
        # Sonuçları temizle
        self.clear_results()
        
        # Thread'de tarama başlat
        self.scan_thread = threading.Thread(target=self._scan_thread, daemon=True)
        self.scan_thread.start()
        
    def _scan_thread(self):
        """Tarama thread'i"""
        try:
            self._update_status(lang_manager.get_text('duplicate_finder.scanning_images'))
            self._update_progress(0)
            
            # Resim dosyalarını bul
            image_files = self._find_image_files()
            
            if self.stop_scanning:
                self._update_status(lang_manager.get_text('duplicate_finder.scan_stopped'))
                self._reset_ui_after_scan()
                return
            
            if not image_files:
                self._update_status(lang_manager.get_text('duplicate_finder.no_images_found'))
                self._reset_ui_after_scan()
                return
                
            self._update_status(f"{lang_manager.get_text('duplicate_finder.images_found')}: {len(image_files)}")
            
            # Duplikatları bul
            duplicates = self._find_duplicates(image_files)
            
            if self.stop_scanning:
                self._update_status(lang_manager.get_text('duplicate_finder.scan_stopped'))
                self._reset_ui_after_scan()
                return
            
            # Sonuçları kaydet
            self.duplicate_groups = duplicates
            self.total_files = len(image_files)
            
            # Duplikat dosya sayısını hesapla
            self.duplicate_files = 0
            self.space_saved = 0
            for group in duplicates:
                # İlk dosya orijinal, diğerleri duplikat
                self.duplicate_files += len(group['files']) - 1
                for file_info in group['files'][1:]:  # İlk dosyayı atla
                    self.space_saved += file_info['size']
            
            # Sonuçları göster
            self._show_results()
            
            self._update_status(f"{lang_manager.get_text('duplicate_finder.scan_completed').format(groups=len(duplicates))}")
            self._update_progress(100)
            
        except Exception as e:
            error_msg = lang_manager.get_text('duplicate_finder.scan_error').format(error=str(e))
            self._update_status(error_msg)
            messagebox.showerror(lang_manager.get_text('duplicate_finder.error'), error_msg)
            
        finally:
            self._reset_ui_after_scan()
        
    def _find_image_files(self):
        """Klasördeki resim dosyalarını bul"""
        image_files = []
        
        try:
            for root, dirs, files in os.walk(self.selected_folder.get()):
                if self.stop_scanning:
                    break
                for file in files:
                    if self.stop_scanning:
                        break
                    if os.path.splitext(file)[1].lower() in self.image_extensions:
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            image_files.append({
                                'path': file_path,
                                'name': file,
                                'size': file_size
                            })
                        except (OSError, IOError):
                            continue
        except Exception as e:
            print(f"Error finding image files: {e}")
            
        return image_files
    
    def _find_duplicates(self, image_files):
        """Duplikat resimleri bul"""
        duplicates = []
        
        # Boyuta göre grupla
        size_groups = {}
        for file_info in image_files:
            if self.stop_scanning:
                break
            size = file_info['size']
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(file_info)
        
        # Hash ile gerçek duplikatları bul
        group_counter = 1
        processed = 0
        
        for size, files in size_groups.items():
            if self.stop_scanning:
                break
                
            if len(files) > 1:  # Aynı boyutta birden fazla dosya var
                hash_groups = {}
                
                for file_info in files:
                    if self.stop_scanning:
                        break
                    
                    file_hash = self._calculate_file_hash(file_info['path'])
                    if file_hash:
                        if file_hash not in hash_groups:
                            hash_groups[file_hash] = []
                        hash_groups[file_hash].append(file_info)
                    
                    processed += 1
                    progress = (processed / len(image_files)) * 100
                    self._update_progress(progress)
                
                # Hash gruplarından duplikatları al
                for hash_value, hash_files in hash_groups.items():
                    if len(hash_files) > 1:
                        duplicates.append({
                            'group_id': group_counter,
                            'files': hash_files,
                            'count': len(hash_files),
                            'method': 'hash'
                        })
                        group_counter += 1
        
        return duplicates
    
    def _show_results(self):
        """Tarama sonuçlarını göster"""
        def update_tree():
            # Mevcut öğeleri temizle
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
                
            # Duplikat gruplarını ekle
            for i, group in enumerate(self.duplicate_groups):
                group_id = f"group_{i}"
                total_size = sum(file_info['size'] for file_info in group['files'])
                size_str = self._format_file_size(total_size)
                
                group_item = self.results_tree.insert("", "end", iid=group_id,
                                              text=f"Duplicate Group {i+1}",
                                              values=(size_str, group['count'], ""))
                
                # Grup içindeki dosyalar
                for j, file_info in enumerate(group['files']):
                    label = lang_manager.get_text('duplicate_finder.original') if j == 0 else lang_manager.get_text('duplicate_finder.duplicate')
                    self.results_tree.insert(group_item, "end",
                                    text=f"  {label}",
                                    values=("", "", file_info['path']))
                                    
                # Grubu genişlet
                self.results_tree.item(group_item, open=True)
        
        # İstatistikleri güncelle
        self._update_statistics()
        
        self.window.after(0, update_tree)
    
    def _update_statistics(self):
        """İstatistikleri güncelle"""
        stats_text = f"{lang_manager.get_text('duplicate_finder.total_files').format(count=self.total_files)}\n"
        stats_text += f"{lang_manager.get_text('duplicate_finder.duplicate_groups_count').format(count=len(self.duplicate_groups))}\n"
        stats_text += f"{lang_manager.get_text('duplicate_finder.duplicate_files_count').format(count=self.duplicate_files)}\n"
        stats_text += f"{lang_manager.get_text('duplicate_finder.space_to_save').format(space=self._format_file_size(self.space_saved))}"
        
        self.stats_label.configure(text=stats_text)
    
    def move_duplicates(self):
        """Duplikat dosyaları taşı"""
        if not self.duplicate_groups:
            messagebox.showwarning(lang_manager.get_text('duplicate_finder.warning'), 
                                 lang_manager.get_text('duplicate_finder.no_duplicates_to_move'))
            return
        
        # Onay iste
        duplicate_count = self.duplicate_files
        space_text = self._format_file_size(self.space_saved)
        
        message = lang_manager.get_text('duplicate_finder.move_confirmation').format(
            count=duplicate_count, space=space_text)
        
        if not messagebox.askyesno(lang_manager.get_text('duplicate_finder.confirm_move'), message):
            return
        
        # UI durumunu güncelle
        self.is_moving = True
        self.move_btn.configure(state="disabled")
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # Thread'de taşıma başlat
        move_thread = threading.Thread(target=self._move_thread, daemon=True)
        move_thread.start()
    
    def _move_thread(self):
        """Taşıma thread'i"""
        try:
            base_folder = self.selected_folder.get()
            duplicates_folder = os.path.join(base_folder, "Duplicates")
            
            # Duplicates klasörü oluştur
            try:
                os.makedirs(duplicates_folder, exist_ok=True)
            except Exception as e:
                error_msg = lang_manager.get_text('duplicate_finder.could_not_create_folder').format(error=str(e))
                self.window.after(0, lambda: messagebox.showerror(lang_manager.get_text('duplicate_finder.error'), error_msg))
                self._reset_ui_after_move()
                return
            
            moved_count = 0
            error_count = 0
            total_to_move = self.duplicate_files
            
            def update_status(moved, total):
                status_text = f"{lang_manager.get_text('duplicate_finder.moving_duplicates')} ({moved}/{total})"
                self.status_var.set(status_text)
                progress = (moved / total) * 100 if total > 0 else 0
                self.progress_var.set(progress)
            
            # Her grup için
            for group in self.duplicate_groups:
                if self.stop_scanning:
                    break
                
                files = group['files']
                
                # Dosyaları taşı (ilk dosya hariç - orijinal)
                for i in range(1, len(files)):
                    if self.stop_scanning:
                        break
                    
                    file_info = files[i]
                    source_path = file_info['path']
                    filename = os.path.basename(source_path)
                    
                    # Hedef dosya yolu
                    target_path = os.path.join(duplicates_folder, filename)
                    
                    # Aynı isimde dosya varsa numara ekle
                    counter = 1
                    while os.path.exists(target_path):
                        name, ext = os.path.splitext(filename)
                        new_filename = f"{name}_{counter}{ext}"
                        target_path = os.path.join(duplicates_folder, new_filename)
                        counter += 1
                    
                    # Dosyayı taşı
                    try:
                        shutil.move(source_path, target_path)
                        moved_count += 1
                        
                        # Progress güncelle
                        self.window.after(0, lambda m=moved_count, t=total_to_move: update_status(m, t))
                        
                    except Exception as e:
                        error_count += 1
                        print(f"Move error: {e}")
            
            # Sonuç mesajı
            if self.stop_scanning:
                result_msg = lang_manager.get_text('duplicate_finder.move_stopped').format(moved=moved_count, errors=error_count)
            else:
                result_msg = lang_manager.get_text('duplicate_finder.move_completed').format(moved=moved_count, errors=error_count)
            
            self.window.after(0, lambda: self.status_var.set(result_msg))
            
            # Detaylı sonuç mesajı
            def show_result():
                if moved_count > 0:
                    message = lang_manager.get_text('duplicate_finder.move_success').format(count=moved_count)
                    if error_count > 0:
                        message += lang_manager.get_text('duplicate_finder.move_errors').format(count=error_count)
                    message += lang_manager.get_text('duplicate_finder.space_saved').format(space=self._format_file_size(self.space_saved))
                    messagebox.showinfo(lang_manager.get_text('duplicate_finder.move_complete'), message)
                elif error_count > 0:
                    message = lang_manager.get_text('duplicate_finder.move_failed').format(errors=error_count)
                    messagebox.showerror(lang_manager.get_text('duplicate_finder.error'), message)
                else:
                    messagebox.showinfo(lang_manager.get_text('duplicate_finder.move_complete'), 
                                      lang_manager.get_text('duplicate_finder.no_action'))
            
            self.window.after(0, show_result)
            
            # Tarama sonuçlarını güncelle
            if moved_count > 0:
                self.window.after(0, self.clear_results)
            
        except Exception as e:
            error_msg = lang_manager.get_text('duplicate_finder.move_error').format(error=str(e))
            self.window.after(0, lambda: messagebox.showerror(lang_manager.get_text('duplicate_finder.error'), error_msg))
        
        finally:
            self._reset_ui_after_move()
    
    def _calculate_file_hash(self, file_path, chunk_size=8192):
        """Dosya hash'ini hesapla"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return None
    
    def _reset_ui_after_scan(self):
        """Tarama sonrası UI durumunu sıfırla"""
        def reset():
            self.is_scanning = False
            self.scan_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            if self.duplicate_groups:
                self.move_btn.configure(state="normal")
        
        self.window.after(0, reset)
    
    def _reset_ui_after_move(self):
        """Taşıma sonrası UI durumunu sıfırla"""
        def reset():
            self.is_moving = False
            self.move_btn.configure(state="normal")
            self.scan_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
        
        self.window.after(0, reset)
    
    def clear_results(self):
        """Sonuçları temizle"""
        self.duplicate_groups = {}
        self.total_files = 0
        self.duplicate_files = 0
        self.space_saved = 0
        
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.move_btn.configure(state='disabled')
        self.stats_label.configure(text=lang_manager.get_text('duplicate_finder.no_scan_performed'))
        self.status_var.set(lang_manager.get_text('duplicate_finder.ready_to_scan'))
        self.progress_var.set(0)
    
    def _format_file_size(self, size_bytes):
        """Dosya boyutunu okunabilir formata çevir"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _update_status(self, message):
        """Status mesajını güncelle"""
        def update():
            self.status_var.set(message)
        self.window.after(0, update)
    
    def _update_progress(self, progress):
        """Progress bar'ı güncelle"""
        def update():
            self.progress_var.set(progress)
        self.window.after(0, update)
    
    def close_window(self):
        """Pencereyi kapat"""
        if self.is_scanning or self.is_moving:
            if messagebox.askyesno(lang_manager.get_text('duplicate_finder.confirm_close'), 
                                 lang_manager.get_text('duplicate_finder.operation_in_progress')):
                self.stop_scanning = True
                self.is_moving = False
                if self.window:
                    self.window.destroy()
        else:
            if self.window:
                self.window.destroy()

    def stop_operation(self):
        """Taramayı veya taşımayı durdur"""
        self.stop_scanning = True
        if self.is_scanning:
            self.status_var.set(lang_manager.get_text('duplicate_finder.stopping_scan'))
        elif self.is_moving:
            self.status_var.set(lang_manager.get_text('duplicate_finder.stopping_move'))
        else:
            self.status_var.set(lang_manager.get_text('duplicate_finder.stopping_operation'))
        self.stop_btn.configure(state="disabled") 