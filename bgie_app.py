import os
import json
import struct
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class BGIExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("BGI Extractor")
        self.geometry("950x650")
        self.resizable(False, False)

        # ---------------- GRID LAYOUT ----------------
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ---------------- SIDEBAR ----------------
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

        # ---------------- MAIN CONTENT ----------------
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Frame Dictionary
        self.frames = {}
        
        # 1. Viewer Frame
        self.frames["viewer"] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.setup_viewer(self.frames["viewer"])
        
        # 2. JSON Frame
        self.frames["json"] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.setup_json(self.frames["json"])
        
        # 3. Inject Frame
        self.frames["inject"] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.setup_inject(self.frames["inject"])
        
        # 4. Pack Frame
        self.frames["pack"] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.setup_pack(self.frames["pack"])

        # ---------------- LOG BOX ----------------
        self.log_box = ctk.CTkTextbox(self, height=100, corner_radius=5)
        self.log_box.grid(row=1, column=1, sticky="nsew", padx=20, pady=(0, 20))
        self.log("BGI Extractor system initialized.")

        # Default frame
        self.select_frame("viewer")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def select_frame(self, name):
        # Reset buttons
        self.btn_viewer.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "viewer" else "transparent", text_color=["#ffffff", "#ffffff"] if name == "viewer" else ["gray10", "gray90"])
        self.btn_json.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "json" else "transparent", text_color=["#ffffff", "#ffffff"] if name == "json" else ["gray10", "gray90"])
        self.btn_inject.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "inject" else "transparent", text_color=["#ffffff", "#ffffff"] if name == "inject" else ["gray10", "gray90"])
        self.btn_pack.configure(fg_color=["#3B8ED0", "#1F6AA5"] if name == "pack" else "transparent", text_color=["#ffffff", "#ffffff"] if name == "pack" else ["gray10", "gray90"])

        # Show frame
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

    # ---------------- TAB SETUP ----------------

    def setup_viewer(self, frame):
        ctk.CTkLabel(frame, text="ARC Viewer & Extractor", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Analyze archive headers or decrypt BGI assets entirely.", text_color="gray").pack(anchor="w", pady=(0, 20))

        f1 = ctk.CTkFrame(frame, fg_color="transparent")
        f1.pack(fill="x", pady=5)
        self.tv_arc = ctk.CTkEntry(f1, placeholder_text="Path to Target .arc Archive", width=420)
        self.tv_arc.pack(side="left", padx=(0, 10))
        ctk.CTkButton(f1, text="Browse", command=lambda: self.browse_file(self.tv_arc), width=80).pack(side="left")
        ctk.CTkButton(f1, text="View Headers", command=self.view_arc, width=120, fg_color="#4da6ff", hover_color="#2b7ec9", text_color="black").pack(side="right")
        
        self.file_list = ctk.CTkTextbox(frame, height=220, state="disabled")
        self.file_list.pack(fill="x", pady=15)
        
        f2 = ctk.CTkFrame(frame, fg_color="transparent")
        f2.pack(fill="x", pady=5)
        self.tv_out = ctk.CTkEntry(f2, placeholder_text="Output Directory for Extraction", width=420)
        self.tv_out.pack(side="left", padx=(0, 10))
        ctk.CTkButton(f2, text="Browse", command=lambda: self.browse_folder(self.tv_out), width=80).pack(side="left")
        
        ctk.CTkButton(frame, text="Extract & Decrypt (Ethornell)", command=self.run_extract, width=200, height=40, font=ctk.CTkFont(weight="bold")).pack(pady=(25, 0))

    def view_arc(self):
        arc_path = self.tv_arc.get()
        if not os.path.exists(arc_path): return messagebox.showerror("Error", "Archive file not found.")
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")
        try:
            with open(arc_path, "rb") as f:
                header = f.read(12)
                if header not in (b"BURIKO ARC20", b"PackFile    "):
                    self.file_list.insert("end", "Error: Unrecognized BURIKO signature.")
                    self.file_list.configure(state="disabled")
                    return
                file_count = int.from_bytes(f.read(4), "little")
                self.file_list.insert("end", f"[ARCHIVE METADATA]\nSignature: {header.decode('utf-8', 'ignore')}\nFiles Detected: {file_count}\n\n")
                for _ in range(min(file_count, 1000)):
                    name_bytes = f.read(16)
                    name = name_bytes.split(b'\x00')[0].decode('shift_jis', errors='ignore')
                    if header == b"BURIKO ARC20": f.read(80)
                    offset, size = int.from_bytes(f.read(4), "little"), int.from_bytes(f.read(4), "little")
                    if header == b"BURIKO ARC20": f.read(24)
                    else: f.read(8)
                    self.file_list.insert("end", f"{name.ljust(35)} | Size: {size} bytes\n")
                if file_count > 1000: self.file_list.insert("end", f"\n... [{file_count - 1000} additional entries hidden] ...\n")
        except Exception as e: self.file_list.insert("end", f"I/O Error: {str(e)}")
        self.file_list.configure(state="disabled")
        self.log("Archive scanning complete.")

    def run_extract(self):
        arc_file, out_dir = self.tv_arc.get(), self.tv_out.get()
        if not arc_file or not out_dir: return messagebox.showerror("Error", "Directories unassigned.")
        exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ethornell.exe" if os.name == 'nt' else "./ethornell_linux")
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
        def is_dialog(text):
            import re
            if len(text) < 5 or ".bss" in text or ".mpg" in text or text.isupper(): return False
            if "_" in text and " " not in text: return False
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
            data_offset = 0
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
