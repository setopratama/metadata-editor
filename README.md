# Adobe Stock Metadata & Renaming Tool

Tool sederhana berbasis Python untuk mengubah nama file gambar (`.jpg`, `.jpeg`, `.png`) secara otomatis berdasarkan deskripsi produk dan menuliskan metadata (`Caption`, `Title`, `Description`, `Keywords`) langsung ke dalam file menggunakan **exiftool**.

## Fitur Utama
- **Pencarian Rekursif**: Memindai file gambar secara otomatis di folder utama maupun di dalam subfolder (misalnya folder hasil upscaled seperti `upscayl_jpg_...` atau `upscayl_png_...`).
- **Rename & Pindahkan ke Folder Output**: Mengubah nama file gambar menjadi ramah SEO menggunakan deskripsi dari `deskripsi.txt` dan memindahkannya langsung ke subfolder `upload/`.
- **Auto-Cleanup**: Memindahkan secara otomatis file-file hasil rename dari eksekusi sebelumnya di root folder ke dalam subfolder `upload/` untuk menjaga folder kerja tetap rapi.
- **Penulisan Metadata EXIF/IPTC/XMP**: Menyisipkan deskripsi dan kata kunci dari `keyword.txt` ke dalam properti metadata gambar secara otomatis.
- **Rerun Aman (Anti-Duplikasi & Overwrite)**: Jika program dijalankan ulang pada folder yang sama:
  - File yang sudah di-rename di dalam subfolder `upload/` **tidak akan diganti namanya lagi**.
  - **Mencegah duplikasi nama** (tidak membuat file dengan suffix akhiran `-1`, `-2`, dll. kecuali deskripsinya memang sama).
  - **Mencegah penimpaan file** (*overwrite*) yang sudah ada.
  - Memperbarui/memverifikasi metadata untuk file yang sudah diproses secara otomatis di dalam folder `upload/`.

---

## Prasyarat
Sebelum menjalankan tool ini, pastikan sistem Anda telah terinstal:
1. **Python 3.x**
2. **Exiftool**: Tool command-line untuk membaca dan menulis metadata file.
   - Pastikan perintah `exiftool` bisa dijalankan melalui Command Prompt / PowerShell Anda (sudah didaftarkan ke PATH sistem).

---

## Struktur Folder Kerja
Pastikan file-file berikut berada dalam satu direktori yang sama:
```text
folder-kerja/
│
├── metadata.py         # Script utama ini
├── deskripsi.txt       # Berisi daftar deskripsi gambar (satu deskripsi per baris)
├── keyword.txt         # Berisi daftar kata kunci gambar (dipisahkan koma, satu baris per gambar)
│
├── upscayl_jpg_.../    # Folder input gambar (opsional, script memindai secara rekursif)
│   ├── gambar1.jpg
│   └── gambar2.jpg
│
└── upload/             # Folder hasil rename & tag metadata (dibuat otomatis)
    ├── Sad_woman_looking...jpg
    └── ...
```

*Catatan: Jumlah baris pada `deskripsi.txt` dan `keyword.txt` harus berurutan dan sesuai dengan urutan file gambar yang ingin Anda proses.*

---

## Cara Menjalankan

1. Buka terminal (Command Prompt / PowerShell / Terminal).
2. Arahkan ke folder kerja Anda.
3. Jalankan perintah berikut:
   ```bash
   python metadata.py
   ```

---

## Log Eksekusi
- `[OK] Rename: ... -> upload/...`: File berhasil diganti namanya dan dipindahkan ke subfolder `upload/`.
- `[INFO] Memindahkan file ke folder upload: ...`: Memindahkan file yang terlanjur di-rename di root folder ke subfolder `upload/`.
- `[INFO] Metadata ditulis/diperbarui: ...`: Metadata berhasil disuntikkan ke dalam file gambar.
- `[INFO] File sudah diproses sebelumnya: ...`: Menandakan file tersebut dilewati proses rename-nya karena sudah diproses pada eksekusi sebelumnya, lalu metadatanya diperbarui secara otomatis.
