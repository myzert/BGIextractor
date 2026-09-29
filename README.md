<div align="center">
  <h1>BGIE (BGI Extractor) Pro</h1>
  <p><b>The Ultimate Open-Source Toolset for SMEE / Ethornell Visual Novel Modding</b></p>
</div>

## 📌 Overview

**BGIE** (formerly BGI Translation Toolkit) is a comprehensive, cross-platform software suite designed to unpack, translate, and repack visual novels running on the **BGI / Ethornell Engine**. 

Whether you are a solo translator or a localization team, this tool is built to handle the complex structure of BGI's `.arc` archives, circumventing the notorious `DSC FORMAT 1.00.` encryption, extracting `.CBG` visual assets, and providing a **safe, crash-proof text injection mechanism** for bytecode editing.

## 🌟 Key Features

- **Built-in Archive Viewer:** Read the internal headers and list all files inside `.arc` archives before extracting them, just like standard archiving tools.
- **Modern GUI Client:** Powered by `CustomTkinter`, BGIE features a sleek, dark-themed user interface running seamlessly on Windows, Linux, and macOS without the need for a terminal.
- **DSC Decryption Engine:** Includes the blazing-fast C-based `ethornell` engine source code that rips through obfuscated scripts and decompresses BGI assets.
- **Smart BSS ↔ JSON Converter:** Avoid messing with hex editors! The tool automatically isolates English/Japanese dialog strings from compiled `.bss` bytecode and exports them into clean `.json` arrays.
- **Bytecode Auto-Padding Injector:** Re-insert translated text safely. BGIE meticulously adjusts string sizes and applies byte-padding so that internal engine memory pointers remain perfectly intact (Anti-Crash Guarantee).
- **BURIKO ARC20 Compiler:** Build fresh `.arc` patches in a single click, ready to be recognized by the game engine.

## 🚀 How to Launch

**Prerequisites:** 
- Python 3.8+ installed.

### On Windows
Just double-click **`Launcher.bat`**. It will automatically install the UI dependencies and launch the beautiful graphical interface instantly.

### On Linux / macOS
Open a terminal in the folder and run:
```bash
./Launcher.sh
```

## 🛠 Features Walkthrough

1. **ARC Viewer & Extractor:** Browse for an `.arc` file to peek at its files, or pick an output folder and hit *Extract All* to unpack and decrypt the contents.
2. **Text to JSON:** Found `.bss` scripts? Run them through this tab to instantly generate `.json` files containing all the translatable dialogs.
3. **JSON Injector:** Once your JSONs are translated, point this tool at the original `.bss` files and your translated `.json` folder. BGIE will generate brand new patched `.bss` files.
4. **ARC Builder:** Compile your patched `.bss` scripts or edited images back into an `.arc` file (like `data01099.arc.new`).

## 👨‍💻 Source Code & Compilation

Unlike closed-source extraction tools (like older builds of GARbro), **BGIE is completely open-source**.

Inside the `src/` directory, you will find the complete C source code for the core DSC decryptor and BURIKO ARC extractor.

To compile it yourself on Linux:
```bash
cd src
make
```

To compile on Windows, you can use MinGW or MSVC.

## 📄 License

BGIE is distributed under the **GNU General Public License v3.0 (GPLv3)**. You are free to modify, distribute, and contribute to this project to help localize visual novels worldwide!
