"""
File Operations Module
Dosya yönetimi işlemlerini içerir
"""

import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from pathlib import Path
import json
import hashlib
import time
import stat
from collections import defaultdict

class FileOperations:
    def __init__(self, gui_manager):
        self.gui = gui_manager
        self.target_path = "D:/"  # Default hedef klasör
        self.source_path = ""
        self.current_path = self.target_path
        self.navigation_history = []
        self.history_index = -1
        self.clipboard = []
        self.clipboard_operation = None  # 'copy' veya 'cut'
        self.sort_column = None
        self.sort_reverse = False
        
        # Dosya kategorileri
        self.file_categories = self.get_file_categories()
        
        # GUI değişkenlerini güncelle
        self.gui.target_var.set(self.target_path)
        self.gui.current_path_var.set(self.current_path)
        
        # Ayarları yükle
        self.load_settings()
        
        # Drag & Drop verisi
        self.drag_data = {"item": None, "x": 0, "y": 0}
        
        # İlk yükleme
        self.refresh_target()
        
        # Drag & Drop özelliğini ayarla
        self.setup_drag_drop()
        
        # Target tree'ye focus ver
        self.gui.target_tree.focus_set()
        
    def get_file_categories(self):
        """Dosya kategorilerini tanımla"""
        return {
            'images': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico'],
                'folder': 'Resimler',
                'subfolders': {
                    '.jpg': 'JPG', '.jpeg': 'JPG', '.png': 'PNG', '.gif': 'GIF',
                    '.bmp': 'BMP', '.tiff': 'TIFF', '.webp': 'WEBP', '.svg': 'SVG', '.ico': 'ICO'
                }
            },
            'documents': {
                'extensions': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
                'folder': 'Belgeler',
                'subfolders': {
                    '.pdf': 'PDF', '.doc': 'DOC', '.docx': 'DOCX', '.txt': 'Metin', '.rtf': 'RTF', '.odt': 'ODT'
                }
            },
            'spreadsheets': {
                'extensions': ['.xls', '.xlsx', '.csv', '.ods'],
                'folder': 'Excel',
                'subfolders': {
                    '.xls': 'XLS', '.xlsx': 'XLSX', '.csv': 'CSV', '.ods': 'ODS'
                }
            },
            'archives': {
                'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz'],
                'folder': 'Arsiv',
                'subfolders': {
                    '.zip': 'ZIP', '.rar': 'RAR', '.7z': '7Z', '.tar': 'TAR', '.gz': 'GZ'
                }
            },
            'programs': {
                'extensions': ['.exe', '.msi', '.deb', '.rpm', '.dmg'],
                'folder': 'Programlar',
                'subfolders': {
                    '.exe': 'EXE', '.msi': 'MSI', '.deb': 'DEB', '.rpm': 'RPM', '.dmg': 'DMG'
                }
            },
            'cad': {
                'extensions': ['.dwg', '.dxf', '.step', '.iges'],
                'folder': 'CAD',
                'subfolders': {
                    '.dwg': 'DWG', '.dxf': 'DXF', '.step': 'STEP', '.iges': 'IGES'
                }
            },
            'video': {
                'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
                'folder': 'Videolar',
                'subfolders': {
                    '.mp4': 'MP4', '.avi': 'AVI', '.mkv': 'MKV', '.mov': 'MOV', '.wmv': 'WMV', '.flv': 'FLV'
                }
            },
            'audio': {
                'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
                'folder': 'Muzik',
                'subfolders': {
                    '.mp3': 'MP3', '.wav': 'WAV', '.flac': 'FLAC', '.aac': 'AAC', '.ogg': 'OGG'
                }
            }
        }
    
    def get_file_category(self, file_path):
        """Dosyanın kategorisini belirle"""
        file_ext = Path(file_path).suffix.lower()
        
        for category, info in self.file_categories.items():
            if file_ext in info['extensions']:
                return category, info
        
        # Bilinmeyen uzantı için otomatik kategori oluştur
        if file_ext:
            folder_name = f"{file_ext.replace('.', '').upper()}"
            auto_category = {
                'extensions': [file_ext],
                'folder': folder_name,
                'subfolders': {file_ext: file_ext.replace('.', '').upper()}
            }
            return 'unknown', auto_category
        else:
            # Uzantısız dosyalar
            return 'unknown', {
                'extensions': [''],
                'folder': 'Uzantisiz_Dosyalar',
                'subfolders': {'': 'Uzantisiz'}
            }
    
    def select_source_folder(self):
        """Kaynak klasör seçimi"""
        folder = filedialog.askdirectory(title="Kaynak Klasör Seçin")
        if folder:
            self.source_path = folder
            self.gui.source_var.set(folder)
            self.gui.status_var.set(f"Kaynak klasör seçildi: {folder}")
            
            # Kaynak tree'yi temizle
            self.gui.source_tree.delete(*self.gui.source_tree.get_children())
        else:
            self.gui.status_var.set("Kaynak klasör seçimi iptal edildi.")
    
    def select_target_folder(self):
        """Hedef klasör seçimi"""
        folder = filedialog.askdirectory(title="Hedef SSD Seçin", initialdir=self.target_path)
        if folder:
            self.target_path = folder
            self.current_path = folder
            self.gui.target_var.set(folder)
            self.gui.current_path_var.set(folder)
            
            # Ayarları kaydet
            self.save_settings()
            
            # Hedef klasörü yenile
            self.refresh_target()
            self.gui.status_var.set(f"Hedef klasör değiştirildi: {folder}")
        else:
            self.gui.status_var.set("Hedef klasör seçimi iptal edildi.")
    
    def add_to_history(self, path):
        """Navigasyon geçmişine ekle"""
        if self.history_index < len(self.navigation_history) - 1:
            self.navigation_history = self.navigation_history[:self.history_index + 1]
        
        if not self.navigation_history or self.navigation_history[-1] != path:
            self.navigation_history.append(path)
            self.history_index = len(self.navigation_history) - 1
    
    def go_back(self):
        """Geri git"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.navigation_history[self.history_index]
            self.gui.current_path_var.set(self.current_path)
            self.refresh_target(add_to_history=False)
    
    def go_up(self):
        """Üst klasöre git"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.current_path = parent
            self.gui.current_path_var.set(parent)
            self.refresh_target()
    
    def go_home(self):
        """Ana klasöre git"""
        self.current_path = self.target_path
        self.gui.current_path_var.set(self.target_path)
        self.refresh_target()
    
    def navigate_to_path(self, event=None):
        """Belirtilen yola git"""
        path = self.gui.current_path_var.get()
        if os.path.exists(path) and os.path.isdir(path):
            self.current_path = path
            self.refresh_target()
        else:
            messagebox.showerror("Hata", "Geçersiz klasör yolu!")
            self.gui.current_path_var.set(self.current_path)
    
    def refresh_target(self, add_to_history=True):
        """Hedef klasörü yenile"""
        # Geçerli yol kontrolü
        if not os.path.exists(self.current_path):
            self.current_path = self.target_path
            self.gui.current_path_var.set(self.current_path)
        
        if add_to_history:
            self.add_to_history(self.current_path)
        
        # Tree'yi temizle
        self.gui.target_tree.delete(*self.gui.target_tree.get_children())
        
        try:
            items = []
            
            # Klasörleri ekle
            for item in os.listdir(self.current_path):
                if self.is_hidden_file(item):
                    continue
                    
                item_path = os.path.join(self.current_path, item)
                
                if os.path.isdir(item_path):
                    try:
                        modified_time = self.get_modified_time(item_path)
                        items.append((item, "📁 Klasör", "", modified_time, item_path, True))
                    except:
                        items.append((item, "📁 Klasör", "", "Bilinmiyor", item_path, True))
            
            # Dosyaları ekle
            for item in os.listdir(self.current_path):
                if self.is_hidden_file(item):
                    continue
                    
                item_path = os.path.join(self.current_path, item)
                
                if os.path.isfile(item_path):
                    try:
                        file_size = os.path.getsize(item_path)
                        file_ext = Path(item_path).suffix.upper()
                        modified_time = self.get_modified_time(item_path)
                        items.append((item, file_ext, self.format_size(file_size), modified_time, item_path, False))
                    except:
                        items.append((item, "Dosya", "Bilinmiyor", "Bilinmiyor", item_path, False))
            
            # Sıralama uygula
            if self.sort_column:
                items.sort(key=self.get_sort_key, reverse=self.sort_reverse)
            
            # Tree'ye ekle
            for item_name, item_type, size, modified, full_path, is_dir in items:
                self.gui.target_tree.insert('', 'end', text=item_name, 
                                          values=(size, item_type, modified),
                                          tags=('directory' if is_dir else 'file',))
            
            self.gui.status_var.set(f"📁 {len([i for i in items if i[5]])} klasör, 📄 {len([i for i in items if not i[5]])} dosya")
            
        except PermissionError:
            messagebox.showerror("Hata", "Bu klasöre erişim izniniz yok!")
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör yüklenirken hata: {e}")
    
    def get_modified_time(self, file_path):
        """Dosya değiştirilme zamanını al"""
        try:
            import time
            timestamp = os.path.getmtime(file_path)
            return time.strftime("%d.%m.%Y %H:%M", time.localtime(timestamp))
        except:
            return "Bilinmiyor"
    
    def is_hidden_file(self, filename, file_path=None):
        """Gizli dosya kontrolü - Ana programdan alındı"""
        # Windows gizli dosyaları
        if filename.startswith('.'):
            return True
        
        # Sistem dosyaları
        system_files = [
            'thumbs.db', 'desktop.ini', 'folder.jpg', 'folder.png',
            'albumartsmall.jpg', 'albumart_{', '.ds_store',
            'system volume information', '$recycle.bin', 'recycler',
            'pagefile.sys', 'hiberfil.sys', 'swapfile.sys'
        ]
        
        if filename.lower() in system_files:
            return True
        
        # Geçici dosyalar
        temp_extensions = ['.tmp', '.temp', '.bak', '.old', '.cache', '.log']
        if any(filename.lower().endswith(ext) for ext in temp_extensions):
            return True
        
        # Windows gizli dosya attribute kontrolü
        if file_path and os.path.exists(file_path):
            try:
                import stat
                file_stat = os.stat(file_path)
                # Windows'ta gizli dosya kontrolü
                if hasattr(stat, 'FILE_ATTRIBUTE_HIDDEN'):
                    return bool(file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
            except:
                pass
        
        return False
    
    def format_size(self, size_bytes):
        """Dosya boyutunu formatla"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def get_sort_key(self, item):
        """Sıralama anahtarı"""
        item_name, item_type, size, modified, full_path, is_dir = item
        
        if self.sort_column == '#0':  # İsim
            return (not is_dir, item_name.lower())
        elif self.sort_column == 'size':  # Boyut
            if is_dir:
                return (0, item_name.lower())
            try:
                return (1, self.parse_size_string(size))
            except:
                return (1, 0)
        elif self.sort_column == 'type':  # Tür
            return (not is_dir, item_type.lower())
        elif self.sort_column == 'modified':  # Değiştirilme
            return (not is_dir, modified)
        
        return (not is_dir, item_name.lower())
    
    def parse_size_string(self, size_str):
        """Boyut string'ini sayıya çevir"""
        if not size_str or size_str == "":
            return 0
        
        try:
            parts = size_str.split()
            if len(parts) != 2:
                return 0
            
            number = float(parts[0])
            unit = parts[1].upper()
            
            multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
            return number * multipliers.get(unit, 1)
        except:
            return 0
    
    def sort_tree(self, column):
        """Tree sıralama"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        self.refresh_target(add_to_history=False)
    
    def on_target_double_click(self, event):
        """Çift tıklama olayı"""
        selection = self.gui.target_tree.selection()
        if not selection:
            return
        
        item = self.gui.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_path, item_name)
        
        print(f"🖱️ Çift tıklama: {item_name} -> {item_path}")
        
        if os.path.isdir(item_path):
            # Klasöre gir
            print(f"📁 Klasöre giriliyor: {item_path}")
            self.add_to_history(self.current_path)
            self.current_path = item_path
            self.gui.current_path_var.set(item_path)
            self.refresh_target(add_to_history=False)
        else:
            # Dosyayı aç
            try:
                print(f"📄 Dosya açılıyor: {item_path}")
                os.startfile(item_path)
            except Exception as e:
                print(f"❌ Dosya açma hatası: {e}")
                messagebox.showerror("Hata", f"Dosya açılamadı: {e}")
    
    def show_context_menu(self, event):
        """Sağ tık menüsü"""
        try:
            # Seçili öğeyi belirle
            item = self.gui.target_tree.identify_row(event.y)
            if item:
                self.gui.target_tree.selection_set(item)
                
            # Sağ tık menüsü oluştur
            context_menu = tk.Menu(self.gui.root, tearoff=0)
            
            selection = self.gui.target_tree.selection()
            
            if selection:
                # Dosya/klasör seçili
                context_menu.add_command(label="🔓 Aç", command=self.open_selected)
                context_menu.add_command(label="🔍 Dosya Konumunu Aç", command=self.open_file_location)
                context_menu.add_separator()
                context_menu.add_command(label="📋 Kopyala (Ctrl+C)", command=self.copy_selected)
                context_menu.add_command(label="✂️ Kes (Ctrl+X)", command=self.cut_selected)
                
                # Yapıştırma - pano doluysa aktif
                paste_state = tk.NORMAL if self.clipboard else tk.DISABLED
                context_menu.add_command(label="📁 Yapıştır (Ctrl+V)", command=self.paste_selected, state=paste_state)
                
                context_menu.add_separator()
                context_menu.add_command(label="🗑️ Sil (Del)", command=self.delete_selected)
                context_menu.add_command(label="✏️ Yeniden Adlandır (F2)", command=self.rename_selected)
                context_menu.add_separator()
                
                # Tek dosya seçiliyse ek seçenekler
                if len(selection) == 1:
                    item_data = self.gui.target_tree.item(selection[0])
                    item_name = item_data['text'].replace("📁 ", "").replace("📄 ", "")
                    item_path = os.path.join(self.current_path, item_name)
                    
                    if os.path.isfile(item_path):
                        context_menu.add_command(label="📊 Dosya Bilgileri", command=self.show_file_info)
                        context_menu.add_command(label="🔄 Dosya Hash", command=self.show_file_hash)
                    
                context_menu.add_command(label="📋 Özellikler", command=self.show_properties)
            else:
                # Boş alan
                context_menu.add_command(label="📁 Yapıştır (Ctrl+V)", command=self.paste_selected, 
                                       state=tk.NORMAL if self.clipboard else tk.DISABLED)
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
    
    def get_selected_items(self):
        """Seçili öğeleri al"""
        selection = self.gui.target_tree.selection()
        items = []
        
        for item in selection:
            item_data = self.gui.target_tree.item(item)
            item_text = item_data['text'].replace("📁 ", "").replace("📄 ", "")
            item_path = os.path.join(self.current_path, item_text)
            items.append(item_path)
        
        return items
    
    def delete_selected(self):
        """Seçili dosyaları sil"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Uyarı", "Silinecek dosya seçin!")
            return
        
        # Onay al
        if len(items) == 1:
            message = f"'{os.path.basename(items[0])}' dosyasını silmek istediğinizden emin misiniz?"
        else:
            message = f"{len(items)} dosyayı silmek istediğinizden emin misiniz?"
        
        if not messagebox.askyesno("Silme Onayı", message):
            return
        
        # Sil
        deleted_count = 0
        for item_path in items:
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                deleted_count += 1
            except Exception as e:
                messagebox.showerror("Hata", f"'{os.path.basename(item_path)}' silinemedi: {e}")
        
        if deleted_count > 0:
            self.gui.status_var.set(f"{deleted_count} öğe silindi.")
            self.refresh_target(add_to_history=False)
    
    def copy_selected(self):
        """Seçili dosyaları kopyala"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Uyarı", "Kopyalanacak dosya seçin!")
            return
        
        self.clipboard = items
        self.clipboard_operation = 'copy'
        self.gui.status_var.set(f"{len(items)} öğe kopyalandı.")
    
    def cut_selected(self):
        """Seçili dosyaları kes"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Uyarı", "Kesilecek dosya seçin!")
            return
        
        self.clipboard = items
        self.clipboard_operation = 'cut'
        self.gui.status_var.set(f"{len(items)} öğe kesildi.")
    
    def paste_selected(self):
        """Dosyaları yapıştır"""
        if not self.clipboard:
            messagebox.showwarning("Uyarı", "Yapıştırılacak dosya yok!")
            return
        
        pasted_count = 0
        for source_path in self.clipboard:
            try:
                filename = os.path.basename(source_path)
                target_path = os.path.join(self.current_path, filename)
                
                # Aynı isimde dosya varsa numara ekle
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while os.path.exists(target_path):
                    new_name = f"{base_name}_{counter}{ext}"
                    target_path = os.path.join(self.current_path, new_name)
                    counter += 1
                
                if self.clipboard_operation == 'copy':
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, target_path)
                    else:
                        shutil.copy2(source_path, target_path)
                elif self.clipboard_operation == 'cut':
                    shutil.move(source_path, target_path)
                
                pasted_count += 1
                
            except Exception as e:
                messagebox.showerror("Hata", f"'{os.path.basename(source_path)}' yapıştırılamadı: {e}")
        
        if self.clipboard_operation == 'cut':
            self.clipboard = []
            self.clipboard_operation = None
        
        if pasted_count > 0:
            self.gui.status_var.set(f"{pasted_count} öğe yapıştırıldı.")
            self.refresh_target(add_to_history=False)
    
    def create_folder(self):
        """Yeni klasör oluştur"""
        folder_name = simpledialog.askstring("Yeni Klasör", "Klasör adını girin:")
        if folder_name:
            folder_path = os.path.join(self.current_path, folder_name)
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.gui.status_var.set(f"'{folder_name}' klasörü oluşturuldu.")
                self.refresh_target(add_to_history=False)
            except Exception as e:
                messagebox.showerror("Hata", f"Klasör oluşturulamadı: {e}")
    
    def open_selected(self):
        """Seçili dosyayı aç veya klasöre gir"""
        selection = self.gui.target_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Açılacak dosya/klasör seçin!")
            return
        
        # İlk seçili öğeyi al
        item = self.gui.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_path, item_name)
        
        if os.path.isdir(item_path):
            # Klasöre gir
            self.add_to_history(self.current_path)
            self.current_path = item_path
            self.gui.current_path_var.set(item_path)
            self.refresh_target(add_to_history=False)
        else:
            # Dosyayı aç
            try:
                os.startfile(item_path)
            except Exception as e:
                messagebox.showerror("Hata", f"'{item_name}' açılamadı: {e}")
    
    def rename_selected(self):
        """Seçili dosyayı yeniden adlandır"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Uyarı", "Yeniden adlandırılacak dosya seçin!")
            return
        
        if len(items) > 1:
            messagebox.showwarning("Uyarı", "Tek dosya seçin!")
            return
        
        old_path = items[0]
        old_name = os.path.basename(old_path)
        
        new_name = simpledialog.askstring("Yeniden Adlandır", "Yeni adı girin:", initialvalue=old_name)
        if new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.gui.status_var.set(f"'{old_name}' -> '{new_name}' olarak değiştirildi.")
                self.refresh_target(add_to_history=False)
            except Exception as e:
                messagebox.showerror("Hata", f"Yeniden adlandırılamadı: {e}")
    
    def show_properties(self):
        """Dosya özelliklerini göster"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Uyarı", "Özelliklerini görmek istediğiniz dosyayı seçin!")
            return
        
        if len(items) > 1:
            messagebox.showwarning("Uyarı", "Tek dosya seçin!")
            return
        
        file_path = items[0]
        try:
            stat = os.stat(file_path)
            import time
            
            properties = f"""Dosya Özellikleri:
            
Adı: {os.path.basename(file_path)}
Yol: {file_path}
Boyut: {self.format_size(stat.st_size)}
Oluşturulma: {time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(stat.st_ctime))}
Değiştirilme: {time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(stat.st_mtime))}
Erişim: {time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(stat.st_atime))}
Tür: {"Klasör" if os.path.isdir(file_path) else "Dosya"}
"""
            
            messagebox.showinfo("Özellikler", properties)
        except Exception as e:
            messagebox.showerror("Hata", f"Özellikler alınırken hata: {e}")
    
    def get_file_hash(self, file_path):
        """Dosya hash'ini hesapla - Ana programdan alındı"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return f"Hata: {e}"
    
    def is_file_locked(self, file_path):
        """Dosya kilitli mi kontrol et"""
        try:
            with open(file_path, 'r+b'):
                return False
        except (IOError, OSError):
            return True
    
    def copy_file_optimized(self, source_path, target_path):
        """Optimize edilmiş dosya kopyalama"""
        try:
            # Dosya kilitli mi kontrol et
            if self.is_file_locked(source_path):
                return False, "Dosya kullanımda"
            
            # Büyük dosyalar için chunk-based kopyalama
            file_size = os.path.getsize(source_path)
            if file_size > 50 * 1024 * 1024:  # 50MB'dan büyükse
                return self.copy_file_chunked(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
                return True, "Başarılı"
        except Exception as e:
            return False, str(e)
    
    def copy_file_chunked(self, source_path, target_path):
        """Chunk-based dosya kopyalama"""
        try:
            chunk_size = 1024 * 1024  # 1MB chunks
            with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
            return True, "Başarılı"
        except Exception as e:
            return False, str(e)
    
    def load_settings(self):
        """Ayarları yükle"""
        try:
            if os.path.exists('file_manager_settings.json'):
                with open('file_manager_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Son hedef klasörü yükle
                if 'target_path' in settings:
                    self.target_path = settings['target_path']
                    self.current_path = self.target_path
                    self.gui.target_var.set(self.target_path)
                    self.gui.current_path_var.set(self.current_path)
                    
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            settings = {
                'target_path': self.target_path,
                'current_path': self.current_path
            }
            
            with open('file_manager_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
    
    def setup_drag_drop(self):
        """Sürükleyip bırakma özelliğini ayarla"""
        # Sürükleme başlangıcı
        self.gui.target_tree.bind('<Button-1>', self.on_drag_start)
        self.gui.target_tree.bind('<B1-Motion>', self.on_drag_motion)
        self.gui.target_tree.bind('<ButtonRelease-1>', self.on_drag_end)
        
    def on_drag_start(self, event):
        """Sürükleme başlangıcı"""
        item = self.gui.target_tree.identify_row(event.y)
        if item:
            self.drag_data["item"] = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            # İlk sürükleme cursor'u
            self.gui.target_tree.config(cursor="hand2")
            
    def on_drag_motion(self, event):
        """Sürükleme hareketi"""
        if self.drag_data["item"]:
            # Sürüklenen öğeyi vurgula
            self.gui.target_tree.selection_set(self.drag_data["item"])
            
            # Cursor'ı taşıma ikonu yap
            self.gui.target_tree.config(cursor="fleur")  # Taşıma cursor'u
            
            # Hedef kontrolü - eğer klasör üzerindeyse farklı cursor
            target_item = self.gui.target_tree.identify_row(event.y)
            if target_item and target_item != self.drag_data["item"]:
                target_item_data = self.gui.target_tree.item(target_item)
                target_name = target_item_data['text'].replace("📁 ", "").replace("📄 ", "")
                target_path = os.path.join(self.current_path, target_name)
                
                if os.path.isdir(target_path):
                    self.gui.target_tree.config(cursor="dotbox")  # Hedef klasör cursor'u
                else:
                    self.gui.target_tree.config(cursor="X_cursor")  # Geçersiz hedef
            
    def on_drag_end(self, event):
        """Sürükleme bitişi"""
        if not self.drag_data["item"]:
            return
            
        # Hedef öğeyi bul
        target_item = self.gui.target_tree.identify_row(event.y)
        
        if target_item and target_item != self.drag_data["item"]:
            source_item = self.gui.target_tree.item(self.drag_data["item"])
            target_item_data = self.gui.target_tree.item(target_item)
            
            source_name = source_item['text'].replace("📁 ", "").replace("📄 ", "")
            target_name = target_item_data['text'].replace("📁 ", "").replace("📄 ", "")
            
            source_path = os.path.join(self.current_path, source_name)
            target_path = os.path.join(self.current_path, target_name)
            
            # Hedef bir klasör mü kontrol et
            if os.path.isdir(target_path):
                self.move_file_to_folder(source_path, target_path)
        
        # Sürükleme verilerini temizle
        self.drag_data = {"item": None, "x": 0, "y": 0}
        
        # Cursor'ı normale döndür
        self.gui.target_tree.config(cursor="")
        
    def move_file_to_folder(self, source_path, target_folder):
        """Dosya/klasörü hedef klasöre taşı"""
        source_name = os.path.basename(source_path)
        is_folder = os.path.isdir(source_path)
        
        try:
            if is_folder:
                # Klasör taşıma için özel dialog
                choice = self._ask_folder_move_method(source_name, target_folder)
                if choice == "cancel":
                    return
                elif choice == "complete":
                    self._move_complete_folder(source_path, target_folder)
                elif choice == "categorize":
                    self._move_folder_with_categorization(source_path, target_folder)
            else:
                # Normal dosya taşıma - basit onay dialog'u
                message = f"'{source_name}' dosyasını '{os.path.basename(target_folder)}' klasörüne taşımak istiyor musunuz?"
                if messagebox.askyesno("Taşıma Onayı", message):
                    self._move_single_file(source_path, target_folder)
                else:
                    return
            
            self.refresh_target()
            self.gui.status_var.set(f"'{source_name}' başarıyla taşındı.")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Taşıma hatası: {e}")
    
    def _ask_folder_move_method(self, source_name, target_folder):
        """Klasör taşıma yöntemi için kullanıcıya sor"""
        import tkinter as tk
        from tkinter import ttk
        
        # Özel dialog oluştur
        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Klasör Taşıma Yöntemi")
        dialog.geometry("650x500")
        dialog.transient(self.gui.root)
        dialog.grab_set()
        
        # Dialog'u merkeze yerleştir
        dialog.geometry("+%d+%d" % (self.gui.root.winfo_rootx() + 50, self.gui.root.winfo_rooty() + 50))
        
        result = {"choice": "cancel"}  # Default
        
        # İçerik
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ttk.Label(main_frame, text=f"📁 '{source_name}' klasörünü nasıl taşımak istiyorsunuz?", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Hedef bilgisi
        target_label = ttk.Label(main_frame, text=f"🎯 Hedef: {os.path.basename(target_folder)}", font=("Arial", 10))
        target_label.pack(pady=(0, 20))
        
        # Seçenekler
        option_frame = ttk.Frame(main_frame)
        option_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Radio button değişkeni
        choice_var = tk.StringVar(value="complete")
        
        # Seçenek 1: Komple taşı
        complete_frame = ttk.LabelFrame(option_frame, text="🗂️ Klasörü Komple Taşı", padding=15)
        complete_frame.pack(fill=tk.X, pady=(0, 15))
        
        complete_radio = ttk.Radiobutton(complete_frame, text="Bu seçeneği seç", 
                                       variable=choice_var, value="complete")
        complete_radio.pack(anchor=tk.W)
        
        ttk.Label(complete_frame, text="• Klasör yapısını korur\n• Tüm alt klasörler ve dosyalar olduğu gibi taşınır\n• Hızlı işlem", 
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(8, 0))
        
        # Seçenek 2: Kategorilere göre organize et
        categorize_frame = ttk.LabelFrame(option_frame, text="📂 İçeriği Kategorilere Göre Organize Et", padding=15)
        categorize_frame.pack(fill=tk.X)
        
        categorize_radio = ttk.Radiobutton(categorize_frame, text="Bu seçeneği seç", 
                                         variable=choice_var, value="categorize")
        categorize_radio.pack(anchor=tk.W)
        
        ttk.Label(categorize_frame, text="• Dosyalar uzantılarına göre kategorilere ayrılır\n• Mevcut klasör yapısı ile birleştirilir\n• Duplikat kontrolü yapılır", 
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(8, 0))
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(40, 0))
        
        def on_ok():
            result["choice"] = choice_var.get()
            dialog.destroy()
            
        def on_cancel():
            result["choice"] = "cancel"
            dialog.destroy()
        
        # Butonları daha büyük ve görünür yap
        ok_button = ttk.Button(button_frame, text="✅ Tamam", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=(0, 30), ipadx=25, ipady=8)
        
        cancel_button = ttk.Button(button_frame, text="❌ İptal", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, ipadx=25, ipady=8)
        
        # Enter ve Escape tuş bağlamaları
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        # Focus ayarla
        ok_button.focus_set()
        
        # Dialog'u bekle
        dialog.wait_window()
        
        return result["choice"]
    
    def _move_complete_folder(self, source_path, target_folder):
        """Klasörü komple taşı (yapıyı koru)"""
        folder_name = os.path.basename(source_path)
        target_path = os.path.join(target_folder, folder_name)
        
        # Aynı isimde klasör varsa numara ekle
        counter = 1
        base_target = target_path
        while os.path.exists(target_path):
            target_path = f"{base_target}_{counter}"
            counter += 1
        
        # Klasörü taşı
        shutil.move(source_path, target_path)
        print(f"📁 Klasör komple taşındı: {source_path} -> {target_path}")
    
    def _move_single_file(self, source_path, target_folder):
        """Tek dosyayı taşı"""
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
    
    def _move_folder_with_categorization(self, source_folder, target_folder):
        """Klasörü kategorilere göre organize ederek taşı"""
        print(f"🗂️ Klasör kategorilere göre taşınıyor: {source_folder} -> {target_folder}")
        
        # Hedef klasör analizi yap (kaynak klasörü hariç tut)
        target_analysis = self._analyze_target_folders_for_move(target_folder, exclude_folder=source_folder)
        
        # Klasördeki tüm dosyaları tara
        files_to_move = []
        
        for root, dirs, files in os.walk(source_folder):
            # Gizli klasörleri atla
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):  # Gizli dosyaları atla
                    file_path = os.path.join(root, file)
                    files_to_move.append(file_path)
        
        print(f"📊 Taşınacak dosya sayısı: {len(files_to_move)}")
        
        # Dosyaları kategorilerine göre organize et
        moved_count = 0
        duplicate_count = 0
        
        for file_path in files_to_move:
            try:
                # Dosya kategorisini belirle
                category, category_info = self.get_file_category(file_path)
                file_ext = os.path.splitext(file_path)[1].lower()
                
                # Hedef klasörde uygun klasör var mı kontrol et
                suggested_folder = self._find_suitable_target_folder_for_move(file_ext, target_analysis)
                
                if suggested_folder:
                    # Mevcut klasör bulundu - doğrudan o klasöre yerleştir
                    final_target_folder = suggested_folder
                    print(f"📁 {file_ext} dosyası mevcut klasöre yerleştirilecek: {suggested_folder}")
                else:
                    # Standart kategori kullan - yeni klasör oluştur
                    category_folder = os.path.join(target_folder, category_info['folder'])
                    
                    # Alt kategori klasörü
                    subfolder = file_ext.replace('.', '').upper() if file_ext else 'Uzantisiz'
                    final_target_folder = os.path.join(category_folder, subfolder)
                    print(f"📁 {file_ext} dosyası yeni kategori klasörüne yerleştirilecek: {category_info['folder']}/{subfolder}")
                
                # Klasörleri oluştur
                os.makedirs(final_target_folder, exist_ok=True)
                
                # Dosya adı ve hedef yol
                file_name = os.path.basename(file_path)
                target_file_path = os.path.join(final_target_folder, file_name)
                
                # Gelişmiş duplikat kontrolü
                duplicate_found = self._check_for_duplicates_in_target(file_path, final_target_folder)
                
                if duplicate_found:
                    # Duplikat dosya bulundu
                    if self._handle_duplicate_file(file_path, duplicate_found):
                        moved_count += 1
                    else:
                        duplicate_count += 1
                        print(f"⏭️ Duplikat atlandı: {file_name}")
                else:
                    # Dosyayı taşı
                    shutil.move(file_path, target_file_path)
                    moved_count += 1
                    print(f"✅ Taşındı: {file_name} -> {final_target_folder}")
                
            except Exception as e:
                print(f"❌ Hata: {file_path} taşınamadı - {e}")
                continue
        
        # Kaynak klasörü sil (boşsa)
        try:
            if not os.listdir(source_folder):
                os.rmdir(source_folder)
                print(f"🗑️ Boş kaynak klasör silindi: {source_folder}")
        except:
            pass
        
        print(f"📈 Sonuç: {moved_count} dosya taşındı, {duplicate_count} duplikat atlandı")
    
    def _analyze_target_folders_for_move(self, target_folder, exclude_folder=None):
        """Hedef klasördeki mevcut klasörleri analiz et (drag & drop için)"""
        folder_analysis = {}
        
        if not os.path.exists(target_folder):
            return folder_analysis
        
        print("🔍 Hedef klasör analizi başlatılıyor...")
        
        # Sistem klasörlerini hariç tut
        system_folders = {
            'system volume information', '$recycle.bin', 'recycler',
            'windows', 'program files', 'program files (x86)', 'programdata',
            'users', 'temp', 'tmp', 'cache', '.git', '.svn', 'node_modules',
            '__pycache__', '.vscode', '.idea'
        }
        
        try:
            # Tüm klasörleri recursive olarak analiz et (3 seviye derinlik)
            for root, dirs, files in os.walk(target_folder):
                # Derinlik kontrolü
                current_level = root.count(os.sep) - target_folder.count(os.sep)
                if current_level >= 3:
                    dirs.clear()  # Daha derine inme
                    continue
                
                # Gizli ve sistem klasörlerini atla
                dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in system_folders]
                
                # Kaynak klasörü hariç tut
                if exclude_folder and os.path.exists(exclude_folder):
                    try:
                        if os.path.samefile(root, exclude_folder):
                            print(f"⏭️ Kaynak klasör atlandı: {os.path.basename(root)}")
                            dirs.clear()  # Alt klasörlerini de atla
                            continue
                    except:
                        if os.path.basename(root) == os.path.basename(exclude_folder):
                            print(f"⏭️ Kaynak klasör atlandı: {os.path.basename(root)}")
                            dirs.clear()
                            continue
                
                # Bu klasörde dosya var mı kontrol et
                folder_extensions = {}
                for file in files:
                    if not file.startswith('.'):
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext:
                            if file_ext not in folder_extensions:
                                folder_extensions[file_ext] = 0
                            folder_extensions[file_ext] += 1
                
                # Eğer bu klasörde dosya varsa analiz sonuçlarına ekle
                if folder_extensions and root != target_folder:
                    # Relative path oluştur
                    rel_path = os.path.relpath(root, target_folder)
                    folder_analysis[rel_path] = {
                        'path': root,
                        'extensions': folder_extensions,
                        'file_count': len(folder_extensions)
                    }
                    print(f"📂 {rel_path}: {list(folder_extensions.keys())} uzantıları bulundu")
        
        except Exception as e:
            print(f"❌ Hedef klasör analizi hatası: {e}")
        
        return folder_analysis
    
    def _analyze_folder_extensions_for_move(self, folder_path, max_depth=5):
        """Klasördeki dosya uzantılarını analiz et (drag & drop için - derin tarama)"""
        extensions = {}
        
        try:
            # os.walk ile tüm alt klasörleri tara
            for root, dirs, files in os.walk(folder_path):
                # Derinlik kontrolü
                current_level = root.count(os.sep) - folder_path.count(os.sep)
                if current_level >= max_depth:
                    continue
                
                # Gizli ve sistem klasörlerini atla
                dirs[:] = [d for d in dirs if not d.startswith('.') and not self._is_system_folder_for_move(d)]
                
                # Dosyaları analiz et
                for file in files:
                    if not file.startswith('.'):
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext:
                            if file_ext not in extensions:
                                extensions[file_ext] = 0
                            extensions[file_ext] += 1
        
        except Exception as e:
            print(f"❌ Klasör uzantı analizi hatası: {folder_path} - {e}")
        
        return extensions
    
    def _is_system_folder_for_move(self, folder_name):
        """Sistem klasörü mü kontrol et (drag & drop için)"""
        system_folders = {
            'system volume information', '$recycle.bin', 'recycler',
            'windows', 'program files', 'program files (x86)', 'programdata',
            'users', 'temp', 'tmp', 'cache', '.git', '.svn', 'node_modules',
            '__pycache__', '.vscode', '.idea', 'appdata', 'application data'
        }
        return folder_name.lower() in system_folders
    
    def _find_suitable_target_folder_for_move(self, extension, target_analysis):
        """Uzantı için uygun hedef klasör bul (drag & drop için)"""
        if not extension or not target_analysis:
            return None
        
        # En uygun klasörü bul
        best_folder = None
        best_score = 0
        
        # Dosyanın kategorisini belirle
        category, _ = self.get_file_category(f"test{extension}")
        category_keywords = {
            'audio': ['müzik', 'ses', 'music', 'audio', 'sound'],
            'video': ['video', 'film', 'movie', 'sinema'],
            'images': ['resim', 'foto', 'image', 'picture', 'photo'],
            'documents': ['belge', 'doc', 'document', 'text', 'yazı'],
            'archives': ['arşiv', 'archive', 'zip', 'sıkıştır'],
            'programs': ['program', 'uygulama', 'app', 'software'],
            'cad': ['cad', 'çizim', 'tasarım', 'design']
        }
        
        for folder_name, folder_info in target_analysis.items():
            extensions = folder_info['extensions']
            score = 0
            
            # 1. Bu uzantı bu klasörde var mı VE klasör adı uzantıyla eşleşiyor mu?
            if extension in extensions:
                ext_name = extension.replace('.', '').upper()
                folder_upper = folder_name.upper()
                
                # Klasör adında uzantı geçiyor mu kontrol et
                if ext_name in folder_upper or folder_upper.endswith(ext_name):
                    score = extensions[extension] + 100
                    print(f"🎯 {extension} uzantısı {folder_name} klasöründe bulundu VE klasör adı eşleşiyor (tam eşleşme)")
                else:
                    # Uzantı var ama klasör adı eşleşmiyor - düşük puan
                    score = extensions[extension] * 5
                    print(f"⚠️ {extension} uzantısı {folder_name} klasöründe var ama klasör adı eşleşmiyor")
            
            # 2. Aynı kategorideki başka uzantılar var mı?
            elif category in category_keywords:
                # Aynı kategorideki diğer uzantıları kontrol et
                same_category_extensions = []
                for cat, info in self.get_file_categories().items():
                    if cat == category:
                        same_category_extensions = info['extensions']
                        break
                
                # Bu klasörde aynı kategoriden uzantı var mı?
                for ext in same_category_extensions:
                    if ext in extensions:
                        score += extensions[ext] * 10  # Kategori eşleşmesi için puan
                        print(f"🔗 {extension} için {folder_name} klasöründe aynı kategori uzantısı bulundu: {ext}")
                        break
            
            # 3. Klasör adında kategori kelimesi geçiyor mu?
            if category in category_keywords:
                for keyword in category_keywords[category]:
                    if keyword in folder_name.lower():
                        score += 50
                        print(f"📝 {folder_name} klasör adında kategori kelimesi bulundu: {keyword}")
                        break
            
            # 4. Klasör adında uzantı geçiyor mu?
            ext_name = extension.replace('.', '').upper()
            if ext_name in folder_name.upper():
                score += 100
                print(f"📝 {folder_name} klasör adında uzantı bulundu: {ext_name}")
            
            # 5. Dosya sayısı bonus
            file_count = folder_info.get('file_count', 0)
            if file_count > 10:
                score += 20
            elif file_count > 5:
                score += 10
            
            if score > best_score:
                best_score = score
                best_folder = folder_info['path']
        
        # Sadece gerçek tam eşleşme kabul et (uzantı var VE klasör adı eşleşiyor)
        # Skor >= 100 VE uzantı + klasör adı eşleşmesi olmalı
        if best_score >= 100:
            # Gerçek tam eşleşme mi kontrol et
            best_folder_name = None
            best_folder_extensions = None
            for folder_name, folder_info in target_analysis.items():
                if folder_info['path'] == best_folder:
                    best_folder_name = folder_name
                    best_folder_extensions = folder_info['extensions']
                    break
            
            if best_folder_extensions and extension in best_folder_extensions:
                ext_name = extension.replace('.', '').upper()
                # Klasör adının son kısmını kontrol et (örn: "Resimler/SVG" -> "SVG")
                folder_basename = os.path.basename(best_folder_name) if best_folder_name else ""
                if (ext_name in best_folder_name.upper() or 
                    best_folder_name.upper().endswith(ext_name) or
                    ext_name in folder_basename.upper() or
                    folder_basename.upper() == ext_name):
                    print(f"📁 {extension} için gerçek tam eşleşme bulundu: {os.path.basename(best_folder)} (skor: {best_score})")
                    return best_folder
        
        print(f"❌ {extension} için gerçek tam eşleşme bulunamadı - yeni klasör oluşturulacak")
        return None
    
    def _check_for_duplicates_in_target(self, source_file, target_folder):
        """Hedef klasörde duplikat dosya var mı kontrol et (hash bazlı)"""
        if not os.path.exists(target_folder):
            return None
        
        source_name = os.path.basename(source_file)
        source_size = os.path.getsize(source_file)
        
        try:
            # Hedef klasördeki dosyaları kontrol et
            for existing_file in os.listdir(target_folder):
                existing_path = os.path.join(target_folder, existing_file)
                
                if os.path.isfile(existing_path):
                    # İsim kontrolü
                    if existing_file == source_name:
                        print(f"🔍 Aynı isimli dosya bulundu: {existing_file}")
                        return existing_path
                    
                    # Boyut kontrolü (hızlı ön kontrol)
                    if os.path.getsize(existing_path) == source_size:
                        # Hash kontrolü (kesin kontrol)
                        if self._files_are_identical(source_file, existing_path):
                            print(f"🔍 Aynı içerikli dosya bulundu: {existing_file}")
                            return existing_path
        
        except Exception as e:
            print(f"❌ Duplikat kontrol hatası: {e}")
        
        return None
    
    def _files_are_identical(self, file1, file2):
        """İki dosyanın içeriği aynı mı kontrol et"""
        try:
            # Hızlı boyut kontrolü
            if os.path.getsize(file1) != os.path.getsize(file2):
                return False
            
            # Hash karşılaştırması
            hash1 = self._calculate_file_hash(file1)
            hash2 = self._calculate_file_hash(file2)
            
            return hash1 == hash2 and hash1 is not None
        
        except Exception as e:
            print(f"❌ Dosya karşılaştırma hatası: {e}")
            return False
    
    def _calculate_file_hash(self, file_path, chunk_size=8192):
        """Dosya hash'ini hesapla"""
        try:
            import hashlib
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"❌ Hash hesaplama hatası: {file_path} - {e}")
            return None
    
    def _handle_duplicate_file(self, source_file, target_file):
        """Duplikat dosyayı işle"""
        # Duplikat işlem seçeneğini al
        duplicate_action = self.gui.duplicate_action.get()
        
        if duplicate_action == "skip":
            print(f"⏭️ Duplikat atlandı: {os.path.basename(source_file)}")
            return False
        elif duplicate_action == "copy":
            # Numara ekleyerek kopyala
            counter = 1
            base_name, ext = os.path.splitext(target_file)
            new_target = f"{base_name}_{counter}{ext}"
            
            while os.path.exists(new_target):
                counter += 1
                new_target = f"{base_name}_{counter}{ext}"
            
            shutil.move(source_file, new_target)
            print(f"📋 Duplikat taşındı: {os.path.basename(new_target)}")
            return True
        else:  # ask
            # Kullanıcıya sor
            response = messagebox.askyesnocancel(
                "Duplikat Dosya",
                f"'{os.path.basename(source_file)}' dosyası zaten mevcut.\n\n"
                "Evet: Numara ekleyerek taşı\n"
                "Hayır: Atla\n"
                "İptal: İşlemi durdur"
            )
            
            if response is True:  # Evet
                counter = 1
                base_name, ext = os.path.splitext(target_file)
                new_target = f"{base_name}_{counter}{ext}"
                
                while os.path.exists(new_target):
                    counter += 1
                    new_target = f"{base_name}_{counter}{ext}"
                
                shutil.move(source_file, new_target)
                return True
            elif response is False:  # Hayır
                return False
            else:  # İptal
                raise Exception("İşlem kullanıcı tarafından iptal edildi")
        
        return False
    
    def open_file_location(self):
        """Dosya konumunu aç"""
        selection = self.gui.target_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir dosya seçin!")
            return
            
        item = self.gui.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_path, item_name)
        
        try:
            # Windows Explorer'da dosya konumunu aç
            os.system(f'explorer /select,"{item_path}"')
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya konumu açılamadı: {e}")
    
    def show_file_info(self):
        """Dosya bilgilerini göster"""
        selection = self.gui.target_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir dosya seçin!")
            return
            
        item = self.gui.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_path, item_name)
        
        if not os.path.exists(item_path):
            messagebox.showerror("Hata", "Dosya bulunamadı!")
            return
        
        try:
            stat_info = os.stat(item_path)
            file_size = self.format_size(stat_info.st_size)
            
            import datetime
            created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            info_text = f"""📄 Dosya Bilgileri

📁 Dosya Adı: {item_name}
📂 Tam Yol: {item_path}
📊 Boyut: {file_size}
📅 Oluşturulma: {created_time}
🔄 Değiştirilme: {modified_time}
🔒 İzinler: {oct(stat_info.st_mode)[-3:]}"""

            if os.path.isfile(item_path):
                file_ext = os.path.splitext(item_name)[1].lower()
                category, _ = self.get_file_category(item_path)
                info_text += f"\n🏷️ Kategori: {category.title()}"
                info_text += f"\n📎 Uzantı: {file_ext if file_ext else 'Uzantısız'}"
            
            messagebox.showinfo("Dosya Bilgileri", info_text)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya bilgileri alınamadı: {e}")
    
    def show_file_hash(self):
        """Dosya hash'ini göster"""
        selection = self.gui.target_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir dosya seçin!")
            return
            
        item = self.gui.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_path, item_name)
        
        if not os.path.isfile(item_path):
            messagebox.showwarning("Uyarı", "Sadece dosyalar için hash hesaplanabilir!")
            return
        
        # Hash hesaplama dialog'u
        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Hash Hesaplanıyor...")
        dialog.geometry("400x150")
        dialog.transient(self.gui.root)
        dialog.grab_set()
        
        # Dialog'u merkeze yerleştir
        dialog.geometry("+%d+%d" % (self.gui.root.winfo_rootx() + 50, self.gui.root.winfo_rooty() + 50))
        
        tk.Label(dialog, text=f"Hash hesaplanıyor: {item_name}", font=("Arial", 10)).pack(pady=20)
        
        progress_var = tk.StringVar()
        progress_label = tk.Label(dialog, textvariable=progress_var)
        progress_label.pack(pady=10)
        
        result_var = tk.StringVar()
        
        def calculate_hash():
            try:
                progress_var.set("Hash hesaplanıyor...")
                dialog.update()
                
                file_hash = self.get_file_hash(item_path)
                
                if file_hash:
                    result_var.set(file_hash)
                    progress_var.set("✅ Hash hesaplandı!")
                else:
                    progress_var.set("❌ Hash hesaplanamadı!")
                    
            except Exception as e:
                progress_var.set(f"❌ Hata: {e}")
            
            dialog.after(1000, dialog.destroy)
            
            if result_var.get():
                messagebox.showinfo("Dosya Hash", f"📄 Dosya: {item_name}\n🔄 MD5 Hash:\n{result_var.get()}")
        
        # Hash hesaplamayı thread'de başlat
        import threading
        threading.Thread(target=calculate_hash, daemon=True).start()
    
    def create_new_file(self):
        """Yeni dosya oluştur"""
        file_name = simpledialog.askstring("Yeni Dosya", "Dosya adı (uzantı ile):")
        if file_name:
            file_path = os.path.join(self.current_path, file_name)
            try:
                # Boş dosya oluştur
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                
                self.refresh_target()
                self.gui.status_var.set(f"'{file_name}' dosyası oluşturuldu.")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya oluşturulamadı: {e}")
    
    def show_folder_properties(self):
        """Klasör özelliklerini göster"""
        try:
            # Klasördeki dosya sayısını hesapla
            total_files = 0
            total_folders = 0
            total_size = 0
            
            for root, dirs, files in os.walk(self.current_path):
                total_folders += len(dirs)
                total_files += len(files)
                
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except:
                        continue
            
            folder_name = os.path.basename(self.current_path)
            if not folder_name:
                folder_name = self.current_path
            
            info_text = f"""📁 Klasör Özellikleri

📂 Klasör Adı: {folder_name}
📍 Tam Yol: {self.current_path}
📊 Toplam Boyut: {self.format_size(total_size)}
📄 Dosya Sayısı: {total_files}
📁 Klasör Sayısı: {total_folders}
📈 Toplam Öğe: {total_files + total_folders}"""

            messagebox.showinfo("Klasör Özellikleri", info_text)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör bilgileri alınamadı: {e}") 