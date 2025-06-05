project = "tabx"
copyright = "2025, jsr-p"
author = "jsr-p"


extensions = [
    "sphinx.ext.napoleon",  # before autodoc2
    "myst_parser",
    "autodoc2",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "tabx._ext.fix_xrefs",
    "tabx._ext.add_types_modules",
]

intersphinx_mapping = {
    # downloads objects.inv from python which allows for referencing their
    # objects using e.g. {py:attr}`polars.Series.dtype` see:
    # https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
    "python": ("https://docs.python.org/3", None),
}

autodoc2_packages = [
    "../../src/tabx",
]

# only include __all__
autodoc2_module_all_regexes = [r"tabx\..*"]

autodoc2_hidden_objects = [
    "inherited",
]
autodoc2_module_summary = True
autodoc2_no_index = False

autodoc2_render_plugin = "myst"
autodoc2_hidden_objects = [
    "inherited",
    "dunder",
    "private",
]


autodoc2_skip_module_regexes = [
    r"tabx._ext*",
]

myst_enable_extensions = [
    "attrs_block",
    "attrs_inline",
    "amsmath",
    # for writing :param:`param_name` in docstrings
    "fieldlist",
]
myst_number_code_blocks = ["python"]
myst_heading_anchors = 2


# autodoc-typehints
always_use_bars_union = True
typehints_fully_qualified = False
always_document_param_types = False
typehints_defaults = "comma"  # Use braces for type hints


# python options:
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-python_maximum_signature_line_length
python_maximum_signature_line_length = 80
python_use_unqualified_type_names = True


templates_path = ["_templates"]
exclude_patterns = []

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}


html_theme = "furo"
