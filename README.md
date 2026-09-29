# BGI Engine Translation Toolkit (Ethornell)

A comprehensive, cross-platform, open-source toolkit designed to unpack, translate, and repack visual novels running on the **BGI / Ethornell Engine** (commonly used by SMEE, ASa Project, August, etc.).

This project was built to empower the Linux and Windows visual novel translation communities.

## 🌟 Features

- **Full GUI Support:** Includes a user-friendly Graphical User Interface (`bgi_toolkit.py`) built with Tkinter.
- **ARC Extractor & DSC Decryptor:** C-based fast extractor (`src/`) capable of decrypting `DSC FORMAT 1.00.` obfuscation and extracting `CBG`/`PBG` image assets.
- **Smart BSS ↔ JSON Converter:** Automatically identifies dialogue strings within compiled bytecode (`.bss` / `.bgi`) and exports them to human-readable JSON files, ignoring engine opcodes.
- **Safe Bytecode Injector:** Injects translated strings back into the bytecode. It features a robust auto-padding/truncation mechanism to ensure the file size and byte offsets remain identical, preventing the game engine from crashing.
- **ARC20 Repacker (Builder):** Packs your modified `.bss` and assets back into a `BURIKO ARC20` format archive ready to be loaded by the game.

## 📦 Project Structure

- `bgi_toolkit.py` - The main Python GUI application.
- `bgi_extractor.py` - Standalone Python CLI for ARC extraction.
- `ethornell_linux` - Pre-compiled binary for Linux to extract ARC and decrypt DSC files.
- `src/` - The complete C source code for the ARC reader/extractor (to compile for Windows, Linux, or macOS).
- `LICENSE` - GNU GPLv3 License.

## 🚀 How to Use (GUI)

**Prerequisites:** Python 3.x installed.

1. Open your terminal or command prompt.
2. Run the application:
   ```bash
   python3 bgi_toolkit.py
   ```
3. **Tab 1 (BSS to JSON):** Select your folder containing decrypted `.bss` files. The tool will output `.json` files containing the English/Japanese text.
4. **Translate:** Open the `.json` files in any text editor or pass them to an automatic translator. Translate the text inside the `"translated"` field.
5. **Tab 2 (JSON to BSS):** Select the original `.bss` folder and your newly translated `.json` folder. The tool will safely inject your translations into new `.bss` files.
6. **Tab 3 (Build ARC):** Select the folder containing your injected `.bss` files and specify the output filename (e.g., `data01099.arc.new`). Drop this new ARC file into your game's `Archive` folder (ensure it has the highest priority number).

## 🛠 Compiling the Extractor

If you wish to compile the `ethornell` C-based extractor yourself (required for Windows `.exe`):

```bash
cd src
make
```
*(Requires `gcc` and `libpng-dev`)*

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. You are free to modify, distribute, and use it to help localize visual novels, provided you keep the software open-source.

---
*Happy Translating!*
