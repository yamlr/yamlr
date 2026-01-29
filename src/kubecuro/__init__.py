# Akeso Namespace Initialization
import pkgutil
import sys
from pathlib import Path

# Enable "Namespace Packaging" so Kubecuro Pro can merge into this folder
__path__ = pkgutil.extend_path(__path__, __name__)

# Helper to identify if we are running in a PyInstaller bundle
dist_root = getattr(sys, '_MEIPASS', Path(__file__).parent.parent)