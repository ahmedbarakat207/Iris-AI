#!/usr/bin/env python3
"""
Generate multi-platform icon assets for Electron and electron-builder
from the high-resolution images in the logo/ directory.

Outputs:
  - build/icon.icns (macOS)
  - build/icon.ico  (Windows)
  - build/icon.png  (Linux / Web / Electron default 512x512)
  - build/icons/<size>x<size>.png (Linux desktop icons)
"""

import os
import sys
import shutil
import subprocess
from PIL import Image

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_dir = os.path.join(root_dir, "logo")
    build_dir = os.path.join(root_dir, "build")
    icons_dir = os.path.join(build_dir, "icons")
    
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(icons_dir, exist_ok=True)
    
    # Preferred source logo (logo3.png or logo1.png)
    src_logo = os.path.join(logo_dir, "logo3.png")
    if not os.path.exists(src_logo):
        src_logo = os.path.join(logo_dir, "logo1.png")
    if not os.path.exists(src_logo):
        src_logo = os.path.join(logo_dir, "logo-dark.png")
    
    print(f"[Icon Generator] Using source logo: {src_logo}")
    img = Image.open(src_logo).convert("RGBA")
    
    # 1. Generate standard Linux / Electron main PNG icon (512x512)
    png_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    png_512_path = os.path.join(build_dir, "icon.png")
    png_512.save(png_512_path, format="PNG")
    print(f"[Icon Generator] Saved {png_512_path}")
    
    # 2. Generate Linux resolution icons in build/icons/
    linux_sizes = [16, 24, 32, 48, 64, 96, 128, 256, 512, 1024]
    for s in linux_sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        out_path = os.path.join(icons_dir, f"{s}x{s}.png")
        resized.save(out_path, format="PNG")
    print(f"[Icon Generator] Saved {len(linux_sizes)} Linux icons to {icons_dir}")
    
    # 3. Generate Windows ICO file (multi-resolution)
    ico_path = os.path.join(build_dir, "icon.ico")
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=ico_sizes)
    print(f"[Icon Generator] Saved Windows icon: {ico_path}")
    
    # 4. Generate macOS ICNS file
    icns_path = os.path.join(build_dir, "icon.icns")
    iconset_dir = os.path.join(build_dir, "icon.iconset")
    
    # Try iconutil on macOS first if available
    has_iconutil = shutil.which("iconutil") is not None
    if has_iconutil:
        os.makedirs(iconset_dir, exist_ok=True)
        mac_iconset = {
            "icon_16x16.png": 16,
            "icon_16x16@2x.png": 32,
            "icon_32x32.png": 32,
            "icon_32x32@2x.png": 64,
            "icon_128x128.png": 128,
            "icon_128x128@2x.png": 256,
            "icon_256x256.png": 256,
            "icon_256x256@2x.png": 512,
            "icon_512x512.png": 512,
            "icon_512x512@2x.png": 1024,
        }
        for name, size in mac_iconset.items():
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(os.path.join(iconset_dir, name), format="PNG")
            
        try:
            res = subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], check=True)
            print(f"[Icon Generator] Successfully generated macOS ICNS via iconutil: {icns_path}")
            shutil.rmtree(iconset_dir, ignore_errors=True)
        except Exception as e:
            print(f"[Icon Generator] Warning: iconutil failed: {e}")
    
    # Fallback to Pillow ICNS if iconutil was not used or failed
    if not os.path.exists(icns_path):
        try:
            img.save(icns_path, format="ICNS")
            print(f"[Icon Generator] Saved macOS ICNS via PIL: {icns_path}")
        except Exception as e:
            print(f"[Icon Generator] Could not save ICNS via PIL: {e}")
            
    print("[Icon Generator] All platform icons successfully generated!")

if __name__ == "__main__":
    main()
