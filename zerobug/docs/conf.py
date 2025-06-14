# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation on 2019-11-01 17:49:31
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath("."))
# import sphinx_rtd_theme


# -- Project information -----------------------------------------------------

project = "zerobug"
copyright = "2019-25, SHS-AV s.r.l."
author = "Antonio Maria Vigliotti"

# The short X.Y version
version = "2.0.19"
# The full version, including alpha/beta/rc tags
release = "2.0.19"


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = "1.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = [".rst", ".md"]
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set 'language' from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "description*",
    "descrizione*",
    "features*",
    "oca_diff*",
    "certifications*",
    "prerequisites*",
    "installation*",
    "configuration*",
    "upgrade*",
    "support*",
    "usage*",
    "maintenance*",
    "troubleshooting*",
    "known_issues*",
    "proposals_for_enhancement*",
    "history*",
    "faq*",
    "sponsor*",
    "copyright_notes*",
    "available_addons*",
    "contact_us*",
    "__init__*",
    "name*",
    "summary*",
    "sommario*",
    "maturity*",
    "module_name*",
    "repos_name*",
    "today*",
    "authors*",
    "contributors*",
    "translators*",
    "acknowledges*",
    "MAINPAGE.rst",
]

# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = None
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# on_rtd is whether we are on readthedocs.org,
# this line of code grabbed from docs.readthedocs.org
# html_theme = "sphinx_rtd_theme"
# html_theme = "python_docs_theme"
html_theme = "nature"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    # "canonical_url": "",
    # "analytics_id": "UA-XXXXXXX-1",
    # "logo_only": False,
    # "display_version": True,
    # "prev_next_buttons_location": "bottom",
    # "style_external_links": False,
    # "vcs_pageview_mode": "",
    # "style_nav_header_background": "white",
    # Toc options
    # "collapse_navigation": True,
    # "sticky_navigation": True,
    # "navigation_depth": 4,
    # "includehidden": True,
    # "titles_only": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named 'default.css' will overwrite the builtin 'default.css'.
# html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don"t match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ["localtoc.html", "relations.html", "sourcelink.html",
# "searchbox.html"].
#
# html_sidebars = {}
html_logo = "logozero_180x46.png"
#
# autodoc_default_flags = ["members"]
autosummary_generate = True
autodoc_default_options = {
    "members": "Z0test, Z0testOdoo",
    "undoc-members": True,
    "exclude-members": "Macro, SanityTest",
}

