import os
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
REMOTES = {
    "enterprise": {
        "url": "https://github.com/yamlr/yamlr-enterprise.git",
        "exclude": [], # Full Repo
        "branch": "main"
    },
    "core": {
        "url": "https://github.com/yamlr/yamlr-core.git",
        "exclude": [
            "src/yamlr/pro",            # OSS Core
            "VISA_STRATEGY.md", "error.log", "*.log"
        ], 
        "branch": "main"
    },
    "public": {
        "url": "https://github.com/yamlr/yamlr.git",
        "exclude": [
            # Enterprise
            "src/yamlr/pro", 
            # Core Logic (The Engine)
            "src/yamlr/core", 
            "src/yamlr/parsers",
            "src/yamlr/analyzers",
            "src/yamlr/ui", 
            "src/yamlr/models.py",
            # Dev Tools
            "tests", 
            "tools",
            # Confidential Specs
            "VISA*.md", "error.log", "*.log"
        ],
        "branch": "main"
    }
}

SCRIPTS_TO_HIDE = ["hack/push_all.py"]

def run_git(args, cwd=None, error_ok=False):
    cmd = ["git"] + args
    print(f"👉 {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0 and not error_ok:
        print(f"❌ Error: {res.stderr}")
        sys.exit(1)
    return res.stdout.strip()

def setup_remotes():
    """Ensures local git has the correct remotes defined."""
    current_remotes = run_git(["remote"]).splitlines()
    for name, config in REMOTES.items():
        if name not in current_remotes:
            print(f"⚠️ Remote '{name}' missing. Adding...")
            run_git(["remote", "add", name, config["url"]])

def push_target(name, config):
    print(f"\n🚀 Processing: {name.upper()}")
    
    # Check dirty
    if run_git(["status", "--porcelain"]):
        print("❌ Git dirty. Commit changes first.")
        sys.exit(1)

    # 1. If Enterprise (Full), just push
    if not config["exclude"]:
        print("📦 Pushing Full Repo...")
        run_git(["push", name, f"HEAD:{config['branch']}"])
        print("✅ Done.")
        return

    # 2. If filtering needed, use temp branch
    current_branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    temp_branch = f"temp-release-{name}"
    
    run_git(["branch", "-D", temp_branch], error_ok=True)
    run_git(["checkout", "-b", temp_branch])
    
    try:
        print("✂️  Pruning files...")
        print("✂️  Pruning files...")
        exclusions = config["exclude"] + SCRIPTS_TO_HIDE
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
    setup_remotes()
    
    # Push in order of importance/completeness
    push_target("enterprise", REMOTES["enterprise"])
    push_target("core", REMOTES["core"])
    push_target("public", REMOTES["public"])
    
    print("\n✨ All repos synced!")

if __name__ == "__main__":
    main()
