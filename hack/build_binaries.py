import subprocess
import sys
import os
import shutil
import platform

def main():
    print("📦 Yamlr Binary Builder")
    
    # 1. Install PyInstaller if missing
    try:
        import PyInstaller
    except ImportError:
        print("⬇️  Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Configure Paths
    base_dir = os.path.abspath(os.curdir)
    src_data = os.path.join(base_dir, "src", "yamlr", "core", "data")
    
    # Windows uses ';', Linux/Mac uses ':'
    sep = ";" if os.name == 'nt' else ":"
    
    # Destination inside the bundle must match package structure
    dst_data = os.path.join("yamlr", "core", "data")
    
    add_data_arg = f"{src_data}{sep}{dst_data}"
    
    # 3. Build Command
    # We target src/yamlr/__main__.py as the entry point
    cmd = [
        "pyinstaller",
        "--name=yamlr",
        "--onefile",            # Single .exe file
        "--clean",              # content cache cleanup
        "--noconfirm",          # overwrite output directory
        "--exclude-module=yamlr.pro", # Ensure checks fail cleanly
        "--collect-all=rich",   # Fix: 'rich' missing unicode tables
        f"--add-data={add_data_arg}",
        f"--add-data=catalog{sep}Yamlr/catalog", # Fix: Bundle catalogs
        os.path.join("src", "yamlr", "__main__.py")
    ]
    
    print(f"🔨 Executing: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\n✅ Build Successful!")
        print(f"🚀 Binary location: dist/yamlr{'.exe' if os.name == 'nt' else ''}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
