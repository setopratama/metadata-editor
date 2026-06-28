import os
import sys
import glob
import re
import subprocess
import tempfile

MAX_PATH_LENGTH = 240

def sanitize_filename(name):
    # Match Go's regexp.MustCompile(`[<>:"/\\|?*]`)
    clean = re.sub(r'[<>:"/\\|?*]', '', name)
    clean = clean.strip()
    clean = clean.rstrip(' .')
    return clean

def trim_to_max_length(base, ext, folder):
    full = os.path.join(folder, base + ext)
    if len(full) > MAX_PATH_LENGTH:
        # Go code logic: avail := maxPathLength - len(folder) - len(ext) - 1
        avail = MAX_PATH_LENGTH - len(folder) - len(ext) - 1
        if avail < 10:
            avail = 10
        if len(base) > avail:
            base = base[:avail] + "…"
    return base

def is_file_matching_desc(f_path, desc, folder):
    f_base, f_ext = os.path.splitext(os.path.basename(f_path))
    target_base = sanitize_filename(desc)
    if not target_base:
        return False
    trimmed_base = trim_to_max_length(target_base, f_ext, folder)
    if f_base == trimmed_base:
        return True
    pattern = r"^" + re.escape(trimmed_base) + r"-\d+$"
    if re.match(pattern, f_base):
        return True
    return False

def write_exif_with_argfile(file_path, caption, keywords):
    # Write to a temporary arg file
    fd, tmp_arg_file = tempfile.mkstemp(suffix="_exif_args.txt", text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write("-overwrite_original_in_place\n")
            f.write(f"-IPTC:Caption-Abstract={caption}\n")
            f.write(f"-XMP:Title={caption}\n")
            f.write(f"-XMP:Description={caption}\n")
            f.write(f"-EXIF:ImageDescription={caption}\n")
            f.write(f"-EXIF:XPTitle={caption}\n")
            for kw in keywords:
                if kw:
                    f.write(f"-IPTC:Keywords={kw}\n")
                    f.write(f"-XMP:Subject={kw}\n")
            f.write(f"{file_path}\n")

        # Execute exiftool
        cmd = ["exiftool", "-@", tmp_arg_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"exiftool failed: {result.stderr or result.stdout}")
    finally:
        try:
            os.remove(tmp_arg_file)
        except OSError:
            pass

def main():
    folder = os.getcwd()
    print("Working folder:", folder)

    # Find matching files
    files = []
    # Support jpg, jpeg, png (case-insensitive)
    patterns = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]
    for pat in patterns:
        files.extend(glob.glob(os.path.join(folder, pat)))
    
    # Remove duplicates and sort
    files = sorted(list(set(files)))
    
    if not files:
        print("[FAIL] Tidak ada file JPG/JPEG/PNG.")
        return

    desc_path = os.path.join(folder, "deskripsi.txt")
    if not os.path.exists(desc_path):
        print("[FAIL] Gagal buka deskripsi.txt: File tidak ditemukan")
        return

    descs = []
    with open(desc_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                descs.append(line_str)

    kw_path = os.path.join(folder, "keyword.txt")
    if not os.path.exists(kw_path):
        print("[FAIL] Gagal buka keyword.txt: File tidak ditemukan")
        return

    kw_list = []
    with open(kw_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                kw = [k.strip() for k in line_str.split(",")]
                kw_list.append(kw)

    # 1. Pasangkan deskripsi dan kata kunci berdasarkan indeks baris asli
    desc_keyword_pairs = list(zip(descs, kw_list))
    
    processed_files = set()
    used_desc_indices = set()
    
    # 2. Deteksi file yang sudah diproses di folder
    for idx, (caption, keywords) in enumerate(desc_keyword_pairs):
        # Cari file di folder yang namanya cocok dengan deskripsi ini
        for file_path in files:
            if file_path in processed_files:
                continue
            if is_file_matching_desc(file_path, caption, folder):
                processed_files.add(file_path)
                used_desc_indices.add(idx)
                print(f"[INFO] File sudah diproses sebelumnya: {os.path.basename(file_path)} (Indeks deskripsi ke-{idx+1})")
                # Tulis ulang/pastikan metadata tetap ter-update
                try:
                    write_exif_with_argfile(file_path, caption, keywords)
                    print(f"[INFO] Metadata diperbarui: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"[WARN] Gagal memperbarui metadata: {os.path.basename(file_path)} : {e}")
                break

    # 3. Kumpulkan file yang belum diproses dan deskripsi yang belum digunakan
    unprocessed_files = [f for f in files if f not in processed_files]
    unused_desc_indices = [idx for idx in range(len(desc_keyword_pairs)) if idx not in used_desc_indices]

    n_unprocessed = len(unprocessed_files)
    n_unused = len(unused_desc_indices)
    n_process = min(n_unprocessed, n_unused)
    
    files_to_process = unprocessed_files[:n_process]
    descs_to_use_indices = unused_desc_indices[:n_process]
    
    # Kumpulkan nama file saat ini di folder untuk menghindari tabrakan penamaan baru
    current_names_in_folder = set(os.listdir(folder))
    
    # 4. Proses file yang belum diproses
    for i, src in enumerate(files_to_process):
        desc_idx = descs_to_use_indices[i]
        caption, keywords = desc_keyword_pairs[desc_idx]
        
        ext = os.path.splitext(src)[1].lower()
        base = sanitize_filename(caption)
        if not base:
            base = sanitize_filename(os.path.splitext(os.path.basename(src))[0])
        base = trim_to_max_length(base, ext, folder)
        
        name = base + ext
        j = 1
        while name in current_names_in_folder:
            name = f"{base}-{j}{ext}"
            j += 1
            
        current_names_in_folder.add(name)
        dst = os.path.join(folder, name)
        
        try:
            os.rename(src, dst)
            print(f"[OK] Rename: {os.path.basename(src)} -> {name}")
            write_exif_with_argfile(dst, caption, keywords)
            print(f"[INFO] Metadata ditulis: {name}")
        except Exception as e:
            print(f"[FAIL] Gagal memproses {os.path.basename(src)}: {e}")

    print("\n[SUCCESS] Semua selesai diproses.")

if __name__ == "__main__":
    main()
