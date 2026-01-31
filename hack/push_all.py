import os
import subprocess
import sys
import yaml
from pathlib import Path

# --- Configuration ---
CONFIG_FILE = Path(__file__).parent / "sync_config.yaml"

def load_config():
    if not CONFIG_FILE.exists():
        print(f"❌ Config file not found: {CONFIG_FILE}")
        sys.exit(1)
    
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)

def run_git(args, cwd=None, error_ok=False):
    cmd = ["git"] + args
    print(f"👉 {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0 and not error_ok:
        print(f"❌ Error: {res.stderr}")
        sys.exit(1)
    return res.stdout.strip()

def setup_remotes(remotes):
    """Ensures local git has the correct remotes defined."""
    current_remotes = run_git(["remote"]).splitlines()
    for name, config in remotes.items():
        if name not in current_remotes:
            print(f"⚠️ Remote '{name}' missing. Adding...")
            run_git(["remote", "add", name, config["url"]])

def push_target(name, config, items_to_hide):
    print(f"\n🚀 Processing: {name.upper()}")
    
    # Check dirty
    if run_git(["status", "--porcelain"]):
        print("❌ Git dirty. Commit changes first.")
        sys.exit(1)

    # 1. If Enterprise (Full), just push
    if not config.get("exclude"):
        print("📦 Pushing Full Repo...")
        run_git(["push", name, f"HEAD:{config['branch']}"])
        print("✅ Done.")
        return

    # 2. If filtering needed, use temp branch
    current_branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    temp_branch = f"temp-release-{name}"
    
    # Clean up previous runs if any
    run_git(["branch", "-D", temp_branch], error_ok=True)
    
    # Create temp branch
    run_git(["checkout", "-b", temp_branch])
    
    try:
        print("✂️  Pruning files...")
        exclusions = config.get("exclude", []) + items_to_hide
        for path_pattern in exclusions:
            # Always try to remove, let git handle existence checks via --ignore-unmatch
            # We pass the pattern directly to git to handle globs (e.g. *.log)
            run_git(["rm", "-r", "--cached", "--ignore-unmatch", path_pattern], error_ok=True)
        
        run_git(["commit", "-m", f"RELEASE: Automatic Sync to {name.upper()}"])
        
        print(f"📤 Pushing filtered branch to {name}...")
        run_git(["push", "--force", name, f"{temp_branch}:{config['branch']}"])
        print("✅ Done.")
        
    finally:
        run_git(["checkout", "-f", current_branch])
        run_git(["branch", "-D", temp_branch], error_ok=True)

def main():
    root_dir = Path(__file__).parent.parent.resolve()
    os.chdir(root_dir)
    
    print("🔄 Yamlr Multi-Repo Sync")
    
    config = load_config()
    remotes = config.get("remotes", {})
    items_to_hide = config.get("items_to_hide", [])

    setup_remotes(remotes)
    
    # Push in order of importance/completeness
    # We explicitly define order to ensure Enterprise is first
    priority_order = ["enterprise", "core", "public"]
    
    for key in priority_order:
        if key in remotes:
            push_target(key, remotes[key], items_to_hide)
    
    print("\n✨ All repos synced!")

if __name__ == "__main__":
    main()
