# File Organizer - Modular Version

A comprehensive file organization tool with modular architecture, designed to efficiently organize and manage large file collections.

## Features

### 🗂️ File Organization
- **Automatic categorization** by file type (Images, Documents, Videos, Audio, etc.)
- **Smart folder structure** creation
- **Duplicate detection** with multiple methods (name, size, hash)
- **Batch processing** for large file collections
- **Progress tracking** with time estimation

### 🔍 Advanced Scanning
- **Recursive folder scanning** with subfolder support
- **File filtering** by size, extension, and attributes
- **Hidden file detection** option
- **Real-time progress** updates
- **Detailed file analysis**

### 📊 Analysis and Reporting
- **Target disk analysis** to understand existing structure
- **Duplicate file reports** with detailed information
- **File type statistics** and distribution
- **Storage optimization** suggestions
- **Export capabilities** for reports

### 🖥️ User Interface
- **Modern GUI** with tabbed interface
- **Drag and drop** support
- **Context menus** for quick actions
- **Keyboard shortcuts** for power users
- **Real-time status** updates

### 🛠️ File Management
- **Built-in file browser** with navigation
- **Copy, cut, paste** operations
- **File and folder** creation/deletion
- **Rename** functionality
- **Properties** viewing
- **File opening** with default applications

## Installation

1. **Clone or download** this repository
2. **Install Python 3.7+** if not already installed
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python main_modular.py
   ```

## Usage

### Basic Workflow

1. **Select Source Folder**: Choose the folder containing files to organize
2. **Select Target Folder**: Choose where organized files will be placed
3. **Configure Scan Options**: Set filters and preferences
4. **Scan Files**: Analyze source folder contents
5. **Review Preview**: Check organization structure
6. **Start Organization**: Begin the file organization process

### Advanced Features

#### Duplicate Handling
- **Name-based**: Compare file names
- **Size-based**: Compare file sizes
- **Hash-based**: Compare file content (most accurate)

#### Organization Options
- **Ask each time**: Manual decision for each duplicate
- **Auto skip**: Skip duplicate files automatically
- **Copy with number**: Add numbers to duplicate filenames

#### File Filtering
- **Size filters**: Set minimum/maximum file sizes
- **Extension filters**: Include/exclude specific file types
- **Hidden files**: Choose whether to include hidden files

## Modular Architecture

The application is built with a modular design:

### Core Modules

- **`main_modular.py`**: Main application coordinator
- **`gui_manager.py`**: User interface management
- **`file_operations.py`**: File system operations
- **`scan_engine.py`**: File scanning and analysis
- **`reporting.py`**: Reports and statistics

### Benefits

- **Maintainable**: Each module has specific responsibilities
- **Extensible**: Easy to add new features
- **Testable**: Individual modules can be tested separately
- **Reusable**: Modules can be used in other projects

## File Categories

The application automatically categorizes files into:

- **📷 Images**: jpg, png, gif, bmp, tiff, svg, etc.
- **📄 Documents**: pdf, doc, docx, txt, rtf, etc.
- **🎵 Audio**: mp3, wav, flac, aac, ogg, etc.
- **🎬 Videos**: mp4, avi, mkv, mov, wmv, etc.
- **📦 Archives**: zip, rar, 7z, tar, gz, etc.
- **💻 Programs**: exe, msi, deb, dmg, etc.
- **📊 Spreadsheets**: xls, xlsx, csv, ods, etc.
- **🎨 Design**: psd, ai, sketch, fig, etc.
- **⚙️ Other**: Files that don't fit other categories

## Keyboard Shortcuts

### Global Shortcuts
- **Ctrl+O**: Select source folder
- **Ctrl+T**: Select target folder
- **Ctrl+S**: Scan files
- **Ctrl+R**: Analyze target disk
- **F5**: Refresh current view
- **Ctrl+Q**: Quit application

### File Operations
- **Ctrl+C**: Copy selected files
- **Ctrl+X**: Cut selected files
- **Ctrl+V**: Paste files
- **Delete**: Delete selected files
- **F2**: Rename selected file
- **Enter**: Open selected file/folder
- **Backspace**: Go to parent folder

## Configuration

Settings are automatically saved in:
- **`file_manager_settings.json`**: User preferences
- **`file_manager_config.json`**: Application configuration

## Troubleshooting

### Common Issues

1. **Permission Errors**: Run as administrator if needed
2. **Large Files**: Increase timeout settings for very large files
3. **Memory Usage**: Close other applications for large operations
4. **Antivirus**: Add application to antivirus exceptions

### Performance Tips

- **Use SSD**: Faster storage improves performance
- **Close other apps**: Free up system resources
- **Batch size**: Adjust for your system capabilities
- **Hash checking**: Disable for faster scanning (less accurate)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute.

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review existing issues
- Create a new issue with detailed information

## Version History

### v2.0 - Modular Version
- Complete modular architecture
- Improved performance
- Enhanced user interface
- Better error handling
- Advanced duplicate detection

### v1.0 - Initial Release
- Basic file organization
- Simple GUI
- Basic duplicate detection
- File categorization

---

**Note**: This is the English version of the File Organizer. The original Turkish version is available in the parent directory. 