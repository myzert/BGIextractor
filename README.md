<div align="center">

# 🔥 BGIE (BGI Extractor) Pro

[![Build Status](https://github.com/myzert/BGIextractor/actions/workflows/build.yml/badge.svg)](https://github.com/myzert/BGIextractor/actions)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#)
[![Theme](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)](#)

*The Ultimate Open-Source Toolset for SMEE / Ethornell Visual Novel Modding*

</div>

<hr>

## 📖 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Built With](#-built-with)
- [Installation / Downloads](#-installation)
- [Usage Guide](#-usage-guide)
- [Important Notes & Warnings](#-important-notes)
- [Contributing](#-contributing)
- [License](#-license)

## 📌 About the Project

**BGIE** (formerly BGI Translation Toolkit) is a professional, open-source software suite designed to empower the visual novel localization community. It allows translators and modders to unpack, decrypt, translate, and repack assets from visual novels running on the **BGI / Ethornell Engine** (commonly used by developers like SMEE, ASa Project, and August).

Traditional tools often crash the game when text is translated due to broken byte pointers. BGIE solves this by implementing a **smart Auto-Padding JSON Injector** that ensures the compiled bytecode `.bss` remains perfectly stable.

## ✨ Key Features

- **Built-in Archive Viewer:** Read `BURIKO ARC20` internal headers and list all files inside `.arc` archives instantly, without having to extract them first.
- **Modern GUI Client:** A sleek, dark-themed user interface powered by `CustomTkinter`. No terminal commands required!
- **DSC Decryption Engine:** Includes a lightning-fast C-based engine capable of ripping through obfuscated scripts and decompressed `.CBG` visual assets.
- **Smart BSS ↔ JSON Converter:** Automatically isolates dialog strings from compiled `.bss` bytecode and exports them into human-readable `.json` arrays.
- **Crash-Proof Injector:** Safely re-insert translated text. BGIE adjusts string sizes and applies space-padding so memory offsets match the original Japanese text length exactly.
- **ARC Builder:** Compile your modified `.bss` scripts and edited images back into a fresh `.arc` archive in a single click.

## 🛠 Built With

This project relies on the following open-source technologies:
- **[Python](https://www.python.org/)** - Core logic and scripting backend.
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Modern, customizable UI library.
- **[C / GCC](https://gcc.gnu.org/)** - For the high-speed DSC decryption logic and extraction.
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD pipeline for automated `.exe` and `.deb` packaging.

## 📥 Installation

You do not need to install Python if you are using the pre-compiled binaries!

### Windows
1. Go to the [Releases Tab](https://github.com/myzert/BGIextractor/releases) and download **`BGIExtractor-Win64.exe`**.
2. Run the standalone `.exe` directly (No installation required).

### Linux (Debian / Ubuntu)
1. Go to the [Releases Tab](https://github.com/myzert/BGIextractor/releases) and download **`bgiextractor_1.0.0_amd64.deb`**.
2. Install the package via terminal:
   ```bash
   sudo dpkg -i bgiextractor_1.0.0_amd64.deb
   ```
3. Run `bgiextractor` from your terminal or application launcher.

*(If you prefer to run from source, simply clone the repo and double-click `Launcher.bat` or `Launcher.sh`).*

## 🎮 Usage Guide

1. **ARC Viewer & Extractor:** Browse for an `.arc` file to inspect its contents. Pick an output folder and click *Extract All* to unpack and decrypt the DSC files.
2. **Text to JSON:** Select the folder containing your newly decrypted `.bss` scripts. BGIE will extract all dialogue strings into `.json` files for your translation team.
3. **JSON Injector:** Once translation is done, point the tool at the original `.bss` files and your translated `.json` folder. BGIE will automatically generate patched, game-ready `.bss` files.
4. **ARC Builder:** Compile your patched files into an `.arc` file (e.g., `data01099.arc.new`). Drop this into your game folder to see your translations in-game!

## ⚠️ Important Notes

> [!WARNING]
> **Bytecode Length Constraints**
> The BGI Engine is extremely sensitive to bytecode shifts. Our injector currently pads translated text with spaces (`\x20`) if the English translation is shorter than the Japanese text. If your translation is *longer* than the Japanese text, the tool will **truncate** it to prevent engine crashes. We recommend using concise translations or abbreviations for long sentences.

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the **GNU General Public License v3.0 (GPLv3)**. See `LICENSE` for more information. You are free to modify, distribute, and contribute to this project to help localize visual novels worldwide!

---
<div align="center">
  <p>Made with ❤️ for the VN Translation Community by <b>myzert</b>.</p>
</div>
