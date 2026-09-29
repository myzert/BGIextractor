import os
import json
import struct
import subprocess
import threading
import tempfile
import shutil
import re
from PIL import Image
from deep_translator import GoogleTranslator
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def is_dialog(text):
    import re
    if len(text) < 2: return False
    if re.search(r'\.(bmp|png|jpg|jpeg|ogg|wav|mp3|mpg|bss|arc|csv)$', text, re.IGNORECASE): return False
    if re.match(r'^[A-Za-z0-9_]+$', text) and '_' in text: return False
    if text.isupper() and re.match(r'^[A-Z0-9_ ]+$', text): return False
    if text.startswith(('@', '#', '$', '%', 'sys_', 'Sys_', 'se_', 'bgm_', 'bg_')): return False
    
    # Check if purely ascii with no spaces (likely a variable)
    if re.match(r'^[A-Za-z0-9]+$', text): return False
    
    return True

class TranslationEditor(ctk.CTkToplevel):
    def __init__(self, parent, target_file, bss_data):
        super().__init__(parent)
        self.title(f"Translation Editor - {target_file}")
        self.geometry("900x600")
        self.bss_data = bss_data
        self.target_file = target_file
        self.strings = []
        self.entries = []
        
        self.parse_bss()
        self.setup_ui()
        
    def parse_bss(self):
        data = self.bss_data
        i = 0
        while i < len(data) - 4:
            if data[i:i+4] == b'\x03\x00\x00\x00':
                start, end = i + 4, i + 4
                while end < len(data) and data[end] != 0x00: end += 1
                if end > start:
                    try:
                        text = data[start:end].decode('shift_jis')
                        if is_dialog(text): 
                            self.strings.append({"offset": start, "original": text, "translated": text})
                    except: pass
                i = end
            else: i += 1

    def setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(header_frame, text=f"File: {self.target_file}", font=ctk.CTkFont(weight="bold", size=16)).pack(side="left")
        ctk.CTkButton(header_frame, text="Export as JSON", command=self.save_json, fg_color="#28a745", hover_color="#218838").pack(side="right", padx=(10, 0))
        ctk.CTkButton(header_frame, text="Auto-Translate All (ID)", command=self.auto_translate, fg_color="#3B8ED0", hover_color="#1F6AA5").pack(side="right")
        
        if not self.strings:
            ctk.CTkLabel(self, text="No translatable dialogue found in this file.").grid(row=1, column=0)
            return

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll.grid_columnconfigure(1, weight=1)
        
        for idx, item in enumerate(self.strings):
            orig_lbl = ctk.CTkLabel(self.scroll, text=item["original"], wraplength=400, justify="left", anchor="w")
            orig_lbl.grid(row=idx, column=0, padx=10, pady=10, sticky="ew")
            
            trans_entry = ctk.CTkTextbox(self.scroll, height=50)
            trans_entry.insert("1.0", item["translated"])
            trans_entry.grid(row=idx, column=1, padx=10, pady=10, sticky="ew")
            self.entries.append(trans_entry)

    def auto_translate(self):
        def task():
            try:
                translator = GoogleTranslator(source='ja', target='id')
                for idx, item in enumerate(self.strings):
                    text = item["original"]
                    if len(text.strip()) > 0:
                        try:
                            result = translator.translate(text)
                            self.entries[idx].delete("1.0", "end")
                            self.entries[idx].insert("1.0", result)
                        except: pass
                messagebox.showinfo("Success", "Auto-Translation finished!")
            except Exception as e:
                messagebox.showerror("Translation Error", str(e))
        threading.Thread(target=task).start()

    def save_json(self):
        for idx, entry in enumerate(self.entries):
            self.strings[idx]["translated"] = entry.get("1.0", "end-1c").strip()
            
        out_file = filedialog.asksaveasfilename(defaultextension=".json", initialfile=self.target_file.replace(".bss", ".json"), title="Save Translation JSON")
        if out_file:
            try:
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(self.strings, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Success", f"Translation saved to {os.path.basename(out_file)}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

class BGIExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("BGI Extractor")
        self.geometry("1000x700")
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BGI Extractor", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.logo_sub = ctk.CTkLabel(self.sidebar_frame, text="Translation Toolkit", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
        self.logo_sub.grid(row=1, column=0, padx=20, pady=(0, 30))

        self.btn_viewer = ctk.CTkButton(self.sidebar_frame, text="1. ARC Viewer & Extractor", anchor="w", height=40, command=lambda: self.select_frame("viewer"))
        self.btn_viewer.grid(row=2, column=0, padx=20, pady=10)

        self.btn_json = ctk.CTkButton(self.sidebar_frame, text="2. BSS to JSON", anchor="w", height=40, command=lambda: self.select_frame("json"))
        self.btn_json.grid(row=3, column=0, padx=20, pady=10)

        self.btn_inject = ctk.CTkButton(self.sidebar_frame, text="3. JSON Injector", anchor="w", height=40, command=lambda: self.select_frame("inject"))
        self.btn_inject.grid(row=4, column=0, padx=20, pady=10)
        
        self.btn_pack = ctk.CTkButton(self.sidebar_frame, text="4. ARC Builder", anchor="w", height=40, command=lambda: self.select_frame("pack"))
        self.btn_pack.grid(row=5, column=0, padx=20, pady=10, sticky="n")

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))

        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        self.frames["viewer"] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.setup_viewer(self.frames["viewer"])
        
        self.frames["json"] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.setup_json(self.frames["json"])
        
        self.frames["inject"] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.setup_inject(self.frames["inject"])
        
        self.frames["pack"] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.setup_pack(self.frames["pack"])

        self.log_box = ctk.CTkTextbox(self, height=100, corner_radius=5)
        self.log_box.grid(row=1, column=1, sticky="nsew", padx=20, pady=(0, 20))
        self.log("BGI Extractor system initialized.")

        self.select_frame("viewer")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def select_frame(self, name):
        self.btn_viewer.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "viewer" else "transparent", text_color=["#ffffff", "#ffffff"] if name == "viewer" else ["gray10", "gray90"])
        self.btn_json.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "json" else "transparent", text_color=["#ffffff", "#ffffff"] if name == "json" else ["gray10", "gray90"])
        self.btn_inject.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "inject" else "transparent", text_color=["#ffffff", "#ffffff"] if name == "inject" else ["gray10", "gray90"])
        self.btn_pack.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "pack" else "transparent", text_color=["#ffffff", "#ffffff"] if name == "pack" else ["gray10", "gray90"])

        for frame in self.frames.values():
            frame.grid_forget()
        self.frames[name].grid(row=0, column=0, sticky="nsew")

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

    def setup_viewer(self, frame):
        ctk.CTkLabel(frame, text="ARC Viewer & Extractor", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Analyze archive headers or decrypt BGI assets entirely.", text_color="gray").pack(anchor="w", pady=(0, 20))

        f1 = ctk.CTkFrame(frame, fg_color="transparent")
        f1.pack(fill="x", pady=5)
        self.tv_arc = ctk.CTkEntry(f1, placeholder_text="Path to Target .arc Archive", width=420)
        self.tv_arc.pack(side="left", padx=(0, 10))
        ctk.CTkButton(f1, text="Browse", command=lambda: self.browse_file(self.tv_arc), width=80).pack(side="left")
        ctk.CTkButton(f1, text="View Headers", command=self.view_arc, width=120, fg_color="#4da6ff", hover_color="#2b7ec9", text_color="black").pack(side="right")
        
        self.list_frame = ctk.CTkFrame(frame, height=250)
        self.list_frame.pack(fill="x", pady=15)
        self.list_frame.pack_propagate(False)
        
        # Modern Treeview Styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0, font=("Helvetica", 11))
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", relief="flat", font=("Helvetica", 11, "bold"))
        style.map("Treeview", background=[('selected', '#1f6aa5')])
        
        self.tree = ttk.Treeview(self.list_frame, columns=("size", "name"), show="headings")
        self.tree.heading("size", text="Size")
        self.tree.heading("name", text="File Name")
        self.tree.column("size", width=100, anchor="e")
        self.tree.column("name", width=600, anchor="w")
        
        scrollbar = ctk.CTkScrollbar(self.list_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind('<Double-1>', self.preview_file)
        
        f2 = ctk.CTkFrame(frame, fg_color="transparent")
        f2.pack(fill="x", pady=5)
        self.tv_out = ctk.CTkEntry(f2, placeholder_text="Output Directory for Extraction", width=420)
        self.tv_out.pack(side="left", padx=(0, 10))
        ctk.CTkButton(f2, text="Browse", command=lambda: self.browse_folder(self.tv_out), width=80).pack(side="left")
        
        ctk.CTkButton(frame, text="Extract & Decrypt (Ethornell)", command=self.run_extract, width=200, height=40, font=ctk.CTkFont(weight="bold")).pack(pady=(25, 0))

    def view_arc(self):
        arc_path = self.tv_arc.get()
        if not os.path.exists(arc_path): return messagebox.showerror("Error", "Archive file not found.")
        self.tree.delete(*self.tree.get_children())
        self.arc_files = []
        try:
            with open(arc_path, "rb") as f:
                header = f.read(12)
                if header not in (b"BURIKO ARC20", b"PackFile    "):
                    self.log("Error: Unrecognized BURIKO signature.")
                    return
                file_count = int.from_bytes(f.read(4), "little")
                for _ in range(file_count):
                    name_bytes = f.read(16)
                    name = name_bytes.split(b'\x00')[0].decode('shift_jis', errors='ignore')
                    if header == b"BURIKO ARC20": f.read(80)
                    offset, size = int.from_bytes(f.read(4), "little"), int.from_bytes(f.read(4), "little")
                    if header == b"BURIKO ARC20": f.read(24)
                    else: f.read(8)
                    
                    # Format size cleanly
                    size_str = f"{size} B"
                    if size > 1024*1024: size_str = f"{size/(1024*1024):.2f} MB"
                    elif size > 1024: size_str = f"{size/1024:.2f} KB"
                    
                    self.tree.insert("", "end", values=(size_str, name))
                    self.arc_files.append(name)
        except Exception as e: self.log(f"I/O Error: {str(e)}")
        self.log("Archive scanning complete. Double click a file to preview/edit.")

    def preview_file(self, event):
        selection = self.tree.selection()
        if not selection: return
        item = self.tree.item(selection[0])
        target_file = item['values'][1]
        
        arc_path = self.tv_arc.get()
        import sys
        base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(base_path, "src", "ethornell.exe" if os.name == 'nt' else "ethornell_linux")
        if not os.path.exists(exe_path):
            exe_path = os.path.join(base_path, "ethornell.exe" if os.name == 'nt' else "ethornell_linux")
            
        temp_dir = tempfile.mkdtemp()
        try:
            subprocess.run([exe_path, arc_path, temp_dir, target_file], check=True, stdout=subprocess.DEVNULL)
            extracted_files = os.listdir(temp_dir)
            if not extracted_files:
                messagebox.showerror("Preview Error", "File extraction failed.")
                return
            ext_path = os.path.join(temp_dir, extracted_files[0])
            
            # Interactive Editor for BSS
            if target_file.lower().endswith('.bss'):
                with open(ext_path, "rb") as f:
                    bss_data = f.read()
                editor = TranslationEditor(self, target_file, bss_data)
                editor.focus()
            
            # Image Viewer for graphics
            elif ext_path.lower().endswith(('.png', '.bmp', '.jpg', '.jpeg', '.cbg')):
                prev_win = ctk.CTkToplevel(self)
                prev_win.title(f"Image Viewer - {target_file}")
                prev_win.geometry("800x600")
                img = Image.open(ext_path)
                
                # Maintain aspect ratio in viewer
                img.thumbnail((780, 580))
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                lbl = ctk.CTkLabel(prev_win, image=photo, text="")
                lbl.pack(expand=True, fill="both", padx=10, pady=10)
            
            # Fallback Text Viewer
            else:
                prev_win = ctk.CTkToplevel(self)
                prev_win.title(f"Raw Viewer - {target_file}")
                prev_win.geometry("600x500")
                txt = ctk.CTkTextbox(prev_win, wrap="word", font=("Consolas", 12))
                txt.pack(expand=True, fill="both", padx=10, pady=10)
                try:
                    with open(ext_path, "r", encoding="shift_jis") as f:
                        txt.insert("1.0", f.read())
                except:
                    with open(ext_path, "rb") as f:
                        txt.insert("1.0", str(f.read(3000)) + "\n...[binary truncated]")
                txt.configure(state="disabled")
                
        except Exception as e:
            messagebox.showerror("Preview Error", str(e))

    def run_extract(self):
        arc_file, out_dir = self.tv_arc.get(), self.tv_out.get()
        if not arc_file or not out_dir: return messagebox.showerror("Error", "Directories unassigned.")
        import sys
        base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(base_path, "src", "ethornell.exe" if os.name == 'nt' else "ethornell_linux")
        if not os.path.exists(exe_path):
            exe_path = os.path.join(base_path, "ethornell.exe" if os.name == 'nt' else "ethornell_linux")
        def task():
            self.log(f"Initiating DSC decryption for {os.path.basename(arc_file)}...")
            os.makedirs(out_dir, exist_ok=True)
            try:
                subprocess.run([exe_path, arc_file, out_dir], check=True)
                self.log("Extraction sequence complete.")
            except Exception as e: self.log(f"Extraction halted: {str(e)}")
        threading.Thread(target=task).start()

    def setup_json(self, frame):
        ctk.CTkLabel(frame, text="Bytecode to JSON Compiler", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Isolate text arrays from decompiled .bss engine scripts.", text_color="gray").pack(anchor="w", pady=(0, 20))
        
        self.t2_in = ctk.CTkEntry(frame, placeholder_text="Input Directory (.bss bytecode)", width=480)
        self.t2_in.pack(pady=(20, 5))
        ctk.CTkButton(frame, text="Select Directory", command=lambda: self.browse_folder(self.t2_in)).pack(pady=5)
        
        self.t2_out = ctk.CTkEntry(frame, placeholder_text="Output Directory (.json structures)", width=480)
        self.t2_out.pack(pady=(25, 5))
        ctk.CTkButton(frame, text="Select Directory", command=lambda: self.browse_folder(self.t2_out)).pack(pady=5)
        
        ctk.CTkButton(frame, text="Compile JSON Files", command=self.run_json, width=200, height=40, font=ctk.CTkFont(weight="bold")).pack(pady=(40, 0))

    def run_json(self):
        indir, outdir = self.t2_in.get(), self.t2_out.get()
        if not indir or not outdir: return
        count = 0
        os.makedirs(outdir, exist_ok=True)
        for f in os.listdir(indir):
            bss_file = os.path.join(indir, f)
            if not os.path.isfile(bss_file): continue
            with open(bss_file, "rb") as bf: data = bf.read()
            strings, i = [], 0
            while i < len(data) - 4:
                if data[i:i+4] == b'\x03\x00\x00\x00':
                    start, end = i + 4, i + 4
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
        self.log(f"Compiler executed: Generated {count} data structures.")

    def setup_inject(self, frame):
        ctk.CTkLabel(frame, text="Bytecode Injector", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Embed translated structures into target .bss archives securely.", text_color="gray").pack(anchor="w", pady=(0, 30))
        
        self.t3_bss = ctk.CTkEntry(frame, placeholder_text="Original Bytecode Directory (.bss)", width=420)
        self.t3_bss.pack(pady=2)
        ctk.CTkButton(frame, text="Select Assets", command=lambda: self.browse_folder(self.t3_bss)).pack(pady=(0, 15))
        
        self.t3_json = ctk.CTkEntry(frame, placeholder_text="Translation Directory (.json)", width=420)
        self.t3_json.pack(pady=2)
        ctk.CTkButton(frame, text="Select Assets", command=lambda: self.browse_folder(self.t3_json)).pack(pady=(0, 15))
        
        self.t3_out = ctk.CTkEntry(frame, placeholder_text="Output Directory (Patched Binaries)", width=420)
        self.t3_out.pack(pady=2)
        ctk.CTkButton(frame, text="Select Output", command=lambda: self.browse_folder(self.t3_out)).pack(pady=(0, 20))
        
        ctk.CTkButton(frame, text="Execute Injection Pipeline", command=self.run_inject, width=200, height=40, font=ctk.CTkFont(weight="bold")).pack(pady=10)

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
        self.log(f"Injection sequence completed: {count} assets padded and secured.")

    def setup_pack(self, frame):
        ctk.CTkLabel(frame, text="BURIKO ARC20 Builder", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Compile independent assets into unified engine archives.", text_color="gray").pack(anchor="w", pady=(0, 20))
        
        self.t4_in = ctk.CTkEntry(frame, placeholder_text="Asset Directory (Files to compile)", width=480)
        self.t4_in.pack(pady=(30, 5))
        ctk.CTkButton(frame, text="Select Assets", command=lambda: self.browse_folder(self.t4_in)).pack(pady=(0, 20))
        
        self.t4_out = ctk.CTkEntry(frame, placeholder_text="Compiled Archive Target (.arc)", width=480)
        self.t4_out.pack(pady=5)
        ctk.CTkButton(frame, text="Select Destination", command=lambda: self.browse_file(self.t4_out, save=True, ext=".arc")).pack(pady=(0, 30))
        
        ctk.CTkButton(frame, text="Initialize Build Engine", command=self.run_pack, width=200, height=40, font=ctk.CTkFont(weight="bold")).pack(pady=10)

    def run_pack(self):
        indir, outfile = self.t4_in.get(), self.t4_out.get()
        if not indir or not outfile: return
        self.log("Assembling binary archive structure...")
        files = sorted([os.path.join(indir, f) for f in os.listdir(indir) if os.path.isfile(os.path.join(indir, f))])
        with open(outfile, "wb") as arc_file:
            arc_file.write(b"BURIKO ARC20")
            arc_file.write(len(files).to_bytes(4, "little"))
            data_offset = 16 + (len(files) * 128)
            for file_path in files:
                file_size = os.path.getsize(file_path)
                name_padded = os.path.basename(file_path).encode("shift_jis")[:96].ljust(96, b'\x00')
                arc_file.write(name_padded + data_offset.to_bytes(4, "little") + file_size.to_bytes(4, "little") + b'\x00' * 24)
                data_offset += file_size
            for file_path in files:
                with open(file_path, "rb") as f: arc_file.write(f.read())
        self.log(f"Build executed successfully: {os.path.basename(outfile)}")

if __name__ == "__main__":
    app = BGIExtractorApp()
    app.mainloop()
