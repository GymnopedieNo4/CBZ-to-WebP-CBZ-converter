# CBZ to WebP/JPG CBZ Converter
Multithreaded ZIP/CBZ to ZIP/CBZ converter that converts the image files archived inside it to WebP/JPEG.
Supports recursive conversion until acceptable compression size is achieved.
Caveat: It will ruins any folder & subfolders structure/directory inside the Zip file into simplistic `root/image_files.ext` format.

## Requirements
* Python 3
* Pillow / Python Imaging Libraries package installed

## How to Use
1. Select the script according to your desired image format; `CBZ to JPG converter.py' for JPEG output & `CBZ to WEBP converter.py` for WEBP output.
2. Open the `.py` file with your text editor & tweak the ALL-CAPS parameters defined on the first few lines according to your needs.
3. Run the script or open it in your terminal/command shell.
4. Drag & drop or copy paste the INPUT path containing the `.cbz` or `.zip` files (including subfolders too).
5. Drag & drop or copy paste the OUTPUT path for it to saves the resulting `.cbz` or `.zip` files (will replicate the subfolders structure too).
6. Drag & drop or copy paste the TEMP path, an empty folder temporarily used for processing the files.

### *Multithreading... on Python?*
Sounds asinine but I did saw noticeable improvements from 17.94 sec (1-thread) to 12.43 sec (2-thread) to 8.36 (4-thread) on my dual-core 4-thread CPU.
