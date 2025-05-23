"""
Extension to append types to autodoc2 generated api docs.

Requires my PR:
    /home/jsr-p/gh-repos/documentation-stuff/sphinx-autodoc2
"""

from pathlib import Path

from autodoc2 import analysis
from autodoc2.config import Config
from autodoc2.render import myst_
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util.typing import ExtensionMetadata

HEADER = """
#### Types
"""


def get_type_aliases(path, mod):
    renderer = myst_.MystRenderer(db=_, config=Config())  # type: ignore
    for item in analysis.analyse_module(path, mod):
        if item["type"] == "typealias":
            yield "\n".join(renderer.render_typealias(item))


def append_extra(app: Sphinx, docname: str, source: list[str]) -> None:
    base = Path("/home/jsr-p/projects/tabx-py/src/")
    modules = [
        "tabx.custom",
        "tabx.utils",
        "tabx.table",
    ]
    for mod in modules:
        if docname.endswith(f"tabx/{mod}"):
            extra = []
            path = base / f"{mod.replace('.', '/')}.py"
            for item in get_type_aliases(path, mod):
                extra.append(item)
            if extra:
                extra.insert(0, HEADER)
                source[0] += "\n".join(extra)


def setup(app: Sphinx) -> ExtensionMetadata:
    app.connect("source-read", append_extra)

    return {
        "version": "0.1",
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
