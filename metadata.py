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

    n = len(files)
    if len(descs) < n:
        n = len(descs)
        files = files[:n]
    if len(kw_list) < n:
        n = len(kw_list)
        files = files[:n]
        descs = descs[:n]

    used = set()

    for i, src in enumerate(files):
        caption = descs[i]
        keywords = kw_list[i]

        ext = os.path.splitext(src)[1].lower()
        base = sanitize_filename(caption)
        if not base:
            base = sanitize_filename(os.path.splitext(os.path.basename(src))[0])
        base = trim_to_max_length(base, ext, folder)

        name = base + ext
        j = 1
        while name in used or os.path.exists(os.path.join(folder, name)):
            name = f"{base}-{j}{ext}"
            j += 1
        used.add(name)

        dst = os.path.join(folder, name)
        if src != dst:
            try:
                os.rename(src, dst)
                print(f"[OK] Rename: {os.path.basename(src)} -> {name}")
            except Exception as e:
                print(f"[WARN] Gagal rename: {os.path.basename(src)} -> {name} : {e}")
                dst = src
        
        try:
            write_exif_with_argfile(dst, caption, keywords)
            print(f"[INFO] Metadata ditulis: {os.path.basename(dst)}")
        except Exception as e:
            print(f"[FAIL] Gagal tulis metadata: {os.path.basename(dst)}")
            print(f"   Error: {e}")

    print("\n[SUCCESS] Semua selesai diproses.")

if __name__ == "__main__":
    main()
