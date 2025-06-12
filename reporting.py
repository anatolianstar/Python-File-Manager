"""
Reporting Module
Raporlama işlemlerini içerir
"""

import os
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import threading
import time
from pathlib import Path
from collections import defaultdict
from lang_manager import lang_manager

class ReportingManager:
    def __init__(self, gui_manager, file_operations, scan_engine):
        self.gui = gui_manager
        self.file_ops = file_operations
        self.scan_engine = scan_engine
        
        # Analiz sonuçları
        self.target_analysis = {}
        self.disk_analysis = {}
        
    def analyze_target_disk(self):
        """Hedef disk analizi"""
        if not self.gui.source_var.get():
            messagebox.showwarning("Uyarı", "Önce kaynak klasör seçin!")
            return
        
        if not self.scan_engine.all_scanned_files:
            messagebox.showwarning("Uyarı", "Önce dosyaları tarayın!")
            return
        
        # Thread başlat
        analysis_thread = threading.Thread(target=self._analyze_target_thread, daemon=True)
        analysis_thread.start()
    
    def _analyze_target_thread(self):
        """Hedef disk analizi thread'i"""
        try:
            self.gui.status_var.set("Hedef disk analiz ediliyor...")
            self.gui.progress_var.set(0)
            
            # Time estimation başlat
            self.gui.start_time_estimation()
            
            # Hedef disk analizi yap
            self._perform_target_analysis()
            
            # Sonuçları göster
            self.gui.root.after(0, self._show_analysis_results)
            
        except Exception as e:
            self.gui.root.after(0, lambda: messagebox.showerror("Hata", f"Analiz hatası: {e}"))
        finally:
            self.gui.root.after(0, lambda: self.gui.status_var.set("Analiz tamamlandı"))
            # Time estimation durdur
            self.gui.root.after(0, lambda: self.gui.stop_time_estimation())
    
    def _perform_target_analysis(self):
        """Hedef disk analizini gerçekleştir"""
        target_path = self.gui.target_var.get()
        
        # Hedef diskteki mevcut dosyaları tara
        existing_files = self._scan_target_files(target_path)
        
        # Kaynak dosyalarla karşılaştır
        self._compare_source_target(existing_files)
        
        # Disk alanı analizi
        self._analyze_disk_space(target_path)
        
        # Kategori bazlı analiz
        self._analyze_by_categories()
    
    def _scan_target_files(self, target_path):
        """Hedef diskteki dosyaları tara"""
        existing_files = {}
        
        try:
            for root, dirs, files in os.walk(target_path):
                # Progress güncelle
                self.gui.root.after(0, lambda: self.gui.progress_var.set(25))
                
                for i, file in enumerate(files):
                    if self.file_ops.is_hidden_file(file):
                        continue
                    
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        file_key = f"{file}_{stat.st_size}"  # İsim + boyut
                        existing_files[file_key] = {
                            'path': file_path,
                            'name': file,
                            'size': stat.st_size,
                            'relative_path': os.path.relpath(file_path, target_path)
                        }
                    except:
                        continue
                    
                    # Time estimation güncelle
                    self.gui.root.after(0, lambda p=25 + (i + 1) / len(files) * 50, processed=i+1, total=len(files): 
                                       self.gui.update_time_estimation(p, processed, total))
        except:
            pass
        
        return existing_files
    
    def _compare_source_target(self, existing_files):
        """Kaynak ve hedef dosyaları karşılaştır"""
        self.target_analysis = {
            'files_to_copy': [],
            'files_existing': [],
            'new_files': 0,
            'existing_files': 0,
            'total_copy_size': 0,
            'existing_size': 0
        }
        
        total_files = len(self.scan_engine.unique_files)
        
        for i, file_info in enumerate(self.scan_engine.unique_files):
            # Progress güncelle
            progress = 25 + (i + 1) / total_files * 50  # %25-75 arası
            self.gui.root.after(0, lambda p=progress: self.gui.progress_var.set(p))
            
            # Time estimation güncelle
            self.gui.root.after(0, lambda p=progress, processed=i+1, total=total_files: 
                               self.gui.update_time_estimation(p, processed, total))
            
            file_key = f"{file_info['name']}_{file_info['size']}"
            
            if file_key in existing_files:
                # Dosya zaten mevcut
                self.target_analysis['files_existing'].append({
                    'source': file_info,
                    'target': existing_files[file_key]
                })
                self.target_analysis['existing_files'] += 1
                self.target_analysis['existing_size'] += file_info['size']
            else:
                # Dosya kopyalanacak
                self.target_analysis['files_to_copy'].append(file_info)
                self.target_analysis['new_files'] += 1
                self.target_analysis['total_copy_size'] += file_info['size']
    
    def _analyze_disk_space(self, target_path):
        """Disk alanı analizi"""
        try:
            # Disk alanı bilgisi
            statvfs = os.statvfs(target_path) if hasattr(os, 'statvfs') else None
            
            if statvfs:
                total_space = statvfs.f_frsize * statvfs.f_blocks
                free_space = statvfs.f_frsize * statvfs.f_available
                used_space = total_space - free_space
            else:
                # Windows için alternatif
                import shutil
                total_space, used_space, free_space = shutil.disk_usage(target_path)
            
            self.disk_analysis = {
                'total_space': total_space,
                'free_space': free_space,
                'used_space': used_space,
                'required_space': self.target_analysis['total_copy_size'],
                'space_after_copy': free_space - self.target_analysis['total_copy_size'],
                'space_sufficient': free_space >= self.target_analysis['total_copy_size']
            }
            
        except Exception as e:
            self.disk_analysis = {
                'error': str(e),
                'space_sufficient': True  # Güvenli taraf
            }
    
    def _analyze_by_categories(self):
        """Kategori bazlı analiz"""
        self.category_analysis = defaultdict(lambda: {
            'to_copy': 0,
            'existing': 0,
            'copy_size': 0,
            'existing_size': 0,
            'files_to_copy': [],
            'files_existing': []
        })
        
        # Kopyalanacak dosyalar
        for file_info in self.target_analysis['files_to_copy']:
            category, _ = self.file_ops.get_file_category(file_info['path'])
            self.category_analysis[category]['to_copy'] += 1
            self.category_analysis[category]['copy_size'] += file_info['size']
            self.category_analysis[category]['files_to_copy'].append(file_info)
        
        # Mevcut dosyalar
        for existing_info in self.target_analysis['files_existing']:
            file_info = existing_info['source']
            category, _ = self.file_ops.get_file_category(file_info['path'])
            self.category_analysis[category]['existing'] += 1
            self.category_analysis[category]['existing_size'] += file_info['size']
            self.category_analysis[category]['files_existing'].append(existing_info)
        
        # Progress tamamla
        self.gui.root.after(0, lambda: self.gui.progress_var.set(100))
    
    def _show_analysis_results(self):
        """Analiz sonuçlarını göster"""
        # Yeni pencere oluştur
        analysis_window = tk.Toplevel(self.gui.root)
        analysis_window.title(lang_manager.get_text('reports.analysis.title'))
        analysis_window.geometry("800x600")
        analysis_window.transient(self.gui.root)
        
        # Scrollable text widget
        text_frame = tk.Frame(analysis_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Rapor içeriği
        report_content = self._generate_analysis_report()
        text_widget.insert(tk.END, report_content)
        text_widget.config(state=tk.DISABLED)
        
        # Butonlar
        button_frame = tk.Frame(analysis_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text="📄 Raporu Kaydet", 
                 command=lambda: self._save_report(report_content)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="❌ Kapat", 
                 command=analysis_window.destroy).pack(side=tk.RIGHT)
    
    def _generate_analysis_report(self):
        """Analiz raporunu oluştur"""
        report = "🔍 HEDEF DİSK ANALİZİ RAPORU\n"
        report += "=" * 50 + "\n\n"
        
        # Genel istatistikler
        report += f"{lang_manager.get_text('reports.analysis.general_stats')}\n"
        report += "-" * 30 + "\n"
        report += f"{lang_manager.get_text('reports.analysis.source_folder')}: {self.gui.source_var.get()}\n"
        report += f"{lang_manager.get_text('reports.analysis.target_folder')}: {self.gui.target_var.get()}\n"
        report += f"{lang_manager.get_text('reports.analysis.scan_date')}: {time.strftime('%d.%m.%Y %H:%M:%S')}\n\n"
        
        # Dosya sayıları
        total_source = len(self.scan_engine.unique_files)
        new_files = self.target_analysis['new_files']
        existing_files = self.target_analysis['existing_files']
        
        report += f"{lang_manager.get_text('reports.analysis.total_source_files')}: {total_source}\n"
        report += f"{lang_manager.get_text('reports.analysis.files_to_copy')}: {new_files}\n"
        report += f"{lang_manager.get_text('reports.analysis.existing_files')}: {existing_files}\n"
        report += f"{lang_manager.get_text('reports.analysis.duplicate_files')}: {len(self.scan_engine.duplicate_files)}\n\n"
        
        # Boyut bilgileri
        report += f"{lang_manager.get_text('reports.analysis.size_info')}\n"
        report += "-" * 30 + "\n"
        report += f"{lang_manager.get_text('reports.analysis.total_copy_size')}: {self._format_size(self.target_analysis['total_copy_size'])}\n"
        report += f"{lang_manager.get_text('reports.analysis.existing_size')}: {self._format_size(self.target_analysis['existing_size'])}\n\n"
        
        # Disk alanı analizi
        if 'error' not in self.disk_analysis:
            report += f"{lang_manager.get_text('reports.analysis.disk_analysis')}\n"
            report += "-" * 30 + "\n"
            report += f"{lang_manager.get_text('reports.analysis.total_disk_space')}: {self._format_size(self.disk_analysis['total_space'])}\n"
            report += f"{lang_manager.get_text('reports.analysis.used_space')}: {self._format_size(self.disk_analysis['used_space'])}\n"
            report += f"{lang_manager.get_text('reports.analysis.free_space')}: {self._format_size(self.disk_analysis['free_space'])}\n"
            report += f"{lang_manager.get_text('reports.analysis.required_space')}: {self._format_size(self.disk_analysis['required_space'])}\n"
            
            if self.disk_analysis['space_sufficient']:
                remaining = self.disk_analysis['space_after_copy']
                report += f"{lang_manager.get_text('reports.analysis.sufficient_space')}: {self._format_size(remaining)}\n\n"
            else:
                shortage = self.disk_analysis['required_space'] - self.disk_analysis['free_space']
                report += f"{lang_manager.get_text('reports.analysis.insufficient_space')}: {self._format_size(shortage)}\n\n"
        
        # Kategori bazlı analiz
        report += f"{lang_manager.get_text('reports.analysis.category_analysis')}\n"
        report += "-" * 30 + "\n"
        
        for category, analysis in self.category_analysis.items():
            if analysis['to_copy'] > 0 or analysis['existing'] > 0:
                category_name = category.title().replace('_', ' ')
                report += f"\n🏷️ {category_name}:\n"
                report += f"  • {lang_manager.get_text('reports.analysis.to_copy')}: {analysis['to_copy']} dosya ({self._format_size(analysis['copy_size'])})\n"
                report += f"  • {lang_manager.get_text('reports.analysis.existing')}: {analysis['existing']} dosya ({self._format_size(analysis['existing_size'])})\n"
        
        # Detaylı organizasyon yapısı
        report += f"\n\n{lang_manager.get_text('reports.analysis.organization_structure')}\n"
        report += "-" * 40 + "\n"
        
        for main_folder, subfolders in self.scan_engine.organization_structure.items():
            total_files = sum(len(files) for files in subfolders.values())
            total_size = sum(sum(f['size'] for f in files) for files in subfolders.values())
            
            report += f"\n📁 {main_folder}/ ({total_files} dosya, {self._format_size(total_size)})\n"
            
            for subfolder, files in subfolders.items():
                subfolder_size = sum(f['size'] for f in files)
                report += f"  📂 {subfolder}/ ({len(files)} dosya, {self._format_size(subfolder_size)})\n"
                
                # İlk birkaç dosyayı listele
                for i, file_info in enumerate(files[:5]):
                    report += f"    📄 {file_info['name']} ({self._format_size(file_info['size'])})\n"
                
                if len(files) > 5:
                    report += f"    ... ve {len(files) - 5} dosya daha\n"
        
        # Duplikat analizi
        if self.scan_engine.source_duplicates:
            report += f"\n\n{lang_manager.get_text('reports.analysis.duplicate_analysis')}\n"
            report += "-" * 40 + "\n"
            report += f"{lang_manager.get_text('reports.analysis.total_duplicate_groups')}: {len(self.scan_engine.source_duplicates)}\n"
            report += f"{lang_manager.get_text('reports.analysis.total_duplicate_files')}: {len(self.scan_engine.duplicate_files)}\n\n"
            
            for i, duplicate_group in enumerate(self.scan_engine.source_duplicates[:10]):  # İlk 10 grup
                report += f"Grup {i+1}: {len(duplicate_group)} dosya\n"
                for file_info in duplicate_group:
                    report += f"  📄 {file_info['name']} - {file_info['path']}\n"
                report += "\n"
            
            if len(self.scan_engine.source_duplicates) > 10:
                report += f"... ve {len(self.scan_engine.source_duplicates) - 10} grup daha\n"
        
        # Öneriler
        report += f"\n\n{lang_manager.get_text('reports.analysis.suggestions')}\n"
        report += "-" * 20 + "\n"
        
        if self.target_analysis['new_files'] == 0:
            report += f"{lang_manager.get_text('reports.analysis.all_files_exist')}\n"
        elif not self.disk_analysis.get('space_sufficient', True):
            report += f"{lang_manager.get_text('reports.analysis.insufficient_disk')}\n"
        else:
            report += f"✅ {lang_manager.get_text('messages.ready_to_copy').format(count=new_files)}\n"
        
        if len(self.scan_engine.duplicate_files) > 0:
            report += f"{lang_manager.get_text('reports.analysis.duplicates_found').format(count=len(self.scan_engine.duplicate_files))}\n"
        
        report += "\n" + "=" * 50 + "\n"
        report += f"{lang_manager.get_text('reports.analysis.report_end')}"
        
        return report
    
    def _save_report(self, report_content):
        """Raporu dosyaya kaydet"""
        filename = filedialog.asksaveasfilename(
            title=lang_manager.get_text('reports.save.title'),
            defaultextension=".txt",
            filetypes=[("Metin Dosyası", "*.txt"), ("Tüm Dosyalar", "*.*")],
            initialname=f"hedef_disk_analizi_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), f"{lang_manager.get_text('reports.save.success')}:\n{filename}")
            except Exception as e:
                messagebox.showerror(lang_manager.get_text('dialogs.error.title'), f"{lang_manager.get_text('reports.save.error')}: {e}")
    
    def show_duplicates(self):
        """Duplikat dosyaları detaylı göster"""
        if not self.scan_engine.source_duplicates:
            messagebox.showinfo(lang_manager.get_text('dialogs.info.title'), lang_manager.get_text('reports.duplicate.no_duplicates'))
            return
        
        # Duplikat raporu penceresi
        dup_window = tk.Toplevel(self.gui.root)
        dup_window.title(lang_manager.get_text('reports.duplicate.title'))
        dup_window.geometry("700x500")
        dup_window.transient(self.gui.root)
        
        # Text widget
        text_frame = tk.Frame(dup_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 9))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Duplikat raporu oluştur
        dup_report = self._generate_duplicate_report()
        text_widget.insert(tk.END, dup_report)
        text_widget.config(state=tk.DISABLED)
        
        # Butonlar
        button_frame = tk.Frame(dup_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text=lang_manager.get_text('reports.duplicate.save_report'), 
                 command=lambda: self._save_report(dup_report)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text=lang_manager.get_text('reports.duplicate.close'), 
                 command=dup_window.destroy).pack(side=tk.RIGHT)
    
    def _generate_duplicate_report(self):
        """Duplikat raporu oluştur"""
        report = f"{lang_manager.get_text('reports.duplicate.title')}\n"
        report += "=" * 40 + "\n\n"
        
        report += f"{lang_manager.get_text('reports.analysis.total_duplicate_groups')}: {len(self.scan_engine.source_duplicates)}\n"
        report += f"{lang_manager.get_text('reports.analysis.total_duplicate_files')}: {len(self.scan_engine.duplicate_files)}\n"
        report += f"{lang_manager.get_text('reports.duplicate.report_date')}: {time.strftime('%d.%m.%Y %H:%M:%S')}\n\n"
        
        # Her duplikat grubu için
        for i, duplicate_group in enumerate(self.scan_engine.source_duplicates):
            report += f"{lang_manager.get_text('reports.duplicate.group')} {i+1} ({len(duplicate_group)} dosya)\n"
            report += "-" * 30 + "\n"
            
            # Grup bilgileri
            first_file = duplicate_group[0]
            report += f"{lang_manager.get_text('reports.duplicate.file_name')}: {first_file['name']}\n"
            report += f"{lang_manager.get_text('reports.duplicate.size')}: {self._format_size(first_file['size'])}\n"
            report += f"{lang_manager.get_text('reports.duplicate.extension')}: {first_file['extension']}\n\n"
            
            # Dosya yolları
            report += f"{lang_manager.get_text('reports.duplicate.locations')}:\n"
            for j, file_info in enumerate(duplicate_group):
                report += f"  {j+1}. {file_info['path']}\n"
            
            report += "\n" + "="*40 + "\n\n"
        
        return report
    
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
    
    def generate_organization_report(self):
        """Organizasyon raporu oluştur"""
        if not self.scan_engine.organization_structure:
            messagebox.showwarning("Uyarı", "Önce dosyaları tarayın!")
            return
        
        report = "📂 ORGANİZASYON RAPORU\n"
        report += "=" * 30 + "\n\n"
        
        # Özet
        total_files = sum(len(files) for subfolders in self.scan_engine.organization_structure.values() 
                         for files in subfolders.values())
        total_size = sum(sum(f['size'] for f in files) for subfolders in self.scan_engine.organization_structure.values() 
                        for files in subfolders.values())
        
        report += f"Toplam dosya: {total_files}\n"
        report += f"Toplam boyut: {self._format_size(total_size)}\n"
        report += f"Kategori sayısı: {len(self.scan_engine.organization_structure)}\n\n"
        
        # Detaylar
        for main_folder, subfolders in self.scan_engine.organization_structure.items():
            folder_files = sum(len(files) for files in subfolders.values())
            folder_size = sum(sum(f['size'] for f in files) for files in subfolders.values())
            
            report += f"📁 {main_folder}/ ({folder_files} dosya, {self._format_size(folder_size)})\n"
            
            for subfolder, files in subfolders.items():
                subfolder_size = sum(f['size'] for f in files)
                report += f"  📂 {subfolder}/ ({len(files)} dosya, {self._format_size(subfolder_size)})\n"
        
        return report 