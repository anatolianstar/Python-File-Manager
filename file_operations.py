"""
File Operations Module
Dosya yönetimi işlemlerini içerir
"""

import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
from pathlib import Path
import json
import hashlib
import time
import stat
from collections import defaultdict
import threading
import traceback

# Multi-language support
from lang_manager import t
from lang_manager import lang_manager

class FileOperations:
    def __init__(self, gui_manager):
        self.gui = gui_manager
        self.source_path = ""
        self.target_path = ""
        self.current_target_dir = ""
        self.history_index = -1
        self.navigation_history = []
        self.clipboard_data = None
        
        # Sürükle-bırak için
        self.drag_data = {"item": None, "x": 0, "y": 0}
        
        # Sıralama bilgileri
        self.sort_column = None
        self.sort_reverse = False
        self.current_path = ""
        
        # Clipboard işlemleri için
        self.clipboard_operation = None  # 'copy' veya 'cut'
        
        # Dinamik kategori öğrenme sistemi
        self.learned_categories = {}  # {extension: category_name}
        self.load_learned_categories()
        
        self.load_settings()
        self.setup_drag_drop()
        
    def get_file_categories(self):
        """Dosya kategorilerini döndür - SABİT İNGİLİZCE SİSTEM"""
        return {
            'image_files': {
                'folder': 'Image Files',           # Sabit İngilizce
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp', '.ico', '.psd', '.ai', '.eps'],
                'subfolders': {
                    '.jpg': 'JPG',
                    '.jpeg': 'JPEG', 
                    '.png': 'PNG',
                    '.gif': 'GIF',
                    '.bmp': 'BMP',
                    '.tiff': 'TIFF',
                    '.tif': 'TIF',
                    '.svg': 'SVG',
                    '.webp': 'WEBP',
                    '.ico': 'ICO',
                    '.psd': 'PSD',
                    '.ai': 'AI',
                    '.eps': 'EPS'
                }
            },
            'document_files': {
                'folder': 'Document Files',           # Sabit İngilizce
                'extensions': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv'],
                'subfolders': {
                    '.pdf': 'PDF',
                    '.doc': 'DOC',
                    '.docx': 'DOCX',
                    '.txt': 'TXT',
                    '.rtf': 'RTF',
                    '.odt': 'ODT',
                    '.xls': 'XLS',
                    '.xlsx': 'XLSX',
                    '.ppt': 'PPT',
                    '.pptx': 'PPTX',
                    '.csv': 'CSV'
                }
            },
            'video_files': {
                'folder': 'Video Files',           # Sabit İngilizce
                'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'],
                'subfolders': {
                    '.mp4': 'MP4',
                    '.avi': 'AVI',
                    '.mkv': 'MKV',
                    '.mov': 'MOV',
                    '.wmv': 'WMV',
                    '.flv': 'FLV',
                    '.webm': 'WEBM',
                    '.m4v': 'M4V',
                    '.3gp': '3GP',
                    '.mpg': 'MPG',
                    '.mpeg': 'MPEG'
                }
            },
            'audio_files': {
                'folder': 'Audio Files',             # Sabit İngilizce
                'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'],
                'subfolders': {
                    '.mp3': 'MP3',
                    '.wav': 'WAV',
                    '.flac': 'FLAC',
                    '.aac': 'AAC',
                    '.ogg': 'OGG',
                    '.wma': 'WMA',
                    '.m4a': 'M4A',
                    '.opus': 'OPUS'
                }
            },
            'archive_files': {
                'folder': 'Compressed Files',           # Sabit İngilizce
                'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
                'subfolders': {
                    '.zip': 'ZIP',
                    '.rar': 'RAR',
                    '.7z': '7Z',
                    '.tar': 'TAR',
                    '.gz': 'GZ',
                    '.bz2': 'BZ2',
                    '.xz': 'XZ',
                    '.iso': 'ISO'
                }
            },
            'program_files': {
                'folder': 'Program Files',         # Sabit İngilizce
                'extensions': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.app', '.apk'],
                'subfolders': {
                    '.exe': 'EXE',
                    '.msi': 'MSI',
                    '.deb': 'DEB',
                    '.rpm': 'RPM',
                    '.dmg': 'DMG',
                    '.pkg': 'PKG',
                    '.app': 'APP',
                    '.apk': 'APK'
                }
            },
            'software_packages': {
                'folder': 'Software Packages',          # Sabit İngilizce - yazılım paketleri
                'extensions': [],  # Boş - uzantı bazlı tarama yapılmaz
                'subfolders': {},  # Boş - alt klasör oluşturulmaz
                'duplicate_only': True  # Sadece duplicate tarama yapılır
            },
            'cad_3d_files': {
                'folder': 'CAD and 3D Files',      # Sabit İngilizce
                'extensions': [
                    # CAD Uzantıları
                    '.dwg', '.dxf', '.step', '.stp', '.iges', '.igs',
                    # 3D Model Uzantıları
                    '.stl', '.obj', '.3mf', '.ply', '.fbx', '.dae', '.blend',
                    # 3D Yazılım Uzantıları
                    '.max', '.mtl', '.c4d', '.ma', '.mb', '.skp', '.3ds', '.lwo', '.lws',
                    # FBX Preset Dosyaları
                    '.fbximportpreset', '.fbxexportpreset',
                    # Diğer 3D Formatları
                    '.x3d', '.collada', '.gltf', '.glb', '.usd', '.usda', '.usdc'
                ],
                'subfolders': {
                    # CAD
                    '.dwg': 'DWG',
                    '.dxf': 'DXF',
                    '.step': 'STEP',
                    '.stp': 'STP',
                    '.iges': 'IGES',
                    '.igs': 'IGS',
                    # 3D Models
                    '.stl': 'STL',
                    '.obj': 'OBJ',
                    '.3mf': '3MF',
                    '.ply': 'PLY',
                    '.fbx': 'FBX',
                    '.dae': 'DAE',
                    '.blend': 'BLEND',
                    # 3D Software
                    '.max': 'MAX',
                    '.mtl': 'MTL',
                    '.c4d': 'C4D',
                    '.ma': 'MAYA',
                    '.mb': 'MAYA_BINARY',
                    '.skp': 'SKETCHUP',
                    '.3ds': '3DS_MAX',
                    '.lwo': 'LIGHTWAVE',
                    '.lws': 'LIGHTWAVE_SCENE',
                    # FBX Presets
                    '.fbximportpreset': 'FBX_IMPORT_PRESET',
                    '.fbxexportpreset': 'FBX_EXPORT_PRESET',
                    # Modern 3D
                    '.x3d': 'X3D',
                    '.collada': 'COLLADA',
                    '.gltf': 'GLTF',
                    '.glb': 'GLB',
                    '.usd': 'USD',
                    '.usda': 'USD_ASCII',
                    '.usdc': 'USD_CRATE'
                }
            },
            'code_files': {
                'folder': 'Code Files',             # Sabit İngilizce
                'extensions': ['.py', '.js', '.html', '.css', '.php', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.rs', '.swift'],
                'subfolders': {
                    '.py': 'PYTHON',
                    '.js': 'JAVASCRIPT',
                    '.html': 'HTML',
                    '.css': 'CSS',
                    '.php': 'PHP',
                    '.java': 'JAVA',
                    '.cpp': 'CPP',
                    '.c': 'C',
                    '.cs': 'CSHARP',
                    '.rb': 'RUBY',
                    '.go': 'GO',
                    '.rs': 'RUST',
                    '.swift': 'SWIFT'
                }
            },
            'font_files': {
                'folder': 'Font Files',            # Sabit İngilizce
                'extensions': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
                'subfolders': {
                    '.ttf': 'TTF',
                    '.otf': 'OTF',
                    '.woff': 'WOFF',
                    '.woff2': 'WOFF2',
                    '.eot': 'EOT'
                }
            },
            'other_files': {
                'folder': 'Other Files',            # Sabit İngilizce - Bilinmeyen uzantılar için
                'extensions': [],  # Boş - tüm bilinmeyen uzantılar buraya gider
                'subfolders': {}   # Dynamic olarak oluşturulacak
            }
        }
    
    def get_file_category(self, file_path):
        """Dosyanın kategorisini belirle - YENİ ALGORİTMA"""
        extension = os.path.splitext(file_path)[1].lower()
        categories = self.get_file_categories()
        
        # Tüm kategorileri kontrol et
        for category_name, category_info in categories.items():
            if category_name == 'other_files':  # 'other_files' son kontrol edilecek
                continue
                
            if extension in category_info['extensions']:
                return category_name, category_info
        
        # Bilinmeyen uzantılar için TARGET LEARNING sistemini kontrol et
        learned_result = self._check_learned_category_for_scan(extension)
        if learned_result:
            # Öğrenilmiş kategori bulundu
            learned_category = learned_result['category']
            if learned_category in categories:
                return learned_category, categories[learned_category]
        
        # Hala bulunamadıysa "Other Files" kategorisine gönder
        print(f"⚠️ Unknown extension {extension}, sending to other_files")
        return 'other_files', categories['other_files']
    
    def select_source_folder(self):
        """Kaynak klasör seçimi"""
        folder = filedialog.askdirectory(title=t('dialogs.select_source'))
        if folder:
            self.source_path = folder
            self.gui.source_var.set(folder)
            
            # KAYNAK SEÇİLDİĞİNDE TARGET'TAKİ ÖĞRENME SİSTEMİNİ HEMEN YÜKLE
            if hasattr(self, 'target_path') and self.target_path:
                self.load_learned_categories()
                print(f"📂 Source selected: {folder}")
                print(f"🎯 Target: {self.target_path}")
                print(f"📚 Learning loaded: {len(self.learned_categories)} extensions")
                if self.learned_categories:
                    print(f"📋 Learned extensions: {list(self.learned_categories.keys())}")
                    for ext, cat in self.learned_categories.items():
                        print(f"   {ext} → {cat}")
                else:
                    print("📭 No learning found - will use default English categories")
            
            self.gui.status_var.set(t('messages.source_selected', folder=folder))
            
            # Kaynak tree'yi temizle
            self.gui.source_tree.delete(*self.gui.source_tree.get_children())
        else:
            self.gui.status_var.set(t('messages.source_cancelled'))
    
    def select_target_folder(self):
        """Hedef klasör seçimi"""
        folder = filedialog.askdirectory(title=t('dialogs.select_target'), initialdir=self.target_path)
        if folder:
            self.target_path = folder
            self.current_path = folder
            self.gui.target_var.set(folder)
            self.gui.current_path_var.set(folder)
            
            # Yeni target seçildi - öğrenme sistemini yeniden yükle
            self.load_learned_categories()
            print(f"🎯 Target changed: {folder}")
            print(f"📚 Learning reloaded: {len(self.learned_categories)} extensions")
            
            # Ayarları kaydet
            self.save_settings()
            
            # Hedef klasörü yenile
            self.refresh_target()
            self.gui.status_var.set(t('messages.target_changed', folder=folder))
        else:
            self.gui.status_var.set(t('messages.target_cancelled'))
    
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
            messagebox.showerror(t('dialogs.error.title'), t('messages.invalid_folder_path'))
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
            
            # Status mesajını çeviri sistemi ile göster
            folder_count = len([i for i in items if i[5]])
            file_count = len([i for i in items if not i[5]])
            status_message = f"📁 {folder_count} {t('status.folders')}, 📄 {file_count} {t('status.files')}"
            self.gui.status_var.set(status_message)
            
        except PermissionError:
            messagebox.showerror(t('dialogs.error.title'), t('messages.access_denied'))
        except Exception as e:
            messagebox.showerror(t('dialogs.error.title'), t('messages.folder_load_error', error=str(e)))
    
    def get_modified_time(self, file_path):
        """Dosya değiştirilme zamanını al"""
        try:
            import time
            timestamp = os.path.getmtime(file_path)
            return time.strftime("%d.%m.%Y %H:%M", time.localtime(timestamp))
        except:
            from lang_manager import t
            return t('properties.unknown')
    
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
            print(f"📁 {lang_manager.get_text('messages.entering_folder').format(path=item_path)}")
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
                context_menu.add_command(label=t('context_menu.open'), command=self.open_selected)
                context_menu.add_command(label=t('context_menu.open_location'), command=self.open_file_location)
                context_menu.add_separator()
                context_menu.add_command(label=t('context_menu.copy'), command=self.copy_selected)
                context_menu.add_command(label=t('context_menu.cut'), command=self.cut_selected)
                
                # Yapıştırma - pano doluysa aktif
                paste_state = tk.NORMAL if self.clipboard_data else tk.DISABLED
                context_menu.add_command(label=t('context_menu.paste'), command=self.paste_selected, state=paste_state)
                
                context_menu.add_separator()
                context_menu.add_command(label=t('context_menu.delete'), command=self.delete_selected)
                context_menu.add_command(label=t('context_menu.rename'), command=self.rename_selected)
                context_menu.add_separator()
                
                # Tek dosya seçiliyse ek seçenekler
                if len(selection) == 1:
                    item_data = self.gui.target_tree.item(selection[0])
                    item_name = item_data['text'].replace("📁 ", "").replace("📄 ", "")
                    item_path = os.path.join(self.current_path, item_name)
                    
                    if os.path.isfile(item_path):
                        context_menu.add_command(label=t('context_menu.file_info'), command=self.show_file_info)
                        context_menu.add_command(label=t('context_menu.file_hash'), command=self.show_file_hash)
                    
                context_menu.add_command(label=t('context_menu.properties'), command=self.show_properties)
            else:
                # Boş alan
                context_menu.add_command(label=t('context_menu.paste'), command=self.paste_selected, 
                                       state=tk.NORMAL if self.clipboard_data else tk.DISABLED)
                context_menu.add_separator()
                context_menu.add_command(label=t('context_menu.new_folder'), command=self.create_folder)
                context_menu.add_command(label=t('context_menu.new_file'), command=self.create_new_file)
                context_menu.add_separator()
                context_menu.add_command(label=t('context_menu.refresh'), command=self.refresh_target)
                context_menu.add_separator()
                context_menu.add_command(label=t('context_menu.folder_properties'), command=self.show_folder_properties)
            
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
        print("📋 COPY İŞLEMİ BAŞLADI")
        
        items = self.get_selected_items()
        if not items:
            print("❌ Hiçbir öğe seçilmemiş!")
            messagebox.showwarning("Uyarı", "Kopyalanacak dosya seçin!")
            return
        
        print(f"📋 Seçilen öğeler: {items}")
        
        # Yeni clipboard format - her item için operation bilgisi
        self.clipboard_data = [{'path': item, 'operation': 'copy'} for item in items]
        self.gui.status_var.set(f"{len(items)} öğe kopyalandı.")
        
        # Clipboard içeriğini kontrol et
        for i, item in enumerate(self.clipboard_data):
            if os.path.isdir(item['path']):
                print(f"📁 Klasör {i+1}: {item['path']}")
            else:
                print(f"📄 Dosya {i+1}: {item['path']}")
        
        print(f"✅ {len(items)} öğe panoya kopyalandı")
    
    def cut_selected(self):
        """Seçili dosyaları kes - HIZLI VERSİYON"""
        items = self.get_selected_items()
        if not items:
            messagebox.showwarning("Uyarı", "Kesilecek dosya seçin!")
            return
        
        # Direkt kes - onay yok
        self.clipboard_data = [{'path': item, 'operation': 'cut'} for item in items]
        self.gui.status_var.set(f"✂️ {len(items)} öğe kesildi")
        
        # Kısa bilgi mesajı - sadece status bar'da
        print(f"⚠️ {len(items)} dosya kesildi - güvenli yapıştırma aktif")
    
    def _count_total_items_recursive(self, items):
        """Klasörler içindeki tüm dosya ve klasörleri sayar"""
        total_count = 0
        
        for item_data in items:
            source_path = item_data['path']
            
            if os.path.isdir(source_path):
                # Klasör ise içindeki tüm öğeleri say
                try:
                    for root, dirs, files in os.walk(source_path):
                        total_count += len(dirs) + len(files)  # Alt klasörler + dosyalar
                except (PermissionError, OSError):
                    # Erişim hatası durumunda sadece ana klasörü say
                    total_count += 1
            else:
                # Dosya ise direkt say
                total_count += 1
                
        return total_count

    def paste_selected(self):
        """Seçili öğeleri yapıştır - gelişmiş kopyalama ile"""
        print("🔄 PASTE İŞLEMİ BAŞLADI")
        
        if not self.clipboard_data:
            print("❌ Pano boş!")
            messagebox.showwarning("Uyarı", "Pano boş - önce dosya kopyalayın veya kesin!")
            return
            
        print(f"📋 Pano içeriği: {len(self.clipboard_data)} öğe")
        
        # Gerçek toplam öğe sayısını hesapla (klasör içlerini dahil ederek)
        print("📊 Toplam öğe sayısı hesaplanıyor...")
        total_items = self._count_total_items_recursive(self.clipboard_data)
        print(f"📊 Toplam öğe sayısı: {total_items}")
        
        # Progress dialog
        if len(self.clipboard_data) > 1 or (len(self.clipboard_data) == 1 and os.path.isdir(self.clipboard_data[0]['path'])):
            progress_dialog = self._create_progress_dialog("Yapıştırma İşlemi", "Dosyalar yapıştırılıyor...")
            
            processed_items = [0]  # List kullanarak reference passing
            
            def progress_callback(progress, current, total):
                if progress_dialog and not progress_dialog.cancelled:
                    progress_dialog.update_progress(progress, f"{current}/{total_items} öğe")
                elif progress_dialog and progress_dialog.cancelled:
                    raise Exception("İşlem kullanıcı tarafından iptal edildi")
        else:
            progress_dialog = None
            progress_callback = None
            processed_items = [0]
        
        try:
            self.gui.status_var.set("Yapıştırma işlemi başlatılıyor...")
            
            for item_data in self.clipboard_data:
                if progress_dialog and progress_dialog.cancelled:
                    break
                    
                source_path = item_data['path']
                source_name = os.path.basename(source_path)
                target_path = os.path.join(self.current_path, source_name)
                
                # Aynı konuma yapıştırma kontrolü - güvenli versiyon
                try:
                    same_location = os.path.samefile(os.path.dirname(source_path), self.current_path)
                except (OSError, ValueError):
                    # Farklı diskler veya hatalı path durumunda
                    same_location = os.path.normpath(os.path.dirname(source_path)).lower() == os.path.normpath(self.current_path).lower()
                
                if same_location:
                    # Aynı konuma yapıştırma - kopyalama durumunda yeniden adlandır
                    if item_data['operation'] == 'copy':
                        counter = 1
                        name, ext = os.path.splitext(source_name)
                        while os.path.exists(target_path):
                            if os.path.isdir(source_path):
                                new_name = f"{name} - Kopya ({counter})"
                            else:
                                new_name = f"{name} - Kopya ({counter}){ext}"
                            target_path = os.path.join(self.current_path, new_name)
                            counter += 1
                    else:
                        # Taşıma durumunda skip
                        if os.path.isdir(source_path):
                            # Klasör ise içindeki öğe sayısını processed_items'a ekle
                            try:
                                for root, dirs, files in os.walk(source_path):
                                    processed_items[0] += len(dirs) + len(files)
                            except:
                                processed_items[0] += 1
                        else:
                            processed_items[0] += 1
                        continue
                
                try:
                    # ÖĞRENMESİ: Cut işleminden önce öğren (dosya henüz mevcut)
                    if item_data['operation'] == 'cut' and os.path.isfile(source_path):
                        print(f"🎓 PASTE ÖĞRENME: Cut-paste işleminden öğrenme başlatılıyor")
                        print(f"🔍 DEBUG: source_path={source_path}, target_path={target_path}, current_path={self.current_path}")
                        self.detect_category_move_for_file(source_path, self.current_path)
                        print(f"🎓 PASTE ÖĞRENME TAMAMLANDI")
                    
                    if os.path.isdir(source_path):
                        # Klasör işlemi - gelişmiş progress callback ile
                        def folder_progress_callback(progress, current, total):
                            processed_items[0] = current
                            if progress_callback:
                                overall_progress = (processed_items[0] / total_items) * 100
                                progress_callback(overall_progress, processed_items[0], total_items)
                        
                        if item_data['operation'] == 'copy':
                            success, message = self.copy_folder_parallel(source_path, target_path, max_workers=4, progress_callback=folder_progress_callback)
                        else:  # cut/move
                            success, message = self.copy_folder_parallel(source_path, target_path, max_workers=4, progress_callback=folder_progress_callback)
                            if success:
                                # GÜVENLİK KONTROLÜ: Hedef klasörün gerçekten oluştuğunu doğrula
                                if os.path.exists(target_path) and os.path.isdir(target_path):
                                    # Klasör içeriğini karşılaştır
                                    source_files = set(os.listdir(source_path)) if os.path.exists(source_path) else set()
                                    target_files = set(os.listdir(target_path)) if os.path.exists(target_path) else set()
                                    
                                    # Kritik dosyalar kopyalandı mı kontrol et
                                    if len(source_files) > 0 and len(target_files) >= len(source_files) * 0.9:  # %90 dosya kopyalandıysa
                                        try:
                                            import shutil
                                            shutil.rmtree(source_path)
                                        except Exception as e:
                                            print(f"Uyarı: Kaynak klasör silinemedi ama kopyalama başarılı: {e}")
                                    else:
                                        print(f"Güvenlik nedeniyle kaynak klasör silinmedi. Kopyalama eksik görünüyor.")
                                        success = False
                                else:
                                    print("Hata: Hedef klasör oluşturulamadı, kaynak klasör silinmedi!")
                                    success = False
                    else:
                        # Dosya işlemi
                        def file_progress_callback(progress, bytes_done, file_total):
                            if progress >= 100:
                                processed_items[0] += 1
                                if progress_callback:
                                    overall_progress = (processed_items[0] / total_items) * 100
                                    progress_callback(overall_progress, processed_items[0], total_items)
                        
                        if item_data['operation'] == 'copy':
                            success, message = self.copy_file_optimized(source_path, target_path, file_progress_callback)
                        else:  # cut/move
                            success, message = self.copy_file_optimized(source_path, target_path, file_progress_callback)
                            if success:
                                # GÜVENLİK KONTROLÜ: Hedef dosyanın gerçekten oluştuğunu ve doğru boyutta olduğunu doğrula
                                if os.path.exists(target_path) and os.path.isfile(target_path):
                                    try:
                                        source_size = os.path.getsize(source_path)
                                        target_size = os.path.getsize(target_path)
                                        
                                        # Dosya boyutları eşleşiyorsa sil
                                        if source_size == target_size:
                                            os.remove(source_path)
                                        else:
                                            print(f"Hata: Dosya boyutları eşleşmiyor! Kaynak: {source_size}, Hedef: {target_size}. Güvenlik nedeniyle kaynak dosya silinmedi.")
                                            success = False
                                    except Exception as e:
                                        print(f"Uyarı: Kaynak dosya silinemedi ama kopyalama başarılı: {e}")
                                else:
                                    print("Hata: Hedef dosya oluşturulamadı, kaynak dosya silinmedi!")
                                    success = False
                    
                    if not success:
                        print(f"Hata: {source_name}: {message}")
                        
                except Exception as e:
                    print(f"Hata: {source_name}: {str(e)}")
            
            # Taşıma işleminde clipboard'u temizle
            if self.clipboard_data and self.clipboard_data[0]['operation'] == 'cut':
                self.clipboard_data = []
            
            if progress_dialog:
                if hasattr(progress_dialog, 'cancelled') and progress_dialog.cancelled:
                    progress_dialog.set_error("İşlem iptal edildi")
                else:
                    progress_dialog.set_completed(f"{processed_items[0]} öğe yapıştırıldı")
            
            self.refresh_target()
            
            if not progress_dialog or not (hasattr(progress_dialog, 'cancelled') and progress_dialog.cancelled):
                self.gui.status_var.set(f"{processed_items[0]} öğe başarıyla yapıştırıldı")
                
        except Exception as e:
            error_msg = f"Yapıştırma hatası: {str(e)}"
            if progress_dialog and hasattr(progress_dialog, 'set_error'):
                progress_dialog.set_error(error_msg)
            else:
                messagebox.showerror("Hata", error_msg)
                print(f"Yapıştırma hatası: {e}")
    
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
            messagebox.showwarning(t('dialogs.warning.title'), t('messages.select_file_for_properties'))
            return
        
        if len(items) > 1:
            messagebox.showwarning(t('dialogs.warning.title'), t('messages.select_single_file'))
            return
        
        file_path = items[0]
        try:
            stat = os.stat(file_path)
            import time
            
            file_type = t('properties.folder') if os.path.isdir(file_path) else t('properties.file')
            
            properties = f"""{t('properties.title')}:
            
{t('properties.name')}: {os.path.basename(file_path)}
{t('properties.path')}: {file_path}
{t('properties.size')}: {self.format_size(stat.st_size)}
{t('properties.created')}: {time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(stat.st_ctime))}
{t('properties.modified')}: {time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(stat.st_mtime))}
{t('properties.accessed')}: {time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(stat.st_atime))}
{t('properties.type')}: {file_type}
"""
            
            messagebox.showinfo(t('properties.title'), properties)
        except Exception as e:
            messagebox.showerror(t('dialogs.error.title'), t('messages.properties_error', error=str(e)))
    
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
    
    def copy_file_optimized(self, source_path, target_path, progress_callback=None):
        """Gelişmiş ve güvenli dosya kopyalama"""
        try:
            # Dosya kilitli mi kontrol et
            if self.is_file_locked(source_path):
                return False, "Dosya kullanımda"
            
            # Dosya boyutunu al
            file_size = os.path.getsize(source_path)
            
            # Hash verification için kaynak dosyanın hash'ini hesapla
            source_hash = self._calculate_file_hash(source_path)
            
            # Büyük dosyalar için gelişmiş kopyalama
            if file_size > 10 * 1024 * 1024:  # 10MB'dan büyükse
                success, message = self.copy_file_advanced(
                    source_path, target_path, file_size, source_hash, progress_callback
                )
            else:
                # Küçük dosyalar için hızlı kopyalama
                success, message = self.copy_file_fast(
                    source_path, target_path, source_hash
                )
            
            return success, message
            
        except Exception as e:
            return False, f"Kopyalama hatası: {str(e)}"
    
    def move_file_optimized(self, source_path, target_path, progress_callback=None):
        """Optimize edilmiş dosya taşıma - Aynı disk için hızlı rename, farklı disk için kopyala+sil"""
        try:
            # Kaynak ve hedef dosyaların disk sürücülerini kontrol et
            source_drive = os.path.splitdrive(os.path.abspath(source_path))[0].upper()
            target_drive = os.path.splitdrive(os.path.abspath(target_path))[0].upper()
            
            # Aynı disk ise hızlı rename kullan
            if source_drive == target_drive:
                try:
                    # Hedef dizin yoksa oluştur
                    target_dir = os.path.dirname(target_path)
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir, exist_ok=True)
                    
                    # Hızlı taşıma - sadece dosya tablosu güncellenir
                    os.rename(source_path, target_path)
                    
                    # Progress callback - anında %100
                    if progress_callback:
                        progress_callback(100, 1, 1)
                    
                    return True, "Dosya hızlı taşıma ile başarıyla taşındı"
                except Exception as e:
                    # Rename başarısız olursa fallback: kopyala+sil
                    print(f"⚠️ Hızlı taşıma başarısız, kopyala+sil moduna geçiliyor: {e}")
                    return self._move_file_copy_delete(source_path, target_path, progress_callback)
            else:
                # Farklı diskler - kopyala+sil gerekli
                return self._move_file_copy_delete(source_path, target_path, progress_callback)
                
        except Exception as e:
            return False, str(e)
    
    def _move_file_copy_delete(self, source_path, target_path, progress_callback=None):
        """Farklı diskler için kopyala+sil taşıma"""
        try:
            # Önce dosyayı kopyala
            success, message = self.copy_file_optimized(source_path, target_path, progress_callback)
            
            if success:
                # Kopyalama başarılıysa kaynak dosyayı sil
                try:
                    os.remove(source_path)
                    return True, "Dosya başarıyla taşındı (kopyala+sil)"
                except Exception as e:
                    # Silme başarısız olursa uyarı ver ama başarılı say
                    return True, f"Dosya kopyalandı ama orijinal silinemedi: {e}"
            else:
                return False, f"Taşıma başarısız: {message}"
                
        except Exception as e:
            return False, str(e)

    def copy_file_advanced(self, source_path, target_path, file_size, source_hash, progress_callback=None):
        """Gelişmiş büyük dosya kopyalama - Hash verification, Resume, Progress"""
        try:
            # Geçici dosya adı
            temp_target = target_path + ".tmp"
            
            # Resume capability - kısmi kopyalama var mı kontrol et
            start_position = 0
            if os.path.exists(temp_target):
                try:
                    start_position = os.path.getsize(temp_target)
                    if start_position >= file_size:
                        # Dosya zaten tamamen kopyalanmış, hash kontrol et
                        if self._verify_file_integrity(temp_target, source_hash):
                            os.rename(temp_target, target_path)
                            return True, "Dosya zaten kopyalanmış"
                        else:
                            # Hash uyuşmuyor, baştan kopyala
                            os.remove(temp_target)
                            start_position = 0
                except (OSError, PermissionError):
                    # Temp dosya silinemiyor, yeni isim dene
                    import random
                    temp_target = target_path + f".tmp{random.randint(1000,9999)}"
                    start_position = 0
            
            # Adaptive chunk size - dosya boyutuna göre ayarla
            chunk_size = self._calculate_optimal_chunk_size(file_size)
            
            # Kopyalama işlemi
            bytes_copied = start_position
            
            with open(source_path, 'rb') as src, open(temp_target, 'ab' if start_position > 0 else 'wb') as dst:
                # Resume için başlangıç pozisyonuna git
                if start_position > 0:
                    src.seek(start_position)
                
                while bytes_copied < file_size:
                    # Dinamik chunk size - kalan boyuta göre ayarla
                    remaining = file_size - bytes_copied
                    current_chunk_size = min(chunk_size, remaining)
                    
                    chunk = src.read(current_chunk_size)
                    if not chunk:
                        break
                    
                    dst.write(chunk)
                    dst.flush()  # Disk'e hemen yaz
                    os.fsync(dst.fileno())  # Sistem buffer'ını boşalt
                    
                    bytes_copied += len(chunk)
                    
                    # Progress callback
                    if progress_callback:
                        progress = (bytes_copied / file_size) * 100
                        progress_callback(progress, bytes_copied, file_size)
            
            # Hash verification - kopyalanan dosya doğru mu?
            if not self._verify_file_integrity(temp_target, source_hash):
                os.remove(temp_target)
                return False, "Hash verification failed - dosya bozuk"
            
            # Metadata kopyalama (timestamps, permissions)
            self._copy_metadata(source_path, temp_target)
            
            # Atomic rename - son adımda dosyayı gerçek adına çevir
            backup_path = None  # Başlangıçta None olarak tanımla
            try:
                # Hedef dosya varsa önce yedekle
                if os.path.exists(target_path):
                    backup_path = target_path + ".backup"
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    os.rename(target_path, backup_path)
                
                os.rename(temp_target, target_path)
                
                # Başarılıysa backup'ı sil
                if backup_path and os.path.exists(backup_path):
                    os.remove(backup_path)
                    
            except Exception as e:
                # Rename başarısız, backup'ı geri yükle
                if backup_path and os.path.exists(backup_path):
                    try:
                        if os.path.exists(target_path):
                            os.remove(target_path)
                        os.rename(backup_path, target_path)
                    except:
                        pass
                raise e
            
            return True, "Güvenli kopyalama tamamlandı"
            
        except Exception as e:
            # Cleanup
            if os.path.exists(temp_target):
                try:
                    os.remove(temp_target)
                except:
                    pass
            return False, f"Gelişmiş kopyalama hatası: {str(e)}"

    def copy_file_fast(self, source_path, target_path, source_hash):
        """Küçük dosyalar için hızlı kopyalama"""
        try:
            # Memory mapping ile hızlı kopyalama
            import mmap
            
            with open(source_path, 'rb') as src:
                with mmap.mmap(src.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_src:
                    with open(target_path, 'wb') as dst:
                        dst.write(mmapped_src)
                        dst.flush()
                        os.fsync(dst.fileno())
            
            # Hash verification
            if not self._verify_file_integrity(target_path, source_hash):
                os.remove(target_path)
                return False, "Hash verification failed"
            
            # Metadata kopyalama
            self._copy_metadata(source_path, target_path)
            
            return True, "Hızlı kopyalama tamamlandı"
            
        except Exception as e:
            # Fallback to standard copy
            try:
                shutil.copy2(source_path, target_path)
                if self._verify_file_integrity(target_path, source_hash):
                    return True, "Standart kopyalama tamamlandı"
                else:
                    os.remove(target_path)
                    return False, "Hash verification failed"
            except Exception as e2:
                return False, f"Hızlı kopyalama hatası: {str(e2)}"

    def _calculate_optimal_chunk_size(self, file_size):
        """Dosya boyutuna göre optimal chunk size hesapla"""
        if file_size < 100 * 1024 * 1024:  # 100MB'dan küçük
            return 1024 * 1024  # 1MB
        elif file_size < 1024 * 1024 * 1024:  # 1GB'dan küçük
            return 4 * 1024 * 1024  # 4MB
        else:  # 1GB'dan büyük
            return 8 * 1024 * 1024  # 8MB

    def _verify_file_integrity(self, file_path, expected_hash):
        """Dosya bütünlüğünü hash ile doğrula"""
        try:
            actual_hash = self._calculate_file_hash(file_path)
            return actual_hash == expected_hash
        except:
            return False

    def _copy_metadata(self, source_path, target_path):
        """Dosya metadata'sını kopyala (timestamps, permissions)"""
        try:
            stat = os.stat(source_path)
            os.utime(target_path, (stat.st_atime, stat.st_mtime))
            if hasattr(os, 'chmod'):
                os.chmod(target_path, stat.st_mode)
        except:
            pass  # Metadata kopyalama başarısız olsa da dosya kopyalama devam eder

    def copy_file_chunked(self, source_path, target_path):
        """Eski chunk-based kopyalama - geriye uyumluluk için"""
        return self.copy_file_optimized(source_path, target_path)

    def copy_folder_parallel(self, source_folder, target_folder, max_workers=4, progress_callback=None):
        """Paralel klasör kopyalama - çoklu thread ile"""
        import concurrent.futures
        import threading
        
        try:
            # Tüm dosyaları listele
            all_files = []
            
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    source_file = os.path.join(root, file)
                    rel_path = os.path.relpath(source_file, source_folder)
                    target_file = os.path.join(target_folder, rel_path)
                    
                    # Hedef klasörü oluştur
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    
                    file_size = os.path.getsize(source_file)
                    all_files.append((source_file, target_file, file_size))
            
            # Progress tracking
            copied_files = 0
            lock = threading.Lock()
            
            def file_progress_callback(progress, bytes_done, file_total):
                nonlocal copied_files
                with lock:
                    # Dosya tamamlandığında sayacı artır
                    if progress >= 100:
                        copied_files += 1
                        # Üst seviye progress callback'i çağır
                        if progress_callback:
                            progress_callback(0, copied_files, len(all_files))
            
            def copy_single_file(file_info):
                source_file, target_file, file_size = file_info
                return self.copy_file_optimized(source_file, target_file, file_progress_callback)
            
            # Paralel kopyalama
            failed_files = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {executor.submit(copy_single_file, file_info): file_info 
                                for file_info in all_files}
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file_info = future_to_file[future]
                    try:
                        success, message = future.result()
                        if not success:
                            failed_files.append((file_info[0], message))
                    except Exception as e:
                        failed_files.append((file_info[0], str(e)))
            
            if failed_files:
                error_msg = f"{len(failed_files)} dosya kopyalanamadı:\n"
                for file_path, error in failed_files[:5]:  # İlk 5 hatayı göster
                    error_msg += f"• {os.path.basename(file_path)}: {error}\n"
                if len(failed_files) > 5:
                    error_msg += f"... ve {len(failed_files) - 5} dosya daha"
                return False, error_msg
            
            return True, f"{len(all_files)} dosya başarıyla kopyalandı"
            
        except Exception as e:
            return False, f"Paralel kopyalama hatası: {str(e)}"
    
    def load_settings(self):
        """Ayarları yükle"""
        try:
            if os.path.exists('file_manager_settings.json'):
                with open('file_manager_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Son hedef klasörü yükle
                if 'target_path' in settings and settings['target_path']:
                    self.target_path = settings['target_path']
                    self.current_path = self.target_path
                    self.gui.target_var.set(self.target_path)
                    self.gui.current_path_var.set(self.current_path)
                    
                    # ÇÖZÜM: Hedef klasör içeriğini göster
                    if os.path.exists(self.target_path) and os.path.isdir(self.target_path):
                        print(f"📁 Son hedef klasör yükleniyor: {self.target_path}")
                        self.refresh_target(add_to_history=False)  # History'e ekleme, sadece göster
                        print(f"✅ Hedef klasör içeriği gösterildi")
                    else:
                        print(f"⚠️ Son hedef klasör bulunamadı: {self.target_path}")
                        # Geçersiz yol varsa temizle
                        self.target_path = ""
                        self.current_path = ""
                        self.gui.target_var.set("")
                        self.gui.current_path_var.set("")
                    
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
            
            # DİNAMİK ÖĞRENMESİ: Klasör taşıması sonrası kategori öğrenme
            target_path = os.path.join(target_folder, source_name)
            if os.path.isdir(target_path) and target_path != source_path:
                self.detect_category_move(target_path, target_folder)
                
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
        """Klasörü komple taşı - gelişmiş kopyalama ile"""
        try:
            target_path = os.path.join(target_folder, os.path.basename(source_path))
            
            if os.path.exists(target_path):
                # Hedefte aynı isimde klasör var
                action = self._ask_folder_merge_action(os.path.basename(source_path), target_path)
                if action == "cancel":
                    return
                elif action == "merge":
                    self._merge_folders_with_conflict_resolution(source_path, target_path)
                    return
                elif action == "rename":
                    counter = 1
                    base_name = os.path.basename(source_path)
                    while os.path.exists(target_path):
                        new_name = f"{base_name} ({counter})"
                        target_path = os.path.join(target_folder, new_name)
                        counter += 1
            
            # Progress dialog göster
            progress_dialog = self._create_progress_dialog("Klasör Taşınıyor", f"'{os.path.basename(source_path)}' taşınıyor...")
            
            def progress_callback(progress, current, total):
                if not progress_dialog.cancelled:
                    progress_dialog.update_progress(progress, f"{current}/{total} dosya")
                else:
                    # İptal edildi, işlemi durdur
                    raise Exception("İşlem kullanıcı tarafından iptal edildi")
            
            try:
                # Gelişmiş paralel kopyalama kullan
                success, message = self.copy_folder_parallel(source_path, target_path, max_workers=4, progress_callback=progress_callback)
                
                if success and not progress_dialog.cancelled:
                    # Kopyalama başarılı, kaynak klasörü sil
                    import shutil
                    shutil.rmtree(source_path)
                    progress_dialog.set_completed("Klasör başarıyla taşındı")
                elif progress_dialog.cancelled:
                    # İptal edildi, kopyalanmış dosyaları temizle
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    progress_dialog.set_error("İşlem iptal edildi")
                else:
                    progress_dialog.set_error(f"Taşıma hatası: {message}")
                    
            except Exception as e:
                progress_dialog.set_error(f"Taşıma hatası: {str(e)}")
                # Cleanup
                if os.path.exists(target_path):
                    try:
                        shutil.rmtree(target_path)
                    except:
                        pass
            
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör taşıma hatası: {e}")
    
    def _ask_folder_merge_action(self, folder_name, target_path):
        """Aynı isimde klasör varsa kullanıcıya ne yapacağını sor"""
        import tkinter as tk
        from tkinter import ttk
        
        # Özel dialog oluştur
        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Klasör Çakışması")
        dialog.geometry("550x300")
        dialog.transient(self.gui.root)
        dialog.grab_set()
        
        # Dialog'u merkeze yerleştir
        dialog.geometry("+%d+%d" % (self.gui.root.winfo_rootx() + 50, self.gui.root.winfo_rooty() + 50))
        
        result = {"action": "cancel"}  # Default
        
        # İçerik
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık ve açıklama
        title_label = ttk.Label(main_frame, text=f"📁 '{folder_name}' klasörü zaten mevcut!", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        desc_label = ttk.Label(main_frame, text=f"Hedef konumda: {target_path}", 
                              font=("Arial", 9))
        desc_label.pack(pady=(0, 20))
        
        # Seçenekler
        option_frame = ttk.Frame(main_frame)
        option_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Radio button değişkeni
        choice_var = tk.StringVar(value="merge")
        
        # Seçenek 1: İçerikleri birleştir (ÖNERILEN)
        merge_frame = ttk.LabelFrame(option_frame, text="🔄 İçerikleri Birleştir (Önerilen)", padding=10)
        merge_frame.pack(fill=tk.X, pady=(0, 10))
        
        merge_radio = ttk.Radiobutton(merge_frame, text="Bu seçeneği seç", 
                                     variable=choice_var, value="merge")
        merge_radio.pack(anchor=tk.W)
        
        ttk.Label(merge_frame, text="• Dosyalar mevcut klasörün içine taşınır\n• Aynı dosyalar varsa tekrar sorulur (üstüne yaz/atla)", 
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        
        # Seçenek 2: Yeni isimle oluştur  
        rename_frame = ttk.LabelFrame(option_frame, text="📝 Yeni İsimle Oluştur", padding=10)
        rename_frame.pack(fill=tk.X, pady=(0, 10))
        
        rename_radio = ttk.Radiobutton(rename_frame, text="Bu seçeneği seç", 
                                      variable=choice_var, value="rename")
        rename_radio.pack(anchor=tk.W)
        
        ttk.Label(rename_frame, text=f"• Yeni klasör oluşturur: {folder_name}_1", 
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        
        # Seçenek 3: İptal
        cancel_frame = ttk.LabelFrame(option_frame, text="❌ İptal Et", padding=10)
        cancel_frame.pack(fill=tk.X)
        
        cancel_radio = ttk.Radiobutton(cancel_frame, text="Bu seçeneği seç", 
                                      variable=choice_var, value="cancel")
        cancel_radio.pack(anchor=tk.W)
        
        ttk.Label(cancel_frame, text="• Klasör taşıma işlemini iptal et", 
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def on_ok():
            result["action"] = choice_var.get()
            dialog.destroy()
            
        def on_cancel():
            result["action"] = "cancel"
            dialog.destroy()
        
        ok_button = ttk.Button(button_frame, text="✅ Tamam", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=(0, 20))
        
        cancel_button = ttk.Button(button_frame, text="❌ İptal", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT)
        
        # Enter ve Escape tuş bağlamaları
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        # Focus ayarla
        ok_button.focus_set()
        
        # Dialog'u bekle
        dialog.wait_window()
        
        return result["action"]
    
    def _merge_folders_with_conflict_resolution(self, source_folder, target_folder):
        """Klasörleri birleştir - dosya çakışmalarını çözerek"""
        if not os.path.exists(source_folder):
            raise ValueError(f"Kaynak klasör bulunamadı: {source_folder}")
        
        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)
        
        print(f"🔄 Klasör birleştiriliyor: {source_folder} -> {target_folder}")
        
        # Toplam dosya sayısını hesapla
        total_files = 0
        for root, dirs, files in os.walk(source_folder):
            total_files += len(files)
        
        processed_files = 0
        moved_files = 0
        skipped_files = 0
        error_files = 0
        
        # Global mod kontrolü
        global_mode = None  # None, "skip_all", "overwrite_all"
        
        for root, dirs, files in os.walk(source_folder):
            # Relatif yol hesapla
            rel_path = os.path.relpath(root, source_folder)
            target_dir = os.path.join(target_folder, rel_path) if rel_path != '.' else target_folder
            
            # Hedef klasörü oluştur
            os.makedirs(target_dir, exist_ok=True)
            
            # Dosyaları işle
            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)
                
                processed_files += 1
                
                try:
                    # Dosya mevcutsa çakışma çözümü sor
                    if os.path.exists(target_file):
                        if global_mode == "skip_all":
                            skipped_files += 1
                            print(f"⏭️ Dosya atlandı (global): {file}")
                            continue
                        elif global_mode == "overwrite_all":
                            # Global overwrite modunda sor
                            pass
                        else:
                            action = self._ask_file_conflict_resolution(file, source_file, target_file)
                            
                            if action == "skip":
                                skipped_files += 1
                                print(f"⏭️ Dosya atlandı: {file}")
                                continue
                            elif action == "skip_all":
                                global_mode = "skip_all"
                                skipped_files += 1
                                print(f"⏭️ Dosya atlandı (global moda geçildi): {file}")
                                continue
                            elif action == "overwrite_all":
                                global_mode = "overwrite_all"
                                # Devam et ve üstüne yaz
                            # "overwrite" durumunda normal akış devam eder
                    
                    # Dosyayı taşı
                    shutil.move(source_file, target_file)
                    moved_files += 1
                    print(f"✅ Dosya birleştirildi: {file}")
                
                except Exception as e:
                    error_files += 1
                    print(f"❌ Dosya birleştirme hatası: {file} - {e}")
                    continue
        
        # Kaynak klasörü temizle (boş ise)
        try:
            if not os.listdir(source_folder):
                os.rmdir(source_folder)
                print(f"🗑️ Boş kaynak klasör silindi: {source_folder}")
            else:
                print(f"📁 Kaynak klasör korundu (içerik var): {source_folder}")
        except Exception as e:
            print(f"⚠️ Kaynak klasör temizleme hatası: {e}")
        
        # Sonuç raporu
        print(f"📊 BİRLEŞTİRME SONUCU:")
        print(f"   📄 Toplam dosya: {total_files}")
        print(f"   ✅ Taşınan: {moved_files}")
        print(f"   ⏭️ Atlanan: {skipped_files}")
        print(f"   ❌ Hata: {error_files}")
        
        # Status bar güncelle
        self.gui.status_var.set(f"Klasör birleştirildi: {moved_files} dosya taşındı, {skipped_files} atlandı")
    
    def _ask_file_conflict_resolution(self, filename, source_file, target_file):
        """Dosya çakışması durumunda kullanıcıya sor"""
        import tkinter as tk
        from tkinter import ttk
        
        # Özel dialog oluştur
        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Dosya Çakışması")
        dialog.geometry("500x250")
        dialog.transient(self.gui.root)
        dialog.grab_set()
        
        # Dialog'u merkeze yerleştir
        dialog.geometry("+%d+%d" % (self.gui.root.winfo_rootx() + 50, self.gui.root.winfo_rooty() + 50))
        
        result = {"action": "skip"}  # Default
        
        # İçerik
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Uyarı ikonu ve mesaj
        msg_frame = ttk.Frame(main_frame)
        msg_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(msg_frame, text="⚠️", font=("Arial", 24)).pack(side=tk.LEFT, padx=(0, 10))
        
        msg_text = f"Dosya zaten mevcut:\n\n📄 {filename}"
        ttk.Label(msg_frame, text=msg_text, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dosya bilgileri
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        try:
            source_size = os.path.getsize(source_file)
            target_size = os.path.getsize(target_file)
            source_time = os.path.getmtime(source_file)
            target_time = os.path.getmtime(target_file)
            
            import datetime
            source_date = datetime.datetime.fromtimestamp(source_time).strftime("%Y-%m-%d %H:%M")
            target_date = datetime.datetime.fromtimestamp(target_time).strftime("%Y-%m-%d %H:%M")
            
            info_text = f"Kaynak: {self.format_size(source_size)} - {source_date}\nHedef:  {self.format_size(target_size)} - {target_date}"
            ttk.Label(info_frame, text=info_text, font=("Arial", 9)).pack()
            
        except Exception:
            pass
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def on_skip():
            result["action"] = "skip"
            dialog.destroy()
            
        def on_overwrite():
            result["action"] = "overwrite"
            dialog.destroy()
            
        def on_skip_all():
            result["action"] = "skip_all"
            dialog.destroy()
            
        def on_overwrite_all():
            result["action"] = "overwrite_all"
            dialog.destroy()
        
        ttk.Button(button_frame, text="⏭️ Atla", command=on_skip).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📝 Üstüne Yaz", command=on_overwrite).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="⏭️ Tümünü Atla", command=on_skip_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📝 Tümünü Yaz", command=on_overwrite_all).pack(side=tk.LEFT)
        
        # Dialog'u bekle
        dialog.wait_window()
        
        return result["action"]
    
    def _move_single_file(self, source_path, target_folder):
        """Tek dosya taşıma - gelişmiş kopyalama ile"""
        try:
            filename = os.path.basename(source_path)
            target_path = os.path.join(target_folder, filename)
            
            # Duplikat kontrolü
            if os.path.exists(target_path):
                if self._files_are_identical(source_path, target_path):
                    # Aynı dosya, kaynak dosyayı sil
                    os.remove(source_path)
                    return
                else:
                    # Farklı dosya, kullanıcıya sor
                    action = self._ask_file_conflict_resolution(filename, source_path, target_path)
                    if action == "skip":
                        return
                    elif action == "rename":
                        counter = 1
                        name, ext = os.path.splitext(filename)
                        while os.path.exists(target_path):
                            new_filename = f"{name} ({counter}){ext}"
                            target_path = os.path.join(target_folder, new_filename)
                            counter += 1
            
            # Progress dialog - küçük dosyalar için basit
            file_size = os.path.getsize(source_path)
            if file_size > 50 * 1024 * 1024:  # 50MB'dan büyük dosyalar için progress göster
                progress_dialog = self._create_progress_dialog("Dosya Taşınıyor", f"'{filename}' taşınıyor...")
                
                def progress_callback(progress, bytes_done, file_total):
                    if not progress_dialog.cancelled:
                        progress_dialog.update_progress(progress, f"{self.format_size(bytes_done)}/{self.format_size(file_total)}")
                    else:
                        raise Exception("İşlem kullanıcı tarafından iptal edildi")
                
                try:
                    # Gelişmiş kopyalama
                    success, message = self.copy_file_optimized(source_path, target_path, progress_callback)
                    
                    if success and not progress_dialog.cancelled:
                        os.remove(source_path)  # Kaynak dosyayı sil
                        progress_dialog.set_completed("Dosya başarıyla taşındı")
                    elif progress_dialog.cancelled:
                        if os.path.exists(target_path):
                            os.remove(target_path)
                        progress_dialog.set_error("İşlem iptal edildi")
                    else:
                        progress_dialog.set_error(f"Taşıma hatası: {message}")
                        
                except Exception as e:
                    progress_dialog.set_error(f"Taşıma hatası: {str(e)}")
                    if os.path.exists(target_path):
                        try:
                            os.remove(target_path)
                        except:
                            pass
            else:
                # Küçük dosyalar için basit kopyalama
                success, message = self.copy_file_optimized(source_path, target_path)
                if success:
                    os.remove(source_path)
                else:
                    raise Exception(message)
            
            # ÖĞRENMESİ: Dosya taşıma işleminden öğren
            file_extension = os.path.splitext(source_path)[1].lower()
            if file_extension:
                print(f"🎓 DOSYA TAŞIMA ÖĞRENME: {file_extension} -> {target_folder}")
                print(f"🔍 DEBUG: source_path={source_path}, target_folder={target_folder}")
                self.detect_category_move_for_file(source_path, target_folder)
                print(f"🎓 DOSYA TAŞIMA ÖĞRENME TAMAMLANDI")
                    
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya taşıma hatası: {e}")
    
    def _move_folder_with_categorization(self, source_folder, target_folder):
        """Klasörü kategorilere göre organize ederek taşı"""
        print(f"🗂️ Klasör kategorilere göre taşınıyor: {source_folder} -> {target_folder}")
        
        # GÜVENLIK KONTROLLÜ: Kaynak klasörün varlığını kontrol et
        if not os.path.exists(source_folder):
            print(f"❌ Kaynak klasör bulunamadı: {source_folder}")
            return
        
        if not os.path.isdir(source_folder):
            print(f"❌ Kaynak bir klasör değil: {source_folder}")
            return
        
        # Hedef klasör analizi yap (kaynak klasörü hariç tut)
        target_analysis = self._analyze_target_folders_for_move(target_folder, exclude_folder=source_folder)
        
        # Klasördeki tüm dosyaları tara (SADECE DOSYALAR, ALT KLASÖRLER KORUNACAK)
        files_to_move = []
        original_file_count = 0
        
        for root, dirs, files in os.walk(source_folder):
            # Gizli klasörleri atla
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):  # Gizli dosyaları atla
                    file_path = os.path.join(root, file)
                    files_to_move.append(file_path)
                    original_file_count += 1
        
        print(f"📊 Taşınacak dosya sayısı: {len(files_to_move)}")
        
        if len(files_to_move) == 0:
            print("⚠️ Taşınacak dosya bulunamadı!")
            return
        
        # GÜVENLIK: Dosyaların mevcut olduğunu kontrol et
        existing_files = []
        for file_path in files_to_move:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                existing_files.append(file_path)
            else:
                print(f"⚠️ Dosya bulunamadı veya erişilemiyor: {file_path}")
        
        files_to_move = existing_files
        print(f"📊 Mevcut dosya sayısı: {len(files_to_move)}")
        
        # Dosyaları kategorilerine göre organize et
        moved_count = 0
        duplicate_count = 0
        error_count = 0
        
        for file_path in files_to_move:
            try:
                # GÜVENLIK: Her dosya taşınmadan önce tekrar kontrol et
                if not os.path.exists(file_path):
                    print(f"⚠️ Dosya artık mevcut değil: {file_path}")
                    error_count += 1
                    continue
                
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
                    if file_ext in category_info['subfolders']:
                        subfolder = category_info['subfolders'][file_ext]
                    else:
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
                        print(f"✅ Duplikat çözüldü ve taşındı: {file_name}")
                    else:
                        duplicate_count += 1
                        print(f"⏭️ Duplikat atlandı: {file_name}")
                else:
                    # GÜVENLIK: Hedef dosya zaten var mı kontrol et
                    if os.path.exists(target_file_path):
                        print(f"⚠️ Hedef dosya zaten mevcut: {target_file_path}")
                        # Yeni isim üret
                        base_name, ext = os.path.splitext(file_name)
                        counter = 1
                        while os.path.exists(target_file_path):
                            new_name = f"{base_name}_{counter}{ext}"
                            target_file_path = os.path.join(final_target_folder, new_name)
                            counter += 1
                        print(f"📝 Yeni isim: {os.path.basename(target_file_path)}")
                    
                    # Dosyayı güvenli şekilde taşı
                    try:
                        shutil.move(file_path, target_file_path)
                        moved_count += 1
                        print(f"✅ Taşındı: {file_name} -> {final_target_folder}")
                        
                        # DOĞRULAMA: Dosyanın başarıyla taşındığını kontrol et
                        if not os.path.exists(target_file_path):
                            print(f"❌ HATA: Dosya taşınamadı! {file_name}")
                            error_count += 1
                        elif os.path.exists(file_path):
                            print(f"❌ HATA: Kaynak dosya hala mevcut! {file_name}")
                            error_count += 1
                            
                    except Exception as move_error:
                        print(f"❌ Taşıma hatası: {file_name} - {move_error}")
                        error_count += 1
                        continue
                
            except Exception as e:
                print(f"❌ Hata: {file_path} işlenirken - {e}")
                error_count += 1
                continue
        
        # ÖNEMLİ: Kaynak klasörü SİLME - sadece boş ise temizle
        try:
            # Alt klasörleri kontrol et
            remaining_items = []
            for root, dirs, files in os.walk(source_folder):
                remaining_items.extend(files)
                remaining_items.extend(dirs)
            
            if len(remaining_items) == 0:
                # Tamamen boş - silebiliriz
                os.rmdir(source_folder)
                print(f"🗑️ Boş kaynak klasör silindi: {source_folder}")
            else:
                print(f"📁 Kaynak klasör korundu (içinde {len(remaining_items)} öğe kaldı): {source_folder}")
                
        except Exception as cleanup_error:
            print(f"⚠️ Kaynak klasör temizleme hatası: {cleanup_error}")
        
        # Sonuç raporu
        print(f"📈 TAŞIMA SONUCU:")
        print(f"   📊 Toplam dosya: {original_file_count}")
        print(f"   ✅ Başarıyla taşınan: {moved_count}")
        print(f"   ⏭️ Duplikat atlanan: {duplicate_count}")
        print(f"   ❌ Hata olan: {error_count}")
        
        # BAŞARI ORANI KONTROLÜ
        success_rate = (moved_count / original_file_count * 100) if original_file_count > 0 else 0
        if success_rate < 50:
            print(f"⚠️ UYARI: Başarı oranı düşük (%{success_rate:.1f})")
        else:
            print(f"✅ İşlem başarıyla tamamlandı (%{success_rate:.1f} başarı)")
    
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
        """İki dosyanın içeriği aynı mı kontrol et - Optimize edilmiş"""
        try:
            # 1. Hızlı boyut kontrolü
            size1 = os.path.getsize(file1)
            size2 = os.path.getsize(file2)
            
            if size1 != size2:
                return False
            
            # 2. Küçük dosyalar için direkt hash karşılaştırması (1MB altı)
            if size1 < 1024 * 1024:  # 1MB
                hash1 = self._calculate_file_hash(file1)
                hash2 = self._calculate_file_hash(file2)
                return hash1 == hash2 and hash1 is not None
            
            # 3. Büyük dosyalar için önce değişiklik tarihi kontrolü
            stat1 = os.stat(file1)
            stat2 = os.stat(file2)
            
            # Eğer boyutlar aynı ama değişiklik tarihleri farklıysa muhtemelen farklı dosyalar
            if abs(stat1.st_mtime - stat2.st_mtime) > 1:  # 1 saniye tolerans
                # Yine de emin olmak için hash kontrolü yap (ama sadece başlangıç)
                return self._quick_hash_check(file1, file2)
            
            # 4. Büyük dosyalar için kısmi hash kontrolü (ilk ve son 64KB)
            return self._partial_hash_check(file1, file2, size1)
            
        except Exception as e:
            print(f"❌ Dosya karşılaştırma hatası: {e}")
            return False

    def _quick_hash_check(self, file1, file2, chunk_size=65536):
        """Hızlı hash kontrolü - sadece ilk 64KB'yi kontrol et"""
        try:
            with open(file1, "rb") as f1, open(file2, "rb") as f2:
                chunk1 = f1.read(chunk_size)
                chunk2 = f2.read(chunk_size)
                return chunk1 == chunk2
        except Exception:
            return False

    def _partial_hash_check(self, file1, file2, file_size, chunk_size=65536):
        """Kısmi hash kontrolü - başlangıç, orta ve son kısımları kontrol et"""
        try:
            with open(file1, "rb") as f1, open(file2, "rb") as f2:
                # İlk 64KB
                chunk1_start = f1.read(chunk_size)
                chunk2_start = f2.read(chunk_size)
                
                if chunk1_start != chunk2_start:
                    return False
                
                # Dosya yeterince büyükse ortayı da kontrol et
                if file_size > chunk_size * 3:
                    mid_pos = file_size // 2
                    f1.seek(mid_pos)
                    f2.seek(mid_pos)
                    
                    chunk1_mid = f1.read(chunk_size)
                    chunk2_mid = f2.read(chunk_size)
                    
                    if chunk1_mid != chunk2_mid:
                        return False
                
                # Son 64KB (dosya yeterince büyükse)
                if file_size > chunk_size * 2:
                    f1.seek(-chunk_size, 2)  # Dosya sonundan 64KB geriye
                    f2.seek(-chunk_size, 2)
                    
                    chunk1_end = f1.read(chunk_size)
                    chunk2_end = f2.read(chunk_size)
                    
                    if chunk1_end != chunk2_end:
                        return False
                
                # Tüm kontroller geçtiyse muhtemelen aynı dosya
                return True
                
        except Exception as e:
            print(f"❌ Kısmi hash kontrol hatası: {e}")
            return False
    
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
            from lang_manager import lang_manager
            response = messagebox.askyesnocancel(
                lang_manager.get_text('dialogs.duplicate_found.title'),
                f"'{os.path.basename(source_file)}' {lang_manager.get_text('dialogs.file_conflict.message')}\n\n"
                f"{lang_manager.get_text('buttons.ok')}: Numara ekleyerek taşı\n"
                f"{lang_manager.get_text('dialogs.file_conflict.skip')}: {lang_manager.get_text('dialogs.file_conflict.skip')}\n"
                f"{lang_manager.get_text('buttons.cancel')}: İşlemi durdur"
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
            
            info_text = f"""📁 {t('properties.folder_properties')}

📂 {t('properties.folder_name')}: {folder_name}
📍 {t('properties.full_path')}: {self.current_path}
📊 {t('properties.total_size')}: {self.format_size(total_size)}
📄 {t('status.file_count')}: {total_files}
📁 {t('status.folder_count')}: {total_folders}
📈 {t('properties.total_items')}: {total_files + total_folders}"""

            messagebox.showinfo(t('properties.folder_properties'), info_text)
            
        except Exception as e:
            messagebox.showerror(t('dialogs.error.title'), t('messages.folder_info_error', error=str(e))) 
    
    def create_full_default_categories_json(self):
        """DEFAULT kategori sistemindeki TÜM uzantıları tam JSON formatına çevir"""
        try:
            default_categories = self.get_file_categories()
            learned_categories = {}
            
            # Tüm default kategorilerden uzantıları çıkar
            for category_key, category_info in default_categories.items():
                if category_key == 'other_files':  # Other files'ı atla
                    continue
                
                # Bu kategorideki tüm uzantıları learned_categories'e ekle
                for extension in category_info['extensions']:
                    learned_categories[extension] = category_key
            
            print(f"🔧 FULL DEFAULT MAPPING: {len(learned_categories)} extensions mapped to categories")
            return learned_categories
            
        except Exception as e:
            print(f"⚠️ Default JSON oluşturma hatası: {e}")
            return {}

    def load_learned_categories(self):
        """KALıCı ÇÖZÜM: TARGET-BAZLI kategorileri yükle veya tam default JSON oluştur"""
        try:
            if not hasattr(self, 'target_path') or not self.target_path:
                print("⚠️ Target path henüz set edilmemiş")
                return
            
            # Target klasöründe JSON dosyası ara
            target_json_path = os.path.join(self.target_path, 'learned_categories.json')
            
            if os.path.exists(target_json_path):
                # MEVCUT JSON DOSYASINI YÜKLE
                with open(target_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Format kontrolü
                if isinstance(data, dict) and 'learned_categories' in data:
                    # Yeni detaylı format
                    self.learned_categories = data.get('learned_categories', {})
                    self.category_confidence = data.get('category_confidence', {})
                    self.category_conflicts = data.get('category_conflicts', {})
                    print(f"✅ EXISTING TARGET JSON: {len(self.learned_categories)} categories loaded")
                else:
                    # Basit format - sadece uzantı->kategori
                    self.learned_categories = data
                    self.category_confidence = {}
                    self.category_conflicts = {}
                    print(f"✅ EXISTING TARGET JSON: {len(self.learned_categories)} simple categories loaded")
                
                # DEFAULT SYNC: Default kategorilerle senkronize et
                sync_updated = self._sync_with_default_categories()
                if sync_updated:
                    print(f"🔄 SYNC: Default kategorilerle senkronize edildi, JSON güncellenecek")
                    self.save_learned_categories()
                
                self.gui.status_var.set(f"📚 Target learning: {len(self.learned_categories)} extensions")
            else:
                # JSON YOK - FULL DEFAULT SİSTEMDEN TAM JSON OLUŞTUR
                print(f"📂 NO TARGET JSON: Creating complete default mapping for all extensions")
                self.learned_categories = self.create_full_default_categories_json()
                self.category_confidence = {}
                self.category_conflicts = {}
                
                # Yeni oluşturulan tam JSON'ı kaydet
                if self.learned_categories:
                    self.save_learned_categories()
                    print(f"✅ FULL DEFAULT MAPPING SAVED: {len(self.learned_categories)} extensions auto-mapped")
                    self.gui.status_var.set(f"🚀 Auto-created: {len(self.learned_categories)} extension mappings")
                else:
                    print("⚠️ Default mapping creation failed")
                    self.gui.status_var.set("⚠️ Default mapping failed")
                
        except Exception as e:
            print(f"⚠️ Target learning load error: {e}")
            self.learned_categories = {}
            self.category_confidence = {}
            self.category_conflicts = {}
            self.gui.status_var.set(f"⚠️ Learning error: {e}")
    
    def save_learned_categories(self):
        """TARGET KLASÖR BAZLI öğrenme kaydet"""
        try:
            if not self.target_path:
                return
                
            # Target klasöründe kaydet
            target_json_path = os.path.join(self.target_path, 'learned_categories.json')
            
            # Tüm öğrenme verilerini birleştir
            save_data = {
                'learned_categories': self.learned_categories,
                'category_confidence': getattr(self, 'category_confidence', {}),
                'category_conflicts': getattr(self, 'category_conflicts', {}),
                'target_path': self.target_path,
                'last_updated': time.time(),
                'version': '3.0',
                'description': 'Target-specific learning for file categorization'
            }
            
            # JSON formatını düzelt
            formatted_data = {}
            for ext, cat in save_data['learned_categories'].items():
                if isinstance(cat, str):
                    formatted_data[ext] = cat
                elif isinstance(cat, dict):
                    formatted_data[ext] = cat.get('category', '')
            
            save_data['learned_categories'] = formatted_data
            
            # JSON'ı kaydet
            with open(target_json_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.gui.status_var.set(f"Learned categories saved: {len(formatted_data)} extensions")
            
        except Exception as e:
            self.gui.status_var.set(f"Save error: {e}")
    
    def _get_target_drive(self):
        """Hedef klasörün drive'ını belirle"""
        try:
            if hasattr(self, 'target_path') and self.target_path:
                # Windows için drive letter (C:, D:, etc.)
                drive = os.path.splitdrive(self.target_path)[0]
                if drive:
                    return drive + os.sep  # C:\ formatında döndür
                
                # Linux/Mac için root path
                return "/"
            return None
        except Exception as e:
            print(f"⚠️ Drive belirleme hatası: {e}")
            return None
    
    def _get_disk_info(self, drive_path):
        """Disk bilgilerini al"""
        try:
            import shutil
            if drive_path and os.path.exists(drive_path):
                total, used, free = shutil.disk_usage(drive_path)
                
                # Disk etiketi almaya çalış (Windows)
                label = "Bilinmiyor"
                try:
                    import win32api
                    label = win32api.GetVolumeInformation(drive_path)[0] or "Etiket Yok"
                except:
                    # Windows API yoksa basit isim kullan
                    label = f"Disk {drive_path}"
                
                return {
                    'label': label,
                    'drive_path': drive_path,
                    'total_size': self.format_size(total),
                    'free_size': self.format_size(free),
                    'used_size': self.format_size(used)
                }
        except Exception as e:
            print(f"⚠️ Disk bilgisi alınamadı: {e}")
        
        return {}
    
    def _analyze_existing_categories_on_disk(self):
        """İlk kez kullanılan harddiskte mevcut kategori yapısını analiz et ve öğren"""
        try:
            if not hasattr(self, 'target_path') or not self.target_path:
                return
            
            print(f"🔍 {self.target_path} diskinde mevcut kategori yapısı analiz ediliyor...")
            
            # Ana klasörleri tara
            for item in os.listdir(self.target_path):
                item_path = os.path.join(self.target_path, item)
                
                if os.path.isdir(item_path) and not self._is_system_folder_for_move(item):
                    # Bu klasör bir kategori olabilir mi?
                    category = self._determine_category_from_path(item_path)
                    
                    if category and category != 'other_files':
                        print(f"📂 Kategori tespit edildi: {item} -> {category}")
                        
                        # Alt klasörleri kontrol et (uzantı klasörleri)
                        self._scan_category_subfolders(item_path, category)
            
            # Öğrenilenleri kaydet
            if self.learned_categories:
                self.save_learned_categories()
                print(f"✅ {len(self.learned_categories)} uzantı mevcut yapıdan öğrenildi")
        
        except Exception as e:
            print(f"⚠️ Mevcut kategori analizi hatası: {e}")
    
    def _scan_category_subfolders(self, category_path, category):
        """Kategori klasörü içindeki uzantı klasörlerini tara ve öğren"""
        try:
            for subfolder in os.listdir(category_path):
                subfolder_path = os.path.join(category_path, subfolder)
                
                if os.path.isdir(subfolder_path):
                    # Alt klasör adı uzantı olabilir mi?
                    potential_extension = f".{subfolder.lower()}"
                    
                    # Klasördeki dosyaları kontrol et
                    has_matching_files = False
                    file_count = 0
                    
                    for file in os.listdir(subfolder_path):
                        if os.path.isfile(os.path.join(subfolder_path, file)):
                            file_count += 1
                            file_ext = os.path.splitext(file)[1].lower()
                            if file_ext == potential_extension:
                                has_matching_files = True
                    
                    # Eğer klasörde bu uzantıdan dosyalar varsa öğren
                    if has_matching_files and file_count > 0:
                        print(f"📁 Uzantı klasörü bulundu: {potential_extension} -> {category} ({file_count} dosya)")
                        
                        # Öğren
                        self.learned_categories[potential_extension] = category
                        
                        if not hasattr(self, 'category_confidence'):
                            self.category_confidence = {}
                        
                        self.category_confidence[potential_extension] = {
                            'category': category,
                            'confidence': 95,  # Mevcut yapıdan öğrenme = %95 güven
                            'source': 'existing_structure',
                            'timestamp': time.time(),
                            'learned_folder': subfolder_path
                        }
        
        except Exception as e:
            print(f"⚠️ Alt klasör tarama hatası: {e}")
    
    def detect_category_move(self, moved_folder_path, target_parent_path):
        """KULLANICI TERCİHİ ÖĞRENME SİSTEMİ - Güçlendirilmiş Versiyon"""
        try:
            # Taşınan klasörün adını al
            folder_name = os.path.basename(moved_folder_path).upper()
            
            # Hedef klasörün kategori ismini belirle
            target_category = self._determine_category_from_path(target_parent_path)
            
            if target_category and target_category != 'other_files':
                print(f"🎯 KULLANICI TERCİHİ TESPİT EDİLDİ: {folder_name} -> {target_category}")
                
                # 1. UZANTI KLASÖRÜ TAŞIMA - En güçlü öğrenme sinyali
                potential_extension = f".{folder_name.lower()}"
                
                # Mevcut kategori sisteminde bu uzantı var mı?
                current_category = self._find_extension_in_categories(potential_extension)
                
                if current_category:
                    if current_category != target_category:
                        # KATEGORİ DEĞİŞİKLİĞİ - Kullanıcı farklı bir kategori seçti
                        print(f"🔄 KATEGORİ DEĞİŞİKLİĞİ: {potential_extension} {current_category} -> {target_category}")
                        self._override_extension_category(potential_extension, current_category, target_category)
                    else:
                        # AYNI KATEGORİ - Tercihi pekiştir
                        print(f"✅ KATEGORİ PEKİŞTİRME: {potential_extension} -> {target_category}")
                        self._reinforce_extension_category(potential_extension, target_category)
                else:
                    # YENİ UZANTI - İlk kez öğreniliyor
                    print(f"🆕 YENİ UZANTI ÖĞRENMESİ: {potential_extension} -> {target_category}")
                    self._learn_new_extension(potential_extension, target_category)
                
                # 2. KLASÖR İÇERİĞİ ÖĞRENME - Taşınan klasördeki dosyalardan öğren
                if os.path.exists(moved_folder_path):
                    self._learn_from_folder_contents_enhanced(moved_folder_path, target_category)
                    
        except Exception as e:
            print(f"⚠️ Kategori öğrenme hatası: {e}")
    
    def detect_category_move_for_file(self, moved_file_path, target_folder):
        """DOSYA TAŞIMA ÖĞRENME SİSTEMİ - Tek dosya için"""
        try:
            # Dosya uzantısını al
            file_extension = os.path.splitext(moved_file_path)[1].lower()
            if not file_extension:
                print("⚠️ Uzantısız dosya - öğrenme yapılmadı")
                return
            
            # Hedef klasörün kategori ismini belirle
            target_category = self._determine_category_from_path(target_folder)
            
            if target_category and target_category != 'other_files':
                print(f"🎯 DOSYA TAŞIMA ÖĞRENME: {file_extension} -> {target_category}")
                
                # Mevcut kategori sisteminde bu uzantı var mı?
                current_category = self._find_extension_in_categories(file_extension)
                
                if current_category:
                    if current_category != target_category:
                        # KATEGORİ DEĞİŞİKLİĞİ - Kullanıcı farklı bir kategori seçti
                        print(f"🔄 UZANTI KATEGORİ DEĞİŞİKLİĞİ: {file_extension} {current_category} -> {target_category}")
                        self._override_extension_category(file_extension, current_category, target_category)
                    else:
                        # AYNI KATEGORİ - Tercihi pekiştir
                        print(f"✅ UZANTI PEKİŞTİRME: {file_extension} -> {target_category}")
                        self._reinforce_extension_category(file_extension, target_category)
                else:
                    # YENİ UZANTI - İlk kez öğreniliyor
                    print(f"🆕 YENİ UZANTI ÖĞRENMESİ: {file_extension} -> {target_category}")
                    self._learn_new_extension(file_extension, target_category)
                
                # Öğrenilenleri kaydet
                self.save_learned_categories()
                print(f"💾 Öğrenme kaydedildi: {file_extension} -> {target_category}")
            else:
                print(f"⚠️ Hedef kategori belirlenemedi: {target_folder}")
                    
        except Exception as e:
            import traceback
            print(f"⚠️ Dosya öğrenme hatası: {e}")
            print(f"⚠️ TRACEBACK: {traceback.format_exc()}")

    def _override_extension_category(self, extension, old_category, new_category):
        """Kullanıcı farklı kategori seçti - eski kategoriyi geçersiz kıl"""
        try:
            # Kullanıcının açık tercihi
            self.learned_categories[extension] = new_category
            
            # Güven skoru ekle - kullanıcı tercihi en yüksek güven
            if not hasattr(self, 'category_confidence'):
                self.category_confidence = {}
            
            self.category_confidence[extension] = {
                'category': new_category,
                'confidence': 100,  # Kullanıcı tercihi = %100 güven
                'source': 'user_override',
                'timestamp': time.time()
            }
            
            # Hemen JSON'ı güncelle
            self.save_learned_categories()
            
            # GUI'yi güncelle
            self.gui.status_var.set(lang_manager.get_text('messages.category_changed', extension=extension, category=new_category))
            print(f"✅ KATEGORİ DEĞİŞTİRİLDİ: {extension} -> {new_category}")
            
        except Exception as e:
            print(f"❌ Kategori değiştirme hatası: {e}")
            print(f"❌ TRACEBACK: {traceback.format_exc()}")

    def _reinforce_extension_category(self, extension, category):
        """Aynı kategori seçimi - tercihi güçlendir"""
        try:
            # Öğrenme verilerini güncelle
            self.learned_categories[extension] = category
            
            if not hasattr(self, 'category_confidence'):
                self.category_confidence = {}
            
            # Güven skorunu artır
            current_confidence = self.category_confidence.get(extension, {}).get('confidence', 50)
            new_confidence = min(100, current_confidence + 10)
            
            self.category_confidence[extension] = {
                'category': category,
                'confidence': new_confidence,
                'source': 'user_reinforcement',
                'timestamp': time.time()
            }
            
            # Hemen JSON'ı güncelle
            self.save_learned_categories()
            
            # GUI'yi güncelle
            print(f"✨ KATEGORİ PEKİŞTİRİLDİ: {extension} -> {category} (güven: {new_confidence}%)")
            
        except Exception as e:
            print(f"❌ Kategori pekiştirme hatası: {e}")
            print(f"❌ TRACEBACK: {traceback.format_exc()}")

    def _learn_new_extension(self, extension, category):
        """Yeni uzantı öğrenme"""
        try:
            # Öğrenme verilerini güncelle
            self.learned_categories[extension] = category
            
            if not hasattr(self, 'category_confidence'):
                self.category_confidence = {}
            
            self.category_confidence[extension] = {
                'category': category,
                'confidence': 80,  # Yeni öğrenme = %80 güven
                'source': 'user_teaching',
                'timestamp': time.time()
            }
            
            # Hemen JSON'ı güncelle
            self.save_learned_categories()
            
            # GUI'yi güncelle
            self.gui.status_var.set(lang_manager.get_text('messages.extension_learned', extension=extension, category=category))
            print(f"✅ YENİ UZANTI ÖĞRENİLDİ: {extension} -> {category}")
            
        except Exception as e:
            print(f"❌ Yeni uzantı öğrenme hatası: {e}")
            print(f"❌ TRACEBACK: {traceback.format_exc()}")

    def _learn_from_folder_contents_enhanced(self, folder_path, target_category):
        """Klasör içeriğinden gelişmiş öğrenme"""
        try:
            learned_extensions = []
            
            # Klasördeki dosyaları analiz et
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                
                if os.path.isfile(item_path):
                    extension = os.path.splitext(item)[1].lower()
                    
                    if extension and len(extension) > 1:  # Geçerli uzantı
                        # Bu uzantı için mevcut tercihi kontrol et
                        current_preference = self.learned_categories.get(extension)
                        
                        if not current_preference:
                            # Hiç öğrenilmemiş - öğren
                            self.learned_categories[extension] = target_category
                            learned_extensions.append(extension)
                            print(f"📚 KLASÖR İÇERİĞİNDEN: {extension} -> {target_category}")
                        elif current_preference != target_category:
                            # Çakışma var - kullanıcının bu hareketi düşük güvenle kaydet
                            if not hasattr(self, 'category_conflicts'):
                                self.category_conflicts = {}
                            
                            if extension not in self.category_conflicts:
                                self.category_conflicts[extension] = []
                            
                            self.category_conflicts[extension].append({
                                'suggested_category': target_category,
                                'timestamp': time.time(),
                                'source': 'folder_content'
                            })
                            
                            print(f"⚠️ KATEGORİ ÇAKIŞMASI: {extension} ({current_preference} vs {target_category})")
            
            if learned_extensions:
                self.save_learned_categories()
                self.gui.status_var.set(lang_manager.get_text('messages.folder_learning', count=len(learned_extensions)))
                
        except Exception as e:
            print(f"⚠️ Klasör içeriği öğrenme hatası: {e}")
    
    def get_file_category_with_learning(self, file_path):
        """YENİ TARGET-BAZLI öğrenme sistemi ile kategori belirleme"""
        extension = os.path.splitext(file_path)[1].lower()
        
        # 1. TARGET-BAZLI ÖĞRENME KONTROLÜ
        if hasattr(self, 'learned_categories') and self.learned_categories and extension in self.learned_categories:
            learned_info = self.learned_categories[extension]
            categories = self.get_file_categories()
            
            # learned_info string ise (basit format: uzantı -> kategori)
            if isinstance(learned_info, str):
                learned_cat_key = learned_info
                confidence = 95  # Target-bazlı öğrenme yüksek güven
            else:
                # Detaylı format - dict
                learned_cat_key = learned_info.get('category', '')
                confidence = learned_info.get('confidence', 95)
            
            # Kategori anahtarını kontrol et
            if learned_cat_key in categories:
                print(f"🎯 TARGET LEARNING APPLIED: {extension} -> {learned_cat_key} (confidence: {confidence}%)")
                return learned_cat_key, categories[learned_cat_key]
            else:
                # Eski kategori adı olabilir, güncelle
                print(f"⚠️ Unknown learned category key: {learned_cat_key}, falling back to default")
        
        # 2. DEFAULT İNGİLİZCE KATEGORİ SİSTEMİ
        return self.get_file_category(file_path)
    
    def _determine_category_from_path(self, folder_path):
        """Hedef klasörün kategori ismini belirle - Geliştirilmiş versiyon"""
        try:
            # Klasör adını al
            folder_name = os.path.basename(folder_path).lower()
            
            # Kategori eşleştirme tablosu
            category_mapping = {
                'image files': 'image_files',
                'images': 'image_files',
                'resimler': 'image_files',
                'fotograflar': 'image_files',
                'document files': 'document_files',
                'documents': 'document_files',
                'belgeler': 'document_files',
                'video files': 'video_files',
                'videos': 'video_files',
                'videolar': 'video_files',
                'audio files': 'audio_files',
                'audios': 'audio_files',
                'sesler': 'audio_files',
                'müzikler': 'audio_files',
                'archive files': 'archive_files',
                'archives': 'archive_files',
                'arşivler': 'archive_files',
                'program files': 'program_files',
                'programs': 'program_files',
                'uygulamalar': 'program_files',
                'cad and 3d files': 'cad_3d_files',
                'cad files': 'cad_3d_files',
                '3d files': 'cad_3d_files',
                'code files': 'code_files',
                'codes': 'code_files',
                'kodlar': 'code_files',
                'font files': 'font_files',
                'fonts': 'font_files',
                'yazı tipleri': 'font_files'
            }
            
            # Doğrudan eşleşme kontrolü
            if folder_name in category_mapping:
                return category_mapping[folder_name]
            
            # Kısmi eşleşme kontrolü
            for key, value in category_mapping.items():
                if key in folder_name:
                    return value
            
            # Klasör içeriğinden kategori tahmini
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                file_extensions = set()
                for file in os.listdir(folder_path):
                    if os.path.isfile(os.path.join(folder_path, file)):
                        ext = os.path.splitext(file)[1].lower()
                        if ext:
                            file_extensions.add(ext)
                
                # En yaygın kategoriyi bul
                category_counts = defaultdict(int)
                for ext in file_extensions:
                    category = self._find_extension_in_categories(ext)
                    if category:
                        category_counts[category] += 1
                
                if category_counts:
                    return max(category_counts.items(), key=lambda x: x[1])[0]
            
            return None
            
        except Exception as e:
            print(f"⚠️ Kategori belirleme hatası: {e}")
            return None
    
    def _find_extension_in_categories(self, extension):
        """Uzantının hangi kategoride olduğunu bul"""
        try:
            categories = self.get_file_categories()
            
            for cat_name, cat_info in categories.items():
                if extension in cat_info['extensions']:
                    return cat_name
            
            return None
            
        except Exception as e:
            print(f"⚠️ Uzantı kategorisi bulunamadı: {e}")
            return None
    
    def _check_learned_category_for_scan(self, extension):
        """YENİ TARGET-BAZLI tarama aşamasında öğrenilen kategoriyi kontrol et"""
        if not extension or not hasattr(self, 'learned_categories'):
            return None
        
        # Öğrenilen kategorileri yükle (target-bazlı)
        if not self.learned_categories:
            self.load_learned_categories()
        
        # Target'ta öğrenme yoksa default sistem
        if not self.learned_categories:
            print(f"📂 DEFAULT SYSTEM: No target learning for {extension}")
            return None
        
        # Uzantı normalize et
        extension_key = extension.lower()
        if not extension_key.startswith('.'):
            extension_key = '.' + extension_key
        
        # Öğrenilen kategorilerde var mı kontrol et
        if extension_key in self.learned_categories:
            learned_info = self.learned_categories[extension_key]
            
            # learned_info string ise (basit format: uzantı -> kategori)
            if isinstance(learned_info, str):
                category = learned_info
                confidence = 95  # Target-bazlı öğrenme yüksek güven
            else:
                # Detaylı format - dict
                confidence = learned_info.get('confidence', 95)
                category = learned_info.get('category', '')
            
            if confidence >= 80:  # %80 ve üzeri confidence
                # Kategori anahtarını İngilizce klasör adına çevir
                categories = self.get_file_categories()
                if category in categories:
                    category_info = categories[category]
                    category_folder_name = category_info['folder']  # Sabit İngilizce
                    
                    print(f"🎯 TARGET LEARNING APPLIED: {extension} -> {category_folder_name} (confidence: {confidence}%)")
                    
                    # Sadece kategori klasör adını döndür - ScanEngine'in organization_structure'ına uygun
                    return {
                        'category': category,
                        'folder': category_folder_name,
                        'confidence': confidence
                    }
                else:
                    print(f"⚠️ Unknown learned category key: {category}, fallback to default")
        
        print(f"📂 DEFAULT SYSTEM: No learning found for {extension}")
        return None

    def _create_progress_dialog(self, title, message):
        """Progress dialog oluştur"""
        import tkinter as tk
        from tkinter import ttk
        
        class ProgressDialog:
            def __init__(self, parent, title, message):
                self.dialog = tk.Toplevel(parent)
                self.dialog.title(title)
                self.dialog.geometry("400x200")
                self.dialog.transient(parent)
                self.dialog.grab_set()
                self.dialog.resizable(False, False)
                
                # Center the dialog
                self.dialog.geometry("+%d+%d" % (
                    parent.winfo_rootx() + 50, 
                    parent.winfo_rooty() + 50
                ))
                
                # Main frame
                main_frame = ttk.Frame(self.dialog)
                main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                # Title label
                self.title_label = ttk.Label(main_frame, text=message, font=("Arial", 10, "bold"))
                self.title_label.pack(pady=(0, 15))
                
                # Progress bar
                self.progress_var = tk.DoubleVar()
                self.progress_bar = ttk.Progressbar(
                    main_frame, 
                    variable=self.progress_var, 
                    maximum=100,
                    mode='determinate'
                )
                self.progress_bar.pack(fill=tk.X, pady=(0, 10))
                
                # Status label
                self.status_label = ttk.Label(main_frame, text="Başlıyor...", font=("Arial", 9))
                self.status_label.pack(pady=(0, 15))
                
                # Cancel button
                self.cancel_button = ttk.Button(main_frame, text="İptal", command=self.cancel)
                self.cancel_button.pack()
                
                self.cancelled = False
                self.completed = False
                
                # Update the dialog
                self.dialog.update()
                
            def update_progress(self, progress, status_text=""):
                if not self.cancelled and not self.completed:
                    self.progress_var.set(progress)
                    if status_text:
                        self.status_label.config(text=status_text)
                    self.dialog.update_idletasks()
                    
            def set_completed(self, message="Tamamlandı"):
                self.completed = True
                self.progress_var.set(100)
                self.status_label.config(text=message)
                self.cancel_button.config(text="Kapat")
                self.dialog.update_idletasks()
                
                # Auto close after 2 seconds
                self.dialog.after(2000, self.close)
                
            def set_error(self, error_message):
                self.completed = True
                self.status_label.config(text=f"Hata: {error_message}")
                self.cancel_button.config(text="Kapat")
                self.dialog.update_idletasks()
                
            def cancel(self):
                if not self.completed:
                    self.cancelled = True
                self.close()
                
            def close(self):
                try:
                    self.dialog.destroy()
                except:
                    pass

    def _sync_with_default_categories(self):
        """Default kategorilerle JSON'u senkronize et - eksik uzantıları ekle, kaldırılanları sil"""
        try:
            # Default kategorilerden mevcut uzantıları al
            default_categories = self.get_file_categories()
            current_default_extensions = {}
            
            # Tüm default uzantıları topla
            for category_name, category_info in default_categories.items():
                if category_name == 'other_files' or category_name == 'software_packages':
                    continue  # Bu kategoriler özel
                
                for extension in category_info.get('extensions', []):
                    current_default_extensions[extension] = category_name
            
            # JSON'da eksik olan default uzantıları ekle
            added_count = 0
            for extension, category in current_default_extensions.items():
                if extension not in self.learned_categories:
                    self.learned_categories[extension] = category
                    added_count += 1
                    print(f"➕ SYNC ADD: {extension} → {category}")
            
            # JSON'da olan ama default'da olmayan uzantıları kontrol et (kullanıcı öğretmişse kalsın)
            removed_count = 0
            default_extension_list = list(current_default_extensions.keys())
            
            # Sadece default kategorilerden kaldırılan uzantıları sil
            # Kullanıcının öğrettiği (learned) uzantıları sakla
            for extension in list(self.learned_categories.keys()):
                # Eğer bu uzantı daha önce default'da vardı ama artık yoksa
                if (extension in default_extension_list and 
                    extension not in current_default_extensions and
                    not self._is_user_learned_extension(extension)):
                    del self.learned_categories[extension]
                    removed_count += 1
                    print(f"➖ SYNC REMOVE: {extension} (default'dan kaldırıldı)")
            
            if added_count > 0 or removed_count > 0:
                print(f"🔄 SYNC RESULT: +{added_count} eklendi, -{removed_count} kaldırıldı")
                return True
            else:
                print(f"✅ SYNC OK: Değişiklik gerekmiyor")
                return False
                
        except Exception as e:
            print(f"⚠️ Sync error: {e}")
            return False
    
    def _is_user_learned_extension(self, extension):
        """Bu uzantı kullanıcı tarafından öğretildi mi? (confidence veya conflict verisi var mı?)"""
        try:
            # Confidence verisi varsa kullanıcı öğretmiştir
            if hasattr(self, 'category_confidence') and extension in self.category_confidence:
                return True
            
            # Conflict verisi varsa kullanıcı öğretmiştir  
            if hasattr(self, 'category_conflicts') and extension in self.category_conflicts:
                return True
                
            # Bu uzantı hiç default kategorilerde yoksa kullanıcı öğretmiştir
            default_categories = self.get_file_categories()
            for category_info in default_categories.values():
                if extension in category_info.get('extensions', []):
                    return False  # Default'da var, kullanıcı öğretmesi değil
            
            return True  # Default'da yok, kullanıcı öğretmesi
            
        except Exception as e:
            print(f"⚠️ User learned check error: {e}")
            return True  # Şüphe durumunda kullanıcı öğretmesi say, silme

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