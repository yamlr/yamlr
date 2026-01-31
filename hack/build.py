#!/usr/bin/env python3
"""
3. YAMLR BUILD SYSTEM (Cross-Platform)
---------------------------------------
Zero-config build script for Windows, Linux, and macOS.
Builds:
1. Standalone Binary (dist/yamlr[.exe])

Future-Proofing:
- Auto-installs dependencies from pyproject.toml
- Auto-detects OS and path separators
- Dynamically includes all catalog/*.json files
"""

import sys
import os
import shutil
import subprocess
import glob
from pathlib import Path
import venv

# Configuration
APP_NAME = "yamlr"
ENTRY_POINT = "src/yamlr/cli/main.py"
BUILD_DIR = Path("build")
DIST_DIR = Path("dist")
VENV_DIR = Path(".venv_build")

def print_header():
    print(r"""
    🧬 Yamlr Build System
    --------------------------------------""")

def print_step(msg):
    print(f"👉 {msg}...", end=" ", flush=True)

def print_done():
    print("\033[1;32m[DONE]\033[0m")

def print_skip():
    print("\033[1;33m[SKIPPED]\033[0m")

def fail(msg):
    print(f"\n\033[1;31m[ERROR] {msg}\033[0m")
    sys.exit(1)

def run_quiet(cmd, env=None, cwd=None):
    """Runs a command silently, capturing output to display only on error."""
    try:
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            env=env, 
            cwd=cwd, 
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"\n\033[1;31m[FAILED]\033[0m")
        print("--------------------------------------------------")
        print(e.stdout)  # Print the captured output
        print("--------------------------------------------------")
        fail(f"Command failed: {' '.join(cmd)}")

def install_binary(src_path: Path):
    """Installs binary to a common system path if possible."""
    # Priority paths for Linux/Mac
    # 1. System: /usr/local/bin (Needs sudo/root)
    # 2. User: ~/.local/bin (Safe fallback, creates if missing)
    
    system_path = Path("/usr/local/bin")
    user_path = Path.home() / ".local" / "bin"
    
    target_dir = None
    
    if sys.platform == "win32":
        return None

    # Check System Path (Preferred)
    if system_path.exists() and os.access(system_path, os.W_OK):
        target_dir = system_path
    else:
        # Fallback to User Path
        if not user_path.exists():
            try:
                user_path.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass # Can't create, likely permission or read-only
        
        if user_path.exists() and os.access(user_path, os.W_OK):
            target_dir = user_path

    if target_dir:
        try:
            dest = target_dir / src_path.name
            shutil.copy2(src_path, dest)
            
            # Check if in PATH
            path_dirs = os.environ.get("PATH", "").split(os.pathsep)
            if str(target_dir) not in path_dirs:
                print(f"\n⚠️  Warning: {target_dir} is not in your PATH.")
                
            return dest
        except Exception as e:
            print(f"Install failed: {e}")
            return None
    return None

def main():
    root_dir = Path(__file__).parent.resolve()
    os.chdir(root_dir)

    print_header()

    # 1. Cleanup
    print_step("Cleaning previous build artifacts")
    if BUILD_DIR.exists(): shutil.rmtree(BUILD_DIR)
    if DIST_DIR.exists(): shutil.rmtree(DIST_DIR)
    for p in glob.glob("*.spec"): os.remove(p)
    print_done()

    # 2. Virtual Environment
    print_step(f"Setting up build environment in {VENV_DIR}")
    if not VENV_DIR.exists():
        venv.create(VENV_DIR, with_pip=True)
    print_done()
    
    # Determine executables
    if sys.platform == "win32":
        python_exe = VENV_DIR / "Scripts" / "python.exe"
        pyinstaller_exe = VENV_DIR / "Scripts" / "pyinstaller.exe"
        bin_ext = ".exe"
        path_sep = ";"
    else:
        python_exe = VENV_DIR / "bin" / "python"
        pyinstaller_exe = VENV_DIR / "bin" / "pyinstaller"
        bin_ext = ""
        path_sep = ":"

    # 3. Install Dependencies
    print_step("Installing dependencies (pip)")
    run_quiet([str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "pyinstaller"])
    run_quiet([str(python_exe), "-m", "pip", "install", "."])
    print_done()

    # 4. Configure Assets
    catalog_path = root_dir / "catalog"
    assets = []
    if catalog_path.exists():
        assets.append(f"{catalog_path}{path_sep}yamlr/catalog")
    
    # 5. Build Binary
    print_step(f"Compiling {APP_NAME}{bin_ext}")
    
    cmd = [
        str(pyinstaller_exe),
        "--log-level", "ERROR",  # Silence PyInstaller
        "--noconfirm",
        "--onefile",
        "--clean",
        "--name", APP_NAME,
        "--strip",
        "--paths", str(root_dir / "src"),
        "--hidden-import", "yamlr.core.io",
        "--hidden-import", "yamlr.core.pipeline",
        "--hidden-import", "yamlr.analyzers.cross_resource",
        "--collect-all", "rich",
    ]
    
    for asset in assets:
        cmd.extend(["--add-data", asset])
        
    cmd.append(str(root_dir / ENTRY_POINT))
    
    run_quiet(cmd)
    print_done()

    # 6. Create Alias (REMOVED for clean refactor)
    # print_step(f"Creating alias {ALIAS_NAME}{bin_ext}")
    # src_bin = DIST_DIR / f"{APP_NAME}{bin_ext}"
    # dest_bin = DIST_DIR / f"{ALIAS_NAME}{bin_ext}"
    
    # if not src_bin.exists():
    #      print("\n")
    #      fail("Build failed - binary not found!")

    # shutil.copy2(src_bin, dest_bin)
    # print_done()
    
    # 7. Installation (Linux/Mac)
    installed_paths = []
    if sys.platform != "win32":
        print_step("Installing to System Path")
        p1 = install_binary(src_bin)
        # p2 = install_binary(dest_bin)
        
        if p1:
            installed_paths = [p1]
            print_done()
        else:
            print_skip()
            
    # 8. Summary
    size_mb = src_bin.stat().st_size / (1024 * 1024)
    print("-" * 38)
    print("\033[1;32m✅ Build & Deployment Complete!\033[0m")
    print(f"📦 Final Size: {size_mb:.2f} MB")
    
    if installed_paths:
        print(f"🚀 Installed to: {installed_paths[0].parent}")
        print(f"   Commands: {APP_NAME}")
    else:
        print(f"📍 Artifacts: {src_bin.relative_to(root_dir)}")
    print("-" * 38)

if __name__ == "__main__":
    main()
