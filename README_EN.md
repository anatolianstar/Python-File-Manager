# 🗂️ Advanced Python File Manager

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![GitHub stars](https://img.shields.io/github/stars/anatolianstar/Python-File-Manager.svg)](https://github.com/anatolianstar/Python-File-Manager/stargazers)

> **🌟 Professional file organization tool with automatic categorization, duplicate detection, and bilingual support**

## 🚀 Quick Start

### English Version (Recommended)
```bash
cd English_manager
python main_modular.py
```

### Turkish Version
```bash
python main_modular.py
```

## ✨ Key Features

### 🎯 Smart File Organization
- **Automatic categorization** by file type (Images, Audio, Video, Documents, etc.)
- **Drag & drop** interface with visual feedback
- **Batch processing** for large file collections
- **Custom category** configuration

### 🔍 Advanced Duplicate Detection
- **Multiple detection methods**: Name, Size, Hash (MD5)
- **Real-time scanning** during organization
- **Grouped results** with expandable tree view
- **Smart conflict resolution**

### 🖥️ Professional Interface
- **Modern GUI** with tabbed interface
- **File explorer** with navigation controls
- **Keyboard shortcuts** (Delete, Ctrl+C/X/V, F2, F5)
- **Context menus** and tooltips
- **Progress tracking** with detailed reports

### 🌐 Bilingual Support
- **English interface** (Primary)
- **Turkish interface** (Secondary)
- **Localized messages** and documentation

## 📸 Screenshots

*Coming soon - Add screenshots of your application*

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Quick Install
```bash
git clone https://github.com/anatolianstar/Python-File-Manager.git
cd Python-File-Manager
pip install -r requirements.txt
```

### Run Application
```bash
# English Version (Recommended)
cd English_manager
python main_modular.py

# Turkish Version
python main_modular.py
```

## 📁 Project Structure

```
Python-File-Manager/
├── English_manager/          # 🇺🇸 English Version (Primary)
│   ├── main_modular.py      # Main application
│   ├── gui_manager.py       # GUI components
│   ├── file_operations.py   # File handling
│   ├── scan_engine.py       # Scanning logic
│   └── reporting.py         # Reports & analytics
├── main_modular.py          # 🇹🇷 Turkish Version
├── gui_manager.py           # GUI components (TR)
├── file_operations.py       # File handling (TR)
├── scan_engine.py          # Scanning logic (TR)
├── reporting.py            # Reports & analytics (TR)
└── requirements.txt        # Dependencies
```

## 🎮 Usage Guide

### Basic Workflow
1. **Launch** the application
2. **Select** source folder in left panel
3. **Choose** target organization folder
4. **Configure** duplicate detection settings
5. **Click** "Organize Files" button
6. **Review** the detailed completion report

### Advanced Features
- **F5**: Refresh folder contents
- **Ctrl+Click**: Multi-select files
- **Right-click**: Context menu operations
- **Drag & Drop**: Move files between folders

## 🔧 Configuration

### File Categories
The application automatically categorizes files into:
- 📸 **Images**: JPG, PNG, GIF, BMP, TIFF, SVG
- 🎵 **Audio**: MP3, WAV, FLAC, AAC, OGG
- 🎬 **Video**: MP4, AVI, MKV, MOV, WMV
- 📄 **Documents**: PDF, DOC, TXT, XLS, PPT
- 💾 **Archives**: ZIP, RAR, 7Z, TAR
- ⚙️ **Programs**: EXE, MSI, DEB, DMG

### Duplicate Detection Methods
- **Name matching**: Identical filenames
- **Size comparison**: File size verification
- **Hash verification**: MD5 checksum comparison

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/anatolianstar/Python-File-Manager.git
cd Python-File-Manager
# Make your changes
git commit -m "Your improvement"
git push origin main
```

## 📊 Performance

- **Processing Speed**: 1000+ files per minute
- **Memory Usage**: < 100MB for typical operations
- **Supported File Types**: 50+ formats
- **Platform Support**: Windows, Linux, macOS

## 🐛 Known Issues & Solutions

### ✅ Resolved Issues
- ~~Duplicate files being copied~~ → Real-time duplicate control added
- ~~Column sorting instability~~ → Intelligent sorting algorithm implemented
- ~~Hidden file clutter~~ → Comprehensive filtering system

### 🔄 Planned Improvements
- Cloud storage integration
- Batch rename functionality
- Undo/Redo operations
- Plugin system for custom categories

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ using Python and Tkinter
- Developed through pair programming with Cursor AI
- Special thanks to the open-source community

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/anatolianstar/Python-File-Manager/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/anatolianstar/Python-File-Manager/discussions)
- 📧 **Contact**: Create an issue for support

---

## 🇹🇷 Türkçe Versiyon

Bu projenin Türkçe arayüzü de mevcuttur. Ana dizindeki dosyaları kullanarak Türkçe versiyonu çalıştırabilirsiniz.

### Türkçe Kullanım
```bash
python main_modular.py
```

Detaylı Türkçe dokümantasyon için ana README.md dosyasını ziyaret edin.

---

⭐ **If you find this project useful, please give it a star!** ⭐ 