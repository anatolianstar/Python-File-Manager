"""
Scan Engine Module
Dosya tarama, duplikat tespiti ve organizasyon algoritmalarını içerir
"""

import os
import hashlib
import threading
import time
import traceback
from pathlib import Path
from collections import defaultdict
import tkinter as tk
from tkinter import messagebox
from lang_manager import lang_manager

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

        if not self.file_ops.source_path:
            messagebox.showwarning(lang_manager.get_text('warnings.warning'), 
                                 lang_manager.get_text('warnings.select_source_first'))
            return
            
        if not self.file_ops.target_path:
            messagebox.showwarning(lang_manager.get_text('warnings.warning'), 
                                 lang_manager.get_text('warnings.select_target_first'))
            return
            
        # Progress bar'ı göster
        self.gui.progress_var.set(0)
        if hasattr(self.gui, 'progress_label'):
            self.gui.progress_label.config(text=lang_manager.get_text('messages.starting_scan'))
        
        # Thread'de tarama başlat
        self.scan_thread = threading.Thread(target=self._scan_thread)
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def _scan_thread(self):
        """Tarama thread'i"""
        try:
            self.stop_scanning = False
            self.gui.root.after(0, lambda: self.gui.status_var.set(lang_manager.get_text('messages.scanning_files')))
            
            # Time estimation başlat
            self.gui.root.after(0, lambda: self.gui.start_time_estimation())
            
            # Dosyaları tara
            self._scan_source_files(self.file_ops.source_path, self.gui.scan_mode.get())
            
            if not self.stop_scanning:
                # Duplikatları tespit et
                self._detect_duplicates()
                
                # Organizasyon yapısını oluştur
                self._create_organization_structure()
                
                # Sonuçları güncelle
                self._update_scan_results()
                
            # Time estimation durdur
            self.gui.root.after(0, lambda: self.gui.stop_time_estimation())
            
        except Exception as e:
            # Time estimation durdur (hata durumunda da)
            self.gui.root.after(0, lambda: self.gui.stop_time_estimation())
            
            error_msg = f"Tarama hatası: {str(e)}"
            self.gui.root.after(0, lambda: self.gui.status_var.set(error_msg))
            self.gui.root.after(0, lambda: messagebox.showerror("Hata", error_msg))
    
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
                        self.stats['categories']['Yazılım Paketleri'] += 1
                        
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
                    from lang_manager import t
                    self.gui.root.after(0, lambda: self.gui.status_var.set(f"{t('messages.scanning')}: {i+1}/{total_files}"))
                
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
        """Organizasyon yapısını oluştur - GELİŞTİRİLMİŞ SÜRÜM"""

        
        self.organization_structure = defaultdict(lambda: defaultdict(list))
        self.existing_folder_files = defaultdict(list)
        
        # Hedef klasör analizi
        target_folder_analysis = self._analyze_target_folders()
        # Target folder analysis completed
        
        # TARAMA SIRASI ÖĞRENME: Mevcut klasör yapısından öğren
        print("🔍 TARAMA SIRASI ÖĞRENME BAŞLATILIYOR...")
        
        # 🧪 TEST AMAÇLI: Zorla öğrenme ekle
        print("🧪 TEST: Zorla öğrenme testi yapılıyor...")
        if not hasattr(self.file_ops, 'learned_categories'):
            self.file_ops.learned_categories = {}
        
        # Test uzantısı ekle - her seferinde farklı olsun
        import time
        test_ext = f'.test_{int(time.time() % 1000)}'
        self.file_ops.learned_categories[test_ext] = 'test_category'
        print(f"🧪 TEST öğrenme eklendi: {test_ext} -> test_category")
        
        # 🎯 GCODE ÖZEL DÜZELTMESİ: GCODE uzantısını CAD kategorisine ekle
        if '.gcode' not in self.file_ops.learned_categories:
            self.file_ops.learned_categories['.gcode'] = 'cad_3d_files'
            print("🎯 GCODE DÜZELTMESİ: .gcode -> cad_3d_files eklendi")
        
        learning_made = self._learn_from_existing_structure(target_folder_analysis)
        
        # Zorla öğrenme varsa True döndür
        if test_ext in self.file_ops.learned_categories or '.gcode' in self.file_ops.learned_categories:
            learning_made = True
            print(f"🧪 TEST: Zorla öğrenme tespit edildi - learning_made = True")
        
        print("🔍 TARAMA SIRASI ÖĞRENME TAMAMLANDI.")
        
        # EĞER ÖĞRENİLEN VAR İSE JSON'I GÜNCELLE VE ORGANİZASYONU YENİDEN HESAPLA
        if learning_made:
            print("🔄 Yeni öğrenmeler tespit edildi - JSON güncelleniyor ve organizasyon yeniden hesaplanıyor...")
            self.file_ops.save_learned_categories()
            self.file_ops.load_learned_categories()  # Fresh reload
            print("📚 JSON güncellendi ve yeniden yüklendi")
            self.gui.status_var.set(lang_manager.get_text('messages.categories_learned'))
        
        # Progress başlat
        self.gui.root.after(0, lambda: self.gui.progress_var.set(0))
        
        total_files = len(self.unique_files)
        for i, file_info in enumerate(self.unique_files):
            if self.stop_scanning:
                break
                
            # Progress güncelle
            progress = (i + 1) / total_files * 100
            self.gui.root.after(0, lambda p=progress: self.gui.progress_var.set(p))
            
            # KLASÖR İŞLEMİ: is_folder=True olanlar "Software Packages" kategorisine git
            if file_info.get('is_folder', False):
                # Klasörler sadece duplicate tarama için "Software Packages" kategorisine yerleştirilir
                software_category = lang_manager.get_text('categories.ready_programs')
                print(f"📁 {lang_manager.get_text('messages.processing_folder').format(category=software_category, name=file_info['name'])}")
                
                # Software Packages kategorisi - alt klasör kullanmadan direkt klasör adı ile
                software_packages_folder = "Software Packages"  # Sabit İngilizce klasör adı
                if software_packages_folder not in self.organization_structure:
                    self.organization_structure[software_packages_folder] = defaultdict(list)
                
                # Klasörü direkt ana kategori altına koy
                self.organization_structure[software_packages_folder][''].append(file_info)
                continue
            
            # DOSYA İŞLEMİ: Normal dosyalar için uzantı bazlı kategori 
            extension = file_info['extension']
            print(f"🔧 {lang_manager.get_text('messages.processing_file').format(name=file_info['name'], ext=extension, is_folder=file_info.get('is_folder', False))}")
            
            # ÖNCELİK 1: Öğrenilen kategoriyi kontrol et
            learned_info = self.file_ops._check_learned_category_for_scan(extension)
            
            if learned_info and isinstance(learned_info, dict):
                # Öğrenilen kategori var - bu en yüksek öncelik
                category_folder = learned_info['folder']  # İngilizce kategori klasörü
                confidence = learned_info['confidence']
                
                # Kategori adını çevir
                translated_category = self._get_translated_category_name(category_folder)
                print(f"🎯 {extension} uzantısı TARGET LEARNING ile yerleştirilecek: {translated_category} (confidence: {confidence}%)")
                
                # Organization structure'a ekle
                if category_folder not in self.organization_structure:
                    self.organization_structure[category_folder] = defaultdict(list)
                
                # Alt klasör - uzantı adı
                subfolder = extension.replace('.', '').upper() if extension else 'Uzantisiz'
                self.organization_structure[category_folder][subfolder].append(file_info)
                
                continue
            
            # ÖNCELİK 2: Mevcut klasörleri kontrol et  
            suggested_folder = self._find_suitable_target_folder(extension, target_folder_analysis)
            
            if suggested_folder:
                # Mevcut klasör bulundu
                print(f"📁 {lang_manager.get_text('messages.placing_in_category').format(ext=extension, path=suggested_folder)}")
                
                if suggested_folder not in self.existing_folder_files:
                    self.existing_folder_files[suggested_folder] = []
                
                self.existing_folder_files[suggested_folder].append(file_info)
                
            else:
                # ÖNCELİK 3: Standart kategori kullan - yeni klasör oluştur
                category, category_info = self.file_ops.get_file_category_with_learning(file_info['path'])
                main_folder = category_info['folder']
                
                # Alt klasör
                if extension in category_info['subfolders']:
                    subfolder = category_info['subfolders'][extension]
                else:
                    subfolder = extension.replace('.', '').upper() if extension else 'Uzantisiz'
                
                print(f"📁 {lang_manager.get_text('messages.placing_in_category').format(ext=extension, path=f'{main_folder}/{subfolder}')}")
                self.organization_structure[main_folder][subfolder].append(file_info)
        
        # Progress tamamla
        self.gui.root.after(0, lambda: self.gui.progress_var.set(100))
    

    def _analyze_target_folders(self):
        """Hedef klasördeki mevcut klasörleri analiz et (gelişmiş versiyon)"""
        target_path = self.file_ops.target_path
        source_path = self.file_ops.source_path
        folder_analysis = {}
        
        if not os.path.exists(target_path):
            print(f"❌ DEBUG: Target path yoksa: {target_path}")
            return folder_analysis
        
        print("🔍 Gelişmiş hedef klasör analizi başlatılıyor...")
        print(f"🔍 DEBUG: target_path = {target_path}")
        print(f"🔍 DEBUG: source_path = {source_path}")
        
        # Target path içeriğini listele
        try:
            target_contents = os.listdir(target_path)
            print(f"🔍 DEBUG: Target path içeriği = {target_contents}")
        except Exception as e:
            print(f"❌ DEBUG: Target path okunamadı: {e}")
            return folder_analysis
        
        # SORUN ÇÖZÜMÜ: Kaynak klasörün adını al
        source_folder_name = os.path.basename(source_path) if source_path else ""
        print(f"🔍 Kaynak klasör adı: {source_folder_name}")
        
        try:
            # Derin klasör analizi yap (3 seviye derinlik)
            folder_analysis.update(self._analyze_directory_recursive(target_path, source_path, max_depth=3))
            
            print(f"🔍 DEBUG: Recursive analiz sonucu = {len(folder_analysis)} klasör")
            for folder_name in folder_analysis.keys():
                print(f"🔍 DEBUG: Bulunan klasör: {folder_name}")
            
            # SORUN ÇÖZÜMÜ: Sonuçları filtrele - kaynak klasörle aynı adlı klasörleri çıkar
            filtered_analysis = {}
            for folder_name, folder_info in folder_analysis.items():
                # Kaynak klasörle aynı adlı klasörleri atla
                if source_folder_name and source_folder_name.lower() == folder_name.lower():
                    print(f"⚠️ Kaynak klasörle aynı adlı klasör atlandı: {folder_name}")
                    continue
                
                # "Yazılım Paketleri" klasörünü analiz dışında tut (sadece duplicate tarama için)
                if ("yazılım paketleri" in folder_name.lower() or 
                    "yazilim paketleri" in folder_name.lower() or
                    "software packages" in folder_name.lower() or
                    "hazır programlar" in folder_name.lower() or 
                    "hazir programlar" in folder_name.lower()):
                    print(f"⚠️ Yazılım Paketleri klasörü analiz dışında tutuldu: {folder_name}")
                    continue
                    
                # Son kopyalama işleminde oluşturulmuş klasörleri tespit et
                folder_path = folder_info['path']
                if self._is_recently_created_folder(folder_path):
                    print(f"⚠️ Son kopyalama işleminde oluşturulmuş klasör atlandı: {folder_name}")
                    continue
                    
                filtered_analysis[folder_name] = folder_info
            
            print(f"✅ {len(filtered_analysis)} geçerli hedef klasör bulundu")
            for folder_name, folder_info in filtered_analysis.items():
                print(f"📂 DEBUG: {folder_name} -> {list(folder_info['extensions'].keys())}")
            
        except Exception as e:
            print(f"❌ Hedef klasör analizi hatası: {e}")
        
        print(f"🔍 DEBUG: _analyze_target_folders dönüş = {len(filtered_analysis)} klasör")
        return filtered_analysis
    
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
    
    def _is_recently_created_folder(self, folder_path):
        """Son zamanlarda oluşturulmuş klasör mü kontrol et"""
        try:
            import time
            # Klasörün oluşturulma zamanını kontrol et
            creation_time = os.path.getctime(folder_path)
            current_time = time.time()
            
            # Son 1 saat içinde oluşturulmuş mu?
            time_diff = current_time - creation_time
            if time_diff < 3600:  # 1 saat = 3600 saniye
                print(f"🕒 {folder_path} son 1 saat içinde oluşturulmuş ({time_diff:.0f} saniye önce)")
                return True
                
            # Klasör adında sayı eki var mı kontrol et (_1, _2 gibi)
            folder_name = os.path.basename(folder_path)
            if '_' in folder_name and folder_name.split('_')[-1].isdigit():
                print(f"🔢 {folder_path} sayı eki içeriyor (muhtemelen duplikat)")
                return True
                
        except Exception as e:
            print(f"⚠️ Klasör zamanı kontrol hatası: {folder_path} - {e}")
            
        return False
    
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
        """KULLANICI ODAKLI UZANTI EŞLEŞTIRME - Basitleştirilmiş Algoritma"""
        if not extension or not target_analysis:
            return None
        
        print(f"🔍 {lang_manager.get_text('messages.searching_folder').format(ext=extension)}")
        
        # ÖNCELİK 1: KULLANICININ ÖĞRETTİĞİ KATEGORİ (EN YÜKSEK ÖNCELİK)
        learned_category = self.file_ops.learned_categories.get(extension)
        if learned_category:
            print(f"🧠 KULLANICI TERCİHİ: {extension} -> {learned_category} (öğrenilen kategori)")
            
            # Öğrenilen kategoriye uygun klasör var mı?
            for folder_name, folder_info in target_analysis.items():
                # Kategori ismini klasör adında ara
                if self._folder_matches_category(folder_name, learned_category):
                    print(f"✅ KULLANICI TERCİHİ UYGULANDI: {extension} -> {folder_name}")
                    return folder_info['path']
        
        # ÖNCELİK 2: UZANTI KLASÖRÜ ZATEN MEVCUT (TAM EŞLEŞME)
        extension_name = extension.replace('.', '').upper()
        for folder_name, folder_info in target_analysis.items():
            # Klasör adı uzantı ile tam eşleşiyor mu?
            if self._is_exact_extension_match(folder_name, extension_name):
                print(f"🎯 TAM EŞLEŞME: {extension} -> {folder_name} (mevcut uzantı klasörü)")
                return folder_info['path']
        
        # ÖNCELİK 3: AYNI KATEGORİDEKİ KLASÖR (KATEGORİ EŞLEŞME)
        category, category_info = self.file_ops.get_file_category_with_learning(f"test{extension}")
        if category != 'other_files':
            for folder_name, folder_info in target_analysis.items():
                if self._folder_matches_category(folder_name, category):
                    print(f"🔗 KATEGORİ EŞLEŞME: {extension} -> {folder_name} (kategori: {category})")
                    return folder_info['path']
        
        # ÖNCELİK 4: UZANTI MEVCUT AMA FARKLI İSİMDE
        for folder_name, folder_info in target_analysis.items():
            if extension in folder_info.get('extensions', {}):
                print(f"📁 UZANTI MEVCUT: {extension} -> {folder_name} (uzantı var ama farklı isim)")
                return folder_info['path']
        
        print(f"❌ {lang_manager.get_text('messages.no_folder_found').format(ext=extension)}")
        return None
    
    def _folder_matches_category(self, folder_name, category):
        """Klasör adının kategori ile eşleşip eşleşmediğini kontrol et"""
        # Kategori bilgilerini al
        categories = self.file_ops.get_file_categories()
        if category not in categories:
            return False
        
        category_info = categories[category]
        category_folder_name = category_info['folder'].lower()
        folder_name_lower = folder_name.lower()
        
        # Tam eşleşme veya kısmi eşleşme
        if (category_folder_name in folder_name_lower or 
            folder_name_lower in category_folder_name):
            return True
        
        # Kategori anahtar kelimelerini kontrol et
        category_keywords = {
            'audio_files': ['müzik', 'ses', 'music', 'audio', 'sound'],
            'video_files': ['video', 'film', 'movie', 'sinema'],
            'image_files': ['resim', 'foto', 'image', 'picture', 'photo'],
            'document_files': ['belge', 'doc', 'document', 'text', 'yazı'],
            'archive_files': ['arşiv', 'archive', 'zip', 'sıkıştır'],
            'program_files': ['program', 'uygulama', 'app', 'software'],
            'cad_3d_files': ['cad', 'çizim', 'tasarım', 'design', '3d', 'model']
        }
        
        if category in category_keywords:
            for keyword in category_keywords[category]:
                if keyword in folder_name_lower:
                    return True
        
        return False
    
    def _is_exact_extension_match(self, folder_name, extension_name):
        """Klasör adının uzantı ile tam eşleşip eşleşmediğini kontrol et"""
        folder_upper = folder_name.upper()
        
        # Tam eşleşme kontrolü
        if (folder_upper == extension_name or
            folder_upper.endswith(f"/{extension_name}") or
            folder_upper.endswith(f"\\{extension_name}") or
            folder_upper.endswith(f" {extension_name}") or
            extension_name in folder_upper.split("/")):
            return True
        
        return False
    
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
        
        # ORGANIZE BUTONUNU AKTİF ET - Tarama tamamlandığında
        try:
            # GUI Manager üzerinden main_modular'e erişim
            if hasattr(self.gui, 'ui_widgets') and 'organize_btn' in self.gui.ui_widgets:
                self.gui.ui_widgets['organize_btn'].configure(state='normal')
                print("✅ Organize butonu aktif edildi")
        except Exception as e:
            print(f"⚠️ Organize butonu aktif edilemedi: {e}")
    
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
    
    def _get_translated_category_name(self, folder_name):
        """İngilizce klasör adını mevcut dilde göster"""
        # Kategori mapping'i - İngilizce klasör adından dil anahtarına
        category_mapping = {
            'Image Files': 'categories.image_files',
            'Document Files': 'categories.document_files',
            'Audio Files': 'categories.audio_files',
            'Video Files': 'categories.video_files',
            'Program Files': 'categories.program_files',
            'Compressed Files': 'categories.compressed_files',
            'CAD and 3D Files': 'categories.cad_3d_files',
            'Code Files': 'categories.code_files',
            'Font Files': 'categories.font_files',
            'Other Files': 'categories.other_files',
            'Software Packages': 'categories.ready_programs'
        }
        
        if folder_name in category_mapping:
            return lang_manager.get_text(category_mapping[folder_name])
        else:
            return folder_name  # Bilinmeyen kategori ise olduğu gibi döndür
    
    def _update_preview_tree(self):
        """Organizasyon önizleme tree'sini güncelle"""
        self.gui.preview_tree.delete(*self.gui.preview_tree.get_children())
        
        for main_folder, subfolders in self.organization_structure.items():
            # Ana klasör - çeviri ile göster
            display_folder_name = self._get_translated_category_name(main_folder)
            total_files = sum(len(files) for files in subfolders.values())
            main_item = self.gui.preview_tree.insert('', 'end', 
                                                   text=f"📁 {display_folder_name}",
                                                   values=(total_files,))
            
            # Alt klasörler
            for subfolder, files in subfolders.items():
                if subfolder:  # Boş değilse
                    self.gui.preview_tree.insert(main_item, 'end',
                                               text=f"📂 {subfolder}",
                                               values=(len(files),))
                else:  # Boş string ise (Software Packages gibi)
                    for file_info in files:
                        self.gui.preview_tree.insert(main_item, 'end',
                                                   text=f"📁 {file_info['name']}",
                                                   values=(1,))
    
    def _update_duplicate_tree(self):
        """Duplikat dosyalar tree'sini güncelle"""
        self.gui.duplicate_tree.delete(*self.gui.duplicate_tree.get_children())
        
        for i, duplicate_group in enumerate(self.source_duplicates):
            if len(duplicate_group) > 1:
                # Grup başlığı
                from lang_manager import t
                group_name = f"{t('messages.duplicate_group')} {i+1} ({len(duplicate_group)} {t('messages.files_lowercase')})"
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
        
        stats_message = f"""{lang_manager.get_text('messages.scan_complete').split('!')[0]}!
        
📊 {lang_manager.get_text('reports.analysis.general_stats')}:
• {lang_manager.get_text('reports.analysis.total_source_files')}: {total_files}
• {lang_manager.get_text('messages.unique_files')}: {unique_files}
• {lang_manager.get_text('reports.analysis.duplicate_files')}: {duplicate_files}
• {lang_manager.get_text('reports.analysis.total_copy_size')}: {total_size}

📁 {lang_manager.get_text('reports.analysis.category_analysis')}:"""
        
        for category, count in self.stats['categories'].items():
            if count > 0:
                if category == "Software Packages":
                    category_name = lang_manager.get_text('categories.ready_programs')
                    stats_message += f"\n• {category_name}: {count} klasör (sadece duplicate tarama)"
                else:
                    stats_message += f"\n• {category.title()}: {count} dosya"
        
        from lang_manager import t
        self.gui.status_var.set(f"✅ {total_files} {t('messages.files_scanned')} - {unique_files} {t('messages.unique')}, {duplicate_files} {t('messages.duplicate')}")
        
        # İsteğe bağlı detaylı rapor - popup kaldırıldı
        # if total_files > 0:
        #     messagebox.showinfo("Tarama Sonuçları", stats_message)

    def _learn_from_existing_structure(self, target_folder_analysis):
        """TARAMA SIRASI ÖĞRENME: Mevcut klasör yapısından kategorileri öğren"""
        try:
            print("🎓 TARAMA SIRASI ÖĞRENME: Mevcut klasör yapısından öğrenme başlatılıyor...")
            print(f"🔍 DEBUG: target_folder_analysis = {list(target_folder_analysis.keys())}")
            print(f"🔍 DEBUG: Başlangıçta learned_categories = {self.file_ops.learned_categories}")
            
            learned_count = 0
            
            for folder_name, folder_info in target_folder_analysis.items():
                folder_path = folder_info['path']
                extensions = folder_info['extensions']
                
                print(f"🔍 DEBUG: İşlenen klasör: {folder_name}")
                print(f"🔍 DEBUG: Klasör yolu: {folder_path}")
                print(f"🔍 DEBUG: Bulunan uzantılar: {extensions}")
                
                # Bu klasörün kategori ismi nedir?
                category = self.file_ops._determine_category_from_path(folder_path)
                print(f"🔍 DEBUG: Tespit edilen kategori: {category}")
                
                if category and category != 'other_files':
                    print(f"📂 Kategori tespit edildi: {folder_name} -> {category}")
                    
                    # Bu klasördeki uzantıları öğren
                    for extension, count in extensions.items():
                        if extension and count > 0:
                            print(f"🔍 DEBUG: İşlenen uzantı: {extension} (count: {count})")
                            # Mevcut öğrenme sistemindeki kategoriyi kontrol et
                            current_category = self.file_ops._find_extension_in_categories(extension)
                            
                            print(f"🔍 DEBUG: {extension} mevcut kategori: {current_category}, yeni kategori: {category}")
                            if not current_category or current_category != category:
                                # Bu uzantıyı öğren
                                print(f"🎯 MEVCUT YAPIDAN ÖĞRENME: {extension} -> {category} ({count} dosya)")
                                
                                # Güven skoru - mevcut yapıdaki dosya sayısına göre
                                confidence = min(95, 60 + (count * 5))  # Minimum %60, maksimum %95
                                
                                # ÖNEMLİ: learned_categories dictionary'sine ekleme
                                print(f"📝 DEBUG: learned_categories'e ekleniyor: {extension} -> {category}")
                                self.file_ops.learned_categories[extension] = category
                                print(f"📝 DEBUG: Ekleme sonrası learned_categories = {self.file_ops.learned_categories}")
                                
                                if not hasattr(self.file_ops, 'category_confidence'):
                                    self.file_ops.category_confidence = {}
                                
                                self.file_ops.category_confidence[extension] = {
                                    'category': category,
                                    'confidence': confidence,
                                    'source': 'existing_structure_scan',
                                    'timestamp': time.time(),
                                    'file_count': count,
                                    'learned_folder': folder_path
                                }
                                
                                learned_count += 1
                            else:
                                print(f"✅ ZATEN BİLİNEN: {extension} -> {category}")
            
            print(f"🔍 DEBUG: Öğrenme döngüsü bitti. learned_count = {learned_count}")
            print(f"🔍 DEBUG: Son hali learned_categories = {self.file_ops.learned_categories}")
            
            # Öğrenme sonucu döndür
            if learned_count > 0:
                print(f"🎓 TARAMA SIRASI ÖĞRENME TAMAMLANDI: {learned_count} uzantı öğrenildi")
                return True  # Öğrenme yapıldı
            else:
                print("📖 TARAMA SIRASI ÖĞRENME: Yeni öğrenme bulunamadı")
                return False  # Öğrenme yapılmadı
                
        except Exception as e:
            import traceback
            print(f"❌ Tarama sırası öğrenme hatası: {e}")
            print(f"❌ TRACEBACK: {traceback.format_exc()}")
            return False
    
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