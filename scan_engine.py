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
        
        # Hash kontrolü uyarısı
        if self.gui.duplicate_check_hash.get():
            result = messagebox.askyesno(
                "⚠️ Hash Kontrolü Uyarısı",
                "Hash kontrolü aktif! Bu işlem çok yavaş olabilir, özellikle büyük dosyalar için.\n\n"
                "• Küçük dosyalar: Hızlı\n"
                "• Büyük dosyalar (>100MB): Çok yavaş\n"
                "• Video/resim dosyaları: Çok yavaş\n\n"
                "Devam etmek istiyor musunuz?\n\n"
                "💡 İpucu: Sadece dosya adı + boyut kontrolü genellikle yeterlidir.",
                icon='warning'
            )
            if not result:
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
            
            # Butonları sıfırla (hata durumunda da)
            if hasattr(self, 'main_app') and self.main_app:
                self.gui.root.after(0, lambda: self.main_app._reset_buttons_after_operation())
            
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
        check_media = self.gui.duplicate_check_media.get()
        check_similar = self.gui.duplicate_check_similar.get()
        
        print(f"🔍 Duplikat kontrol seçenekleri: Name={check_name}, Size={check_size}, Hash={check_hash}, Media={check_media}, Similar={check_similar}")
        
        if check_media:
            print("📸 MEDIA BOYUT+DIMENSIONS MATCH aktif: Dosya Boyutu + Media Boyutları (isim farklı olabilir)")
        if check_similar:
            print("🤔 MUHTEMEL DUPLIKAT aktif: İsim benzerliği + boyut kontrolü (çok sıkı kriterler)")
        if not any([check_name, check_size, check_hash, check_media, check_similar]):
            print("⚠️ Hiçbir duplikat kontrolü seçilmedi - tüm dosyalar unique olacak")
        
        # Dosyaları grupla
        file_groups = defaultdict(list)
        
        total_files = len(self.all_scanned_files)
        
        for i, file_info in enumerate(self.all_scanned_files):
            if self.stop_scanning:
                return
            
            # Duplikat anahtarı oluştur
            key_parts = []
            
            if check_name:
                key_parts.append(f"name:{file_info['name'].lower()}")
            
            if check_size:
                key_parts.append(f"size:{file_info['size']}")
            
            if check_hash:
                if not file_info['hash']:
                    file_info['hash'] = self._calculate_file_hash(file_info['path'])
                if file_info['hash']:
                    key_parts.append(f"hash:{file_info['hash']}")
            
            if check_media:
                # Media duplikat kontrolü: SADECE media dosyaları için boyut + dimensions match
                if self._is_media_file(file_info['path']):
                    # Media boyutları (dimensions) - ZORUNLU
                    if not file_info.get('dimensions'):
                        file_info['dimensions'] = self._get_media_dimensions(file_info['path'])
                    
                    # MEDIA MATCH için kriterler (İSİM KONTROLÜ YOK):
                    # 1. Dosya boyutu (tam eşleşme)
                    key_parts.append(f"media_size:{file_info['size']}")
                    
                    # 2. Media boyutları (tam eşleşme)
                    if file_info.get('dimensions'):
                        key_parts.append(f"media_dim:{file_info['dimensions']}")
                        print(f"📸 Media kontrolü: {file_info['name']} -> {file_info.get('dimensions', 'boyut_yok')} ({file_info['size']} bytes)")
                    else:
                        # Boyutları alınamazsa unique key ver (duplikat olmayacak)
                        key_parts.append(f"media_no_dim:{file_info['path']}")
                        print(f"📸 Media kontrolü (boyut alınamadı): {file_info['name']} -> unique")
                    
                    # NOT: İsim kontrolü YOK - farklı isimlerde ama aynı boyut+dimensions olan dosyalar duplikat bulunacak
                    
                else:
                    # Media olmayan dosyalar için media kontrolü geçersiz
                    # Unique key ver ki duplikat olmasın
                    key_parts.append(f"non_media:{file_info['path']}")
            
            if check_similar:
                # Muhtemel duplikat kontrolü: normalize edilmiş isim + boyut/boyutlar
                # NOT: Bu sadece likely duplicate için kullanılacak, exact duplicate için değil
                normalized_name = self._normalize_filename(file_info['name'])
                if normalized_name.strip():  # Boş değilse
                    key_parts.append(f"norm_name:{normalized_name}")
                    
                    # Dosya boyutu ekle (eğer yoksa)
                    if not check_size:
                        key_parts.append(f"similar_size:{file_info['size']}")
                    
                    # Media dosyası ise boyutları da ekle
                    if self._is_media_file(file_info['path']):
                        if not file_info.get('dimensions'):
                            file_info['dimensions'] = self._get_media_dimensions(file_info['path'])
                        if file_info.get('dimensions'):
                            key_parts.append(f"similar_dim:{file_info['dimensions']}")
                    
                    print(f"🤔 Muhtemel duplikat kontrolü: {file_info['name']} -> '{normalized_name}'")
            
            # Anahtar oluştur
            if key_parts:
                key = '|'.join(key_parts)
                file_groups[key].append(file_info)
            else:
                # Hiçbir kontrol seçilmemişse her dosya unique
                unique_key = f"unique:{file_info['path']}"
                file_groups[unique_key].append(file_info)
            
            # Progress güncelle
            progress = 50 + (i + 1) / total_files * 30  # %50-80 arası
            self.gui.root.after(0, lambda p=progress: self.gui.progress_var.set(p))
            
            # Time estimation güncelle
            self.gui.root.after(0, lambda p=progress: self.gui.update_time_estimation(p))
            
            # UI donmasını önle
            if i % 50 == 0:
                time.sleep(0.001)
        
        # Duplikatları ayır - DÜZELTME: Sadece fazladan olanlar duplikat
        exact_duplicates_found = 0
        print(f"🔍 Dosya grupları analiz ediliyor: {len(file_groups)} grup bulundu")
        
        for key, files in file_groups.items():
            if len(files) > 1:
                # Duplikat grup - İlk dosya orijinal, geri kalanlar duplikat
                original_file = files[0]  # İlk dosyayı orijinal olarak kabul et
                duplicate_files_in_group = files[1:]  # Geri kalanlar duplikat
                
                # Orijinal dosyayı unique'e ekle
                self.unique_files.append(original_file)
                
                # Duplikatları duplikat listesine ekle
                self.duplicate_files.extend(duplicate_files_in_group)
                self.source_duplicates.append(files)  # Tüm grup (debug için)
                
                exact_duplicates_found += len(duplicate_files_in_group)
                print(f"🔍 EXACT duplikat grup bulundu:")
                print(f"   📋 Anahtar: {key}")
                print(f"   📄 Orijinal: {original_file['name']}")
                for i, dup_file in enumerate(duplicate_files_in_group):
                    print(f"   📄 Duplikat {i+1}: {dup_file['name']}")
                print(f"   📊 Toplam: 1 orijinal + {len(duplicate_files_in_group)} duplikat")
            else:
                # Unique dosya
                self.unique_files.extend(files)
                # Sadece media dosyaları için anahtar göster
                if any(self._is_media_file(f['path']) for f in files):
                    print(f"📄 Unique media dosyası: {files[0]['name']} (anahtar: {key})")
        
        print(f"✅ EXACT duplikat kontrolü tamamlandı: {exact_duplicates_found} exact duplikat bulundu")
        
        # Muhtemel duplikatları tespit et (eğer similar kontrolü aktifse)
        if check_similar:
            print("🤔 Muhtemel duplikat kontrolü başlatılıyor...")
            self._detect_likely_duplicates()
        else:
            print("ℹ️ Muhtemel duplikat kontrolü kapalı (isteğe bağlı)")
        
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
    
    def _is_media_file(self, file_path):
        """Dosyanın media dosyası olup olmadığını kontrol et"""
        extension = os.path.splitext(file_path)[1].lower()
        media_extensions = [
            # Resim formatları
            '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.svg', '.ico',
            # Video formatları
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'
        ]
        return extension in media_extensions
    
    def _get_media_dimensions(self, file_path):
        """Media dosyasının boyutlarını al"""
        try:
            extension = os.path.splitext(file_path)[1].lower()
            
            # Resim dosyaları için
            if extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']:
                dimensions = self._get_image_dimensions(file_path)
                if dimensions:
                    print(f"📐 Resim boyutu alındı: {os.path.basename(file_path)} -> {dimensions}")
                else:
                    print(f"❌ Resim boyutu alınamadı: {os.path.basename(file_path)}")
                return dimensions
            
            # Video dosyaları için
            elif extension in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']:
                dimensions = self._get_video_dimensions(file_path)
                if dimensions:
                    print(f"📐 Video boyutu alındı: {os.path.basename(file_path)} -> {dimensions}")
                else:
                    print(f"❌ Video boyutu alınamadı: {os.path.basename(file_path)}")
                return dimensions
            
            return None
            
        except Exception as e:
            print(f"⚠️ Media boyut alma hatası: {os.path.basename(file_path)} - {e}")
            return None
    
    def _get_image_dimensions(self, file_path):
        """Resim dosyasının boyutlarını al"""
        try:
            with open(file_path, 'rb') as f:
                # JPEG için
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    return self._parse_jpeg_dimensions(f)
                # PNG için
                elif file_path.lower().endswith('.png'):
                    return self._parse_png_dimensions(f)
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
            # Video metadata okuma karmaşık, basit tahmin kullanıyoruz
            file_size = os.path.getsize(file_path)
            
            # Dosya boyutuna göre tahmin
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
    
    def _calculate_name_similarity(self, name1, name2):
        """İki dosya isminin benzerlik oranını hesapla (0-100) - GELİŞTİRİLMİŞ ALGORİTMA"""
        try:
            # Uzantıları kaldır
            name1_base = os.path.splitext(name1)[0].lower()
            name2_base = os.path.splitext(name2)[0].lower()
            
            # Boş isim kontrolü
            if not name1_base or not name2_base:
                return 0
            
            # Tamamen aynıysa %100
            if name1_base == name2_base:
                return 100
            
            # Basit Levenshtein distance hesapla
            def levenshtein_distance(s1, s2):
                if len(s1) < len(s2):
                    return levenshtein_distance(s2, s1)
                
                if len(s2) == 0:
                    return len(s1)
                
                previous_row = list(range(len(s2) + 1))
                for i, c1 in enumerate(s1):
                    current_row = [i + 1]
                    for j, c2 in enumerate(s2):
                        insertions = previous_row[j + 1] + 1
                        deletions = current_row[j] + 1
                        substitutions = previous_row[j] + (c1 != c2)
                        current_row.append(min(insertions, deletions, substitutions))
                    previous_row = current_row
                
                return previous_row[-1]
            
            # Levenshtein distance'ı benzerlik oranına çevir
            max_len = max(len(name1_base), len(name2_base))
            distance = levenshtein_distance(name1_base, name2_base)
            similarity = ((max_len - distance) / max_len) * 100
            
            # Ek bonuslar
            # Bonus 1: Bir isim diğerinin içinde geçiyorsa
            if name1_base in name2_base or name2_base in name1_base:
                similarity = min(100, similarity + 10)
            
            # Bonus 2: Aynı kelimeler içeriyorsa (boşluk/tire ile ayrılmış)
            import re
            words1 = set(re.split(r'[\s\-_]+', name1_base))
            words2 = set(re.split(r'[\s\-_]+', name2_base))
            
            if words1 and words2:
                common_words = words1.intersection(words2)
                if common_words:
                    word_bonus = (len(common_words) / max(len(words1), len(words2))) * 15
                    similarity = min(100, similarity + word_bonus)
            
            # Malus: Çok farklı uzunluklarda isimler
            length_ratio = min(len(name1_base), len(name2_base)) / max(len(name1_base), len(name2_base))
            if length_ratio < 0.5:  # Biri diğerinin yarısından kısaysa
                similarity *= 0.8  # %20 azalt
            
            return int(max(0, min(100, similarity)))
            
        except Exception as e:
            print(f"⚠️ İsim benzerliği hesaplama hatası: {e}")
            return 0
    
    def _normalize_filename(self, filename):
        """Dosya ismini normalize et (sayılar, tarihler vs. kaldır)"""
        try:
            import re
            
            # Uzantıyı kaldır
            name_base = os.path.splitext(filename)[0].lower()
            
            # Yaygın kalıpları kaldır
            # Tarih kalıpları: 20231105, 2023-11-05, 05.11.2023
            name_base = re.sub(r'\d{8}', '', name_base)  # 20231105
            name_base = re.sub(r'\d{4}-\d{2}-\d{2}', '', name_base)  # 2023-11-05
            name_base = re.sub(r'\d{2}\.\d{2}\.\d{4}', '', name_base)  # 05.11.2023
            
            # Saat kalıpları: 14:30, 1430
            name_base = re.sub(r'\d{2}:\d{2}', '', name_base)  # 14:30
            name_base = re.sub(r'\d{4}(?=\D|$)', '', name_base)  # 1430
            
            # Sayı dizileri (3+ rakam)
            name_base = re.sub(r'\d{3,}', '', name_base)
            
            # Özel karakterleri kaldır
            name_base = re.sub(r'[_\-\(\)\[\]{}]', ' ', name_base)
            
            # Çoklu boşlukları tek boşluğa çevir
            name_base = re.sub(r'\s+', ' ', name_base).strip()
            
            return name_base
            
        except:
                         return filename
    
    def _detect_likely_duplicates(self):
        """Muhtemel duplikatları tespit et (isim benzerliği + boyut/boyutlar) - ÇOK SIKI KRİTERLER"""
        try:
            self.likely_duplicates = []
            
            # Sadece media dosyalarını kontrol et
            media_files = [f for f in self.unique_files if self._is_media_file(f['path'])]
            
            print(f"🤔 {len(media_files)} media dosyası için muhtemel duplikat kontrolü başlıyor...")
            
            # PERFORMANS OPTİMİZASYONU: Çok fazla dosya varsa sınırla
            if len(media_files) > 500:  # 1000'den 500'e düşürdük
                print(f"⚠️ Çok fazla media dosyası ({len(media_files)}), ilk 500 tanesi kontrol edilecek")
                media_files = media_files[:500]
            
            # PERFORMANS OPTİMİZASYONU: Maksimum çift sayısını sınırla
            max_pairs = 100  # 1000'den 100'e düşürdük (çok daha sıkı)
            pair_count = 0
            
            # Her dosyayı diğerleriyle karşılaştır
            for i, file1 in enumerate(media_files):
                if self.stop_scanning or pair_count >= max_pairs:
                    if pair_count >= max_pairs:
                        print(f"⚠️ Maksimum çift sayısına ulaşıldı ({max_pairs}), kontrol durduruluyor")
                    return
                
                # Progress göster
                if i % 50 == 0:  # 100'den 50'ye düşürdük
                    print(f"🔍 İşlenen dosya: {i}/{len(media_files)}")
                
                for j, file2 in enumerate(media_files[i+1:], i+1):
                    if pair_count >= max_pairs:
                        break
                    
                    # HIZLI FİLTRE 1: Çok farklı boyutları hemen elendir (ÇOK SIKI)
                    size_ratio = min(file1['size'], file2['size']) / max(file1['size'], file2['size'])
                    if size_ratio < 0.95:  # %5'ten fazla boyut farkı varsa atla (çok daha sıkı)
                        continue
                    
                    # HIZLI FİLTRE 2: Boyutlar farklıysa atla (ÇOK SIKI)
                    if file1.get('dimensions') and file2.get('dimensions'):
                        if file1['dimensions'] != file2['dimensions']:
                            continue  # Boyutlar farklıysa kesinlikle duplikat değil
                    elif file1.get('dimensions') or file2.get('dimensions'):
                        # Birinde boyut var diğerinde yok - muhtemelen farklı dosyalar
                        continue
                    
                    # İsim benzerliği hesapla
                    similarity = self._calculate_name_similarity(file1['name'], file2['name'])
                    
                    # HIZLI FİLTRE 3: Çok düşük benzerlik varsa atla (ÇOK SIKI)
                    if similarity < 90:  # %80'den %90'a çıkardık (çok daha sıkı)
                        continue
                    
                    # Boyut benzerliği kontrol et
                    size_diff = abs(file1['size'] - file2['size']) / max(file1['size'], file2['size']) * 100
                    
                    # Boyutlar benzer mi kontrol et (eğer varsa)
                    dimension_match = False
                    if file1.get('dimensions') and file2.get('dimensions'):
                        dimension_match = file1['dimensions'] == file2['dimensions']
                    
                    # Muhtemel duplikat kriterleri - ÇOK ÇOK SIKI (FALSE POSITIVE ÖNLEME)
                    is_likely_duplicate = False
                    confidence = 0
                    
                    # Kriter 1: İsim %98+ benzer + boyut %99+ benzer + aynı boyutlar (neredeyse kesin)
                    if similarity >= 98 and size_diff <= 1 and dimension_match:
                        is_likely_duplicate = True
                        confidence = min(98, similarity + (100 - size_diff))
                    
                    # Kriter 2: İsim %95+ benzer + aynı boyutlar + boyut %98+ benzer (çok yüksek güven)
                    elif similarity >= 95 and dimension_match and size_diff <= 2:
                        is_likely_duplicate = True
                        confidence = min(95, similarity + (100 - size_diff))
                    
                    # Kriter 3: İsim %99+ benzer (neredeyse aynı isim) + boyut %95+ benzer
                    elif similarity >= 99 and size_diff <= 5:
                        is_likely_duplicate = True
                        confidence = min(92, similarity)
                    
                    # ÇOK SIKI: Normalize edilmiş isimler de kontrol et
                    if is_likely_duplicate:
                        norm1 = self._normalize_filename(file1['name'])
                        norm2 = self._normalize_filename(file2['name'])
                        
                        # Normalize edilmiş isimler çok farklıysa false positive olabilir
                        if norm1.strip() and norm2.strip():
                            norm_similarity = self._calculate_name_similarity(norm1, norm2)
                            if norm_similarity < 80:  # Normalize edilmiş isimler %80'den düşükse atla
                                print(f"🚫 False positive önlendi: {file1['name']} vs {file2['name']} (norm: {norm_similarity}%)")
                                continue
                    
                    if is_likely_duplicate:
                        # Muhtemel duplikat çifti kaydet
                        likely_pair = {
                            'file1': file1,
                            'file2': file2,
                            'name_similarity': similarity,
                            'size_difference': size_diff,
                            'dimension_match': dimension_match,
                            'confidence': confidence
                        }
                        
                        self.likely_duplicates.append(likely_pair)
                        pair_count += 1
                        
                        # Her çifti logla (az olacağı için)
                        print(f"🤔 Muhtemel duplikat bulundu ({confidence}% güven): {file1['name']} vs {file2['name']}")
            
            print(f"✅ Muhtemel duplikat kontrolü tamamlandı: {len(self.likely_duplicates)} çift bulundu (max {max_pairs})")
            
        except Exception as e:
            print(f"⚠️ Muhtemel duplikat tespit hatası: {e}")
            import traceback
            traceback.print_exc()
            self.likely_duplicates = []
            
            # UI'yi güncelle
            self.gui.root.after(0, lambda: self.gui.progress_var.set(80))
            print("🔄 Muhtemel duplikat hatası nedeniyle normal taramaya devam ediliyor...")
     
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
                
                # Alt klasör - Other Files için özel işlem
                if main_folder == "Other Files":
                    # Bilinmeyen uzantılar için dinamik alt klasör oluştur
                    if extension:
                        subfolder = extension.replace('.', '').upper()  # .iss -> ISS
                    else:
                        subfolder = 'No_Extension'  # Uzantısız dosyalar için
                    print(f"📁 Bilinmeyen uzantı Other Files'a yerleştiriliyor: {extension} -> Other Files/{subfolder}")
                else:
                    # Diğer kategoriler için normal işlem
                    if extension in category_info['subfolders']:
                        subfolder = category_info['subfolders'][extension]
                    else:
                        subfolder = extension.replace('.', '').upper() if extension else 'Uzantisiz'
                
                print(f"📁 {lang_manager.get_text('messages.placing_in_category').format(ext=extension, path=f'{main_folder}/{subfolder}')}")
                self.organization_structure[main_folder][subfolder].append(file_info)
        
        # Duplikat dosyaları da "Duplicate Files" kategorisine ekle
        if self.duplicate_files:
            print(f"🔍 DUPLIKAT DOSYALAR BULUNDU: {len(self.duplicate_files)} adet")
            duplicate_folder = "Duplicate Files"
            if duplicate_folder not in self.organization_structure:
                self.organization_structure[duplicate_folder] = defaultdict(list)
            
            # Duplikat dosyaları kaynak klasör yapısına göre organize et
            for file_info in self.duplicate_files:
                try:
                    # Kaynak dosyanın relative path'ini bul
                    source_base = self.file_ops.source_path
                    relative_path = os.path.relpath(file_info['path'], source_base)
                    
                    # Klasör yapısını koruyarak ekle
                    subfolder_path = os.path.dirname(relative_path)
                    if not subfolder_path or subfolder_path == '.':
                        subfolder_path = 'Root'  # Ana klasördeki dosyalar için
                    
                    # Duplikat dosyayı işaretle
                    file_info['is_duplicate'] = True
                    file_info['original_path'] = relative_path
                    
                    self.organization_structure[duplicate_folder][subfolder_path].append(file_info)
                    print(f"📋 Duplikat preview'a eklendi: {relative_path} -> Duplicate Files/{subfolder_path}")
                    
                except Exception as e:
                    print(f"⚠️ Duplikat preview ekleme hatası: {e}")
                    # Fallback: direkt ana klasöre ekle
                    self.organization_structure[duplicate_folder]['Duplicates'].append(file_info)
        else:
            print(f"ℹ️ HİÇ DUPLIKAT DOSYA BULUNAMADI - Duplicate Files klasörü oluşturulmayacak")
            print(f"📊 Kontrol edilen dosya sayısı: {len(self.all_scanned_files)}")
            print(f"📊 Unique dosya sayısı: {len(self.unique_files)}")
            print(f"📊 Duplikat dosya sayısı: {len(self.duplicate_files)}")
            
            # Hangi kontrollerin aktif olduğunu tekrar göster
            check_media = self.gui.duplicate_check_media.get()
            check_similar = self.gui.duplicate_check_similar.get()
            check_name = self.gui.duplicate_check_name.get()
            check_size = self.gui.duplicate_check_size.get()
            check_hash = self.gui.duplicate_check_hash.get()
            
            print(f"🔍 Aktif duplikat kontrolleri: Media={check_media}, Similar={check_similar}, Name={check_name}, Size={check_size}, Hash={check_hash}")
            
            if not any([check_media, check_similar, check_name, check_size, check_hash]):
                print("⚠️ HİÇBİR DUPLIKAT KONTROLÜ AKTİF DEĞİL - Bu yüzden duplikat bulunamadı!")
            elif check_media:
                media_file_count = sum(1 for f in self.all_scanned_files if self._is_media_file(f['path']))
                print(f"📸 Media dosya sayısı: {media_file_count}")
                if media_file_count == 0:
                    print("⚠️ HİÇ MEDIA DOSYASI YOK - Media kontrolü çalışmayacak!")
                else:
                    print("🔍 Media dosyaları var ama duplikat bulunamadı - boyut+dimensions eşleşmesi yok")
        
        # Muhtemel duplikatları da "Likely Duplicates" kategorisine ekle
        if hasattr(self, 'likely_duplicates') and self.likely_duplicates:
            likely_folder = "Likely Duplicates"
            if likely_folder not in self.organization_structure:
                self.organization_structure[likely_folder] = defaultdict(list)
            
            # Muhtemel duplikat çiftlerini organize et
            for i, pair in enumerate(self.likely_duplicates):
                try:
                    # Her çift için ayrı bir alt klasör oluştur
                    pair_folder = f"Pair_{i+1}_Confidence_{pair['confidence']}%"
                    
                    # İki dosyayı da aynı klasöre ekle
                    for file_key in ['file1', 'file2']:
                        file_info = pair[file_key].copy()  # Kopyala ki orijinali değişmesin
                        
                        # Muhtemel duplikat işareti ekle
                        file_info['is_likely_duplicate'] = True
                        file_info['pair_info'] = {
                            'confidence': pair['confidence'],
                            'name_similarity': pair['name_similarity'],
                            'size_difference': pair['size_difference'],
                            'dimension_match': pair['dimension_match']
                        }
                        
                        self.organization_structure[likely_folder][pair_folder].append(file_info)
                    
                    print(f"🤔 Muhtemel duplikat çifti preview'a eklendi: {pair['file1']['name']} & {pair['file2']['name']} -> Likely Duplicates/{pair_folder}")
                    
                except Exception as e:
                    print(f"⚠️ Muhtemel duplikat ekleme hatası: {e}")
        
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
            
            # Main app referansı varsa butonları sıfırla
            if hasattr(self, 'main_app') and self.main_app:
                self.main_app._reset_buttons_after_operation()
                print("✅ Tarama tamamlandı - butonlar sıfırlandı")
                
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
                
                # ÖNEMLİ: Öğrenilenleri hemen kaydet
                print("💾 Öğrenilen kategoriler kaydediliyor...")
                self.file_ops.save_learned_categories()
                print("✅ Öğrenilen kategoriler başarıyla kaydedildi!")
                
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