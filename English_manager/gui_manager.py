"""
GUI Manager Module - English Version
Handles all GUI components and window management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from pathlib import Path

class GUIManager:
    """GUI Manager - handles all interface components"""
    
    def __init__(self, root):
        self.root = root
        self.setup_main_window()
        self.setup_variables()
        self.setup_ui()
        
        print("✅ GUI Manager initialized!")
        
    def setup_main_window(self):
        """Setup main window properties"""
        self.root.title("File Organizer - Modular Version")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        
        # Set icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def setup_variables(self):
        """Setup tkinter variables"""
        # Folder paths
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.current_path_var = tk.StringVar()
        
        # Scan options
        self.scan_subfolders = tk.BooleanVar(value=True)
        
        # Scan mode variable: "all", "none", "files_only"
        self.scan_mode = tk.StringVar(value="all")
        
        # Duplicate options
        self.duplicate_check_name = tk.BooleanVar(value=True)
        self.duplicate_check_size = tk.BooleanVar(value=True)
        self.duplicate_check_hash = tk.BooleanVar(value=True)
        self.duplicate_action = tk.StringVar(value="ask")
        
        # Progress and status
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        
        # Time estimation variables
        self.time_estimation_var = tk.StringVar(value="")
        self.operation_start_time = None
        self.last_progress_time = None
        self.estimated_total_time = None
        
        print("✅ Variables initialized!")
        
    def setup_ui(self):
        """Setup user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top Panel - Folder selection
        self.setup_folder_selection(main_frame)
        
        # Middle Panel - Two windows
        self.setup_main_panels(main_frame)
        
        # Bottom Panel - Controls and status
        self.setup_bottom_panel(main_frame)
        
        print("✅ UI setup completed!")
        
    def setup_folder_selection(self, parent):
        """Folder selection panel"""
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Source Folder selection
        ttk.Label(top_frame, text="Source Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(top_frame, textvariable=self.source_var, width=50).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(top_frame, text="Select", command=self.select_source_folder).grid(row=0, column=2)
        
        # Target Drive selection
        ttk.Label(top_frame, text="Target Drive:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Entry(top_frame, textvariable=self.target_var, width=50).grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        ttk.Button(top_frame, text="Change", command=self.select_target_folder).grid(row=1, column=2, pady=(5, 0))
        
        # Subfolder scanning options
        self.setup_scan_options(top_frame)
        
    def setup_scan_options(self, parent):
        """Scan options"""
        scan_frame = ttk.Frame(parent)
        scan_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(scan_frame, text="Subfolder scanning mode:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Option 1: Scan all subfolders
        ttk.Radiobutton(scan_frame, text="✅ Scan all subfolders (categorize files)", 
                       variable=self.scan_mode, value="all").pack(side=tk.LEFT, padx=(0, 15))
        
        # Option 2: Copy folders completely
        ttk.Radiobutton(scan_frame, text="📁 Copy folders completely (preserve structure)", 
                       variable=self.scan_mode, value="none").pack(side=tk.LEFT, padx=(0, 15))
        
        # Option 3: Scan files only
        ttk.Radiobutton(scan_frame, text="📄 Scan files only (ignore subfolders)", 
                       variable=self.scan_mode, value="files_only").pack(side=tk.LEFT)
        
        # Reminder message
        reminder_frame = ttk.Frame(parent)
        reminder_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        reminder_text = ("💡 REMINDER: \n"
                        "• 'Scan all subfolders': Categorizes all files by type\n"
                        "• 'Copy folders completely': Preserves folder structure\n"
                        "• 'Scan files only': Ignores subfolders, processes only root folder files")
        
        reminder_label = ttk.Label(reminder_frame, text=reminder_text, 
                                 foreground="blue", font=('Arial', 8, 'italic'))
        reminder_label.pack(side=tk.LEFT, padx=(20, 0))
        
    def setup_main_panels(self, parent):
        """Main panels - left and right"""
        middle_frame = ttk.Frame(parent)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left Panel - Target File Manager
        self.setup_target_panel(middle_frame)
        
        # Right Panel - Source files and Organization
        self.setup_source_panel(middle_frame)
        
    def setup_target_panel(self, parent):
        """Left Panel - Target Folder file manager"""
        left_frame = ttk.LabelFrame(parent, text="Target Folder - File Manager")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Navigation controls
        nav_frame = ttk.Frame(left_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        ttk.Button(nav_frame, text="◀ Back", command=self.go_back).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="▲ Up", command=self.go_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="🏠 Home", command=self.go_home).pack(side=tk.LEFT, padx=(0, 5))
        
        # Path display bar
        path_frame = ttk.Frame(left_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        ttk.Label(path_frame, text="Location:").pack(side=tk.LEFT)
        self.path_entry = ttk.Entry(path_frame, textvariable=self.current_path_var, font=('Consolas', 9))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.path_entry.bind('<Return>', self.navigate_to_path)
        ttk.Button(path_frame, text="Go", command=self.navigate_to_path).pack(side=tk.RIGHT)

        # File manager controls
        target_controls = ttk.Frame(left_frame)
        target_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(target_controls, text="🔄 Refresh", command=self.refresh_target).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="🗑️ Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="📋 Copy", command=self.copy_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="✂️ Cut", command=self.cut_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="📁 Paste", command=self.paste_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(target_controls, text="➕ New Folder", command=self.create_folder).pack(side=tk.LEFT, padx=(0, 5))
        
        # Target folder tree
        self.setup_target_tree(left_frame)
        
    def setup_target_tree(self, parent):
        """Target folder tree widget"""
        target_frame = ttk.Frame(parent)
        target_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        self.target_tree = ttk.Treeview(target_frame, columns=('size', 'type', 'modified'), show='tree headings')
        self.target_tree.heading('#0', text='📁 Name', command=lambda: self.sort_tree('#0'))
        self.target_tree.heading('size', text='📏 Size', command=lambda: self.sort_tree('size'))
        self.target_tree.heading('type', text='🏷️ Type', command=lambda: self.sort_tree('type'))
        self.target_tree.heading('modified', text='📅 Modified', command=lambda: self.sort_tree('modified'))
        self.target_tree.column('#0', width=250)
        self.target_tree.column('size', width=80)
        self.target_tree.column('type', width=80)
        self.target_tree.column('modified', width=120)
        
        target_scrollbar = ttk.Scrollbar(target_frame, orient=tk.VERTICAL, command=self.target_tree.yview)
        self.target_tree.configure(yscrollcommand=target_scrollbar.set)
        
        self.target_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        target_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Event bindings
        self.setup_target_tree_events()
        
    def setup_target_tree_events(self):
        """Target tree event bindings"""
        # Double click and right click menu
        self.target_tree.bind('<Double-1>', self.on_target_double_click)
        self.target_tree.bind('<Button-3>', self.show_context_menu)
        
        # Keyboard shortcuts - target_tree specific
        self.target_tree.bind('<Delete>', lambda e: self.delete_selected())
        self.target_tree.bind('<Control-c>', lambda e: self.copy_selected())
        self.target_tree.bind('<Control-x>', lambda e: self.cut_selected())
        self.target_tree.bind('<Control-v>', lambda e: self.paste_selected())
        self.target_tree.bind('<F2>', lambda e: self.rename_selected())
        self.target_tree.bind('<F5>', lambda e: self.refresh_target())
        self.target_tree.bind('<BackSpace>', lambda e: self.go_up())
        self.target_tree.bind('<Return>', lambda e: self.open_selected())
        
    def setup_source_panel(self, parent):
        """Right Panel - Source files and Organization"""
        right_frame = ttk.LabelFrame(parent, text="Source Files and Organization Preview")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Source files
        self.setup_source_tab()
        
        # Tab 2: Organization preview
        self.setup_preview_tab()
        
        # Tab 3: Duplicate files
        self.setup_duplicate_tab()
        
    def setup_source_tab(self):
        """Source files tab"""
        source_tab = ttk.Frame(self.notebook)
        self.notebook.add(source_tab, text="Source Files")
        
        self.source_tree = ttk.Treeview(source_tab, columns=('size', 'type'), show='tree headings')
        self.source_tree.heading('#0', text='File Name')
        self.source_tree.heading('size', text='Size')
        self.source_tree.heading('type', text='Type')
        self.source_tree.column('#0', width=250)
        self.source_tree.column('size', width=80)
        self.source_tree.column('type', width=80)
        
        source_scrollbar = ttk.Scrollbar(source_tab, orient=tk.VERTICAL, command=self.source_tree.yview)
        self.source_tree.configure(yscrollcommand=source_scrollbar.set)
        
        self.source_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        source_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_preview_tab(self):
        """Organization preview tab"""
        preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(preview_tab, text="Organization Preview")
        
        self.preview_tree = ttk.Treeview(preview_tab, columns=('count',), show='tree headings')
        self.preview_tree.heading('#0', text='Folder Structure')
        self.preview_tree.heading('count', text='File Count')
        self.preview_tree.column('#0', width=250)
        self.preview_tree.column('count', width=100)
        
        preview_scrollbar = ttk.Scrollbar(preview_tab, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_duplicate_tab(self):
        """Duplicate files tab"""
        duplicate_tab = ttk.Frame(self.notebook)
        self.notebook.add(duplicate_tab, text="🔄 Duplicate Files")
        
        # Duplicate control options
        self.setup_duplicate_controls(duplicate_tab)
        
        # Duplicate tree
        self.setup_duplicate_tree(duplicate_tab)
        
    def setup_duplicate_controls(self, parent):
        """Duplicate control options"""
        # Duplicate check options
        dup_controls = ttk.Frame(parent)
        dup_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dup_controls, text="Duplicate Check:").pack(side=tk.LEFT)
        ttk.Checkbutton(dup_controls, text="Name", variable=self.duplicate_check_name).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Checkbutton(dup_controls, text="Size", variable=self.duplicate_check_size).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(dup_controls, text="Hash", variable=self.duplicate_check_hash).pack(side=tk.LEFT, padx=5)
        
        # Duplicate action options
        dup_action_frame = ttk.Frame(parent)
        dup_action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dup_action_frame, text="For duplicate files:").pack(side=tk.LEFT)
        ttk.Radiobutton(dup_action_frame, text="Ask each time", 
                       variable=self.duplicate_action, value="ask").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Radiobutton(dup_action_frame, text="Auto skip", 
                       variable=self.duplicate_action, value="skip").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(dup_action_frame, text="Copy with number", 
                       variable=self.duplicate_action, value="copy").pack(side=tk.LEFT, padx=5)
        
    def setup_duplicate_tree(self, parent):
        """Duplicate files tree"""
        self.duplicate_tree = ttk.Treeview(parent, columns=('path', 'size', 'hash'), show='tree headings')
        self.duplicate_tree.heading('#0', text='🔄 Duplicate File Groups')
        self.duplicate_tree.heading('path', text='File Path')
        self.duplicate_tree.heading('size', text='Size')
        self.duplicate_tree.heading('hash', text='Hash')
        self.duplicate_tree.column('#0', width=200)
        self.duplicate_tree.column('path', width=300)
        self.duplicate_tree.column('size', width=80)
        self.duplicate_tree.column('hash', width=120)
        
        duplicate_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.duplicate_tree.yview)
        self.duplicate_tree.configure(yscrollcommand=duplicate_scrollbar.set)
        
        self.duplicate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        duplicate_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_bottom_panel(self, parent):
        """Bottom panel - buttons, progress, status"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame, text="Scan Files", command=self.scan_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔍 Target Disk Analysis", command=self.analyze_target_disk).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Start Organization", command=self.start_organization).pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Time estimation label
        time_frame = ttk.Frame(bottom_frame)
        time_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.time_label = ttk.Label(time_frame, textvariable=self.time_estimation_var, 
                                   font=('Arial', 9), foreground='blue')
        self.time_label.pack(side=tk.RIGHT)
        
        # Status label
        status_label = ttk.Label(bottom_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X)
        
    # Placeholder methods - will be replaced with real methods from main_modular.py
    # Placeholder methods - will be replaced with rebind_buttons() in main_modular.py
    def select_source_folder(self):
        """Source folder selection - will be called from file_operations module"""
        pass
        
    def select_target_folder(self):
        """Target folder selection - will be called from file_operations module"""
        pass
        
    def go_back(self):
        """Go back - will be called from file_operations module"""
        pass
        
    def go_up(self):
        """Go up folder - will be called from file_operations module"""
        pass
        
    def go_home(self):
        """Go home folder - will be called from file_operations module"""
        pass
        
    def navigate_to_path(self, event=None):
        """Navigate to path - will be called from file_operations module"""
        pass
        
    def refresh_target(self):
        """Refresh target folder - will be called from file_operations module"""
        pass
        
    def delete_selected(self):
        """Delete selected files - will be called from file_operations module"""
        pass
        
    def copy_selected(self):
        """Copy selected files - will be called from file_operations module"""
        pass
        
    def cut_selected(self):
        """Cut selected files - will be called from file_operations module"""
        pass
        
    def paste_selected(self):
        """Paste files - will be called from file_operations module"""
        pass
        
    def create_folder(self):
        """Create new folder - will be called from file_operations module"""
        pass
        
    def sort_tree(self, column):
        """Tree sorting - will be called from file_operations module"""
        pass
        
    def on_target_double_click(self, event):
        """Double click - will be called from file_operations module"""
        pass
        
    def show_context_menu(self, event):
        """Right click menu - will be called from file_operations module"""
        pass
        
    def rename_selected(self):
        """Rename file - will be called from file_operations module"""
        pass
        
    def open_selected(self):
        """Open file/folder - will be called from file_operations module"""
        pass
        
    def scan_files(self):
        """File scanning - will be called from scan_engine module"""
        pass
        
    def analyze_target_disk(self):
        """Target disk analysis - will be called from reporting module"""
        pass
        
    def start_organization(self):
        """Start organization - will be called from file_operations module"""
        pass
        

        
    def start_time_estimation(self):
        """Start time estimation"""
        import time
        self.operation_start_time = time.time()
        self.last_progress_time = time.time()
        self.estimated_total_time = None
        self.time_estimation_var.set("")
    
    def update_time_estimation(self, current_progress, processed_items=None, total_items=None):
        """Update time estimation"""
        import time
        
        if not self.operation_start_time or current_progress <= 0:
            return
        
        current_time = time.time()
        elapsed_time = current_time - self.operation_start_time
        
        # Progress percentage 0-100
        if current_progress >= 100:
            self.time_estimation_var.set("✅ Completed!")
            return
        
        # Calculate remaining time
        if current_progress > 0:
            estimated_total_time = elapsed_time * (100 / current_progress)
            remaining_time = estimated_total_time - elapsed_time
            
            if remaining_time > 0:
                # Format time
                time_str = self.format_time(remaining_time)
                
                # Add extra info if available
                if processed_items and total_items:
                    remaining_items = total_items - processed_items
                    self.time_estimation_var.set(f"⏱️ Time remaining: {time_str} ({remaining_items} files)")
                else:
                    self.time_estimation_var.set(f"⏱️ Time remaining: {time_str}")
            else:
                self.time_estimation_var.set("⏱️ Calculating...")
    
    def format_time(self, seconds):
        """Convert time to readable format"""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def stop_time_estimation(self):
        """Stop time estimation"""
        self.operation_start_time = None
        self.last_progress_time = None
        self.estimated_total_time = None
        self.time_estimation_var.set("") 