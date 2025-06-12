# 🗂️ Smart Duplicate Control File Distribution Program

🇬🇧 English | [🇹🇷 Türkçe](README.md)

**Advanced file organization and distribution tool** - Automatically organizes your files with intelligent categorization and duplicate control.

## 🌟 Program Features

### 🧠 Smart Categorization System
- **Automatic file classification**: 15+ different categories (images, videos, audio, documents, program files, etc.)
- **Learning system**: Remembers and learns user preferences
- **Target-oriented categorization**: Categories that adapt to specific folder structures
- **Flexible category management**: Ability to add new categories and edit existing ones

### 🔍 Duplicate Control and Security
- **MD5 hash-based duplicate control**: Detects files with identical content
- **Safe copying**: Preserves file integrity
- **Conflict prevention**: Automatically renames different files with the same name
- **Error tolerance**: Failed operations don't halt the system

### ⚡ Performance and User Experience
- **Parallel operations**: Fast copying with multi-threading support
- **Real-time progress tracking**: Accurate progress display including all subfolders
- **Detailed operation reports**: Details of successful, skipped, and failed operations
- **User-friendly interface**: Turkish menus and messages
- **Wide file format support**: Support for 100+ file extensions

### 📁 Folder Operations
- **Deep folder structure support**: Complete organization including subfolders
- **Folder merging**: Automatic merging of folders in the same category
- **Structure preservation**: Important folder structures are preserved
- **Selective organization**: Option to organize specific file types

## 🛠️ Installation

### Requirements
- Python 3.7 or higher
- tkinter (usually comes with Python)
- threading, shutil, hashlib (standard libraries)

### Installation Steps
1. **Download the project:**
   ```bash
   git clone https://github.com/user/smart-file-distribution.git
   cd smart-file-distribution
   ```

2. **Run the program:**
   ```bash
   python main_modular.py
   ```

## 🚀 User Guide

### Main Features

#### 1. 📋 File Scanning and Selection
- **Folder selection**: Choose the source folder to organize
- **File filtering**: Organize by selecting specific file types
- **Preview**: See in advance which files will go where

#### 2. 🎯 Target Folder Settings
- **Select target location**: Specify the folder where files will be organized
- **Category structure**: Preview automatically created category folders
- **Customized organization**: Category settings according to your needs

#### 3. ⚙️ Organize Operation
- **One-click organization**: Press the "Organize" button
- **Progress tracking**: Real-time progress bar and detailed information
- **Error management**: Failed operations are automatically reported

#### 4. 📊 Result Reports
- **Detailed statistics**: Numbers of copied, skipped, and failed files
- **Category distribution**: How many files were placed in each category
- **Error analysis**: Reasons for failed operations

### Advanced Features

#### 🎓 Learning System
The program learns user preferences and uses this information in future organizations:
- Remembers manual category assignments
- Recognizes frequently used folder structures
- File type preferences are saved

#### 🔄 Duplicate Management
- **Smart duplicate detection**: Files with identical content are detected
- **Flexible duplicate handling**: Skip, rename, or overwrite options
- **Safe operations**: Original files are preserved

#### 📁 Category Management
```
📁 Organized Files/
├── 🖼️ Image Files/
│   ├── .jpg, .png, .gif, .bmp, .svg
├── 🎥 Video Files/
│   ├── .mp4, .avi, .mkv, .mov, .wmv
├── 🎵 Audio Files/
│   ├── .mp3, .wav, .flac, .aac, .ogg
├── 📄 Document Files/
│   ├── .pdf, .doc, .docx, .txt, .xls
├── 💾 Program Files/
│   ├── .exe, .msi, .deb, .rpm, .dmg
├── 🗜️ Compressed Files/
│   ├── .zip, .rar, .7z, .tar, .gz
├── 🛠️ CAD & 3D Files/
│   ├── .dwg, .step, .stl, .obj, .blend
├── 💻 Code Files/
│   ├── .py, .js, .html, .css, .java
├── 🔤 Font Files/
│   ├── .ttf, .otf, .woff, .woff2
└── 📦 Software Packages/
    ├── Installation files and folders
```

## 🔧 Technical Details

### System Architecture
- **Modular design**: Each feature developed as a separate module
- **Thread safety**: Safe thread management for parallel operations
- **Memory optimization**: Efficient memory usage for large file operations
- **Error recovery**: Comprehensive error management preventing system crashes

### Performance Features
- **Parallel copying**: Multiple files processed simultaneously
- **Smart caching**: Frequently used information is cached
- **Progressive loading**: Large folder structures are processed incrementally
- **Resource management**: CPU and memory usage is optimized

## 🤝 Contributing

If you want to contribute to the project:

1. **Fork** and create your own branch
2. **Develop features** or fix bugs
3. **Test** - thoroughly test your changes
4. **Send pull request** - with detailed description

### Development Guide
- Follow coding standards (PEP 8)
- Write complete docstrings
- Add unit tests
- Use Turkish comments

## 📝 License

This project is distributed under the MIT license. See the `LICENSE` file for details.

## 🐛 Bug Reporting

If you find bugs or have suggestions:
- Use **GitHub Issues**
- Add **detailed description**
- Specify **reproducible error steps**
- Share **your system information**

## 📚 Frequently Asked Questions

**Q: What operating systems does the program work on?**
A: It works on Windows, macOS, and Linux. Python 3.7+ is required.

**Q: Can large files be processed?**
A: Yes, the program efficiently handles large files. Memory usage is optimized.

**Q: Can category settings be customized?**
A: Yes, both existing categories can be edited and new categories can be added.

**Q: How are duplicate files detected?**
A: File contents are compared using the MD5 hash algorithm.

**Q: Are original files safe?**
A: Yes, the program only copies, it doesn't delete original files.

---

**⭐ Don't forget to star the project if you liked it!**

📧 **Contact**: [GitHub Issues](https://github.com/user/smart-file-distribution/issues)
🐛 **Bug Report**: [Report Bug](https://github.com/user/smart-file-distribution/issues/new)
💡 **Feature Request**: [Request Feature](https://github.com/user/smart-file-distribution/issues/new) 