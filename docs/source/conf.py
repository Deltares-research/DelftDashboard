# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import re
from pathlib import Path

# -- Project information -----------------------------------------------------

# Read __version__ from the package source (the single source of truth)
# WITHOUT importing it: importing delftdashboard would require the full
# GUI/geospatial dependency stack, which is not available (nor needed) on
# the Read the Docs build machines.
_init_py = (
    Path(__file__).resolve().parents[2] / "src" / "delftdashboard" / "__init__.py"
)
_version = re.search(
    r"^__version__\s*=\s*[\"']([^\"']+)[\"']", _init_py.read_text(), re.M
).group(1)

project = "DelftDashboard"
author = "Deltares"
copyright = "2024, Deltares"
version = _version
release = _version

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = []

# Napoleon settings for NumPy-style docstrings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for HTML output -------------------------------------------------

# Same look as the HurryWave documentation: Read the Docs theme with the
# shared Deltares stylesheet (_static/custom.css).
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = [
    "custom.css",
]

html_theme_options = {
    "navigation_depth": 3,
}

# "Edit on GitHub" link in the page header (sphinx_rtd_theme convention).
html_context = {
    "display_github": True,
    "github_user": "Deltares-research",
    "github_repo": "DelftDashboard",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}

# -- Intersphinx mapping ----------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
    "geopandas": ("https://geopandas.org/en/stable/", None),
    "hydromt": ("https://deltares.github.io/hydromt/latest/", None),
}
