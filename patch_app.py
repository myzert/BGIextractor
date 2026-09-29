import re

with open('/root/Games/BGIextractor/bgie_app.py', 'r') as f:
    content = f.read()

import_replacement = """import os
import json
import struct
import subprocess
import threading
import tempfile
import shutil
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk"""

content = re.sub(r'import os\nimport json\nimport struct\nimport subprocess\nimport threading\nimport customtkinter as ctk\nfrom tkinter import filedialog, messagebox', import_replacement, content)

setup_viewer_code = """
    def setup_viewer(self, frame):
        ctk.CTkLabel(frame, text="ARC Viewer & Extractor", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Analyze archive headers or decrypt BGI assets entirely.", text_color="gray").pack(anchor="w", pady=(0, 20))

        f1 = ctk.CTkFrame(frame, fg_color="transparent")
        f1.pack(fill="x", pady=5)
        self.tv_arc = ctk.CTkEntry(f1, placeholder_text="Path to Target .arc Archive", width=420)
        self.tv_arc.pack(side="left", padx=(0, 10))
        ctk.CTkButton(f1, text="Browse", command=lambda: self.browse_file(self.tv_arc), width=80).pack(side="left")
        ctk.CTkButton(f1, text="View Headers", command=self.view_arc, width=120, fg_color="#4da6ff", hover_color="#2b7ec9", text_color="black").pack(side="right")
        
        self.list_frame = ctk.CTkFrame(frame, height=220)
        self.list_frame.pack(fill="x", pady=15)
        self.list_frame.pack_propagate(False)
        
        self.file_listbox = tk.Listbox(self.list_frame, bg="#1a1a1a", fg="white", selectbackground="#3B8ED0", borderwidth=0, highlightthickness=0, font=("Consolas", 11))
        self.file_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.file_listbox.bind('<Double-1>', self.preview_file)
        
        f2 = ctk.CTkFrame(frame, fg_color="transparent")
        f2.pack(fill="x", pady=5)
        self.tv_out = ctk.CTkEntry(f2, placeholder_text="Output Directory for Extraction", width=420)
        self.tv_out.pack(side="left", padx=(0, 10))
        ctk.CTkButton(f2, text="Browse", command=lambda: self.browse_folder(self.tv_out), width=80).pack(side="left")
        
        ctk.CTkButton(frame, text="Extract & Decrypt (Ethornell)", command=self.run_extract, width=200, height=40, font=ctk.CTkFont(weight="bold")).pack(pady=(25, 0))

    def view_arc(self):
        arc_path = self.tv_arc.get()
        if not os.path.exists(arc_path): return messagebox.showerror("Error", "Archive file not found.")
        self.file_listbox.delete(0, 'end')
        self.arc_files = []
        try:
            with open(arc_path, "rb") as f:
                header = f.read(12)
                if header not in (b"BURIKO ARC20", b"PackFile    "):
                    self.file_listbox.insert("end", "Error: Unrecognized BURIKO signature.")
                    return
                file_count = int.from_bytes(f.read(4), "little")
                for _ in range(file_count):
                    name_bytes = f.read(16)
                    name = name_bytes.split(b'\\x00')[0].decode('shift_jis', errors='ignore')
                    if header == b"BURIKO ARC20": f.read(80)
                    offset, size = int.from_bytes(f.read(4), "little"), int.from_bytes(f.read(4), "little")
                    if header == b"BURIKO ARC20": f.read(24)
                    else: f.read(8)
                    self.file_listbox.insert("end", f"[{size} B] {name}")
                    self.arc_files.append(name)
        except Exception as e: self.file_listbox.insert("end", f"I/O Error: {str(e)}")
        self.log("Archive scanning complete. Double click a file to preview.")

    def preview_file(self, event):
        selection = self.file_listbox.curselection()
        if not selection: return
        idx = selection[0]
        if idx >= len(self.arc_files): return
        target_file = self.arc_files[idx]
        
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
            
            prev_win = ctk.CTkToplevel(self)
            prev_win.title(f"Preview: {target_file}")
            prev_win.geometry("600x500")
            
            if ext_path.lower().endswith(('.png', '.bmp', '.jpg', '.jpeg')):
                img = Image.open(ext_path)
                img.thumbnail((580, 480))
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                lbl = ctk.CTkLabel(prev_win, image=photo, text="")
                lbl.pack(expand=True, fill="both", padx=10, pady=10)
            else:
                txt = ctk.CTkTextbox(prev_win, wrap="word")
                txt.pack(expand=True, fill="both", padx=10, pady=10)
                try:
                    with open(ext_path, "r", encoding="shift_jis") as f:
                        txt.insert("1.0", f.read())
                except:
                    with open(ext_path, "rb") as f:
                        txt.insert("1.0", str(f.read(2000)))
                txt.configure(state="disabled")
                
        except Exception as e:
            messagebox.showerror("Preview Error", str(e))
"""

# Extract everything before setup_viewer
before_setup_viewer = content[:content.find("    def setup_viewer")]
# Extract everything after run_extract (including run_extract)
after_view_arc = content[content.find("    def run_extract"):]

content = before_setup_viewer + setup_viewer_code + "\n" + after_view_arc

with open('/root/Games/BGIextractor/bgie_app.py', 'w') as f:
    f.write(content)
