# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import django

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath('../..'))

# Настройка Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'The_Final_Build.settings'
django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'The Final Build'
copyright = '2026, Drey Sych'
author = 'Drey Sych'
release = '1.0.0'
version = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',          # Автоматическая документация из docstrings
    'sphinx.ext.viewcode',         # Ссылки на исходный код
    'sphinx.ext.napoleon',         # Поддержка Google/NumPy стиля docstrings
    'sphinx.ext.intersphinx',      # Ссылки на другие проекты
    'sphinx.ext.todo',             # Поддержка TODO
    'sphinx.ext.coverage',         # Проверка покрытия документацией
    'sphinx.ext.ifconfig',         # Условная документация
    'sphinx_rtd_theme',            # Read the Docs тема
    'sphinxcontrib.httpdomain',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
}

# -- Extension configuration -------------------------------------------------

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/stable/',
               'https://docs.djangoproject.com/en/stable/_objects/'),
}

# TODO settings
todo_include_todos = True

# Подавить предупреждения о дублирующихся описаниях объектов
suppress_warnings = [
    'autodoc',
    'autodoc.import_object',
    'ref.duplicate',
]

# Настройки autodoc для предотвращения дублей
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'noindex': True,
}