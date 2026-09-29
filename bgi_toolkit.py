import os
import json
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BgiToolkitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BGI Translation Toolkit Pro")
        self.geometry("750x600")
        self.resizable(False, False)
        
        # Header
        self.header = ctk.CTkLabel(self, text="BGI Engine Translation Toolkit", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=(20, 5))
        
        self.subheader = ctk.CTkLabel(self, text="Professional Extractor, Decompiler, and Injector by myzert", font=ctk.CTkFont(size=13, slant="italic"), text_color="gray")
        self.subheader.pack(pady=(0, 20))
        
        # Tab View
        self.tabview = ctk.CTkTabview(self, width=700, height=350)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tabview.add("1. ARC Extractor")
        self.tabview.add("2. BSS to JSON")
        self.tabview.add("3. JSON to BSS")
        self.tabview.add("4. ARC Repacker")
        
        self.setup_tab_extract()
        self.setup_tab_json()
        self.setup_tab_inject()
        self.setup_tab_pack()
        
        # Log Box
        self.log_box = ctk.CTkTextbox(self, height=100, state="disabled")
        self.log_box.pack(padx=20, pady=(0, 20), fill="x")
        self.log("Welcome to BGI Toolkit Pro. The ultimate UI client.")
        
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

    def setup_tab_extract(self):
        tab = self.tabview.tab("1. ARC Extractor")
        
        ctk.CTkLabel(tab, text="Unpack .arc archives and decrypt DSC FORMAT 1.00", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 20))
        
        self.t1_arc = ctk.CTkEntry(tab, placeholder_text="Target .arc File", width=400)
        self.t1_arc.pack(pady=5)
        ctk.CTkButton(tab, text="Browse File", command=lambda: self.browse_file(self.t1_arc)).pack(pady=5)
        
        self.t1_out = ctk.CTkEntry(tab, placeholder_text="Output Folder", width=400)
        self.t1_out.pack(pady=(15, 5))
        ctk.CTkButton(tab, text="Browse Folder", command=lambda: self.browse_folder(self.t1_out)).pack(pady=5)
        
        ctk.CTkButton(tab, text="▶ Extract & Decrypt", command=self.run_extract, fg_color="green", hover_color="darkgreen").pack(pady=30)

    def run_extract(self):
        arc_file, out_dir = self.t1_arc.get(), self.t1_out.get()
        if not arc_file or not out_dir: return messagebox.showerror("Error", "Fill all fields!")
        exe_name = "ethornell.exe" if os.name == 'nt' else "./ethornell_linux"
        exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), exe_name)
        if not os.path.exists(exe_path): return messagebox.showerror("Error", f"Core extractor '{exe_name}' not found!")
        
        def task():
            self.log(f"Extracting {os.path.basename(arc_file)}...")
            os.makedirs(out_dir, exist_ok=True)
            try:
                subprocess.run([exe_path, arc_file, out_dir], check=True)
                self.log("Extraction completed successfully!")
            except Exception as e:
                self.log(f"Extraction failed: {str(e)}")
        threading.Thread(target=task).start()

    def setup_tab_json(self):
        tab = self.tabview.tab("2. BSS to JSON")
        ctk.CTkLabel(tab, text="Extract dialogue strings from decrypted .bss files into JSON", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 20))
        
        self.t2_in = ctk.CTkEntry(tab, placeholder_text="Input Folder (Extracted .bss files)", width=400)
        self.t2_in.pack(pady=5)
        ctk.CTkButton(tab, text="Browse Folder", command=lambda: self.browse_folder(self.t2_in)).pack(pady=5)
        
        self.t2_out = ctk.CTkEntry(tab, placeholder_text="Output Folder (For .json files)", width=400)
        self.t2_out.pack(pady=(15, 5))
        ctk.CTkButton(tab, text="Browse Folder", command=lambda: self.browse_folder(self.t2_out)).pack(pady=5)
        
        ctk.CTkButton(tab, text="▶ Generate JSON Files", command=self.run_json, fg_color="blue", hover_color="darkblue").pack(pady=30)

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
                with open(json_path, "w", encoding="utf-8") as jf: json.dump(strings, jf, ensure_ascii=False, indent=2)
                count += 1
        self.log(f"Successfully generated {count} JSON files.")

    def setup_tab_inject(self):
        tab = self.tabview.tab("3. JSON to BSS")
        ctk.CTkLabel(tab, text="Safely inject translated JSON text back into original .bss files", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 10))
        
        self.t3_bss = ctk.CTkEntry(tab, placeholder_text="Original .bss Folder", width=300)
        self.t3_bss.pack(pady=2)
        ctk.CTkButton(tab, text="Browse BSS", command=lambda: self.browse_folder(self.t3_bss)).pack(pady=2)
        
        self.t3_json = ctk.CTkEntry(tab, placeholder_text="Translated .json Folder", width=300)
        self.t3_json.pack(pady=2)
        ctk.CTkButton(tab, text="Browse JSON", command=lambda: self.browse_folder(self.t3_json)).pack(pady=2)
        
        self.t3_out = ctk.CTkEntry(tab, placeholder_text="Output Patched .bss Folder", width=300)
        self.t3_out.pack(pady=2)
        ctk.CTkButton(tab, text="Browse Output", command=lambda: self.browse_folder(self.t3_out)).pack(pady=2)
        
        ctk.CTkButton(tab, text="▶ Inject Bytecode", command=self.run_inject, fg_color="purple", hover_color="darkmagenta").pack(pady=10)

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
                offset, orig_len = item["offset"], len(item["original"].encode('shift_jis'))
                try: trans_bytes = item["translated"].encode('shift_jis', errors='replace')
                except: trans_bytes = item["translated"].encode('utf-8', errors='ignore')
                
                if len(trans_bytes) < orig_len: trans_bytes = trans_bytes.ljust(orig_len, b'\x20')
                elif len(trans_bytes) > orig_len: trans_bytes = trans_bytes[:orig_len]
                data[offset:offset+orig_len] = trans_bytes
            
            with open(os.path.join(out_dir, os.path.basename(bss_file)), "wb") as outf: outf.write(data)
            count += 1
        self.log(f"Safely patched {count} BSS files with auto-padding.")

    def setup_tab_pack(self):
        tab = self.tabview.tab("4. ARC Repacker")
        ctk.CTkLabel(tab, text="Compile patched files into a fresh BURIKO ARC20 archive", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 20))
        
        self.t4_in = ctk.CTkEntry(tab, placeholder_text="Input Folder (Patched .bss / Assets)", width=400)
        self.t4_in.pack(pady=5)
        ctk.CTkButton(tab, text="Browse Folder", command=lambda: self.browse_folder(self.t4_in)).pack(pady=5)
        
        self.t4_out = ctk.CTkEntry(tab, placeholder_text="Output ARC File (e.g. data01099.arc.new)", width=400)
        self.t4_out.pack(pady=(15, 5))
        ctk.CTkButton(tab, text="Browse File", command=lambda: self.browse_file(self.t4_out, save=True, ext=".arc.new")).pack(pady=5)
        
        ctk.CTkButton(tab, text="▶ Build Archive", command=self.run_pack, fg_color="#C85000", hover_color="#963C00").pack(pady=30)

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
                file_size = os.path.getsize(file_path)
                name_padded = os.path.basename(file_path).encode("shift_jis")[:96].ljust(96, b'\x00')
                arc_file.write(name_padded + data_offset.to_bytes(4, "little") + file_size.to_bytes(4, "little") + b'\x00' * 24)
                data_offset += file_size
                
            for file_path in files:
                with open(file_path, "rb") as f: arc_file.write(f.read())
        self.log(f"Archive packed: {os.path.basename(outfile)}")

if __name__ == "__main__":
    app = BgiToolkitApp()
    app.mainloop()
