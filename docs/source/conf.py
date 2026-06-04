from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPO_ROOT))

project = "FixPriceAPI"
author = "Miskler"
copyright = "2026, Miskler"


def _get_version() -> str:
    for key in ("PROJECT_VERSION", "READTHEDOCS_VERSION", "VERSION"):
        if os.getenv(key):
            return os.environ[key]
    try:
        from importlib.metadata import version

        return version("fixprice_api")
    except Exception:
        return "0.2.4.1"


release = _get_version()
version = ".".join(release.split(".")[:3])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.doctest",
    "sphinx.ext.duration",
    "jsoncrack_for_sphinx",
]

autodoc_mock_imports = [
    "aiohttp",
    "aiohttp_retry",
    "camoufox",
    "playwright",
    "playwright.async_api",
    "PIL",
]

source_suffix = {
    ".rst": "restructuredtext",
}

autosummary_generate = False
autosummary_imported_members = True
autosummary_ignore_module_all = False

autodoc_default_options = {}
autodoc_typehints = "signature"
autodoc_preserve_defaults = True

add_module_names = False
python_use_unqualified_type_names = True
multi_line_parameter_list = True
python_maximum_signature_line_length = 80
default_role = "any"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "human_requests": ("https://miskler.github.io/human-requests/", None),
}

json_schema_dir = str(HERE.parents[2] / "tests" / "__snapshots__")

html_theme = "furo"
html_static_path = ["_static"]
templates_path = ["_templates"]

html_theme_options = {
    "sidebar_hide_name": True,
    "light_logo": "logo-light.webp",
    "dark_logo": "logo-dark.webp",
}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
