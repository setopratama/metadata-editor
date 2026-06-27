# Metadata Editor & Image Renamer (Python Version)

Python utility to batch rename image files (JPG, JPEG, PNG) based on descriptions and embed IPTC/XMP/EXIF metadata (Caption and Keywords) using ExifTool.

## Features

- **Multi-Format Support**: Processes `.jpg`, `.jpeg`, and `.png` images (case-insensitive).
- **Auto-Rename**: Renames images based on text descriptions from `deskripsi.txt`, sanitizing invalid filesystem characters and limiting path lengths to 240 characters.
- **Collision Resolution**: Detects naming duplicates and appends sequential markers (`-1`, `-2`, etc.) to prevent overwriting existing files.
- **ExifTool Integration**: Writes Caption/Abstract, Title, Description, and Keywords to EXIF, IPTC, and XMP metadata fields.
- **Zero Python Dependencies**: Works using only Python 3 built-in modules (`os`, `sys`, `subprocess`, `tempfile`, etc.).

## Prerequisites

1. **Python 3.x**
2. **ExifTool**: Ensure `exiftool` is installed on your system and is accessible via your environment path (`PATH`).
   - *Windows users*: You can extract the `exiftool.exe` binary and place it in a folder added to your system environment variables, or keep it in the same directory as this script.

## Setup & File Structure

Place the following files in your working directory:
- `metadata.py` (the Python script)
- `deskripsi.txt` (contains image descriptions, one description per line)
- `keyword.txt` (contains tags/keywords for each image, comma-separated on each line)
- Your target image files (`.jpg`, `.jpeg`, `.png`)

Example structure:
```text
your-folder/
├── deskripsi.txt
├── keyword.txt
├── metadata.py
├── image1.png
└── image2.jpg
```

## How to Run

1. Open your terminal/command prompt.
2. Navigate to your working directory.
3. Run the script:
   ```bash
   python metadata.py
   ```
