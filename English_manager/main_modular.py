"""
Modular File Manager - Main Module
English Version

A comprehensive file organization tool with modular architecture.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
try:
    from gui_manager import GUIManager
    from file_operations import FileOperations
    from scan_engine import ScanEngine
    from reporting import ReportingManager
except ImportError as e:
    print(f"Module import error: {e}")
    print("Make sure all module files are in the same folder!")
    sys.exit(1)

class ModularFileManager:
    """Main application class - coordinates all modules"""
    
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("File Organizer - Modular Version v2.0")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        
        # Initialize modules
        self.initialize_modules()
        
        # Setup connections between modules
        self.setup_connections()
        
        # Test connections
        self.test_connections()
        
        # Setup initial state
        self.setup_initial_state()
        
        print("✅ Modular File Manager initialized successfully!")
    
    def initialize_modules(self):
        """Initialize all modules"""
        print("🔧 Initializing modules...")
        
        try:
            # GUI Manager - creates the interface
            self.gui_manager = GUIManager(self.root)
            
            # File Operations - handles file operations
            self.file_operations = FileOperations(self.gui_manager)
            
            # Scan Engine - handles file scanning
            self.scan_engine = ScanEngine(self.gui_manager, self.file_operations)
            
            # Reporting - handles analysis and reports
            self.reporting = ReportingManager(self.gui_manager, self.file_operations, self.scan_engine)
            
            print("✅ All modules initialized!")
            
        except Exception as e:
            messagebox.showerror("Startup Error", f"Error loading modules: {e}")
            sys.exit(1)
    
    def setup_connections(self):
        """Setup connections between modules"""
        print("🔗 Setting up module connections...")
        
        # File Operations connections
        self.gui_manager.select_source_folder = self.file_operations.select_source_folder
        self.gui_manager.select_target_folder = self.file_operations.select_target_folder
        self.gui_manager.go_back = self.file_operations.go_back
        self.gui_manager.go_up = self.file_operations.go_up
        self.gui_manager.go_home = self.file_operations.go_home
        self.gui_manager.navigate_to_path = self.file_operations.navigate_to_path
        self.gui_manager.refresh_target = self.file_operations.refresh_target
        self.gui_manager.delete_selected = self.file_operations.delete_selected
        self.gui_manager.copy_selected = self.file_operations.copy_selected
        self.gui_manager.cut_selected = self.file_operations.cut_selected
        self.gui_manager.paste_selected = self.file_operations.paste_selected
        self.gui_manager.create_folder = self.file_operations.create_folder
        self.gui_manager.sort_tree = self.file_operations.sort_tree
        self.gui_manager.on_target_double_click = self.file_operations.on_target_double_click
        self.gui_manager.show_context_menu = self.file_operations.show_context_menu
        self.gui_manager.rename_selected = self.file_operations.rename_selected
        self.gui_manager.open_selected = self.file_operations.open_selected
        
        # Scan Engine connections
        self.gui_manager.scan_files = self.scan_engine.scan_files
        
        # Reporting connections
        self.gui_manager.analyze_target_disk = self.reporting.analyze_target_disk

        
        # Organization operation - special case, uses multiple modules
        self.gui_manager.start_organization = self.start_organization
        
        # Rebind buttons
        self.rebind_buttons()
        
        # Redo event bindings
        self.rebind_events()
        
        print("✅ Module connections established!")
    
    def rebind_buttons(self):
        """Rebind buttons - after GUI is created"""
        print("🔧 Rebinding buttons...")
        
        # Find main buttons and rebind them
        for widget in self.gui_manager.root.winfo_children():
            self._rebind_widget_recursive(widget)
        
        print("✅ Buttons rebound!")
    
    def rebind_events(self):
        """Redo event bindings"""
        print("🔧 Rebinding events...")
        
        # Clear and rebind target tree events
        target_tree = self.gui_manager.target_tree
        
        # Clear old bindings
        target_tree.unbind('<Double-1>')
        target_tree.unbind('<Button-3>')
        target_tree.unbind('<Delete>')
        target_tree.unbind('<Control-c>')
        target_tree.unbind('<Control-x>')
        target_tree.unbind('<Control-v>')
        target_tree.unbind('<F2>')
        target_tree.unbind('<F5>')
        target_tree.unbind('<BackSpace>')
        target_tree.unbind('<Return>')
        
        # Add new bindings
        target_tree.bind('<Double-1>', self.file_operations.on_target_double_click)
        target_tree.bind('<Button-3>', self.file_operations.show_context_menu)
        
        # Rebind keyboard shortcuts
        target_tree.bind('<Delete>', lambda e: self.file_operations.delete_selected())
        target_tree.bind('<Control-c>', lambda e: self.file_operations.copy_selected())
        target_tree.bind('<Control-x>', lambda e: self.file_operations.cut_selected())
        target_tree.bind('<Control-v>', lambda e: self.file_operations.paste_selected())
        target_tree.bind('<F2>', lambda e: self.file_operations.rename_selected())
        target_tree.bind('<F5>', lambda e: self.file_operations.refresh_target())
        target_tree.bind('<BackSpace>', lambda e: self.file_operations.go_up())
        target_tree.bind('<Return>', lambda e: self.file_operations.open_selected())
        
        print("✅ Events rebound!")
    
    def _rebind_widget_recursive(self, widget):
        """Recursively scan widgets and rebind buttons"""
        try:
            # If this is a button
            if isinstance(widget, ttk.Button):
                button_text = widget.cget('text')
                
                # Bind correct method according to button text
                if button_text == "Select":
                    widget.configure(command=self.file_operations.select_source_folder)
                elif button_text == "Change":
                    widget.configure(command=self.file_operations.select_target_folder)
                elif button_text == "◀ Back":
                    widget.configure(command=self.file_operations.go_back)
                elif button_text == "▲ Up":
                    widget.configure(command=self.file_operations.go_up)
                elif button_text == "🏠 Home":
                    widget.configure(command=self.file_operations.go_home)
                elif button_text == "Go":
                    widget.configure(command=self.file_operations.navigate_to_path)
                elif button_text == "🔄 Refresh":
                    widget.configure(command=self.file_operations.refresh_target)
                elif button_text == "🗑️ Delete":
                    widget.configure(command=self.file_operations.delete_selected)
                elif button_text == "📋 Copy":
                    widget.configure(command=self.file_operations.copy_selected)
                elif button_text == "✂️ Cut":
                    widget.configure(command=self.file_operations.cut_selected)
                elif button_text == "📁 Paste":
                    widget.configure(command=self.file_operations.paste_selected)
                elif button_text == "➕ New Folder":
                    widget.configure(command=self.file_operations.create_folder)
                elif button_text == "🔓 Open":
                    widget.configure(command=self.file_operations.open_selected)
                elif button_text == "Scan Files":
                    widget.configure(command=self.scan_engine.scan_files)
                elif button_text == "🔍 Target Disk Analysis":
                    widget.configure(command=self.reporting.analyze_target_disk)
                elif button_text == "Start Organization":
                    widget.configure(command=self.start_organization)
                
            
            # Check child widgets too
            for child in widget.winfo_children():
                self._rebind_widget_recursive(child)
                
        except Exception as e:
            # Continue silently on error
            pass
    
    def test_connections(self):
        """Test and verify connections"""
        print("🔍 Testing connections...")
        
        # Test: select_source_folder connection
        if self.gui_manager.select_source_folder == self.file_operations.select_source_folder:
            print("✅ select_source_folder connection correct")
        else:
            print("❌ select_source_folder connection wrong!")
            # Force fix
            self.gui_manager.select_source_folder = self.file_operations.select_source_folder
            print("🔧 select_source_folder connection fixed")
        
        # Test: select_target_folder connection
        if self.gui_manager.select_target_folder == self.file_operations.select_target_folder:
            print("✅ select_target_folder connection correct")
        else:
            print("❌ select_target_folder connection wrong!")
            # Force fix
            self.gui_manager.select_target_folder = self.file_operations.select_target_folder
            print("🔧 select_target_folder connection fixed")
        
        # Test: scan_files connection
        if self.gui_manager.scan_files == self.scan_engine.scan_files:
            print("✅ scan_files connection correct")
        else:
            print("❌ scan_files connection wrong!")
            # Force fix
            self.gui_manager.scan_files = self.scan_engine.scan_files
            print("🔧 scan_files connection fixed")
        
        print("✅ Connection test completed!")
    
    def setup_initial_state(self):
        """Setup initial state"""
        # Update window title
        self.root.title("File Organizer - Modular Version v2.0")
        
        # Initial message
        self.gui_manager.status_var.set("Modular file organizer ready! Start by selecting source folder.")
        
        # Keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        print("✅ Initial setup completed!")
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Global shortcuts
        self.root.bind('<Control-o>', lambda e: self.file_operations.select_source_folder())
        self.root.bind('<Control-t>', lambda e: self.file_operations.select_target_folder())
        self.root.bind('<F5>', lambda e: self.file_operations.refresh_target())
        self.root.bind('<Control-s>', lambda e: self.scan_engine.scan_files())
        self.root.bind('<Control-r>', lambda e: self.reporting.analyze_target_disk())
        
        # File manager shortcuts
        self.root.bind('<Control-c>', lambda e: self.file_operations.copy_selected())
        self.root.bind('<Control-x>', lambda e: self.file_operations.cut_selected())
        self.root.bind('<Control-v>', lambda e: self.file_operations.paste_selected())
        # Delete key will only be connected to target_tree, not global
        self.root.bind('<F2>', lambda e: self.file_operations.rename_selected())
        
        # Exit
        self.root.bind('<Control-q>', lambda e: self.quit_application())
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
    
    def start_organization(self):
        """Start organization process - coordinates multiple modules"""
        # Pre-checks
        if not self.gui_manager.source_var.get():
            messagebox.showwarning("Warning", "Please select source folder first!")
            return
        
        if not self.gui_manager.target_var.get():
            messagebox.showwarning("Warning", "Please select target folder first!")
            return
        
        if not self.scan_engine.all_scanned_files:
            messagebox.showwarning("Warning", "Please scan files first!")
            return
        
        # Get confirmation
        unique_count = len(self.scan_engine.unique_files)
        duplicate_count = len(self.scan_engine.duplicate_files)
        
        message = f"""Organization will start:

📊 Statistics:
• {unique_count} unique files to be copied
• {duplicate_count} duplicate files found
• Target: {self.gui_manager.target_var.get()}

Are you sure you want to continue?"""
        
        if not messagebox.askyesno("Organization Confirmation", message):
            return
        
        # Start organization thread
        import threading
        org_thread = threading.Thread(target=self._organization_thread, daemon=True)
        org_thread.start()
    
    def _organization_thread(self):
        """Organization thread"""
        try:
            # Start progress
            self.gui_manager.progress_var.set(0)
            self.gui_manager.status_var.set("Starting organization...")
            
            # Start time estimation
            self.gui_manager.start_time_estimation()
            
            # Perform organization
            self._perform_organization()
            
        except Exception as e:
            self.root.after(0, lambda: self.gui_manager.status_var.set(f"❌ Organization error: {e}"))
            print(f"Organization error: {e}")
        finally:
            # Reset progress
            self.root.after(0, lambda: self.gui_manager.progress_var.set(0))
            # Stop time estimation
            self.root.after(0, lambda: self.gui_manager.stop_time_estimation())
    
    def _perform_organization(self):
        """Organization işlemini gerçekleştir - Home programdan optimize edildi"""
        import shutil
        import time
        
        target_base = self.gui_manager.target_var.get()
        total_files = len(self.scan_engine.unique_files)
        copied_files = 0
        skipped_files = 0
        error_files = 0
        
        # Duplicate action option
        duplicate_action = self.gui_manager.duplicate_action.get()
        
        # First process files in existing folders
        if hasattr(self.scan_engine, 'existing_folder_files'):
            for folder_path, files in self.scan_engine.existing_folder_files.items():
                print(f"📁 Copying existing folder files: {folder_path}")
                
                # If folder_path is not absolute, combine with target folder
                if not os.path.isabs(folder_path):
                    full_folder_path = os.path.join(target_base, folder_path)
                else:
                    full_folder_path = folder_path
                
                print(f"📂 Full folder path: {full_folder_path}")
                
                for file_info in files:
                    try:
                        # Target file path
                        target_file = os.path.join(full_folder_path, file_info['name'])
                        
                        # Advanced duplicate check
                        if os.path.exists(target_file):
                            if duplicate_action == "skip":
                                skipped_files += 1
                                continue
                            elif duplicate_action == "ask":
                                # Ask in UI thread
                                result = self._ask_duplicate_action(file_info['name'])
                                if result == "skip":
                                    skipped_files += 1
                                    continue
                                elif result == "skip_all":
                                    duplicate_action = "skip"
                                    skipped_files += 1
                                    continue
                                elif result == "copy_all":
                                    duplicate_action = "copy"
                            
                            # Add number if same name file exists
                            if duplicate_action == "copy":
                                counter = 1
                                base_name, ext = os.path.splitext(file_info['name'])
                                while os.path.exists(target_file):
                                    new_name = f"{base_name}_{counter}{ext}"
                                    target_file = os.path.join(full_folder_path, new_name)
                                    counter += 1
                        
                        # Copy file
                        success, message = self.file_operations.copy_file_optimized(file_info['path'], target_file)
                        
                        if success:
                            copied_files += 1
                            print(f"✅ Existing folder file copied: {file_info['name']} -> {full_folder_path}")
                        else:
                            error_files += 1
                            print(f"❌ Existing folder copy error: {file_info['name']} - {message}")
                    
                    except Exception as e:
                        error_files += 1
                        print(f"❌ Existing folder file error: {file_info['name']} - {e}")
        
        # Then process files in new folder structure
        for i, file_info in enumerate(self.scan_engine.unique_files):
            try:
                # Update progress
                progress = (i + 1) / total_files * 100
                self.root.after(0, lambda p=progress: self.gui_manager.progress_var.set(p))
                
                # Update time estimation
                self.root.after(0, lambda p=progress, processed=i+1, total=total_files: 
                               self.gui_manager.update_time_estimation(p, processed, total))
                
                # Skip if this file was already processed in existing folders
                if hasattr(self.scan_engine, 'existing_folder_files'):
                    skip_file = False
                    for folder_files in self.scan_engine.existing_folder_files.values():
                        if file_info in folder_files:
                            skip_file = True
                            break
                    if skip_file:
                        continue
                
                # Check if it's a folder
                if file_info.get('is_folder', False):
                    # Folder copying
                    source_folder = file_info['path']
                    target_folder = os.path.join(target_base, "Folders", "Subfolders", file_info['name'])
                    
                    # Duplicate check if target folder exists
                    if os.path.exists(target_folder):
                        if duplicate_action == "skip":
                            skipped_files += 1
                            continue
                        elif duplicate_action == "ask":
                            result = self._ask_duplicate_action(file_info['name'])
                            if result == "skip":
                                skipped_files += 1
                                continue
                            elif result == "skip_all":
                                duplicate_action = "skip"
                                skipped_files += 1
                                continue
                            elif result == "copy_all":
                                duplicate_action = "copy"
                        
                        # Add number if same name folder exists
                        counter = 1
                        base_name = file_info['name']
                        while os.path.exists(target_folder):
                            new_name = f"{base_name}_{counter}"
                            target_folder = os.path.join(target_base, "Folders", "Subfolders", new_name)
                            counter += 1
                    
                    # Copy entire folder
                    try:
                        shutil.copytree(source_folder, target_folder, dirs_exist_ok=False)
                        copied_files += 1
                        print(f"✅ Folder copied: {file_info['name']}")
                    except Exception as e:
                        error_files += 1
                        print(f"❌ Folder copy error: {file_info['name']} - {e}")
                
                else:
                    # Normal file copying
                    # Determine category and target path
                    category, category_info = self.file_operations.get_file_category(file_info['path'])
                    
                    # Target folder structure
                    main_folder = os.path.join(target_base, category_info['folder'])
                    
                    extension = file_info['extension']
                    if extension in category_info['subfolders']:
                        subfolder = category_info['subfolders'][extension]
                    else:
                        subfolder = extension.replace('.', '').upper() if extension else 'No Extension'
                    
                    target_folder = os.path.join(main_folder, subfolder)
                    
                    # Create folders
                    os.makedirs(target_folder, exist_ok=True)
                    
                    # Target File Path
                    target_file = os.path.join(target_folder, file_info['name'])
                    
                    # Duplicate check
                    if os.path.exists(target_file):
                        if duplicate_action == "skip":
                            skipped_files += 1
                            continue
                        elif duplicate_action == "ask":
                            # UI thread'inde sor
                            result = self._ask_duplicate_action(file_info['name'])
                            if result == "skip":
                                skipped_files += 1
                                continue
                            elif result == "skip_all":
                                duplicate_action = "skip"
                                skipped_files += 1
                                continue
                            elif result == "copy_all":
                                duplicate_action = "copy"
                        
                        # Add number if same name file exists
                        counter = 1
                        base_name, ext = os.path.splitext(file_info['name'])
                        while os.path.exists(target_file):
                            new_name = f"{base_name}_{counter}{ext}"
                            target_file = os.path.join(target_folder, new_name)
                            counter += 1
                    
                    # Optimized copying
                    success, message = self.file_operations.copy_file_optimized(file_info['path'], target_file)
                    
                    if success:
                        copied_files += 1
                    else:
                        error_files += 1
                        print(f"Copy error: {file_info['name']} - {message}")
                
                # Update status
                self.root.after(0, lambda cf=copied_files, sf=skipped_files, ef=error_files: 
                               self.gui_manager.status_var.set(f"Copied: {cf}, Skipped: {sf}, Errors: {ef}"))
                
                # Prevent UI freezing
                if i % 10 == 0:
                    time.sleep(0.001)
                
            except Exception as e:
                error_files += 1
                print(f"File processing error: {file_info['path']} - {e}")
                continue
        
        # Final update
        self.root.after(0, lambda: self.gui_manager.status_var.set(
            f"✅ Organization completed! Copied: {copied_files}, Skipped: {skipped_files}, Errors: {error_files}"))
    
    def _ask_duplicate_action(self, filename, duplicate_count=1):
        """Ask user for confirmation on duplicate file - taken from main program"""
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Duplicate File Found")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        result = {"action": "skip"}  # Default
        
        # Content
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Warning icon and message
        msg_frame = ttk.Frame(main_frame)
        msg_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(msg_frame, text="⚠️", font=("Arial", 24)).pack(side=tk.LEFT, padx=(0, 10))
        
        msg_text = f"Duplicate file found:\n\n📄 {filename}"
        if duplicate_count > 1:
            msg_text += f"\n\n🔄 Total {duplicate_count} duplicate files found."
        
        ttk.Label(msg_frame, text=msg_text, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Options
        option_frame = ttk.Frame(main_frame)
        option_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(option_frame, text="What would you like to do?", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def on_skip():
            result["action"] = "skip"
            dialog.destroy()
            
        def on_copy():
            result["action"] = "copy"
            dialog.destroy()
            
        def on_skip_all():
            result["action"] = "skip_all"
            self.gui_manager.duplicate_action.set("skip")
            dialog.destroy()
            
        def on_copy_all():
            result["action"] = "copy_all"
            self.gui_manager.duplicate_action.set("copy")
            dialog.destroy()
        
        ttk.Button(button_frame, text="🚫 Skip this file", command=on_skip).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📋 Copy this file", command=on_copy).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🚫 Skip all", command=on_skip_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📋 Copy all", command=on_copy_all).pack(side=tk.LEFT)
        
        # Wait for dialog
        dialog.wait_window()
        
        return result["action"]
    
    def quit_application(self):
        """Close application"""
        # Save settings
        self.file_operations.save_settings()
        
        # Stop running threads
        if hasattr(self.scan_engine, 'stop_scan'):
            self.scan_engine.stop_scan()
        
        # Close window
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run application"""
        try:
            print("🚀 Modular File Organizer starting...")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n⏹️ Application stopped by user")
        except Exception as e:
            print(f"❌ Application error: {e}")
        finally:
            print("👋 Application closed")

def main():
    """Main function"""
    try:
        # Create and run application instance
        app = ModularFileManager()
        app.run()
        
    except Exception as e:
        print(f"Critical Error: {e}")
        messagebox.showerror("Critical Error", f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 