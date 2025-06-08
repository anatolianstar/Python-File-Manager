"""
Scan Engine Module
Dosya tarama, duplikat tespiti ve organizasyon algoritmalarını içerir
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
        
        # Tarama sonuçları
        self.all_scanned_files = []
        self.unique_files = []
        self.duplicate_files = []
        self.source_duplicates = []
        self.target_duplicates = []
        
        # Organizasyon yapısı
        self.organization_structure = defaultdict(list)
        
        # İstatistikler
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
        """Ana tarama fonksiyonu"""
        if not self.gui.source_var.get():
            messagebox.showwarning("Uyarı", "Önce kaynak klasör seçin!")
            return
        
        if self.scan_thread and self.scan_thread.is_alive():
            messagebox.showwarning("Uyarı", "Tarama zaten devam ediyor!")
            return
        
        # Thread başlat
        self.stop_scanning = False
        self.scan_thread = threading.Thread(target=self._scan_thread, daemon=True)
        self.scan_thread.start()
    
    def _scan_thread(self):
        """Tarama thread'i"""
        try:
            # Progress başlat
            self.gui.progress_var.set(0)
            self.gui.status_var.set("Tarama başlatılıyor...")
            
            # Time estimation başlat
            self.gui.start_time_estimation()
            
            # Kaynak klasörü tara
            source_path = self.gui.source_var.get()
            scan_mode = self.gui.scan_mode.get()  # Yeni: scan_mode değişkenini al
            
            if not source_path or not os.path.exists(source_path):
                self.gui.root.after(0, lambda: self.gui.status_var.set("❌ Geçerli bir kaynak klasör seçin"))
                return
            
            self._scan_source_files(source_path, scan_mode)
            
            if not self.stop_scanning:
                # Duplikat tespiti
                self.gui.root.after(0, lambda: self.gui.status_var.set("Duplikat dosyalar tespit ediliyor..."))
                self._detect_duplicates()
                
                if not self.stop_scanning:
                    # Organizasyon yapısı oluştur
                    self.gui.root.after(0, lambda: self.gui.status_var.set("Organizasyon yapısı oluşturuluyor..."))
                    self._create_organization_structure()
                    
                    if not self.stop_scanning:
                        # Sonuçları güncelle
                        self._update_scan_results()
                        
                        # İstatistikleri göster
                        self._show_scan_statistics()
            
        except Exception as e:
            self.gui.root.after(0, lambda: self.gui.status_var.set(f"❌ Tarama hatası: {e}"))
            print(f"Tarama hatası: {e}")
        finally:
            # Progress sıfırla ve time estimation durdur
            self.gui.root.after(0, lambda: self.gui.progress_var.set(0))
            self.gui.root.after(0, lambda: self.gui.stop_time_estimation())
    
    def _scan_source_files(self, source_path, scan_mode):
        """Kaynak dosyaları tara"""
        self.all_scanned_files = []
        self.stats = {
            'total_files': 0,
            'unique_files': 0,
            'duplicate_files': 0,
            'total_size': 0,
            'categories': defaultdict(int)
        }
        
        # Dosyaları topla
        files_to_scan = []
        
        if scan_mode == "all":
            # Tüm alt klasörleri tara (dosyaları kategorilere ayır)
            for root, dirs, files in os.walk(source_path):
                if self.stop_scanning:
                    return
                
                # Gizli klasörleri atla
                dirs[:] = [d for d in dirs if not self._is_hidden_folder(d)]
                
                for file in files:
                    if not self._is_hidden_file(file):
                        file_path = os.path.join(root, file)
                        files_to_scan.append(file_path)
                        
        elif scan_mode == "none":
            # Ana klasördeki dosyaları ve klasörleri tara (alt klasörler komple kopyalanacak)
            try:
                for item in os.listdir(source_path):
                    if self.stop_scanning:
                        return
                    
                    item_path = os.path.join(source_path, item)
                    
                    if os.path.isfile(item_path) and not self._is_hidden_file(item):
                        # Normal dosyalar
                        files_to_scan.append(item_path)
                    elif os.path.isdir(item_path) and not self._is_hidden_folder(item):
                        # Alt klasörler - komple klasör olarak işaretle
                        folder_info = {
                            'path': item_path,
                            'name': item,
                            'is_folder': True,
                            'size': self._get_folder_size(item_path),
                            'modified': os.path.getmtime(item_path),
                            'extension': 'folder',
                            'hash': None
                        }
                        self.all_scanned_files.append(folder_info)
                        self.stats['total_files'] += 1
                        self.stats['total_size'] += folder_info['size']
                        self.stats['categories']['Klasörler'] += 1
                        
            except PermissionError:
                pass
                
        elif scan_mode == "files_only":
            # Sadece ana klasördeki dosyaları tara (alt klasörleri görmezden gel)
            try:
                for item in os.listdir(source_path):
                    if self.stop_scanning:
                        return
                    
                    item_path = os.path.join(source_path, item)
                    
                    # Sadece dosyaları ekle, klasörleri görmezden gel
                    if os.path.isfile(item_path) and not self._is_hidden_file(item):
                        files_to_scan.append(item_path)
                        
            except PermissionError:
                pass
        
        # Dosyaları işle
        total_files = len(files_to_scan)
        
        for i, file_path in enumerate(files_to_scan):
            if self.stop_scanning:
                return
            
            try:
                # Dosya bilgilerini al
                file_info = self._get_file_info(file_path)
                if file_info:
                    self.all_scanned_files.append(file_info)
                    self.stats['total_files'] += 1
                    self.stats['total_size'] += file_info['size']
                    
                    # Kategori istatistiği
                    category, _ = self.file_ops.get_file_category(file_path)
                    self.stats['categories'][category] += 1
                
                # Progress güncelle
                progress = (i + 1) / total_files * 50  # İlk %50
                self.gui.root.after(0, lambda p=progress: self.gui.progress_var.set(p))
                
                # Time estimation güncelle
                self.gui.root.after(0, lambda p=progress, processed=i+1, total=total_files: 
                                   self.gui.update_time_estimation(p, processed, total))
                
                # Status güncelle
                if i % 50 == 0:
                    self.gui.root.after(0, lambda: self.gui.status_var.set(f"Taranıyor: {i+1}/{total_files}"))
                
                # UI donmasını önle
                if i % 100 == 0:
                    time.sleep(0.001)
                    
            except Exception as e:
                print(f"Dosya işlenirken hata: {file_path} - {e}")
                continue
    
    def _get_file_info(self, file_path):
        """Dosya bilgilerini al"""
        try:
            stat = os.stat(file_path)
            
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': Path(file_path).suffix.lower(),
                'hash': None,  # Lazy loading
                'is_folder': False
            }
            
            return file_info
            
        except (OSError, PermissionError):
            return None
    
    def _get_folder_size(self, folder_path):
        """Klasör boyutunu hesapla"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(folder_path):
                # Gizli klasörleri atla
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
        """Gizli dosya kontrolü"""
        # Windows gizli dosyaları
        if filename.startswith('.'):
            return True
        
        # Sistem dosyaları
        system_files = [
            'thumbs.db', 'desktop.ini', 'folder.jpg', 'folder.png',
            'albumartsmall.jpg', 'albumart_{', '.ds_store',
            'system volume information', '$recycle.bin', 'recycler'
        ]
        
        if filename.lower() in system_files:
            return True
        
        # Geçici dosyalar
        temp_extensions = ['.tmp', '.temp', '.bak', '.old', '.cache', '.log']
        if any(filename.lower().endswith(ext) for ext in temp_extensions):
            return True
        
        return False
    
    def _is_hidden_folder(self, foldername):
        """Gizli klasör kontrolü"""
        if foldername.startswith('.'):
            return True
        
        hidden_folders = [
            'system volume information', '$recycle.bin', 'recycler',
            '__pycache__', '.git', '.svn', 'node_modules'
        ]
        
        return foldername.lower() in hidden_folders
    
    def _detect_duplicates(self):
        """Duplikat dosyaları tespit et"""
        self.duplicate_files = []
        self.unique_files = []
        self.source_duplicates = []
        
        # Duplikat kontrol seçeneklerini al
        check_name = self.gui.duplicate_check_name.get()
        check_size = self.gui.duplicate_check_size.get()
        check_hash = self.gui.duplicate_check_hash.get()
        
        # Dosyaları grupla
        file_groups = defaultdict(list)
        
        total_files = len(self.all_scanned_files)
        
        for i, file_info in enumerate(self.all_scanned_files):
            if self.stop_scanning:
                return
            
            # Duplikat anahtarı oluştur
            key_parts = []
            
            if check_name:
                key_parts.append(file_info['name'].lower())
            
            if check_size:
                key_parts.append(str(file_info['size']))
            
            if check_hash:
                if not file_info['hash']:
                    file_info['hash'] = self._calculate_file_hash(file_info['path'])
                if file_info['hash']:
                    key_parts.append(file_info['hash'])
            
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
                # Duplikat grup
                self.duplicate_files.extend(files)
                self.source_duplicates.append(files)
            else:
                # Unique dosya
                self.unique_files.extend(files)
        
        # İstatistikleri güncelle
        self.stats['unique_files'] = len(self.unique_files)
        self.stats['duplicate_files'] = len(self.duplicate_files)
    
    def _calculate_file_hash(self, file_path, chunk_size=8192):
        """Dosya hash'ini hesapla"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def _create_organization_structure(self):
        """Organizasyon yapısını oluştur"""
        self.organization_structure = defaultdict(lambda: defaultdict(list))
        
        # Hedef klasör analizi yap
        target_folder_analysis = self._analyze_target_folders()
        
        # Unique dosyaları organize et
        for file_info in self.unique_files:
            if self.stop_scanning:
                return
            
            # Klasör mü kontrol et
            if file_info.get('is_folder', False):
                # Klasörler için özel kategori
                main_folder = "Klasörler"
                subfolder = "Alt Klasörler"
                self.organization_structure[main_folder][subfolder].append(file_info)
            else:
                # Normal dosyalar için kategori belirleme
                category, category_info = self.file_ops.get_file_category(file_info['path'])
                extension = file_info['extension']
                
                # Hedef klasörde uygun klasör var mı kontrol et
                suggested_folder = self._find_suitable_target_folder(extension, target_folder_analysis)
                
                if suggested_folder:
                    # Mevcut klasör bulundu - doğrudan o klasöre yerleştir
                    print(f"📁 {extension} dosyaları mevcut klasöre yerleştirilecek: {suggested_folder}")
                    
                    # Mevcut klasör için özel işaretleme
                    # organization_structure'a eklemek yerine, özel bir yapı kullan
                    if not hasattr(self, 'existing_folder_files'):
                        self.existing_folder_files = {}
                    
                    if suggested_folder not in self.existing_folder_files:
                        self.existing_folder_files[suggested_folder] = []
                    
                    self.existing_folder_files[suggested_folder].append(file_info)
                    
                else:
                    # Standart kategori kullan - yeni klasör oluştur
                    main_folder = category_info['folder']
                    
                    # Alt klasör
                    if extension in category_info['subfolders']:
                        subfolder = category_info['subfolders'][extension]
                    else:
                        subfolder = extension.replace('.', '').upper() if extension else 'Uzantisiz'
                    
                    print(f"📁 {extension} dosyaları yeni kategori klasörüne yerleştirilecek: {main_folder}/{subfolder}")
                    self.organization_structure[main_folder][subfolder].append(file_info)
        
        # Progress tamamla
        self.gui.root.after(0, lambda: self.gui.progress_var.set(100))
    
    def _analyze_target_folders(self):
        """Hedef klasördeki mevcut klasörleri analiz et (gelişmiş versiyon)"""
        target_path = self.file_ops.target_path
        source_path = self.file_ops.source_path
        folder_analysis = {}
        
        if not os.path.exists(target_path):
            return folder_analysis
        
        print("🔍 Gelişmiş hedef klasör analizi başlatılıyor...")
        
        try:
            # Derin klasör analizi yap (3 seviye derinlik)
            folder_analysis.update(self._analyze_directory_recursive(target_path, source_path, max_depth=3))
        
        except Exception as e:
            print(f"❌ Hedef klasör analizi hatası: {e}")
        
        return folder_analysis
    
    def _analyze_directory_recursive(self, directory_path, source_path, max_depth=3, current_depth=0, parent_path=""):
        """Klasörleri recursive olarak analiz et"""
        analysis = {}
        
        if current_depth >= max_depth:
            return analysis
        
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if (os.path.isdir(item_path) and 
                    not self._is_system_folder(item) and
                    not self._is_source_folder(item_path, source_path)):
                    
                    # Klasördeki dosya uzantılarını analiz et
                    extensions = self._analyze_folder_extensions(item_path, max_depth=5)
                    
                    if extensions:
                        # Klasör yolu oluştur
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
                        print(f"📂 {folder_key}: {list(extensions.keys())} uzantıları bulundu ({sum(extensions.values())} dosya)")
                    
                    # Alt klasörleri de analiz et
                    sub_analysis = self._analyze_directory_recursive(
                        item_path, source_path, max_depth, current_depth + 1, 
                        folder_key if extensions else (f"{parent_path}/{item}" if parent_path else item)
                    )
                    analysis.update(sub_analysis)
        
        except Exception as e:
            print(f"❌ Recursive klasör analizi hatası: {directory_path} - {e}")
        
        return analysis
    
    def _analyze_directory_level(self, directory_path, source_path, level=0, parent_name=""):
        """Belirli bir dizin seviyesini analiz et"""
        analysis = {}
        
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if (os.path.isdir(item_path) and 
                    not self._is_system_folder(item) and
                    not self._is_source_folder(item_path, source_path)):
                    
                    # Klasördeki dosya uzantılarını analiz et
                    extensions = self._analyze_folder_extensions(item_path, max_depth=3)
                    
                    if extensions:
                        # Klasör adını oluştur
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
                        print(f"📂 {folder_key}: {list(extensions.keys())} uzantıları bulundu ({sum(extensions.values())} dosya)")
        
        except Exception as e:
            print(f"❌ Dizin seviye analizi hatası: {directory_path} - {e}")
        
        return analysis
    
    def _is_system_folder(self, folder_name):
        """Sistem klasörü mü kontrol et"""
        system_folders = {
            'system volume information', '$recycle.bin', 'recycler',
            'windows', 'program files', 'program files (x86)', 'programdata',
            'users', 'temp', 'tmp', 'cache', '.git', '.svn', 'node_modules',
            '__pycache__', '.vscode', '.idea', 'appdata', 'application data'
        }
        return folder_name.lower() in system_folders
    
    def _is_source_folder(self, folder_path, source_path):
        """Kaynak klasörü mü kontrol et"""
        if not source_path or not os.path.exists(source_path):
            return False
        
        try:
            return os.path.samefile(folder_path, source_path)
        except:
            # Dosya yolu karşılaştırması başarısız olursa isim karşılaştırması yap
            return os.path.basename(folder_path) == os.path.basename(source_path)
    
    def _analyze_folder_extensions(self, folder_path, max_depth=5, current_depth=0):
        """Klasördeki dosya uzantılarını analiz et (derin tarama)"""
        extensions = {}
        
        try:
            # os.walk ile tüm alt klasörleri tara
            for root, dirs, files in os.walk(folder_path):
                # Derinlik kontrolü
                current_level = root.count(os.sep) - folder_path.count(os.sep)
                if current_level >= max_depth:
                    continue
                
                # Gizli klasörleri atla
                dirs[:] = [d for d in dirs if not d.startswith('.') and not self._is_system_folder(d)]
                
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
    
    def _find_suitable_target_folder(self, extension, target_analysis):
        """Uzantı için uygun hedef klasör bul (gelişmiş versiyon)"""
        if not extension or not target_analysis:
            return None
        
        # En uygun klasörü bul
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
                for cat, info in self.file_ops.get_file_categories().items():
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
            
            # 5. Ana klasör önceliği
            if folder_info.get('level', 0) == 0:
                score += 25
            
            # 6. Dosya sayısı bonus
            file_count = folder_info.get('file_count', 0)
            if file_count > 10:
                score += 20
            elif file_count > 5:
                score += 10
            
            if score > best_score:
                best_score = score
                best_folder = folder_name
                best_folder_path = folder_info['path']
        
        # Sadece gerçek tam eşleşme kabul et (uzantı var VE klasör adı eşleşiyor)
        # Skor >= 100 VE uzantı + klasör adı eşleşmesi olmalı
        if best_score >= 100:
            # Gerçek tam eşleşme mi kontrol et
            best_folder_extensions = target_analysis[best_folder]['extensions']
            if extension in best_folder_extensions:
                ext_name = extension.replace('.', '').upper()
                if ext_name in best_folder.upper() or best_folder.upper().endswith(ext_name):
                    print(f"📁 {extension} için gerçek tam eşleşme bulundu: {best_folder} (skor: {best_score})")
                    return best_folder_path
        
        print(f"❌ {extension} için gerçek tam eşleşme bulunamadı - yeni klasör oluşturulacak")
        return None
    
    def _update_scan_results(self):
        """Tarama sonuçlarını UI'da göster"""
        # Source tree'yi güncelle
        self._update_source_tree()
        
        # Preview tree'yi güncelle
        self._update_preview_tree()
        
        # Duplicate tree'yi güncelle
        self._update_duplicate_tree()
        
        # İstatistikleri göster
        self._show_scan_statistics()
    
    def _update_source_tree(self):
        """Kaynak dosyalar tree'sini güncelle"""
        self.gui.source_tree.delete(*self.gui.source_tree.get_children())
        
        for file_info in self.all_scanned_files[:1000]:  # İlk 1000 dosya
            size_str = self._format_size(file_info['size'])
            
            if file_info.get('is_folder', False):
                file_type = '📁 KLASÖR'
                display_name = f"📁 {file_info['name']}"
            else:
                file_type = file_info['extension'].upper() if file_info['extension'] else 'Dosya'
                display_name = file_info['name']
            
            self.gui.source_tree.insert('', 'end', 
                                      text=display_name,
                                      values=(size_str, file_type))
    
    def _update_preview_tree(self):
        """Organizasyon önizleme tree'sini güncelle"""
        self.gui.preview_tree.delete(*self.gui.preview_tree.get_children())
        
        for main_folder, subfolders in self.organization_structure.items():
            # Ana klasör
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
        """Duplikat dosyalar tree'sini güncelle"""
        self.gui.duplicate_tree.delete(*self.gui.duplicate_tree.get_children())
        
        for i, duplicate_group in enumerate(self.source_duplicates):
            if len(duplicate_group) > 1:
                # Grup başlığı
                group_name = f"Duplikat Grup {i+1} ({len(duplicate_group)} dosya)"
                group_item = self.gui.duplicate_tree.insert('', 'end', 
                                                          text=group_name,
                                                          values=('', '', ''))
                
                # Grup dosyaları
                for file_info in duplicate_group:
                    size_str = self._format_size(file_info['size'])
                    hash_str = file_info.get('hash', '')[:8] + '...' if file_info.get('hash') else ''
                    
                    self.gui.duplicate_tree.insert(group_item, 'end',
                                                 text=file_info['name'],
                                                 values=(file_info['path'], size_str, hash_str))
    
    def _show_scan_statistics(self):
        """Tarama istatistiklerini göster"""
        total_files = self.stats['total_files']
        unique_files = self.stats['unique_files']
        duplicate_files = self.stats['duplicate_files']
        total_size = self._format_size(self.stats['total_size'])
        
        stats_message = f"""Tarama Tamamlandı!
        
📊 İstatistikler:
• Toplam dosya: {total_files}
• Unique dosya: {unique_files}
• Duplikat dosya: {duplicate_files}
• Toplam boyut: {total_size}

📁 Kategoriler:"""
        
        for category, count in self.stats['categories'].items():
            if count > 0:
                stats_message += f"\n• {category.title()}: {count} dosya"
        
        self.gui.status_var.set(f"✅ {total_files} dosya tarandı - {unique_files} unique, {duplicate_files} duplikat")
        
        # İsteğe bağlı detaylı rapor - popup kaldırıldı
        # if total_files > 0:
        #     messagebox.showinfo("Tarama Sonuçları", stats_message)
    
    def _format_size(self, size_bytes):
        """Dosya boyutunu formatla"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def stop_scan(self):
        """Taramayı durdur"""
        self.stop_scanning = True
        if self.scan_thread and self.scan_thread.is_alive():
            self.gui.status_var.set("Tarama durduruluyor...")
    
    def get_organization_preview(self):
        """Organizasyon önizlemesi al"""
        preview = {}
        
        for main_folder, subfolders in self.organization_structure.items():
            preview[main_folder] = {}
            for subfolder, files in subfolders.items():
                preview[main_folder][subfolder] = {
                    'count': len(files),
                    'size': sum(f['size'] for f in files),
                    'files': [f['name'] for f in files[:10]]  # İlk 10 dosya
                }
        
        return preview
    
    def get_scan_summary(self):
        """Tarama özetini al"""
        return {
            'total_files': self.stats['total_files'],
            'unique_files': self.stats['unique_files'],
            'duplicate_files': self.stats['duplicate_files'],
            'total_size': self.stats['total_size'],
            'categories': dict(self.stats['categories']),
            'duplicate_groups': len(self.source_duplicates)
        } 