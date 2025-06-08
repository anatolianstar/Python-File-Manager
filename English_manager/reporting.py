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

class ReportingManager:
    def __init__(self, gui_manager, file_operations, scan_engine):
        self.gui = gui_manager
        self.file_ops = file_operations
        self.scan_engine = scan_engine
        
        # Analysis sonuçları
        self.target_analysis = {}
        self.disk_analysis = {}
        
    def analyze_target_disk(self):
        """Target Disk Analysis"""
        if not self.gui.source_var.get():
            messagebox.showwarning("Warning", "Please select source folder first!")
            return
        
        if not self.scan_engine.all_scanned_files:
            messagebox.showwarning("Warning", "Please scan files first!")
            return
        
        # Thread Start
        analysis_thread = threading.Thread(target=self._analyze_target_thread, daemon=True)
        analysis_thread.start()
    
    def _analyze_target_thread(self):
        """Target Disk Analysis thread'i"""
        try:
            self.gui.status_var.set("Target disk Analysis ediliyor...")
            self.gui.progress_var.set(0)
            
            # Time estimation Start
            self.gui.start_time_estimation()
            
            # Target Disk Analysis yap
            self._perform_target_analysis()
            
            # Sonuçları Show
            self.gui.root.after(0, self._show_analysis_results)
            
        except Exception as e:
            self.gui.root.after(0, lambda: messagebox.showerror("Error", f"Analysis hatası: {e}"))
        finally:
            self.gui.root.after(0, lambda: self.gui.status_var.set("Analysis Completed"))
            # Time estimation Stop
            self.gui.root.after(0, lambda: self.gui.stop_time_estimation())
    
    def _perform_target_analysis(self):
        """Target disk analizini gerçekleştir"""
        target_path = self.gui.target_var.get()
        
        # Target diskteki available files Scan
        existing_files = self._scan_target_files(target_path)
        
        # Source dosyalarla karşılaştır
        self._compare_source_target(existing_files)
        
        # Disk alanı analizi
        self._analyze_disk_space(target_path)
        
        # Kategori bazlı Analysis
        self._analyze_by_categories()
    
    def _scan_target_files(self, target_path):
        """Target diskteki files Scan"""
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
                        file_key = f"{file}_{stat.st_size}"  # Name + Size
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
        """Source ve Target files karşılaştır"""
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
                # File zaten available
                self.target_analysis['files_existing'].append({
                    'source': file_info,
                    'target': existing_files[file_key]
                })
                self.target_analysis['existing_files'] += 1
                self.target_analysis['existing_size'] += file_info['size']
            else:
                # File to be copied
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
                # Windows for alternatif
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
                'space_sufficient': True  # Secure taraf
            }
    
    def _analyze_by_categories(self):
        """Kategori bazlı Analysis"""
        self.category_analysis = defaultdict(lambda: {
            'to_copy': 0,
            'existing': 0,
            'copy_size': 0,
            'existing_size': 0,
            'files_to_copy': [],
            'files_existing': []
        })
        
        # to be copied files
        for file_info in self.target_analysis['files_to_copy']:
            category, _ = self.file_ops.get_file_category(file_info['path'])
            self.category_analysis[category]['to_copy'] += 1
            self.category_analysis[category]['copy_size'] += file_info['size']
            self.category_analysis[category]['files_to_copy'].append(file_info)
        
        # available files
        for existing_info in self.target_analysis['files_existing']:
            file_info = existing_info['source']
            category, _ = self.file_ops.get_file_category(file_info['path'])
            self.category_analysis[category]['existing'] += 1
            self.category_analysis[category]['existing_size'] += file_info['size']
            self.category_analysis[category]['files_existing'].append(existing_info)
        
        # Progress tamamla
        self.gui.root.after(0, lambda: self.gui.progress_var.set(100))
    
    def _show_analysis_results(self):
        """Analysis sonuçlarını Show"""
        # New Window oluştur
        analysis_window = tk.Toplevel(self.gui.root)
        analysis_window.title("🔍 Target Disk Analysis Raporu")
        analysis_window.geometry("800x600")
        analysis_window.transient(self.gui.root)
        
        # Scrollable text widget
        text_frame = tk.Frame(analysis_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Report içeriği
        report_content = self._generate_analysis_report()
        text_widget.insert(tk.END, report_content)
        text_widget.config(state=tk.DISABLED)
        
        # Butonlar
        button_frame = tk.Frame(analysis_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text="📄 Raporu Save", 
                 command=lambda: self._save_report(report_content)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="❌ Close", 
                 command=analysis_window.destroy).pack(side=tk.RIGHT)
    
    def _generate_analysis_report(self):
        """Analysis raporunu oluştur"""
        report = "🔍 Target Disk Analysis RAPORU\n"
        report += "=" * 50 + "\n\n"
        
        # Public Statistics
        report += "📊 Public Statistics\n"
        report += "-" * 30 + "\n"
        report += f"Source Folder: {self.gui.source_var.get()}\n"
        report += f"Target Folder: {self.gui.target_var.get()}\n"
        report += f"scanning tarihi: {time.strftime('%d.%m.%Y %H:%M:%S')}\n\n"
        
        # File sayıları
        total_source = len(self.scan_engine.unique_files)
        new_files = self.target_analysis['new_files']
        existing_files = self.target_analysis['existing_files']
        
        report += f"Total Source File: {total_source}\n"
        report += f"to be copied File: {new_files}\n"
        report += f"Zaten available File: {existing_files}\n"
        report += f"Duplicate File: {len(self.scan_engine.duplicate_files)}\n\n"
        
        # Size bilgileri
        report += "💾 Size BİLGİLERİ\n"
        report += "-" * 30 + "\n"
        report += f"to be copied Total Size: {self._format_size(self.target_analysis['total_copy_size'])}\n"
        report += f"available File boyutu: {self._format_size(self.target_analysis['existing_size'])}\n\n"
        
        # Disk alanı analizi
        if 'error' not in self.disk_analysis:
            report += "💿 DİSK ALANI ANALİZİ\n"
            report += "-" * 30 + "\n"
            report += f"Total disk alanı: {self._format_size(self.disk_analysis['total_space'])}\n"
            report += f"Kullanılan alan: {self._format_size(self.disk_analysis['used_space'])}\n"
            report += f"empty alan: {self._format_size(self.disk_analysis['free_space'])}\n"
            report += f"Gerekli alan: {self._format_size(self.disk_analysis['required_space'])}\n"
            
            if self.disk_analysis['space_sufficient']:
                remaining = self.disk_analysis['space_after_copy']
                report += f"✅ Yeterli alan var! Remaining: {self._format_size(remaining)}\n\n"
            else:
                shortage = self.disk_analysis['required_space'] - self.disk_analysis['free_space']
                report += f"❌ Yetersiz alan! Eksik: {self._format_size(shortage)}\n\n"
        
        # Kategori bazlı Analysis
        report += "📁 KATEGORİ BAZLI Analysis\n"
        report += "-" * 30 + "\n"
        
        for category, analysis in self.category_analysis.items():
            if analysis['to_copy'] > 0 or analysis['existing'] > 0:
                category_name = category.title().replace('_', ' ')
                report += f"\n🏷️ {category_name}:\n"
                report += f"  • to be copied: {analysis['to_copy']} File ({self._format_size(analysis['copy_size'])})\n"
                report += f"  • available: {analysis['existing']} File ({self._format_size(analysis['existing_size'])})\n"
        
        # Detaylı Organization yapısı
        report += "\n\n📂 DETAYLI Organization YAPISI\n"
        report += "-" * 40 + "\n"
        
        for main_folder, subfolders in self.scan_engine.organization_structure.items():
            total_files = sum(len(files) for files in subfolders.values())
            total_size = sum(sum(f['size'] for f in files) for files in subfolders.values())
            
            report += f"\n📁 {main_folder}/ ({total_files} File, {self._format_size(total_size)})\n"
            
            for subfolder, files in subfolders.items():
                subfolder_size = sum(f['size'] for f in files)
                report += f"  📂 {subfolder}/ ({len(files)} File, {self._format_size(subfolder_size)})\n"
                
                # First birkaç file listele
                for i, file_info in enumerate(files[:5]):
                    report += f"    📄 {file_info['name']} ({self._format_size(file_info['size'])})\n"
                
                if len(files) > 5:
                    report += f"    ... ve {len(files) - 5} File daha\n"
        
        # Duplicate analizi
        if self.scan_engine.source_duplicates:
            report += "\n\n🔄 Duplicate File ANALİZİ\n"
            report += "-" * 40 + "\n"
            report += f"Total Duplicate grup: {len(self.scan_engine.source_duplicates)}\n"
            report += f"Total Duplicate File: {len(self.scan_engine.duplicate_files)}\n\n"
            
            for i, duplicate_group in enumerate(self.scan_engine.source_duplicates[:10]):  # First 10 grup
                report += f"Grup {i+1}: {len(duplicate_group)} File\n"
                for file_info in duplicate_group:
                    report += f"  📄 {file_info['name']} - {file_info['path']}\n"
                report += "\n"
            
            if len(self.scan_engine.source_duplicates) > 10:
                report += f"... ve {len(self.scan_engine.source_duplicates) - 10} grup daha\n"
        
        # Öneriler
        report += "\n\n💡 ÖNERİLER\n"
        report += "-" * 20 + "\n"
        
        if self.target_analysis['new_files'] == 0:
            report += "✅ Tüm files zaten Target folder available.\n"
        elif not self.disk_analysis.get('space_sufficient', True):
            report += "⚠️ Disk alanı yetersiz! before yer açın veya gereksiz files silin.\n"
        else:
            report += f"✅ {new_files} File kopyalanmaya Ready.\n"
        
        if len(self.scan_engine.duplicate_files) > 0:
            report += f"🔄 {len(self.scan_engine.duplicate_files)} Duplicate File tespit edildi. İncelemeniz önerilir.\n"
        
        report += "\n" + "=" * 50 + "\n"
        report += "Report sonu - File Organizatörü v2.0"
        
        return report
    
    def _save_report(self, report_content):
        """Raporu dosyaya Save"""
        filename = filedialog.asksaveasfilename(
            title="Raporu Save",
            defaultextension=".txt",
            filetypes=[("Metin Dosyası", "*.txt"), ("Tüm files", "*.*")],
            initialname=f"hedef_disk_analizi_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                messagebox.showinfo("successful", f"Report kaydedildi:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Report kaydedilemedi: {e}")
    
    def show_duplicates(self):
        """Show duplicate files in detail"""
        if not self.scan_engine.source_duplicates:
            messagebox.showinfo("Info", "No duplicate files found!")
            return
        
        # Duplicate raporu penceresi
        dup_window = tk.Toplevel(self.gui.root)
        dup_window.title("🔄 Duplicate File Raporu")
        dup_window.geometry("700x500")
        dup_window.transient(self.gui.root)
        
        # Text widget
        text_frame = tk.Frame(dup_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 9))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Duplicate raporu oluştur
        dup_report = self._generate_duplicate_report()
        text_widget.insert(tk.END, dup_report)
        text_widget.config(state=tk.DISABLED)
        
        # Butonlar
        button_frame = tk.Frame(dup_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text="📄 Raporu Save", 
                 command=lambda: self._save_report(dup_report)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="❌ Close", 
                 command=dup_window.destroy).pack(side=tk.RIGHT)
    
    def _generate_duplicate_report(self):
        """Duplicate raporu oluştur"""
        report = "🔄 Duplicate File RAPORU\n"
        report += "=" * 40 + "\n\n"
        
        report += f"Total Duplicate grup: {len(self.scan_engine.source_duplicates)}\n"
        report += f"Total Duplicate File: {len(self.scan_engine.duplicate_files)}\n"
        report += f"Report tarihi: {time.strftime('%d.%m.%Y %H:%M:%S')}\n\n"
        
        # Her Duplicate grubu for
        for i, duplicate_group in enumerate(self.scan_engine.source_duplicates):
            report += f"📁 GRUP {i+1} ({len(duplicate_group)} File)\n"
            report += "-" * 30 + "\n"
            
            # Grup bilgileri
            first_file = duplicate_group[0]
            report += f"File Name: {first_file['name']}\n"
            report += f"Size: {self._format_size(first_file['size'])}\n"
            report += f"Uzantı: {first_file['extension']}\n\n"
            
            # File yolları
            report += "File konumları:\n"
            for j, file_info in enumerate(duplicate_group):
                report += f"  {j+1}. {file_info['path']}\n"
            
            report += "\n" + "="*40 + "\n\n"
        
        return report
    
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
    
    def generate_organization_report(self):
        """Organization raporu oluştur"""
        if not self.scan_engine.organization_structure:
            messagebox.showwarning("Warning", "Please scan files first!")
            return
        
        report = "📂 Organization RAPORU\n"
        report += "=" * 30 + "\n\n"
        
        # Özet
        total_files = sum(len(files) for subfolders in self.scan_engine.organization_structure.values() 
                         for files in subfolders.values())
        total_size = sum(sum(f['size'] for f in files) for subfolders in self.scan_engine.organization_structure.values() 
                        for files in subfolders.values())
        
        report += f"Total File: {total_files}\n"
        report += f"Total Size: {self._format_size(total_size)}\n"
        report += f"Kategori sayısı: {len(self.scan_engine.organization_structure)}\n\n"
        
        # Detaylar
        for main_folder, subfolders in self.scan_engine.organization_structure.items():
            folder_files = sum(len(files) for files in subfolders.values())
            folder_size = sum(sum(f['size'] for f in files) for files in subfolders.values())
            
            report += f"📁 {main_folder}/ ({folder_files} File, {self._format_size(folder_size)})\n"
            
            for subfolder, files in subfolders.items():
                subfolder_size = sum(f['size'] for f in files)
                report += f"  📂 {subfolder}/ ({len(files)} File, {self._format_size(subfolder_size)})\n"
        
        return report 