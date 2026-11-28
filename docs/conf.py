import os
import sys
from datetime import datetime

# Point to the source code for autodoc
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------

project = "Yamlr"
copyright = f"{datetime.now().year}, Yamlr Team"
author = "Nishar A Sunkesala"
release = "0.1.4"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",  # Support for Google-style docstrings
    "myst_parser",  # Support for Markdown docs
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "venv", ".venv"]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Extension configuration -------------------------------------------------

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
