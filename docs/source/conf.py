import os
import sys
from typing import List
import toml

# -- Project information -----------------------------------------------------

sys.path.insert(0, os.path.abspath("../../"))

with open("../../pyproject.toml") as f:
    data = toml.load(f)


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'openplugin'
copyright = '2023, Imprompt'
author = 'Shrikant M & Barrett J'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

version = data["tool"]["poetry"]["version"]
release = version

html_title = project + " " + version

extensions = ['sphinx_tabs.tabs']

templates_path = ['_templates']
exclude_patterns = []

html_favicon = '_images/favicon.jpg'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ['_static', '_images', '_samples']

html_css_files=["css/custom.css"]