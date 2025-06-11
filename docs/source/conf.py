"""
Sphinx configuration file for Reality Defender SDK documentation
"""

import os
import sys
import re

# Add the src directory to the Python path for autodoc
sys.path.insert(0, os.path.abspath('../../src'))
version = '0.1.0'

# Project information
project = 'Reality Defender SDK'
copyright = '2023, Reality Defender'
author = 'Reality Defender'
release = version

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = []

# Options for HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = f'Reality Defender SDK {version}'
html_favicon = None

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'inherited-members': True,
    'member-order': 'bysource',
}
autodoc_typehints = 'description'
autodoc_typehints_format = 'short'

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'aiohttp': ('https://docs.aiohttp.org/en/stable/', None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
