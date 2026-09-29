<div align="center">

# BGI Extractor

[![Build Status](https://github.com/myzert/BGIextractor/actions/workflows/build.yml/badge.svg)](https://github.com/myzert/BGIextractor/actions)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#)
[![Theme](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)](#)

*A comprehensive open-source toolset for BGI / Ethornell Engine modding and localization.*

</div>

<hr>

## Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Built With](#built-with)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Technical Constraints](#technical-constraints)
- [Contributing](#contributing)
- [License](#license)

## About the Project

**BGI Extractor** is an open-source software suite designed to assist software localization teams. It provides a robust framework to unpack, decrypt, translate, and rebuild assets from applications running on the **BGI / Ethornell Engine** (utilized by developers such as SMEE, ASa Project, and August).

By implementing a calculated byte-padding injection system, BGI Extractor ensures that memory offsets within compiled `.bss` files remain stable, effectively mitigating engine crashes caused by shifted pointers during text modification.

## Features

- **Archive Viewer:** Read `BURIKO ARC20` headers and inspect internal file structures without performing full extraction.
- **Graphical Interface:** A modular, multi-platform graphical client utilizing `CustomTkinter`.
- **DSC Decryption:** Integrates the highly efficient C-based `ethornell` engine for decompression and obfuscation removal.
- **BSS to JSON Converter:** Parses `.bss` bytecode to isolate dialogue strings, exporting them into structured `.json` format for localization teams.
- **Padding Injector:** Reconstructs patched `.bss` files by inserting translated strings. Implements strict length matching (space-padding) to preserve architectural integrity.
- **ARC Compiler:** Packages modified assets and scripts into functional `.arc` archives recognized by the original engine.

## Built With

- **[Python](https://www.python.org/)** - Core application logic.
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - User interface framework.
- **[C / GCC](https://gcc.gnu.org/)** - Core DSC decryption layer.
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD deployment pipeline.

## Installation

Standalone executables are automatically generated via GitHub Actions. Python installation is not required when using the provided binaries.

### Windows
1. Navigate to the [Releases](https://github.com/myzert/BGIextractor/releases) page.
2. Download **`BGIExtractor-Win64.exe`**.
3. Execute the binary directly (Portable software).

### Linux (Debian / Ubuntu)
1. Navigate to the [Releases](https://github.com/myzert/BGIextractor/releases) page.
2. Download the `.deb` package (e.g., `bgiextractor_1.0.0_amd64.deb`).
3. Install using dpkg:
   ```bash
   sudo dpkg -i bgiextractor_1.0.0_amd64.deb
   ```

*(To run the application from source, execute `Launcher.bat` on Windows or `Launcher.sh` on Linux environments).*

## Usage Guide

1. **ARC Viewer & Extractor:** Select an `.arc` archive to parse its contents. Provide an output directory and initiate extraction to decrypt associated DSC files.
2. **Text to JSON:** Specify the directory containing decrypted `.bss` scripts. The application will isolate translatable arrays and output them as `.json`.
3. **JSON Injector:** Provide the original `.bss` files alongside the modified `.json` documents. The system will compile and pad the patched `.bss` outputs.
4. **ARC Builder:** Designate the patched directory to compile the files into a standard `.arc` archive format.

## Technical Constraints

> [!WARNING]
> **Bytecode Offset Limitations**
> The engine is strictly constrained by original bytecode allocation. If a translated string is shorter than the source text, the application automatically pads it with spaces (`\x20`). Conversely, if a translation exceeds the original length, it will be **truncated**. Localization teams are advised to adhere to length limitations to maintain stability.

## Contributing

We welcome contributions from the community. To submit a patch or feature:

1. Fork the Repository.
2. Create a Feature Branch (`git checkout -b feature/ImplementationName`).
3. Commit your changes (`git commit -m 'feat: Add ImplementationName'`).
4. Push to the Branch (`git push origin feature/ImplementationName`).
5. Open a Pull Request.

## License

This software is distributed under the **GNU General Public License v3.0 (GPLv3)**. Please review the `LICENSE` file for full terms and conditions.

---
*Maintained by myzert.*
