import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def is_dialog(text):
    import re
    if len(text) < 5: return False
    if ".bss" in text or ".mpg" in text: return False
    if "_" in text and " " not in text: return False
    if text.isupper(): return False
    if " " not in text and not re.search(r'[a-z]', text): return False
    if any(0x3040 <= ord(c) <= 0x309F for c in text): return False
    return True

def create_json(bss_file, out_dir):
    with open(bss_file, "rb") as f:
        data = f.read()

    strings = []
    i = 0
    while i < len(data) - 4:
        if data[i] == 0x03 and data[i+1] == 0x00 and data[i+2] == 0x00 and data[i+3] == 0x00:
            start = i + 4
            end = start
            while end < len(data) and data[end] != 0x00:
                end += 1
            if end > start:
                try:
                    text = data[start:end].decode('shift_jis')
                    if is_dialog(text):
                        strings.append({"offset": start, "original": text, "translated": text})
                except UnicodeDecodeError:
                    pass
            i = end
        else:
            i += 1

    if strings:
        os.makedirs(out_dir, exist_ok=True)
        base_name = os.path.basename(bss_file)
        json_path = os.path.join(out_dir, base_name.replace(".bss", "").replace(".txt", "") + ".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(strings, f, ensure_ascii=False, indent=2)
        return True
    return False

def inject_json(bss_file, json_file, out_dir):
    with open(bss_file, "rb") as f:
        data = bytearray(f.read())
    with open(json_file, "r", encoding="utf-8") as f:
        translations = json.load(f)

    for item in translations:
        offset = item["offset"]
        orig_text = item["original"]
        trans_text = item["translated"]

        if orig_text == trans_text:
            continue

        orig_bytes = orig_text.encode('shift_jis')
        try:
            trans_bytes = trans_text.encode('shift_jis', errors='replace')
        except:
            trans_bytes = trans_text.encode('utf-8', errors='ignore')

        target_length = len(orig_bytes)
        if len(trans_bytes) < target_length:
            trans_bytes = trans_bytes.ljust(target_length, b'\x20')
        elif len(trans_bytes) > target_length:
            trans_bytes = trans_bytes[:target_length]

        data[offset:offset+target_length] = trans_bytes

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, os.path.basename(bss_file))
    with open(out_path, "wb") as f:
        f.write(data)
    return True

def pack_arc(input_dir, output_file):
    HEADER = b"BURIKO ARC20"
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    
    with open(output_file, "wb") as arc_file:
        arc_file.write(HEADER)
        arc_file.write(len(files).to_bytes(4, "little"))

        data_offset = 0
        offsets = []
        sizes = []

        for file_path in files:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            name_encoded = file_name.encode("shift_jis")[:96]
            name_padded = name_encoded + b"\x00" * (96 - len(name_encoded))
            arc_file.write(name_padded)

            arc_file.write(data_offset.to_bytes(4, "little"))
            arc_file.write(file_size.to_bytes(4, "little"))
            arc_file.write(b"\x00" * 24)

            offsets.append(data_offset)
            sizes.append(file_size)
            data_offset += file_size

        for file_path in files:
            with open(file_path, "rb") as f:
                arc_file.write(f.read())

class BgiToolkitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BGI Engine Script Toolkit")
        self.geometry("500x400")
        
        tab_control = ttk.Notebook(self)
        
        # Tab 1: Extract
        tab1 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='1. BSS to JSON')
        self.setup_tab1(tab1)
        
        # Tab 2: Inject
        tab2 = ttk.Frame(tab_control)
        tab_control.add(tab2, text='2. JSON to BSS')
        self.setup_tab2(tab2)
        
        # Tab 3: Repack
        tab3 = ttk.Frame(tab_control)
        tab_control.add(tab3, text='3. Build ARC')
        self.setup_tab3(tab3)
        
        tab_control.pack(expand=1, fill='both')

    def browse_folder(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, tk.END)
            entry.insert(0, folder)
            
    def browse_file(self, entry, save=False):
        if save:
            file = filedialog.asksaveasfilename(defaultextension=".arc")
        else:
            file = filedialog.askopenfilename()
        if file:
            entry.delete(0, tk.END)
            entry.insert(0, file)

    def setup_tab1(self, tab):
        ttk.Label(tab, text="Input Folder (Extracted .bss files):").pack(pady=5)
        self.t1_in = ttk.Entry(tab, width=50)
        self.t1_in.pack(pady=5)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t1_in)).pack()
        
        ttk.Label(tab, text="Output Folder (For .json files):").pack(pady=5)
        self.t1_out = ttk.Entry(tab, width=50)
        self.t1_out.pack(pady=5)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t1_out)).pack()
        
        ttk.Button(tab, text="Generate JSONs", command=self.run_tab1).pack(pady=20)

    def run_tab1(self):
        indir = self.t1_in.get()
        outdir = self.t1_out.get()
        count = 0
        for f in os.listdir(indir):
            if create_json(os.path.join(indir, f), outdir):
                count += 1
        messagebox.showinfo("Done", f"Generated {count} JSON files!")

    def setup_tab2(self, tab):
        ttk.Label(tab, text="Original .bss Folder:").pack(pady=5)
        self.t2_bss = ttk.Entry(tab, width=50)
        self.t2_bss.pack(pady=5)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t2_bss)).pack()
        
        ttk.Label(tab, text="Translated .json Folder:").pack(pady=5)
        self.t2_json = ttk.Entry(tab, width=50)
        self.t2_json.pack(pady=5)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t2_json)).pack()
        
        ttk.Label(tab, text="Output Folder (Injected .bss):").pack(pady=5)
        self.t2_out = ttk.Entry(tab, width=50)
        self.t2_out.pack(pady=5)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t2_out)).pack()
        
        ttk.Button(tab, text="Inject Translations", command=self.run_tab2).pack(pady=20)

    def run_tab2(self):
        bss_dir = self.t2_bss.get()
        json_dir = self.t2_json.get()
        out_dir = self.t2_out.get()
        count = 0
        for f in os.listdir(json_dir):
            if f.endswith(".json"):
                base = f.replace(".json", "")
                bss_file = os.path.join(bss_dir, base + ".bss")
                if not os.path.exists(bss_file):
                    bss_file = os.path.join(bss_dir, base)
                if os.path.exists(bss_file):
                    if inject_json(bss_file, os.path.join(json_dir, f), out_dir):
                        count += 1
        messagebox.showinfo("Done", f"Injected {count} files!")

    def setup_tab3(self, tab):
        ttk.Label(tab, text="Input Folder (Injected .bss files):").pack(pady=5)
        self.t3_in = ttk.Entry(tab, width=50)
        self.t3_in.pack(pady=5)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_folder(self.t3_in)).pack()
        
        ttk.Label(tab, text="Output ARC File (e.g. data01099.arc.new):").pack(pady=5)
        self.t3_out = ttk.Entry(tab, width=50)
        self.t3_out.pack(pady=5)
        ttk.Button(tab, text="Browse", command=lambda: self.browse_file(self.t3_out, save=True)).pack()
        
        ttk.Button(tab, text="Build ARC", command=self.run_tab3).pack(pady=20)

    def run_tab3(self):
        pack_arc(self.t3_in.get(), self.t3_out.get())
        messagebox.showinfo("Done", "ARC file built successfully!")

if __name__ == "__main__":
    app = BgiToolkitApp()
    app.mainloop()
