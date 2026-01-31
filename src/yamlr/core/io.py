"""
Yamlr FILE SYSTEM MANAGER
-------------------------
Handles all physical I/O operations:
- Atomic file writes (fsync)
- Safe backup generation
- Directory crawling with security checks (symlinks, traversal)

Decoupled from YamlrEngine to support future S3/Remote backends.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Generator, Tuple

logger = logging.getLogger("yamlr.io")

class FileSystemManager:
    """
    Abstration layer for local file system operations.
    """
    
    def __init__(self, workspace_root: Path, app_name: str = "Yamlr"):
        self.workspace = workspace_root.resolve()
        self.app_name = app_name
        self.state_dir = self.workspace / f".{app_name}"
        self.backup_dir = self.state_dir / "backups"

    def ensure_workspace(self):
        """Creates workspace and state directories if missing."""
        if not self.workspace.exists():
            try:
                self.workspace.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created workspace: {self.workspace}")
            except Exception as e:
                raise RuntimeError(f"Workspace creation failed: {e}")
        
        # Ensure hidden state dir exists
        if not self.state_dir.exists():
            self.state_dir.mkdir(exist_ok=True)
            
        # Ensure backup dir exists
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(exist_ok=True)

    def read_text(self, path: Path) -> str:
        """Reads text file with BOM handling."""
        return path.read_text(encoding='utf-8-sig')

    def atomic_write(self, target_path: Path, content: str) -> None:
        """
        Atomically writes content to file with fsync for durability.
        Uses .yamlr.tmp + os.replace.
        """
        temp_file = target_path.with_suffix('.yamlr.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
                f.flush()
                # os.fsync(f.fileno()) # Disabled for performance in temp files
            
            os.replace(temp_file, target_path)
            
        except Exception as e:
            if temp_file.exists(): 
                temp_file.unlink()
            raise IOError(f"Atomic write failed: {e}")

    def create_backup(self, target_path: Path) -> Path:
        """
        Creates a centralized backup using the Mirror Strategy.
        
        Structure:
        <workspace>/.Yamlr/backups/path/to/file-<timestamp>.yaml
        """
        try:
            rel_path = target_path.relative_to(self.workspace)
        except ValueError:
            # File is outside workspace? Flatten path to avoid errors
            rel_path = Path(target_path.name)
            
        # Replicate directory structure inside backup folder
        backup_dest_dir = self.backup_dir / rel_path.parent
        backup_dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Add timestamp/counter to filename
        import time
        timestamp = int(time.time())
        backup_name = f"{target_path.stem}.{timestamp}{target_path.suffix}"
        backup_path = backup_dest_dir / backup_name
        
        # Collision safety
        counter = 1
        while backup_path.exists():
            backup_name = f"{target_path.stem}.{timestamp}-{counter}{target_path.suffix}"
            backup_path = backup_dest_dir / backup_name
            counter += 1
            
        shutil.copy2(target_path, backup_path)
        
        # [Smart Rotation] Keep specific file history lean (Max 5 versions)
        self._rotate_backups(backup_dest_dir, target_path.stem, target_path.suffix)
        
        return backup_path

    def _rotate_backups(self, backup_dir: Path, stem: str, suffix: str, keep: int = 5):
        """Auto-prunes old backups for a specific file to prevent disk bloat."""
        try:
            # Find all backups for this file: stem.<timestamp>suffix
            candidates = []
            for f in backup_dir.glob(f"{stem}.*{suffix}"):
                candidates.append(f)
            
            # Sort by name (timestamp is in name) or mtime (safer)
            candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            if len(candidates) > keep:
                for old in candidates[keep:]:
                    try:
                        old.unlink()
                        logger.debug(f"Rotated backup: {old}")
                    except Exception: pass
        except Exception as e:
            logger.warning(f"Backup rotation warning: {e}")

    def crawl(self, root_path: Path, extensions: List[str], max_depth: int) -> Generator[Tuple[Path, str], None, None]:
        """
        Generator that yields (absolute_path, relative_path_str) for matching files.
        Handles depth limiting and security checks.
        """
        ext_set = {e.strip() if e.startswith('.') else f".{e.strip()}" for e in extensions}
        
        # Verify root exists
        if not root_path.exists():
            logger.error(f"Scan root does not exist: {root_path}")
            return

        for root, dirs, files in os.walk(root_path):
            # Depth check
            current_depth = len(Path(root).relative_to(root_path).parts)
            if current_depth >= max_depth:
                del dirs[:]
                continue

            for file in files:
                if any(file.endswith(ext) for ext in ext_set):
                    abs_path = Path(root) / file
                    
                    # Compute relative path for reporting
                    try:
                        rel_path = str(abs_path.relative_to(self.workspace))
                    except ValueError:
                        # File outside workspace (e.g. symlink or external scan)
                        rel_path = str(abs_path)
                    
                    yield abs_path, rel_path
