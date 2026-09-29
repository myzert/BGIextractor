import os
import json
import struct
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk

# Theme: Black and Blue
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BGIExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BGI Extractor")
        self.geometry("900x650")
        self.resizable(False, False)
        
        # Header
        self.header = ctk.CTkLabel(self, text="BGI Extractor", font=ctk.CTkFont(size=28, weight="bold"), text_color="#3a7ebf")
        self.header.pack(pady=(20, 5))
        
        self.subheader = ctk.CTkLabel(self, text="ARC Extraction and Bytecode Injection Toolkit", font=ctk.CTkFont(size=14, slant="italic"), text_color="gray")
        self.subheader.pack(pady=(0, 15))
        
        # Tabs
        self.tabview = ctk.CTkTabview(self, width=850, height=400)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tabview.add("1. ARC Viewer & Extractor")
        self.tabview.add("2. Text to JSON")
        self.tabview.add("3. JSON Injector")
        self.tabview.add("4. ARC Builder")
        
        self.setup_tab_viewer()
        self.setup_tab_json()
        self.setup_tab_inject()
        self.setup_tab_pack()
        
        # Log Box
        self.log_box = ctk.CTkTextbox(self, height=120, state="disabled", fg_color="#1a1a1a", text_color="#4da6ff")
        self.log_box.pack(padx=20, pady=(0, 20), fill="x")
        self.log("BGI Extractor initialized.")
        
    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def browse_folder(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, 'end')
            entry.insert(0, folder)
            
    def browse_file(self, entry, save=False, ext=".arc"):
        if save:
            file = filedialog.asksaveasfilename(defaultextension=ext)
        else:
            file = filedialog.askopenfilename(filetypes=[("ARC Files", "*.arc"), ("All Files", "*.*")])
        if file:
            entry.delete(0, 'end')
            entry.insert(0, file)

    # --- TAB 1: VIEWER & EXTRACTOR ---
    def setup_tab_viewer(self):
        tab = self.tabview.tab("1. ARC Viewer & Extractor")
        
        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)
        
        self.tv_arc = ctk.CTkEntry(top_frame, placeholder_text="Target .arc File", width=450)
        self.tv_arc.pack(side="left", padx=(0, 10))
        ctk.CTkButton(top_frame, text="Browse ARC", command=lambda: self.browse_file(self.tv_arc), width=100).pack(side="left")
        ctk.CTkButton(top_frame, text="View Contents", command=self.view_arc, width=120, fg_color="#3a7ebf").pack(side="left", padx=10)
        
        # Listbox for files
        self.file_list = ctk.CTkTextbox(tab, height=180, state="disabled", fg_color="#111111", text_color="white")
        self.file_list.pack(fill="x", padx=10, pady=10)
        
        bot_frame = ctk.CTkFrame(tab, fg_color="transparent")
        bot_frame.pack(fill="x", padx=10, pady=10)
        
        self.tv_out = ctk.CTkEntry(bot_frame, placeholder_text="Output Folder to Extract", width=450)
        self.tv_out.pack(side="left", padx=(0, 10))
        ctk.CTkButton(bot_frame, text="Browse Folder", command=lambda: self.browse_folder(self.tv_out), width=100).pack(side="left")
        
        ctk.CTkButton(bot_frame, text="Extract All (Decrypt)", command=self.run_extract, width=140, fg_color="green", hover_color="darkgreen").pack(side="right", padx=10)

    def view_arc(self):
        arc_path = self.tv_arc.get()
        if not os.path.exists(arc_path):
            return messagebox.showerror("Error", "File not found!")
        
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")
        
        try:
            with open(arc_path, "rb") as f:
                header = f.read(12)
                if header not in (b"BURIKO ARC20", b"PackFile    "):
                    self.file_list.insert("end", "Error: Not a valid BURIKO ARC20 file.")
                    self.file_list.configure(state="disabled")
                    return
                    
                file_count = int.from_bytes(f.read(4), "little")
                self.file_list.insert("end", f"--- ARCHIVE HEADER: {header.decode('utf-8', 'ignore')} ---\n")
                self.file_list.insert("end", f"--- TOTAL FILES: {file_count} ---\n\n")
                
                for _ in range(min(file_count, 1000)):  # limit display to 1000
                    name_bytes = f.read(16)
                    name = name_bytes.split(b'\x00')[0].decode('shift_jis', errors='ignore')
                    if header == b"BURIKO ARC20": f.read(80)
                    offset = int.from_bytes(f.read(4), "little")
                    size = int.from_bytes(f.read(4), "little")
                    if header == b"BURIKO ARC20": f.read(24)
                    else: f.read(8)
                    self.file_list.insert("end", f"File: {name.ljust(30)} | Size: {size} bytes\n")
                    
                if file_count > 1000:
                    self.file_list.insert("end", f"... and {file_count - 1000} more files ...\n")
        except Exception as e:
            self.file_list.insert("end", f"Error reading ARC: {str(e)}")
            
        self.file_list.configure(state="disabled")
        self.log(f"Scanned {arc_path}")

    def run_extract(self):
        arc_file, out_dir = self.tv_arc.get(), self.tv_out.get()
        if not arc_file or not out_dir: return messagebox.showerror("Error", "Fill all fields!")
        exe_name = "ethornell.exe" if os.name == 'nt' else "./ethornell_linux"
        exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), exe_name)
        
        def task():
            self.log(f"Extracting & Decrypting {os.path.basename(arc_file)}...")
            os.makedirs(out_dir, exist_ok=True)
            try:
                subprocess.run([exe_path, arc_file, out_dir], check=True)
                self.log("Extraction completed successfully!")
            except Exception as e:
                self.log(f"Extraction failed: {str(e)} (Ensure ethornell engine is present)")
        threading.Thread(target=task).start()

    # --- TAB 2: JSON ---
    def setup_tab_json(self):
        tab = self.tabview.tab("2. Text to JSON")
        self.t2_in = ctk.CTkEntry(tab, placeholder_text="Input Folder (.bss files)", width=500)
        self.t2_in.pack(pady=(20, 5))
        ctk.CTkButton(tab, text="Browse Folder", command=lambda: self.browse_folder(self.t2_in)).pack(pady=5)
        
        self.t2_out = ctk.CTkEntry(tab, placeholder_text="Output Folder (.json files)", width=500)
        self.t2_out.pack(pady=(20, 5))
        ctk.CTkButton(tab, text="Browse Folder", command=lambda: self.browse_folder(self.t2_out)).pack(pady=5)
        
        ctk.CTkButton(tab, text="▶ Generate JSON", command=self.run_json).pack(pady=30)

    def run_json(self):
        indir, outdir = self.t2_in.get(), self.t2_out.get()
        if not indir or not outdir: return
        def is_dialog(text):
            import re
            if len(text) < 5 or ".bss" in text or ".mpg" in text: return False
            if "_" in text and " " not in text: return False
            if text.isupper(): return False
            if " " not in text and not re.search(r'[a-z]', text): return False
            if any(0x3040 <= ord(c) <= 0x309F for c in text): return False
            return True
        count = 0
        os.makedirs(outdir, exist_ok=True)
        for f in os.listdir(indir):
            bss_file = os.path.join(indir, f)
            if not os.path.isfile(bss_file): continue
            with open(bss_file, "rb") as bf: data = bf.read()
            strings, i = [], 0
            while i < len(data) - 4:
                if data[i:i+4] == b'\x03\x00\x00\x00':
                    start = i + 4
                    end = start
                    while end < len(data) and data[end] != 0x00: end += 1
                    if end > start:
                        try:
                            text = data[start:end].decode('shift_jis')
                            if is_dialog(text): strings.append({"offset": start, "original": text, "translated": text})
                        except: pass
                    i = end
                else: i += 1
            if strings:
                with open(os.path.join(outdir, f.replace(".bss", "") + ".json"), "w", encoding="utf-8") as jf:
                    json.dump(strings, jf, ensure_ascii=False, indent=2)
                count += 1
        self.log(f"JSON Generation Done: {count} files created.")

    # --- TAB 3: INJECT ---
    def setup_tab_inject(self):
        tab = self.tabview.tab("3. JSON Injector")
        self.t3_bss = ctk.CTkEntry(tab, placeholder_text="Original .bss Folder", width=400)
        self.t3_bss.pack(pady=(15, 2))
        ctk.CTkButton(tab, text="Browse", command=lambda: self.browse_folder(self.t3_bss)).pack(pady=(0, 10))
        
        self.t3_json = ctk.CTkEntry(tab, placeholder_text="Translated .json Folder", width=400)
        self.t3_json.pack(pady=2)
        ctk.CTkButton(tab, text="Browse", command=lambda: self.browse_folder(self.t3_json)).pack(pady=(0, 10))
        
        self.t3_out = ctk.CTkEntry(tab, placeholder_text="Output Patched .bss Folder", width=400)
        self.t3_out.pack(pady=2)
        ctk.CTkButton(tab, text="Browse", command=lambda: self.browse_folder(self.t3_out)).pack(pady=(0, 10))
        
        ctk.CTkButton(tab, text="▶ Inject Bytes", command=self.run_inject, fg_color="purple", hover_color="darkmagenta").pack(pady=10)

    def run_inject(self):
        bss_dir, json_dir, out_dir = self.t3_bss.get(), self.t3_json.get(), self.t3_out.get()
        if not bss_dir or not json_dir or not out_dir: return
        count = 0
        os.makedirs(out_dir, exist_ok=True)
        for f in os.listdir(json_dir):
            if not f.endswith(".json"): continue
            base = f.replace(".json", "")
            bss_file = os.path.join(bss_dir, base + ".bss")
            if not os.path.exists(bss_file): bss_file = os.path.join(bss_dir, base)
            if not os.path.exists(bss_file): continue
            
            with open(bss_file, "rb") as bf: data = bytearray(bf.read())
            with open(os.path.join(json_dir, f), "r", encoding="utf-8") as jf: translations = json.load(jf)
            
            for item in translations:
                if item["original"] == item["translated"]: continue
                offset, orig_len = item["offset"], len(item["original"].encode('shift_jis'))
                try: trans_bytes = item["translated"].encode('shift_jis', errors='replace')
                except: trans_bytes = item["translated"].encode('utf-8', errors='ignore')
                
                if len(trans_bytes) < orig_len: trans_bytes = trans_bytes.ljust(orig_len, b'\x20')
                elif len(trans_bytes) > orig_len: trans_bytes = trans_bytes[:orig_len]
                data[offset:offset+orig_len] = trans_bytes
            
            with open(os.path.join(out_dir, os.path.basename(bss_file)), "wb") as outf: outf.write(data)
            count += 1
        self.log(f"Injection Done: Patched {count} files.")

    # --- TAB 4: REPACK ---
    def setup_tab_pack(self):
        tab = self.tabview.tab("4. ARC Builder")
        self.t4_in = ctk.CTkEntry(tab, placeholder_text="Input Folder (Patched files)", width=500)
        self.t4_in.pack(pady=(30, 5))
        ctk.CTkButton(tab, text="Browse Folder", command=lambda: self.browse_folder(self.t4_in)).pack(pady=5)
        
        self.t4_out = ctk.CTkEntry(tab, placeholder_text="Output ARC File (.arc)", width=500)
        self.t4_out.pack(pady=(20, 5))
        ctk.CTkButton(tab, text="Browse File", command=lambda: self.browse_file(self.t4_out, save=True, ext=".arc.new")).pack(pady=5)
        
        ctk.CTkButton(tab, text="▶ Build Archive", command=self.run_pack, fg_color="#C85000", hover_color="#963C00").pack(pady=30)

    def run_pack(self):
        indir, outfile = self.t4_in.get(), self.t4_out.get()
        if not indir or not outfile: return
        self.log("Building BURIKO ARC20 Archive...")
        files = sorted([os.path.join(indir, f) for f in os.listdir(indir) if os.path.isfile(os.path.join(indir, f))])
        with open(outfile, "wb") as arc_file:
            arc_file.write(b"BURIKO ARC20")
            arc_file.write(len(files).to_bytes(4, "little"))
            data_offset = 0
            for file_path in files:
                file_size = os.path.getsize(file_path)
                name_padded = os.path.basename(file_path).encode("shift_jis")[:96].ljust(96, b'\x00')
                arc_file.write(name_padded + data_offset.to_bytes(4, "little") + file_size.to_bytes(4, "little") + b'\x00' * 24)
                data_offset += file_size
            for file_path in files:
                with open(file_path, "rb") as f: arc_file.write(f.read())
        self.log(f"Pack Success: {os.path.basename(outfile)}")

if __name__ == "__main__":
    app = BGIExtractorApp()
    app.mainloop()
