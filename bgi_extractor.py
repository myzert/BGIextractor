import os
import struct

def extract_arc(arc_path, out_dir):
    with open(arc_path, "rb") as f:
        header = f.read(12)
        if header != b"BURIKO ARC20" and header != b"PackFile    ":
            return False
            
        file_count = int.from_bytes(f.read(4), "little")
        files = []
        
        for _ in range(file_count):
            name_bytes = f.read(16)
            name = name_bytes.split(b'\x00')[0].decode('shift_jis', errors='ignore')
            
            # Skip padding if BURIKO ARC20 (which is version 2)
            if header == b"BURIKO ARC20":
                f.read(80) # 20 * 4 padding
                
            offset = int.from_bytes(f.read(4), "little")
            size = int.from_bytes(f.read(4), "little")
            
            if header == b"BURIKO ARC20":
                f.read(24) # 6 * 4 padding
            else:
                f.read(8) # v1 padding
                
            files.append((name, offset, size))
            
        data_start = f.tell()
        os.makedirs(out_dir, exist_ok=True)
        
        for name, offset, size in files:
            f.seek(data_start + offset)
            data = f.read(size)
            
            # Simple check if it's DSC encoded
            is_dsc = data.startswith(b"DSC FORMAT 1.00")
            
            out_path = os.path.join(out_dir, name)
            with open(out_path, "wb") as out_f:
                out_f.write(data)
                
    return True
