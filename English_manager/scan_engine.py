"""
Scan Engine Module
Contains file scanning, duplicate detection and organization algorithms
"""

import os
import hashlib
import threading
import time
from pathlib import Path
from collections import defaultdict
import tkinter as tk
from tkinter import messagebox

class ScanEngine:
    def __init__(self, gui_manager, file_operations):
        self.gui = gui_manager
        self.file_ops = file_operations
        
        # Scanning results
        self.all_scanned_files = []
        self.unique_files = []
        self.duplicate_files = []
        self.source_duplicates = []
        self.target_duplicates = []
        
        # Organization structure
        self.organization_structure = defaultdict(list)
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'unique_files': 0,
            'duplicate_files': 0,
            'total_size': 0,
            'categories': defaultdict(int)
        }
        
        # Thread kontrolü
        self.scan_thread = None
        self.stop_scanning = False
        
    def scan_files(self):
        """Main scanning function"""
        if not self.gui.source_var.get():
            messagebox.showwarning("Warning", "Please select source folder first!")
            return
        
        if self.scan_thread and self.scan_thread.is_alive():
            messagebox.showwarning("Warning", "Scanning already in progress!")
            return
        
        # Start thread
        self.stop_scanning = False
        self.scan_thread = threading.Thread(target=self._scan_thread, daemon=True)
        self.scan_thread.start()
    
    def _scan_thread(self):
        """Scanning thread"""
        try:
            # Start progress
            self.gui.progress_var.set(0)
            self.gui.status_var.set("Starting scan...")
            
            # Start time estimation
            self.gui.start_time_estimation()
            
            # Scan source folder
            source_path = self.gui.source_var.get()
            scan_mode = self.gui.scan_mode.get()  # Get scan_mode variable
            
            if not source_path or not os.path.exists(source_path):
                self.gui.root.after(0, lambda: self.gui.status_var.set("❌ Please select a valid source folder"))
                return
            
            self._scan_source_files(source_path, scan_mode)
            
            if not self.stop_scanning:
                # Duplicate detection
                self.gui.root.after(0, lambda: self.gui.status_var.set("Detecting duplicate files..."))
                self._detect_duplicates()
                
                if not self.stop_scanning:
                    # Create organization structure
                    self.gui.root.after(0, lambda: self.gui.status_var.set("Creating organization structure..."))
                    self._create_organization_structure()
                    
                    if not self.stop_scanning:
                        # Update results
                        self._update_scan_results()
                        
                        # Show statistics
                        self._show_scan_statistics()
            
        except Exception as e:
            self.gui.root.after(0, lambda: self.gui.status_var.set(f"❌ Scanning error: {e}"))
            print(f"Scanning error: {e}")
        finally:
            # Reset progress and stop time estimation
            self.gui.root.after(0, lambda: self.gui.progress_var.set(0))
            self.gui.root.after(0, lambda: self.gui.stop_time_estimation())
    
    def _scan_source_files(self, source_path, scan_mode):
        """Source files Scan"""
        self.all_scanned_files = []
        self.stats = {
            'total_files': 0,
            'unique_files': 0,
            'duplicate_files': 0,
            'total_size': 0,
            'categories': defaultdict(int)
        }
        
        # files topla
        files_to_scan = []
        
        if scan_mode == "all":
            # Tüm alt klasörleri Scan (files kategorilere ayır)
            for root, dirs, files in os.walk(source_path):
                if self.stop_scanning:
                    return
                
                # hidden klasörleri atla
                dirs[:] = [d for d in dirs if not self._is_hidden_folder(d)]
                
                for file in files:
                    if not self._is_hidden_file(file):
                        file_path = os.path.join(root, file)
                        files_to_scan.append(file_path)
                        
        elif scan_mode == "none":
            # Home klasördeki files ve klasörleri Scan (alt klasörler komple to be copied)
            try:
                for item in os.listdir(source_path):
                    if self.stop_scanning:
                        return
                    
                    item_path = os.path.join(source_path, item)
                    
                    if os.path.isfile(item_path) and not self._is_hidden_file(item):
                        # Normal files
                        files_to_scan.append(item_path)
                    elif os.path.isdir(item_path) and not self._is_hidden_folder(item):
                        # Alt klasörler - komple Folder olarak işaretle
                        folder_info = {
                            'path': item_path,
                            'name': item,
                            'is_folder': True,
                            'size': self._get_folder_size(item_path),
                            'modified': os.path.getmtime(item_path),
                            'extension': 'folder',
                            'Hash': None
                        }
                        self.all_scanned_files.append(folder_info)
                        self.stats['total_files'] += 1
                        self.stats['total_size'] += folder_info['size']
                        self.stats['categories']['Klasörler'] += 1
                        
            except PermissionError:
                pass
                
        elif scan_mode == "files_only":
            # Sadece Home klasördeki files Scan (alt klasörleri görmezden gel)
            try:
                for item in os.listdir(source_path):
                    if self.stop_scanning:
                        return
                    
                    item_path = os.path.join(source_path, item)
                    
                    # Sadece files ekle, klasörleri görmezden gel
                    if os.path.isfile(item_path) and not self._is_hidden_file(item):
                        files_to_scan.append(item_path)
                        
            except PermissionError:
                pass
        
        # files işle
        total_files = len(files_to_scan)
        
        for i, file_path in enumerate(files_to_scan):
            if self.stop_scanning:
                return
            
            try:
                # File bilgilerini al
                file_info = self._get_file_info(file_path)
                if file_info:
                    self.all_scanned_files.append(file_info)
                    self.stats['total_files'] += 1
                    self.stats['total_size'] += file_info['size']
                    
                    # Kategori istatistiği
                    category, _ = self.file_ops.get_file_category(file_path)
                    self.stats['categories'][category] += 1
                
                # Progress güncelle
                progress = (i + 1) / total_files * 50  # First %50
                self.gui.root.after(0, lambda p=progress: self.gui.progress_var.set(p))
                
                # Time estimation güncelle
                self.gui.root.after(0, lambda p=progress, processed=i+1, total=total_files: 
                                   self.gui.update_time_estimation(p, processed, total))
                
                # Update status
                if i % 50 == 0:
                    self.gui.root.after(0, lambda: self.gui.status_var.set(f"Scanning: {i+1}/{total_files}"))
                
                # UI donmasını önle
                if i % 100 == 0:
                    time.sleep(0.001)
                    
            except Exception as e:
                print(f"File işlenirken Error: {file_path} - {e}")
                continue
    
    def _get_file_info(self, file_path):
        """File bilgilerini al"""
        try:
            stat = os.stat(file_path)
            
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': Path(file_path).suffix.lower(),
                'Hash': None,  # Lazy loading
                'is_folder': False
            }
            
            return file_info
            
        except (OSError, PermissionError):
            return None
    
    def _get_folder_size(self, folder_path):
        """Folder boyutunu hesapla"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(folder_path):
                # hidden klasörleri atla
                dirs[:] = [d for d in dirs if not self._is_hidden_folder(d)]
                
                for file in files:
                    if not self._is_hidden_file(file):
                        try:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                        except (OSError, PermissionError):
                            continue
        except (OSError, PermissionError):
            pass
        
        return total_size
    
    def _is_hidden_file(self, filename):
        """hidden File kontrolü"""
        # Windows hidden files
        if filename.startswith('.'):
            return True
        
        # Sistem files
        system_files = [
            'thumbs.db', 'desktop.ini', 'folder.jpg', 'folder.png',
            'albumartsmall.jpg', 'albumart_{', '.ds_store',
            'system volume information', '$recycle.bin', 'recycler'
        ]
        
        if filename.lower() in system_files:
            return True
        
        # Geçici files
        temp_extensions = ['.tmp', '.temp', '.bak', '.old', '.cache', '.log']
        if any(filename.lower().endswith(ext) for ext in temp_extensions):
            return True
        
        return False
    
    def _is_hidden_folder(self, foldername):
        """hidden Folder kontrolü"""
        if foldername.startswith('.'):
            return True
        
        hidden_folders = [
            'system volume information', '$recycle.bin', 'recycler',
            '__pycache__', '.Go', '.svn', 'node_modules'
        ]
        
        return foldername.lower() in hidden_folders
    
    def _detect_duplicates(self):
        """Detect duplicate files"""
        self.duplicate_files = []
        self.unique_files = []
        self.source_duplicates = []
        
        # Duplicate Check seçeneklerini al
        check_name = self.gui.duplicate_check_name.get()
        check_size = self.gui.duplicate_check_size.get()
        check_hash = self.gui.duplicate_check_hash.get()
        
        # files grupla
        file_groups = defaultdict(list)
        
        total_files = len(self.all_scanned_files)
        
        for i, file_info in enumerate(self.all_scanned_files):
            if self.stop_scanning:
                return
            
            # Duplicate anahtarı oluştur
            key_parts = []
            
            if check_name:
                key_parts.append(file_info['name'].lower())
            
            if check_size:
                key_parts.append(str(file_info['size']))
            
            if check_hash:
                if not file_info['Hash']:
                    file_info['Hash'] = self._calculate_file_hash(file_info['path'])
                if file_info['Hash']:
                    key_parts.append(file_info['Hash'])
            
            # Anahtar oluştur
            if key_parts:
                key = '|'.join(key_parts)
                file_groups[key].append(file_info)
            
            # Progress güncelle
            progress = 50 + (i + 1) / total_files * 30  # %50-80 arası
            self.gui.root.after(0, lambda p=progress: self.gui.progress_var.set(p))
            
            # Time estimation güncelle
            self.gui.root.after(0, lambda p=progress: self.gui.update_time_estimation(p))
            
            # UI donmasını önle
            if i % 50 == 0:
                time.sleep(0.001)
        
        # Duplikatları ayır
        for key, files in file_groups.items():
            if len(files) > 1:
                # Duplicate grup
                self.duplicate_files.extend(files)
                self.source_duplicates.append(files)
            else:
                # Unique File
                self.unique_files.extend(files)
        
        # İstatistikleri güncelle
        self.stats['unique_files'] = len(self.unique_files)
        self.stats['duplicate_files'] = len(self.duplicate_files)
    
    def _calculate_file_hash(self, file_path, chunk_size=8192):
        """File Hash'ini hesapla"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def _create_organization_structure(self):
        """Organization yapısını oluştur"""
        self.organization_structure = defaultdict(lambda: defaultdict(list))
        
        # Target Folder analizi yap
        target_folder_analysis = self._analyze_target_folders()
        
        # Unique files organize et
        for file_info in self.unique_files:
            if self.stop_scanning:
                return
            
            # Folder mü kontrol et
            if file_info.get('is_folder', False):
                # Klasörler for Private kategori
                main_folder = "Klasörler"
                subfolder = "Alt Klasörler"
                self.organization_structure[main_folder][subfolder].append(file_info)
            else:
                # Normal files for kategori belirleme
                category, category_info = self.file_ops.get_file_category(file_info['path'])
                extension = file_info['extension']
                
                # Target folder uygun Folder var mı kontrol et
                suggested_folder = self._find_suitable_target_folder(extension, target_folder_analysis)
                
                if suggested_folder:
                    # available Folder found - doğrudan o folder yerleştir
                    print(f"📁 {extension} files available folder yerleştirilecek: {suggested_folder}")
                    
                    # available Folder for Private işaretleme
                    # organization_structure'a eklemek yerine, Private bir yapı kullan
                    if not hasattr(self, 'existing_folder_files'):
                        self.existing_folder_files = {}
                    
                    if suggested_folder not in self.existing_folder_files:
                        self.existing_folder_files[suggested_folder] = []
                    
                    self.existing_folder_files[suggested_folder].append(file_info)
                    
                else:
                    # Standart kategori kullan - New Folder oluştur
                    main_folder = category_info['folder']
                    
                    # Alt Folder
                    if extension in category_info['subfolders']:
                        subfolder = category_info['subfolders'][extension]
                    else:
                        subfolder = extension.replace('.', '').upper() if extension else 'Uzantisiz'
                    
                    print(f"📁 {extension} files New kategori klasörüne yerleştirilecek: {main_folder}/{subfolder}")
                    self.organization_structure[main_folder][subfolder].append(file_info)
        
        # Progress tamamla
        self.gui.root.after(0, lambda: self.gui.progress_var.set(100))
    
    def _analyze_target_folders(self):
        """Target klasördeki available klasörleri Analysis et (gelişmiş versiyon)"""
        target_path = self.file_ops.target_path
        source_path = self.file_ops.source_path
        folder_analysis = {}
        
        if not os.path.exists(target_path):
            return folder_analysis
        
        print("🔍 Gelişmiş Target Folder analizi starting...")
        
        try:
            # Derin Folder analizi yap (3 seviye derinlik)
            folder_analysis.update(self._analyze_directory_recursive(target_path, source_path, max_depth=3))
        
        except Exception as e:
            print(f"❌ Target Folder analizi hatası: {e}")
        
        return folder_analysis
    
    def _analyze_directory_recursive(self, directory_path, source_path, max_depth=3, current_depth=0, parent_path=""):
        """Klasörleri recursive olarak Analysis et"""
        analysis = {}
        
        if current_depth >= max_depth:
            return analysis
        
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if (os.path.isdir(item_path) and 
                    not self._is_system_folder(item) and
                    not self._is_source_folder(item_path, source_path)):
                    
                    # Klasördeki File uzantılarını Analysis et
                    extensions = self._analyze_folder_extensions(item_path, max_depth=5)
                    
                    if extensions:
                        # Folder yolu oluştur
                        if parent_path:
                            folder_key = f"{parent_path}/{item}"
                        else:
                            folder_key = item
                        
                        analysis[folder_key] = {
                            'path': item_path,
                            'extensions': extensions,
                            'file_count': sum(extensions.values()),
                            'level': current_depth
                        }
                        print(f"📂 {folder_key}: {list(extensions.keys())} uzantıları found ({sum(extensions.values())} File)")
                    
                    # Alt klasörleri de Analysis et
                    sub_analysis = self._analyze_directory_recursive(
                        item_path, source_path, max_depth, current_depth + 1, 
                        folder_key if extensions else (f"{parent_path}/{item}" if parent_path else item)
                    )
                    analysis.update(sub_analysis)
        
        except Exception as e:
            print(f"❌ Recursive Folder analizi hatası: {directory_path} - {e}")
        
        return analysis
    
    def _analyze_directory_level(self, directory_path, source_path, level=0, parent_name=""):
        """Belirli bir dizin seviyesini Analysis et"""
        analysis = {}
        
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if (os.path.isdir(item_path) and 
                    not self._is_system_folder(item) and
                    not self._is_source_folder(item_path, source_path)):
                    
                    # Klasördeki File uzantılarını Analysis et
                    extensions = self._analyze_folder_extensions(item_path, max_depth=3)
                    
                    if extensions:
                        # Folder adını oluştur
                        if level == 0:
                            folder_key = item
                        else:
                            folder_key = f"{parent_name}/{item}"
                        
                        analysis[folder_key] = {
                            'path': item_path,
                            'extensions': extensions,
                            'file_count': sum(extensions.values()),
                            'level': level
                        }
                        print(f"📂 {folder_key}: {list(extensions.keys())} uzantıları found ({sum(extensions.values())} File)")
        
        except Exception as e:
            print(f"❌ Dizin seviye analizi hatası: {directory_path} - {e}")
        
        return analysis
    
    def _is_system_folder(self, folder_name):
        """Sistem folder mü kontrol et"""
        system_folders = {
            'system volume information', '$recycle.bin', 'recycler',
            'windows', 'program files', 'program files (x86)', 'programdata',
            'users', 'temp', 'tmp', 'cache', '.Go', '.svn', 'node_modules',
            '__pycache__', '.vscode', '.idea', 'appdata', 'application data'
        }
        return folder_name.lower() in system_folders
    
    def _is_source_folder(self, folder_path, source_path):
        """Source folder mü kontrol et"""
        if not source_path or not os.path.exists(source_path):
            return False
        
        try:
            return os.path.samefile(folder_path, source_path)
        except:
            # File Path karşılaştırması failed olursa Name karşılaştırması yap
            return os.path.basename(folder_path) == os.path.basename(source_path)
    
    def _analyze_folder_extensions(self, folder_path, max_depth=5, current_depth=0):
        """Klasördeki File uzantılarını Analysis et (derin scanning)"""
        extensions = {}
        
        try:
            # os.walk with tüm alt klasörleri Scan
            for root, dirs, files in os.walk(folder_path):
                # Derinlik kontrolü
                current_level = root.count(os.sep) - folder_path.count(os.sep)
                if current_level >= max_depth:
                    continue
                
                # hidden klasörleri atla
                dirs[:] = [d for d in dirs if not d.startswith('.') and not self._is_system_folder(d)]
                
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
    
    def _find_suitable_target_folder(self, extension, target_analysis):
        """Uzantı for uygun Target Folder Find (gelişmiş versiyon)"""
        if not extension or not target_analysis:
            return None
        
        # En uygun folder Find
        best_folder = None
        best_score = 0
        
        # Dosyanın kategorisini belirle
        category, _ = self.file_ops.get_file_category(f"test{extension}")
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
                for cat, info in self.file_ops.get_file_categories().items():
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
            
            # 5. Home Folder önceliği
            if folder_info.get('level', 0) == 0:
                score += 25
            
            # 6. File Count bonus
            file_count = folder_info.get('file_count', 0)
            if file_count > 10:
                score += 20
            elif file_count > 5:
                score += 10
            
            if score > best_score:
                best_score = score
                best_folder = folder_name
                best_folder_path = folder_info['path']
        
        # Sadece gerçek tam eşleşme kabul et (uzantı var VE Folder Name eşleşiyor)
        # Skor >= 100 VE uzantı + Folder Name eşleşmesi olmalı
        if best_score >= 100:
            # Gerçek tam eşleşme mi kontrol et
            best_folder_extensions = target_analysis[best_folder]['extensions']
            if extension in best_folder_extensions:
                ext_name = extension.replace('.', '').upper()
                if ext_name in best_folder.upper() or best_folder.upper().endswith(ext_name):
                    print(f"📁 {extension} for gerçek tam eşleşme found: {best_folder} (skor: {best_score})")
                    return best_folder_path
        
        print(f"❌ {extension} for gerçek tam eşleşme not found - New Folder oluşturulacak")
        return None
    
    def _update_scan_results(self):
        """scanning sonuçlarını UI'da Show"""
        # Source tree'yi güncelle
        self._update_source_tree()
        
        # Preview tree'yi güncelle
        self._update_preview_tree()
        
        # Duplicate tree'yi güncelle
        self._update_duplicate_tree()
        
        # İstatistikleri Show
        self._show_scan_statistics()
    
    def _update_source_tree(self):
        """Source files tree'sini güncelle"""
        self.gui.source_tree.delete(*self.gui.source_tree.get_children())
        
        for file_info in self.all_scanned_files[:1000]:  # First 1000 File
            size_str = self._format_size(file_info['size'])
            
            if file_info.get('is_folder', False):
                file_type = '📁 Folder'
                display_name = f"📁 {file_info['name']}"
            else:
                file_type = file_info['extension'].upper() if file_info['extension'] else 'File'
                display_name = file_info['name']
            
            self.gui.source_tree.insert('', 'end', 
                                      text=display_name,
                                      values=(size_str, file_type))
    
    def _update_preview_tree(self):
        """Organization önizleme tree'sini güncelle"""
        self.gui.preview_tree.delete(*self.gui.preview_tree.get_children())
        
        for main_folder, subfolders in self.organization_structure.items():
            # Home Folder
            total_files = sum(len(files) for files in subfolders.values())
            main_item = self.gui.preview_tree.insert('', 'end', 
                                                   text=f"📁 {main_folder}",
                                                   values=(total_files,))
            
            # Alt klasörler
            for subfolder, files in subfolders.items():
                self.gui.preview_tree.insert(main_item, 'end',
                                           text=f"📂 {subfolder}",
                                           values=(len(files),))
    
    def _update_duplicate_tree(self):
        """Duplicate files tree'sini güncelle"""
        self.gui.duplicate_tree.delete(*self.gui.duplicate_tree.get_children())
        
        for i, duplicate_group in enumerate(self.source_duplicates):
            if len(duplicate_group) > 1:
                # Grup başlığı
                group_name = f"Duplicate Grup {i+1} ({len(duplicate_group)} File)"
                group_item = self.gui.duplicate_tree.insert('', 'end', 
                                                          text=group_name,
                                                          values=('', '', ''))
                
                # Grup files
                for file_info in duplicate_group:
                    size_str = self._format_size(file_info['size'])
                    hash_str = file_info.get('Hash', '')[:8] + '...' if file_info.get('Hash') else ''
                    
                    self.gui.duplicate_tree.insert(group_item, 'end',
                                                 text=file_info['name'],
                                                 values=(file_info['path'], size_str, hash_str))
    
    def _show_scan_statistics(self):
        """scanning istatistiklerini Show"""
        total_files = self.stats['total_files']
        unique_files = self.stats['unique_files']
        duplicate_files = self.stats['duplicate_files']
        total_size = self._format_size(self.stats['total_size'])
        
        stats_message = f"""scanning Completed!
        
📊 Statistics:
• Total File: {total_files}
• Unique File: {unique_files}
• Duplicate File: {duplicate_files}
• Total Size: {total_size}

📁 Kategoriler:"""
        
        for category, count in self.stats['categories'].items():
            if count > 0:
                stats_message += f"\n• {category.title()}: {count} File"
        
        self.gui.status_var.set(f"✅ {total_files} File tarandı - {unique_files} unique, {duplicate_files} Duplicate")
        
        # İsteğe Connected detaylı Report - popup kaldırıldı
        # if total_files > 0:
        #     messagebox.showinfo("scanning Sonuçları", stats_message)
    
    def _format_size(self, size_bytes):
        """File boyutunu formatla"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def stop_scan(self):
        """Taramayı Stop"""
        self.stop_scanning = True
        if self.scan_thread and self.scan_thread.is_alive():
            self.gui.status_var.set("scanning Stopping...")
    
    def get_organization_preview(self):
        """Organization önizlemesi al"""
        preview = {}
        
        for main_folder, subfolders in self.organization_structure.items():
            preview[main_folder] = {}
            for subfolder, files in subfolders.items():
                preview[main_folder][subfolder] = {
                    'count': len(files),
                    'size': sum(f['size'] for f in files),
                    'files': [f['name'] for f in files[:10]]  # First 10 File
                }
        
        return preview
    
    def get_scan_summary(self):
        """scanning özetini al"""
        return {
            'total_files': self.stats['total_files'],
            'unique_files': self.stats['unique_files'],
            'duplicate_files': self.stats['duplicate_files'],
            'total_size': self.stats['total_size'],
            'categories': dict(self.stats['categories']),
            'duplicate_groups': len(self.source_duplicates)
        } 