"""
File Operations Module
File yönetimi işlemlerini içerir
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
        self.target_path = "D:/"  # Default Target Folder
        self.source_path = ""
        self.current_path = self.target_path
        self.navigation_history = []
        self.history_index = -1
        self.clipboard = []
        self.clipboard_operation = None  # 'copy' veya 'cut'
        self.sort_column = None
        self.sort_reverse = False
        
        # File kategorileri
        self.file_categories = self.get_file_categories()
        
        # GUI değişkenlerini güncelle
        self.gui.target_var.set(self.target_path)
        self.gui.current_path_var.set(self.current_path)
        
        # Ayarları Load
        self.load_settings()
        
        # Drag & Drop verisi
        self.drag_data = {"item": None, "x": 0, "y": 0}
        
        # First yükleme
        self.refresh_target()
        
        # Drag & Drop özelliğini ayarla
        self.setup_drag_drop()
        
        # Target tree'ye focus ver
        self.gui.target_tree.focus_set()
        
    def get_file_categories(self):
        """File kategorilerini tanımla"""
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
        
        # Bilinmeyen uzantı for otomatik kategori oluştur
        if file_ext:
            folder_name = f"{file_ext.replace('.', '').upper()}"
            auto_category = {
                'extensions': [file_ext],
                'folder': folder_name,
                'subfolders': {file_ext: file_ext.replace('.', '').upper()}
            }
            return 'unknown', auto_category
        else:
            # Uzantısız files
            return 'unknown', {
                'extensions': [''],
                'folder': 'Uzantisiz_Dosyalar',
                'subfolders': {'': 'Uzantisiz'}
            }
    
    def select_source_folder(self):
        """Source Folder seçimi"""
        folder = filedialog.askdirectory(title="Source select folder")
        if folder:
            self.source_path = folder
            self.gui.source_var.set(folder)
            self.gui.status_var.set(f"Source Folder seçildi: {folder}")
            
            # Source tree'yi temizle
            self.gui.source_tree.delete(*self.gui.source_tree.get_children())
        else:
            self.gui.status_var.set("Source Folder seçimi cancelled.")
    
    def select_target_folder(self):
        """Target Folder seçimi"""
        folder = filedialog.askdirectory(title="Target SSD select", initialdir=self.target_path)
        if folder:
            self.target_path = folder
            self.current_path = folder
            self.gui.target_var.set(folder)
            self.gui.current_path_var.set(folder)
            
            # Ayarları Save
            self.save_settings()
            
            # Target folder Refresh
            self.refresh_target()
            self.gui.status_var.set(f"Target Folder changed: {folder}")
        else:
            self.gui.status_var.set("Target Folder seçimi cancelled.")
    
    def add_to_history(self, path):
        """Navigasyon geçmişine ekle"""
        if self.history_index < len(self.navigation_history) - 1:
            self.navigation_history = self.navigation_history[:self.history_index + 1]
        
        if not self.navigation_history or self.navigation_history[-1] != path:
            self.navigation_history.append(path)
            self.history_index = len(self.navigation_history) - 1
    
    def go_back(self):
        """Back Go"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.navigation_history[self.history_index]
            self.gui.current_path_var.set(self.current_path)
            self.refresh_target(add_to_history=False)
    
    def go_up(self):
        """Up folder Go"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.current_path = parent
            self.gui.current_path_var.set(parent)
            self.refresh_target()
    
    def go_home(self):
        """Home folder Go"""
        self.current_path = self.target_path
        self.gui.current_path_var.set(self.target_path)
        self.refresh_target()
    
    def navigate_to_path(self, event=None):
        """Belirtilen yola Go"""
        path = self.gui.current_path_var.get()
        if os.path.exists(path) and os.path.isdir(path):
            self.current_path = path
            self.refresh_target()
        else:
            messagebox.showerror("Error", "invalid Folder yolu!")
            self.gui.current_path_var.set(self.current_path)
    
    def refresh_target(self, add_to_history=True):
        """Target folder Refresh"""
        # valid Path kontrolü
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
                        items.append((item, "📁 Folder", "", modified_time, item_path, True))
                    except:
                        items.append((item, "📁 Folder", "", "Bilinmiyor", item_path, True))
            
            # files ekle
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
                        items.append((item, "File", "Bilinmiyor", "Bilinmiyor", item_path, False))
            
            # Sıralama uygula
            if self.sort_column:
                items.sort(key=self.get_sort_key, reverse=self.sort_reverse)
            
            # Tree'ye ekle
            for item_name, item_type, size, modified, full_path, is_dir in items:
                self.gui.target_tree.insert('', 'end', text=item_name, 
                                          values=(size, item_type, modified),
                                          tags=('directory' if is_dir else 'file',))
            
            self.gui.status_var.set(f"📁 {len([i for i in items if i[5]])} Folder, 📄 {len([i for i in items if not i[5]])} File")
            
        except PermissionError:
            messagebox.showerror("Error", "Bu folder Access izniniz yok!")
        except Exception as e:
            messagebox.showerror("Error", f"Folder yüklenirken Error: {e}")
    
    def get_modified_time(self, file_path):
        """File Modified zamanını al"""
        try:
            import time
            timestamp = os.path.getmtime(file_path)
            return time.strftime("%d.%m.%Y %H:%M", time.localtime(timestamp))
        except:
            return "Bilinmiyor"
    
    def is_hidden_file(self, filename, file_path=None):
        """hidden File kontrolü - Home programdan alındı"""
        # Windows hidden files
        if filename.startswith('.'):
            return True
        
        # Sistem files
        system_files = [
            'thumbs.db', 'desktop.ini', 'folder.jpg', 'folder.png',
            'albumartsmall.jpg', 'albumart_{', '.ds_store',
            'system volume information', '$recycle.bin', 'recycler',
            'pagefile.sys', 'hiberfil.sys', 'swapfile.sys'
        ]
        
        if filename.lower() in system_files:
            return True
        
        # Geçici files
        temp_extensions = ['.tmp', '.temp', '.bak', '.old', '.cache', '.log']
        if any(filename.lower().endswith(ext) for ext in temp_extensions):
            return True
        
        # Windows hidden File attribute kontrolü
        if file_path and os.path.exists(file_path):
            try:
                import stat
                file_stat = os.stat(file_path)
                # Windows'ta hidden File kontrolü
                if hasattr(stat, 'FILE_ATTRIBUTE_HIDDEN'):
                    return bool(file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
            except:
                pass
        
        return False
    
    def format_size(self, size_bytes):
        """File boyutunu formatla"""
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
        
        if self.sort_column == '#0':  # Name
            return (not is_dir, item_name.lower())
        elif self.sort_column == 'size':  # Size
            if is_dir:
                return (0, item_name.lower())
            try:
                return (1, self.parse_size_string(size))
            except:
                return (1, 0)
        elif self.sort_column == 'type':  # Type
            return (not is_dir, item_type.lower())
        elif self.sort_column == 'modified':  # Modified
            return (not is_dir, modified)
        
        return (not is_dir, item_name.lower())
    
    def parse_size_string(self, size_str):
        """Size string'ini sayıya çevir"""
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
            # folder gir
            print(f"📁 folder giriliyor: {item_path}")
            self.add_to_history(self.current_path)
            self.current_path = item_path
            self.gui.current_path_var.set(item_path)
            self.refresh_target(add_to_history=False)
        else:
            # file Open
            try:
                print(f"📄 File açılıyor: {item_path}")
                os.startfile(item_path)
            except Exception as e:
                print(f"❌ File açma hatası: {e}")
                messagebox.showerror("Error", f"File could not open: {e}")
    
    def show_context_menu(self, event):
        """Right click menu"""
        try:
            # Identify selected item
            item = self.gui.target_tree.identify_row(event.y)
            if item:
                self.gui.target_tree.selection_set(item)
                
            # Create right click menu
            context_menu = tk.Menu(self.gui.root, tearoff=0)
            
            selection = self.gui.target_tree.selection()
            
            if selection:
                # File/Folder selected
                context_menu.add_command(label="🔓 Open", command=self.open_selected)
                context_menu.add_command(label="🔍 Open File Location", command=self.open_file_location)
                context_menu.add_separator()
                context_menu.add_command(label="📋 Copy (Ctrl+C)", command=self.copy_selected)
                context_menu.add_command(label="✂️ Cut (Ctrl+X)", command=self.cut_selected)
                
                # Paste - active if clipboard has content
                paste_state = tk.NORMAL if self.clipboard else tk.DISABLED
                context_menu.add_command(label="📁 Paste (Ctrl+V)", command=self.paste_selected, state=paste_state)
                
                context_menu.add_separator()
                context_menu.add_command(label="🗑️ Delete (Del)", command=self.delete_selected)
                context_menu.add_command(label="✏️ Rename (F2)", command=self.rename_selected)
                context_menu.add_separator()
                
                # Additional options if single file selected
                if len(selection) == 1:
                    item_data = self.gui.target_tree.item(selection[0])
                    item_name = item_data['text'].replace("📁 ", "").replace("📄 ", "")
                    item_path = os.path.join(self.current_path, item_name)
                    
                    if os.path.isfile(item_path):
                        context_menu.add_command(label="📊 File Information", command=self.show_file_info)
                        context_menu.add_command(label="🔄 File Hash", command=self.show_file_hash)
                    
                context_menu.add_command(label="📋 Properties", command=self.show_properties)
            else:
                # Empty area
                context_menu.add_command(label="📁 Paste (Ctrl+V)", command=self.paste_selected, 
                                       state=tk.NORMAL if self.clipboard else tk.DISABLED)
                context_menu.add_separator()
                context_menu.add_command(label="➕ New Folder", command=self.create_folder)
                context_menu.add_command(label="📄 New File", command=self.create_new_file)
                context_menu.add_separator()
                context_menu.add_command(label="🔄 Refresh (F5)", command=self.refresh_target)
                context_menu.add_separator()
                context_menu.add_command(label="📋 Folder Properties", command=self.show_folder_properties)
            
            # Show menu
            context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Menu error: {e}")
    
    def get_selected_items(self):
        """Get selected items"""
        selection = self.gui.target_tree.selection()
        items = []
        
        for item in selection:
            item_data = self.gui.target_tree.item(item)
            item_text = item_data['text'].replace("📁 ", "").replace("📄 ", "")
            item_path = os.path.join(self.current_path, item_text)
            items.append(item_path)
        
        return items
    
    def delete_selected(self):
        """Delete selected files"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Warning", "Select file to delete!")
            return
        
        # Get confirmation
        if len(items) == 1:
            message = f"Are you sure you want to delete '{os.path.basename(items[0])}'?"
        else:
            message = f"Are you sure you want to delete {len(items)} items?"
        
        if not messagebox.askyesno("Delete Confirmation", message):
            return
        
        # Delete
        deleted_count = 0
        for item_path in items:
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                deleted_count += 1
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete '{os.path.basename(item_path)}': {e}")
        
        if deleted_count > 0:
            self.gui.status_var.set(f"{deleted_count} items deleted.")
            self.refresh_target(add_to_history=False)
    
    def copy_selected(self):
        """Copy selected files"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Warning", "Select file to copy!")
            return
        
        self.clipboard = items
        self.clipboard_operation = 'copy'
        self.gui.status_var.set(f"{len(items)} items copied.")
    
    def cut_selected(self):
        """Cut selected files"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Warning", "Select file to cut!")
            return
        
        self.clipboard = items
        self.clipboard_operation = 'cut'
        self.gui.status_var.set(f"{len(items)} items cut.")
    
    def paste_selected(self):
        """Paste files"""
        if not self.clipboard:
            messagebox.showwarning("Warning", "No file to paste!")
            return
        
        pasted_count = 0
        for source_path in self.clipboard:
            try:
                filename = os.path.basename(source_path)
                target_path = os.path.join(self.current_path, filename)
                
                # Add number if same name file exists
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
                messagebox.showerror("Error", f"Could not paste '{os.path.basename(source_path)}': {e}")
        
        if self.clipboard_operation == 'cut':
            self.clipboard = []
            self.clipboard_operation = None
        
        if pasted_count > 0:
            self.gui.status_var.set(f"{pasted_count} items pasted.")
            self.refresh_target(add_to_history=False)
    
    def create_folder(self):
        """Create new folder"""
        folder_name = simpledialog.askstring("New Folder", "Enter folder name:")
        if folder_name:
            folder_path = os.path.join(self.current_path, folder_name)
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.gui.status_var.set(f"Folder '{folder_name}' created.")
                self.refresh_target(add_to_history=False)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder: {e}")
    
    def open_selected(self):
        """Open selected file or enter folder"""
        selection = self.gui.target_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select file/folder to open!")
            return
        
        # Get first selected item
        item = self.gui.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_path, item_name)
        
        if os.path.isdir(item_path):
            # Enter folder
            self.add_to_history(self.current_path)
            self.current_path = item_path
            self.gui.current_path_var.set(item_path)
            self.refresh_target(add_to_history=False)
        else:
            # Open file
            try:
                os.startfile(item_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open '{item_name}': {e}")
    
    def rename_selected(self):
        """selected file Rename"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Warning", "select file to rename!")
            return
        
        if len(items) > 1:
            messagebox.showwarning("Warning", "select single file!")
            return
        
        old_path = items[0]
        old_name = os.path.basename(old_path)
        
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        if new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.gui.status_var.set(f"'{old_name}' -> '{new_name}' renamed to.")
                self.refresh_target(add_to_history=False)
            except Exception as e:
                messagebox.showerror("Error", f"could not rename: {e}")
    
    def show_properties(self):
        """File özelliklerini Show"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Warning", "select file to view properties!")
            return
        
        if len(items) > 1:
            messagebox.showwarning("Warning", "select single file!")
            return
        
        file_path = items[0]
        try:
            stat = os.stat(file_path)
            import time
            
            properties = f"""File Properties:
            
Name: {os.path.basename(file_path)}
Path: {file_path}
Size: {self.format_size(stat.st_size)}
Created: {time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(stat.st_ctime))}
Modified: {time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(stat.st_mtime))}
Access: {time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(stat.st_atime))}
Type: {"Folder" if os.path.isdir(file_path) else "File"}
"""
            
            messagebox.showinfo("Properties", properties)
        except Exception as e:
            messagebox.showerror("Error", f"Error getting properties: {e}")
    
    def get_file_hash(self, file_path):
        """File Hash'ini hesapla - Home programdan alındı"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return f"Error: {e}"
    
    def is_file_locked(self, file_path):
        """File Locked mi kontrol et"""
        try:
            with open(file_path, 'r+b'):
                return False
        except (IOError, OSError):
            return True
    
    def copy_file_optimized(self, source_path, target_path):
        """Optimize edilmiş File kopyalama"""
        try:
            # File Locked mi kontrol et
            if self.is_file_locked(source_path):
                return False, "File kullanımda"
            
            # Büyük files for chunk-based kopyalama
            file_size = os.path.getsize(source_path)
            if file_size > 50 * 1024 * 1024:  # 50MB'dan büyükse
                return self.copy_file_chunked(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
                return True, "successful"
        except Exception as e:
            return False, str(e)
    
    def copy_file_chunked(self, source_path, target_path):
        """Chunk-based File kopyalama"""
        try:
            chunk_size = 1024 * 1024  # 1MB chunks
            with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
            return True, "successful"
        except Exception as e:
            return False, str(e)
    
    def load_settings(self):
        """Ayarları Load"""
        try:
            if os.path.exists('file_manager_settings.json'):
                with open('file_manager_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Last Target folder Load
                if 'target_path' in settings:
                    self.target_path = settings['target_path']
                    self.current_path = self.target_path
                    self.gui.target_var.set(self.target_path)
                    self.gui.current_path_var.set(self.current_path)
                    
        except Exception as e:
            print(f"settings yüklenirken Error: {e}")
    
    def save_settings(self):
        """Ayarları Save"""
        try:
            settings = {
                'target_path': self.target_path,
                'current_path': self.current_path
            }
            
            with open('file_manager_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"settings kaydedilirken Error: {e}")
    
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
            # First sürükleme cursor'u
            self.gui.target_tree.config(cursor="hand2")
            
    def on_drag_motion(self, event):
        """Sürükleme hareketi"""
        if self.drag_data["item"]:
            # Sürüklenen öğeyi vurgula
            self.gui.target_tree.selection_set(self.drag_data["item"])
            
            # Cursor'ı taşıma ikonu yap
            self.gui.target_tree.config(cursor="fleur")  # Taşıma cursor'u
            
            # Target kontrolü - eğer Folder üzerindeyse farklı cursor
            target_item = self.gui.target_tree.identify_row(event.y)
            if target_item and target_item != self.drag_data["item"]:
                target_item_data = self.gui.target_tree.item(target_item)
                target_name = target_item_data['text'].replace("📁 ", "").replace("📄 ", "")
                target_path = os.path.join(self.current_path, target_name)
                
                if os.path.isdir(target_path):
                    self.gui.target_tree.config(cursor="dotbox")  # Target Folder cursor'u
                else:
                    self.gui.target_tree.config(cursor="X_cursor")  # invalid Target
            
    def on_drag_end(self, event):
        """Sürükleme bitişi"""
        if not self.drag_data["item"]:
            return
            
        # Target öğeyi Find
        target_item = self.gui.target_tree.identify_row(event.y)
        
        if target_item and target_item != self.drag_data["item"]:
            source_item = self.gui.target_tree.item(self.drag_data["item"])
            target_item_data = self.gui.target_tree.item(target_item)
            
            source_name = source_item['text'].replace("📁 ", "").replace("📄 ", "")
            target_name = target_item_data['text'].replace("📁 ", "").replace("📄 ", "")
            
            source_path = os.path.join(self.current_path, source_name)
            target_path = os.path.join(self.current_path, target_name)
            
            # Target bir Folder mü kontrol et
            if os.path.isdir(target_path):
                self.move_file_to_folder(source_path, target_path)
        
        # Sürükleme verilerini temizle
        self.drag_data = {"item": None, "x": 0, "y": 0}
        
        # Cursor'ı normale döndür
        self.gui.target_tree.config(cursor="")
        
    def move_file_to_folder(self, source_path, target_folder):
        """File/folder Target folder taşı"""
        source_name = os.path.basename(source_path)
        is_folder = os.path.isdir(source_path)
        
        try:
            if is_folder:
                # Folder taşıma for Private dialog
                choice = self._ask_folder_move_method(source_name, target_folder)
                if choice == "cancel":
                    return
                elif choice == "complete":
                    self._move_complete_folder(source_path, target_folder)
                elif choice == "categorize":
                    self._move_folder_with_categorization(source_path, target_folder)
            else:
                # Normal File taşıma - basit Confirmation dialog'u
                message = f"'{source_name}' file '{os.path.basename(target_folder)}' klasörüne taşımak istiyor musunuz?"
                if messagebox.askyesno("Taşıma Onayı", message):
                    self._move_single_file(source_path, target_folder)
                else:
                    return
            
            self.refresh_target()
            self.gui.status_var.set(f"'{source_name}' başarıyla moved.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Taşıma hatası: {e}")
    
    def _ask_folder_move_method(self, source_name, target_folder):
        """Folder taşıma yöntemi for kullanıcıya sor"""
        import tkinter as tk
        from tkinter import ttk
        
        # Private dialog oluştur
        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Folder Taşıma Yöntemi")
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
        
        # Target bilgisi
        target_label = ttk.Label(main_frame, text=f"🎯 Target: {os.path.basename(target_folder)}", font=("Arial", 10))
        target_label.pack(pady=(0, 20))
        
        # Seçenekler
        option_frame = ttk.Frame(main_frame)
        option_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Radio button değişkeni
        choice_var = tk.StringVar(value="complete")
        
        # Option 1: Komple taşı
        complete_frame = ttk.LabelFrame(option_frame, text="🗂️ folder Komple Taşı", padding=15)
        complete_frame.pack(fill=tk.X, pady=(0, 15))
        
        complete_radio = ttk.Radiobutton(complete_frame, text="Bu seçeneği Select", 
                                       variable=choice_var, value="complete")
        complete_radio.pack(anchor=tk.W)
        
        ttk.Label(complete_frame, text="• Folder yapısını korur\n• Tüm alt klasörler ve files olduğu gibi taşınır\n• Hızlı Operation", 
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(8, 0))
        
        # Option 2: Kategorilere according to organize et
        categorize_frame = ttk.LabelFrame(option_frame, text="📂 İçeriği Kategorilere according to Organize Et", padding=15)
        categorize_frame.pack(fill=tk.X)
        
        categorize_radio = ttk.Radiobutton(categorize_frame, text="Bu seçeneği Select", 
                                         variable=choice_var, value="categorize")
        categorize_radio.pack(anchor=tk.W)
        
        ttk.Label(categorize_frame, text="• files uzantılarına according to kategorilere ayrılır\n• available Folder Structure with birleştirilir\n• Duplicate kontrolü yapılır", 
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
        
        # Butonları daha büyük ve visible yap
        ok_button = ttk.Button(button_frame, text="✅ OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=(0, 30), ipadx=25, ipady=8)
        
        cancel_button = ttk.Button(button_frame, text="❌ Cancel", command=on_cancel)
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
        """folder komple taşı (yapıyı koru)"""
        folder_name = os.path.basename(source_path)
        target_path = os.path.join(target_folder, folder_name)
        
        # Aynı isimde Folder varsa numara ekle
        counter = 1
        base_target = target_path
        while os.path.exists(target_path):
            target_path = f"{base_target}_{counter}"
            counter += 1
        
        # folder taşı
        shutil.move(source_path, target_path)
        print(f"📁 Folder komple moved: {source_path} -> {target_path}")
    
    def _move_single_file(self, source_path, target_folder):
        """Tek file taşı"""
        file_name = os.path.basename(source_path)
        new_path = os.path.join(target_folder, file_name)
        
        # Aynı isimde File varsa numara ekle
        counter = 1
        base_name, ext = os.path.splitext(file_name)
        while os.path.exists(new_path):
            new_name = f"{base_name}_{counter}{ext}"
            new_path = os.path.join(target_folder, new_name)
            counter += 1
        
        shutil.move(source_path, new_path)
    
    def _move_folder_with_categorization(self, source_folder, target_folder):
        """folder kategorilere according to organize ederek taşı"""
        print(f"🗂️ Folder kategorilere according to taşınıyor: {source_folder} -> {target_folder}")
        
        # Target Folder analizi yap (Source folder exclude tut)
        target_analysis = self._analyze_target_folders_for_move(target_folder, exclude_folder=source_folder)
        
        # Klasördeki tüm files Scan
        files_to_move = []
        
        for root, dirs, files in os.walk(source_folder):
            # hidden klasörleri atla
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):  # hidden files atla
                    file_path = os.path.join(root, file)
                    files_to_move.append(file_path)
        
        print(f"📊 Taşınacak File Count: {len(files_to_move)}")
        
        # files kategorilerine according to organize et
        moved_count = 0
        duplicate_count = 0
        
        for file_path in files_to_move:
            try:
                # File kategorisini belirle
                category, category_info = self.get_file_category(file_path)
                file_ext = os.path.splitext(file_path)[1].lower()
                
                # Target folder uygun Folder var mı kontrol et
                suggested_folder = self._find_suitable_target_folder_for_move(file_ext, target_analysis)
                
                if suggested_folder:
                    # available Folder found - doğrudan o folder yerleştir
                    final_target_folder = suggested_folder
                    print(f"📁 {file_ext} dosyası available folder yerleştirilecek: {suggested_folder}")
                else:
                    # Standart kategori kullan - New Folder oluştur
                    category_folder = os.path.join(target_folder, category_info['folder'])
                    
                    # Alt kategori folder
                    subfolder = file_ext.replace('.', '').upper() if file_ext else 'Uzantisiz'
                    final_target_folder = os.path.join(category_folder, subfolder)
                    print(f"📁 {file_ext} dosyası New kategori klasörüne yerleştirilecek: {category_info['folder']}/{subfolder}")
                
                # Klasörleri oluştur
                os.makedirs(final_target_folder, exist_ok=True)
                
                # File Name ve Target Path
                file_name = os.path.basename(file_path)
                target_file_path = os.path.join(final_target_folder, file_name)
                
                # Gelişmiş Duplicate kontrolü
                duplicate_found = self._check_for_duplicates_in_target(file_path, final_target_folder)
                
                if duplicate_found:
                    # Duplicate File found
                    if self._handle_duplicate_file(file_path, duplicate_found):
                        moved_count += 1
                    else:
                        duplicate_count += 1
                        print(f"⏭️ Duplicate atlandı: {file_name}")
                else:
                    # file taşı
                    shutil.move(file_path, target_file_path)
                    moved_count += 1
                    print(f"✅ moved: {file_name} -> {final_target_folder}")
                
            except Exception as e:
                print(f"❌ Error: {file_path} could not move - {e}")
                continue
        
        # Source folder Delete (boşsa)
        try:
            if not os.listdir(source_folder):
                os.rmdir(source_folder)
                print(f"🗑️ empty Source Folder deleted: {source_folder}")
        except:
            pass
        
        print(f"📈 Sonuç: {moved_count} File moved, {duplicate_count} Duplicate atlandı")
    
    def _analyze_target_folders_for_move(self, target_folder, exclude_folder=None):
        """Target klasördeki available klasörleri Analysis et (drag & drop for)"""
        folder_analysis = {}
        
        if not os.path.exists(target_folder):
            return folder_analysis
        
        print("🔍 Target Folder analizi starting...")
        
        # Sistem klasörlerini exclude tut
        system_folders = {
            'system volume information', '$recycle.bin', 'recycler',
            'windows', 'program files', 'program files (x86)', 'programdata',
            'users', 'temp', 'tmp', 'cache', '.Go', '.svn', 'node_modules',
            '__pycache__', '.vscode', '.idea'
        }
        
        try:
            # Tüm klasörleri recursive olarak Analysis et (3 seviye derinlik)
            for root, dirs, files in os.walk(target_folder):
                # Derinlik kontrolü
                current_level = root.count(os.sep) - target_folder.count(os.sep)
                if current_level >= 3:
                    dirs.clear()  # Daha derine inme
                    continue
                
                # hidden ve sistem klasörlerini atla
                dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in system_folders]
                
                # Source folder exclude tut
                if exclude_folder and os.path.exists(exclude_folder):
                    try:
                        if os.path.samefile(root, exclude_folder):
                            print(f"⏭️ Source Folder atlandı: {os.path.basename(root)}")
                            dirs.clear()  # Alt klasörlerini de atla
                            continue
                    except:
                        if os.path.basename(root) == os.path.basename(exclude_folder):
                            print(f"⏭️ Source Folder atlandı: {os.path.basename(root)}")
                            dirs.clear()
                            continue
                
                # Bu folder File var mı kontrol et
                folder_extensions = {}
                for file in files:
                    if not file.startswith('.'):
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext:
                            if file_ext not in folder_extensions:
                                folder_extensions[file_ext] = 0
                            folder_extensions[file_ext] += 1
                
                # Eğer bu folder File varsa Analysis sonuçlarına ekle
                if folder_extensions and root != target_folder:
                    # Relative path oluştur
                    rel_path = os.path.relpath(root, target_folder)
                    folder_analysis[rel_path] = {
                        'path': root,
                        'extensions': folder_extensions,
                        'file_count': len(folder_extensions)
                    }
                    print(f"📂 {rel_path}: {list(folder_extensions.keys())} uzantıları found")
        
        except Exception as e:
            print(f"❌ Target Folder analizi hatası: {e}")
        
        return folder_analysis
    
    def _analyze_folder_extensions_for_move(self, folder_path, max_depth=5):
        """Klasördeki File uzantılarını Analysis et (drag & drop for - derin scanning)"""
        extensions = {}
        
        try:
            # os.walk with tüm alt klasörleri Scan
            for root, dirs, files in os.walk(folder_path):
                # Derinlik kontrolü
                current_level = root.count(os.sep) - folder_path.count(os.sep)
                if current_level >= max_depth:
                    continue
                
                # hidden ve sistem klasörlerini atla
                dirs[:] = [d for d in dirs if not d.startswith('.') and not self._is_system_folder_for_move(d)]
                
                # files Analysis et
                for file in files:
                    if not file.startswith('.'):
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext:
                            if file_ext not in extensions:
                                extensions[file_ext] = 0
                            extensions[file_ext] += 1
        
        except Exception as e:
            print(f"❌ Folder uzantı analizi hatası: {folder_path} - {e}")
        
        return extensions
    
    def _is_system_folder_for_move(self, folder_name):
        """Sistem folder mü kontrol et (drag & drop for)"""
        system_folders = {
            'system volume information', '$recycle.bin', 'recycler',
            'windows', 'program files', 'program files (x86)', 'programdata',
            'users', 'temp', 'tmp', 'cache', '.Go', '.svn', 'node_modules',
            '__pycache__', '.vscode', '.idea', 'appdata', 'application data'
        }
        return folder_name.lower() in system_folders
    
    def _find_suitable_target_folder_for_move(self, extension, target_analysis):
        """Uzantı for uygun Target Folder Find (drag & drop for)"""
        if not extension or not target_analysis:
            return None
        
        # En uygun folder Find
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
            
            # 1. Bu uzantı bu folder var mı VE Folder Name uzantıyla eşleşiyor mu?
            if extension in extensions:
                ext_name = extension.replace('.', '').upper()
                folder_upper = folder_name.upper()
                
                # Folder adında uzantı geçiyor mu kontrol et
                if ext_name in folder_upper or folder_upper.endswith(ext_name):
                    score = extensions[extension] + 100
                    print(f"🎯 {extension} uzantısı {folder_name} klasöründe found VE Folder Name eşleşiyor (tam eşleşme)")
                else:
                    # Uzantı var ama Folder Name eşleşmiyor - düşük puan
                    score = extensions[extension] * 5
                    print(f"⚠️ {extension} uzantısı {folder_name} klasöründe var ama Folder Name eşleşmiyor")
            
            # 2. Aynı kategorideki başka Extensions var mı?
            elif category in category_keywords:
                # Aynı kategorideki diğer uzantıları kontrol et
                same_category_extensions = []
                for cat, info in self.get_file_categories().items():
                    if cat == category:
                        same_category_extensions = info['extensions']
                        break
                
                # Bu folder aynı kategoriden uzantı var mı?
                for ext in same_category_extensions:
                    if ext in extensions:
                        score += extensions[ext] * 10  # Kategori eşleşmesi for puan
                        print(f"🔗 {extension} for {folder_name} klasöründe aynı kategori uzantısı found: {ext}")
                        break
            
            # 3. Folder adında kategori kelimesi geçiyor mu?
            if category in category_keywords:
                for keyword in category_keywords[category]:
                    if keyword in folder_name.lower():
                        score += 50
                        print(f"📝 {folder_name} Folder adında kategori kelimesi found: {keyword}")
                        break
            
            # 4. Folder adında uzantı geçiyor mu?
            ext_name = extension.replace('.', '').upper()
            if ext_name in folder_name.upper():
                score += 100
                print(f"📝 {folder_name} Folder adında uzantı found: {ext_name}")
            
            # 5. File Count bonus
            file_count = folder_info.get('file_count', 0)
            if file_count > 10:
                score += 20
            elif file_count > 5:
                score += 10
            
            if score > best_score:
                best_score = score
                best_folder = folder_info['path']
        
        # Sadece gerçek tam eşleşme kabul et (uzantı var VE Folder Name eşleşiyor)
        # Skor >= 100 VE uzantı + Folder Name eşleşmesi olmalı
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
                # Folder adının Last kısmını kontrol et (e.g.: "Resimler/SVG" -> "SVG")
                folder_basename = os.path.basename(best_folder_name) if best_folder_name else ""
                if (ext_name in best_folder_name.upper() or 
                    best_folder_name.upper().endswith(ext_name) or
                    ext_name in folder_basename.upper() or
                    folder_basename.upper() == ext_name):
                    print(f"📁 {extension} for gerçek tam eşleşme found: {os.path.basename(best_folder)} (skor: {best_score})")
                    return best_folder
        
        print(f"❌ {extension} for gerçek tam eşleşme not found - New Folder oluşturulacak")
        return None
    
    def _check_for_duplicates_in_target(self, source_file, target_folder):
        """Target folder Duplicate File var mı kontrol et (Hash bazlı)"""
        if not os.path.exists(target_folder):
            return None
        
        source_name = os.path.basename(source_file)
        source_size = os.path.getsize(source_file)
        
        try:
            # Target klasördeki files kontrol et
            for existing_file in os.listdir(target_folder):
                existing_path = os.path.join(target_folder, existing_file)
                
                if os.path.isfile(existing_path):
                    # Name kontrolü
                    if existing_file == source_name:
                        print(f"🔍 Aynı isimli File found: {existing_file}")
                        return existing_path
                    
                    # Size kontrolü (hızlı ön kontrol)
                    if os.path.getsize(existing_path) == source_size:
                        # Hash kontrolü (kesin kontrol)
                        if self._files_are_identical(source_file, existing_path):
                            print(f"🔍 Aynı içerikli File found: {existing_file}")
                            return existing_path
        
        except Exception as e:
            print(f"❌ Duplicate Check hatası: {e}")
        
        return None
    
    def _files_are_identical(self, file1, file2):
        """İki dosyanın içeriği aynı mı kontrol et"""
        try:
            # Hızlı Size kontrolü
            if os.path.getsize(file1) != os.path.getsize(file2):
                return False
            
            # Hash karşılaştırması
            hash1 = self._calculate_file_hash(file1)
            hash2 = self._calculate_file_hash(file2)
            
            return hash1 == hash2 and hash1 is not None
        
        except Exception as e:
            print(f"❌ File karşılaştırma hatası: {e}")
            return False
    
    def _calculate_file_hash(self, file_path, chunk_size=8192):
        """File Hash'ini hesapla"""
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
        """Duplicate file işle"""
        # Duplicate Operation seçeneğini al
        duplicate_action = self.gui.duplicate_action.get()
        
        if duplicate_action == "skip":
            print(f"⏭️ Duplicate atlandı: {os.path.basename(source_file)}")
            return False
        elif duplicate_action == "copy":
            # Numara ekleyerek Copy
            counter = 1
            base_name, ext = os.path.splitext(target_file)
            new_target = f"{base_name}_{counter}{ext}"
            
            while os.path.exists(new_target):
                counter += 1
                new_target = f"{base_name}_{counter}{ext}"
            
            shutil.move(source_file, new_target)
            print(f"📋 Duplicate moved: {os.path.basename(new_target)}")
            return True
        else:  # ask
            # Kullanıcıya sor
            response = messagebox.askyesnocancel(
                "Duplicate File",
                f"'{os.path.basename(source_file)}' dosyası zaten available.\n\n"
                "Yes: Copy with number\n"
                "No: Atla\n"
                "Cancel: İşlemi Stop"
            )
            
            if response is True:  # Yes
                counter = 1
                base_name, ext = os.path.splitext(target_file)
                new_target = f"{base_name}_{counter}{ext}"
                
                while os.path.exists(new_target):
                    counter += 1
                    new_target = f"{base_name}_{counter}{ext}"
                
                shutil.move(source_file, new_target)
                return True
            elif response is False:  # No
                return False
            else:  # Cancel
                raise Exception("Operation kullanıcı tarafından cancelled")
        
        return False
    
    def open_file_location(self):
        """Open file location"""
        selection = self.gui.target_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file!")
            return
            
        item = self.gui.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_path, item_name)
        
        try:
            # Open file location in Windows Explorer
            os.system(f'explorer /select,"{item_path}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file location: {e}")
    
    def show_file_info(self):
        """Show file information"""
        selection = self.gui.target_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file!")
            return
            
        item = self.gui.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_path, item_name)
        
        if not os.path.exists(item_path):
            messagebox.showerror("Error", "File not found!")
            return
        
        try:
            stat_info = os.stat(item_path)
            file_size = self.format_size(stat_info.st_size)
            
            import datetime
            created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            info_text = f"""📄 File Information

📁 File Name: {item_name}
📂 Full Path: {item_path}
📊 Size: {file_size}
📅 Created: {created_time}
🔄 Modified: {modified_time}
🔒 Permissions: {oct(stat_info.st_mode)[-3:]}"""

            if os.path.isfile(item_path):
                file_ext = os.path.splitext(item_name)[1].lower()
                category, _ = self.get_file_category(item_path)
                info_text += f"\n🏷️ Category: {category.title()}"
                info_text += f"\n📎 Extension: {file_ext if file_ext else 'No Extension'}"
            
            messagebox.showinfo("File Information", info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not get file information: {e}")
    
    def show_file_hash(self):
        """File Hash'ini Show"""
        selection = self.gui.target_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file!")
            return
            
        item = self.gui.target_tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        item_path = os.path.join(self.current_path, item_name)
        
        if not os.path.isfile(item_path):
            messagebox.showwarning("Warning", "Sadece files for Hash hesaplanabilir!")
            return
        
        # Hash hesaplama dialog'u
        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Hash Calculating...")
        dialog.geometry("400x150")
        dialog.transient(self.gui.root)
        dialog.grab_set()
        
        # Dialog'u merkeze yerleştir
        dialog.geometry("+%d+%d" % (self.gui.root.winfo_rootx() + 50, self.gui.root.winfo_rooty() + 50))
        
        tk.Label(dialog, text=f"Hash Calculating: {item_name}", font=("Arial", 10)).pack(pady=20)
        
        progress_var = tk.StringVar()
        progress_label = tk.Label(dialog, textvariable=progress_var)
        progress_label.pack(pady=10)
        
        result_var = tk.StringVar()
        
        def calculate_hash():
            try:
                progress_var.set("Hash Calculating...")
                dialog.update()
                
                file_hash = self.get_file_hash(item_path)
                
                if file_hash:
                    result_var.set(file_hash)
                    progress_var.set("✅ Hash hesaplandı!")
                else:
                    progress_var.set("❌ Hash hesaplanamadı!")
                    
            except Exception as e:
                progress_var.set(f"❌ Error: {e}")
            
            dialog.after(1000, dialog.destroy)
            
            if result_var.get():
                messagebox.showinfo("File Hash", f"📄 File: {item_name}\n🔄 MD5 Hash:\n{result_var.get()}")
        
        # Hash hesaplamayı thread'de Start
        import threading
        threading.Thread(target=calculate_hash, daemon=True).start()
    
    def create_new_file(self):
        """New File oluştur"""
        file_name = simpledialog.askstring("New File", "File Name (uzantı with):")
        if file_name:
            file_path = os.path.join(self.current_path, file_name)
            try:
                # empty File oluştur
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                
                self.refresh_target()
                self.gui.status_var.set(f"'{file_name}' dosyası created.")
                
            except Exception as e:
                messagebox.showerror("Error", f"File could not create: {e}")
    
    def show_folder_properties(self):
        """Folder özelliklerini Show"""
        try:
            # Klasördeki File sayısını hesapla
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
            
            info_text = f"""📁 Folder Properties

📂 Folder Name: {folder_name}
📍 Tam Path: {self.current_path}
📊 Total Size: {self.format_size(total_size)}
📄 File Count: {total_files}
📁 Folder Sayısı: {total_folders}
📈 Total Item: {total_files + total_folders}"""

            messagebox.showinfo("Folder Properties", info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Folder bilgileri alınamadı: {e}") 