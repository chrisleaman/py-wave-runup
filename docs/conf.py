# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../py_wave_runup/"))


# -- Project information -----------------------------------------------------

project = "py-wave-runup"
copyright = "2019, Chris Leaman"
author = "Chris Leaman"

# The full version, including alpha/beta/rc tags
release = "v0.1.4"


# -- General configuration ---------------------------------------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The master toctree document.
master_doc = "index"

source_suffix = ".rst"
autoclass_content = "both"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

pygments_style = "sphinx"

html_sidebars = {
    "**": ["globaltoc.html", "relations.html", "sourcelink.html", "searchbox.html"]
}

html_sidebars = {
    "**": ["about.html", "navigation.html", "relations.html", "searchbox.html"]
}

html_theme_options = {
    "description": "Empirical wave runup models implemented in Python for coastal engineers and scientists.",
    "github_user": "chrisleaman",
    "github_repo": "py-wave-runup",
    "fixed_sidebar": True,
    "github_button": True,
}

# Autodoc options

# Define what classes to skip
def autodoc_skip_member(app, what, name, obj, skip, options):
    exclusions = ("RunupModel",)
    exclude = name in exclusions
    return skip or exclude


def setup(app):
    app.connect("autodoc-skip-member", autodoc_skip_member)


# Define order
autodoc_member_order = "bysource"
