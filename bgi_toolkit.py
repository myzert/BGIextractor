import os
import json
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

class BgiToolkitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BGI Translation Toolkit Pro - by myzert")
        self.geometry("650x550")
        self.configure(padx=10, pady=10)
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(header_frame, text="BGI Engine Translation Toolkit", font=("Helvetica", 16, "bold")).pack()
        ttk.Label(header_frame, text="Ultimate Solution for SMEE / Ethornell Visual Novels", font=("Helvetica", 10)).pack()
        
        tab_control = ttk.Notebook(self)
        
        # Tabs
        tab1 = ttk.Frame(tab_control, padding=10)
        tab_control.add(tab1, text='1. ARC Extractor')
        self.setup_tab_extract(tab1)
        
        tab2 = ttk.Frame(tab_control, padding=10)
        tab_control.add(tab2, text='2. BSS Decompiler (JSON)')
        self.setup_tab_json(tab2)
        
        tab3 = ttk.Frame(tab_control, padding=10)
        tab_control.add(tab3, text='3. BSS Injector')
        self.setup_tab_inject(tab3)
        
        tab4 = ttk.Frame(tab_control, padding=10)
        tab_control.add(tab4, text='4. ARC Repacker')
        self.setup_tab_pack(tab4)
        
        tab_control.pack(expand=1, fill='both')

        # Status Log
        self.log_area = ScrolledText(self, height=8, state='disabled', bg='#f4f4f4')
        self.log_area.pack(fill='x', pady=(10, 0))
        self.log("Welcome to BGI Translation Toolkit Pro.")
        self.log("Designed to prevent crashes using safe auto-padding injection.")

    def log(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def browse_folder(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, tk.END)
            entry.insert(0, folder)
            
    def browse_file(self, entry, save=False, ext=".arc"):
        if save:
            file = filedialog.asksaveasfilename(defaultextension=ext)
        else:
            file = filedialog.askopenfilename(filetypes=[("ARC Files", "*.arc"), ("All Files", "*.*")])
        if file:
            entry.delete(0, tk.END)
            entry.insert(0, file)

    # ---------------- TAB 1: EXTRACT ----------------
    def setup_tab_extract(self, tab):
        ttk.Label(tab, text="Unpack .arc archives and decrypt DSC FORMAT 1.00", font=("Helvetica", 10, "italic")).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(tab, text="Target .arc File:").pack(anchor='w')
        self.t1_arc = ttk.Entry(tab, width=60)
        self.t1_arc.pack(anchor='w', pady=2)
        ttk.Button(tab, text="Browse File", command=lambda: self.browse_file(self.t1_arc)).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(tab, text="Output Folder:").pack(anchor='w')
        self.t1_out = ttk.Entry(tab, width=60)
        self.t1_out.pack(anchor='w', pady=2)
        ttk.Button(tab, text="Browse Folder", command=lambda: self.browse_folder(self.t1_out)).pack(anchor='w', pady=(0, 10))
        
        ttk.Button(tab, text="Extract & Decrypt", command=self.run_extract, width=20).pack(pady=20)

    def run_extract(self):
        arc_file = self.t1_arc.get()
        out_dir = self.t1_out.get()
        if not arc_file or not out_dir: return messagebox.showerror("Error", "Fill all fields!")
        
        exe_name = "ethornell.exe" if os.name == 'nt' else "./ethornell_linux"
        exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), exe_name)
        
        if not os.path.exists(exe_path):
            return messagebox.showerror("Error", f"Core extractor '{exe_name}' not found!")
            
        def task():
            self.log(f"Starting extraction for {os.path.basename(arc_file)}...")
            os.makedirs(out_dir, exist_ok=True)
            try:
                subprocess.run([exe_path, arc_file, out_dir], check=True)
                self.log("Extraction completed successfully!")
            except Exception as e:
                self.log(f"Extraction failed: {str(e)}")
        
        threading.Thread(target=task).start()

    # ---------------- TAB 2: DECOMPILE (JSON) ----------------
    def setup_tab_json(self, tab):
        ttk.Label(tab, text="Extract dialogue strings from decrypted .bss files into JSON", font=("Helvetica", 10, "italic")).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(tab, text="Input Folder (Extracted .bss files):").pack(anchor='w')
        self.t2_in = ttk.Entry(tab, width=60)
        self.t2_in.pack(anchor='w', pady=2)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t2_in)).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(tab, text="Output Folder (For .json translation files):").pack(anchor='w')
        self.t2_out = ttk.Entry(tab, width=60)
        self.t2_out.pack(anchor='w', pady=2)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t2_out)).pack(anchor='w', pady=(0, 10))
        
        ttk.Button(tab, text="Generate JSON Files", command=self.run_json, width=20).pack(pady=20)

    def run_json(self):
        indir, outdir = self.t2_in.get(), self.t2_out.get()
        if not indir or not outdir: return messagebox.showerror("Error", "Fill all fields!")
        
        def is_dialog(text):
            import re
            if len(text) < 5: return False
            if ".bss" in text or ".mpg" in text: return False
            if "_" in text and " " not in text: return False
            if text.isupper(): return False
            if " " not in text and not re.search(r'[a-z]', text): return False
            if any(0x3040 <= ord(c) <= 0x309F for c in text): return False
            return True

        self.log("Scanning .bss files for strings...")
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
                json_path = os.path.join(outdir, f.replace(".bss", "").replace(".txt", "") + ".json")
                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump(strings, jf, ensure_ascii=False, indent=2)
                count += 1
        self.log(f"Successfully generated {count} JSON files.")

    # ---------------- TAB 3: INJECT ----------------
    def setup_tab_inject(self, tab):
        ttk.Label(tab, text="Safely inject translated JSON text back into original .bss files", font=("Helvetica", 10, "italic")).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(tab, text="Original .bss Folder:").pack(anchor='w')
        self.t3_bss = ttk.Entry(tab, width=60)
        self.t3_bss.pack(anchor='w', pady=2)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t3_bss)).pack(anchor='w')
        
        ttk.Label(tab, text="Translated .json Folder:").pack(anchor='w')
        self.t3_json = ttk.Entry(tab, width=60)
        self.t3_json.pack(anchor='w', pady=2)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t3_json)).pack(anchor='w')
        
        ttk.Label(tab, text="Output Folder (For patched .bss files):").pack(anchor='w')
        self.t3_out = ttk.Entry(tab, width=60)
        self.t3_out.pack(anchor='w', pady=2)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t3_out)).pack(anchor='w')
        
        ttk.Button(tab, text="Inject Bytecode", command=self.run_inject, width=20).pack(pady=15)

    def run_inject(self):
        bss_dir, json_dir, out_dir = self.t3_bss.get(), self.t3_json.get(), self.t3_out.get()
        if not bss_dir or not json_dir or not out_dir: return messagebox.showerror("Error", "Fill all fields!")
        
        self.log("Injecting JSON translations into bytecode...")
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
                offset = item["offset"]
                orig_len = len(item["original"].encode('shift_jis'))
                try: trans_bytes = item["translated"].encode('shift_jis', errors='replace')
                except: trans_bytes = item["translated"].encode('utf-8', errors='ignore')
                
                if len(trans_bytes) < orig_len: trans_bytes = trans_bytes.ljust(orig_len, b'\x20')
                elif len(trans_bytes) > orig_len: trans_bytes = trans_bytes[:orig_len]
                
                data[offset:offset+orig_len] = trans_bytes
            
            with open(os.path.join(out_dir, os.path.basename(bss_file)), "wb") as outf: outf.write(data)
            count += 1
        self.log(f"Safely patched {count} BSS files with auto-padding.")

    # ---------------- TAB 4: REPACK ----------------
    def setup_tab_pack(self, tab):
        ttk.Label(tab, text="Compile patched files into a fresh BURIKO ARC20 archive", font=("Helvetica", 10, "italic")).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(tab, text="Input Folder (Patched .bss / Assets):").pack(anchor='w')
        self.t4_in = ttk.Entry(tab, width=60)
        self.t4_in.pack(anchor='w', pady=2)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t4_in)).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(tab, text="Output ARC File (e.g. data01099.arc.new):").pack(anchor='w')
        self.t4_out = ttk.Entry(tab, width=60)
        self.t4_out.pack(anchor='w', pady=2)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_file(self.t4_out, save=True, ext=".arc.new")).pack(anchor='w', pady=(0, 10))
        
        ttk.Button(tab, text="Build Archive", command=self.run_pack, width=20).pack(pady=20)

    def run_pack(self):
        indir, outfile = self.t4_in.get(), self.t4_out.get()
        if not indir or not outfile: return messagebox.showerror("Error", "Fill all fields!")
        
        self.log("Building BURIKO ARC20 Archive...")
        files = sorted([os.path.join(indir, f) for f in os.listdir(indir) if os.path.isfile(os.path.join(indir, f))])
        
        with open(outfile, "wb") as arc_file:
            arc_file.write(b"BURIKO ARC20")
            arc_file.write(len(files).to_bytes(4, "little"))
            
            data_offset = 0
            for file_path in files:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                name_padded = file_name.encode("shift_jis")[:96].ljust(96, b'\x00')
                
                arc_file.write(name_padded)
                arc_file.write(data_offset.to_bytes(4, "little"))
                arc_file.write(file_size.to_bytes(4, "little"))
                arc_file.write(b'\x00' * 24)
                data_offset += file_size
                
            for file_path in files:
                with open(file_path, "rb") as f:
                    arc_file.write(f.read())
        self.log(f"Archive successfully packed: {os.path.basename(outfile)}")

if __name__ == "__main__":
    app = BgiToolkitApp()
    app.mainloop()
