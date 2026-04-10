# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import delftdashboard

# -- Project information -----------------------------------------------------

project = "DelftDashboard"
author = "Deltares"
copyright = "2024, Deltares"
version = delftdashboard.__version__
release = delftdashboard.__version__

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

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

html_theme_options = {
    "navigation_with_keys": True,
    "show_nav_level": 2,
    "navbar_align": "left",
    "default_mode": "light",
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/Deltares-research/DelftDashboard",
            "icon": "fa-brands fa-github",
        },
    ],
}

html_context = {
    "github_user": "Deltares-research",
    "github_repo": "DelftDashboard",
    "github_version": "main",
    "doc_path": "docs/source",
}

# -- Intersphinx mapping ----------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
    "geopandas": ("https://geopandas.org/en/stable/", None),
    "hydromt": ("https://deltares.github.io/hydromt/latest/", None),
}
