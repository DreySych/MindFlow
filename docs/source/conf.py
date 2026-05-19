"""Sphinx configuration for MindFlow documentation."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Sphinx may be built in CI without a local .env file. These defaults are used
# only for importing Django modules while generating documentation.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "The_Final_Build.settings")
os.environ.setdefault("SECRET_KEY", "docs-build-secret-key")
os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("EMAIL_HOST_USER", "")
os.environ.setdefault("EMAIL_HOST_PASSWORD", "")
os.environ.setdefault("OPENROUTER_API_KEY", "")

try:
    import django
    django.setup()
except Exception as exc:  # pragma: no cover - documentation fallback only
    print(f"Django setup was skipped during docs build: {exc}")

project = "MindFlow"
author = "MindFlow Team"
copyright = "2026, MindFlow Team"
release = "1.0"
version = "1.0"

language = "ru"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
]

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_mock_imports = [
    "requests",
    "sentence_transformers",
    "torch",
    "transformers",
    "channels",
    "daphne",
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = ["_static"]
html_title = "MindFlow documentation"
html_short_title = "MindFlow"

todo_include_todos = True
