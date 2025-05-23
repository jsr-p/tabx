"""
Module to fix xref stuff related to python.
Works on my machine; will fix it later for others.
"""

import re
from functools import partial
from pathlib import Path

from autodoc2 import analysis
from docutils import nodes
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx


def get_aliases():
    """
    Finds type aliases in modules.

    E.g. returns:

    ```
    [
        'tabx.custom.RCMap',
        'tabx.custom.ColMaps',
        'tabx.custom.RowMaps',
        'tabx.table.TableRow',
        'tabx.table.SequenceKind'
    ]
    ```

    """
    base = Path("/home/jsr-p/projects/tabx-py/src/")
    modules = [
        "tabx.custom",
        "tabx.utils",
        "tabx.table",
    ]
    aliases = []
    for mod in modules:
        path = base / f"{mod.replace('.', '/')}.py"
        for item in analysis.analyse_module(path, mod):
            if item["type"] == "typealias":
                aliases.append(item["full_name"])
    return aliases


def retype_known_aliases(
    app: Sphinx,
    doctree: nodes.document,
    verbose: bool = False,
) -> None:
    """Changes reftype of all typealiases to type.

    The aliases are found in the modules specified in `get_aliases`.
    Run it together with `strip_fully_qualified_reftargets`.

    `RowMap` is a typealias.
    Thus, in the snippet below, reftype="class" is wrong.
    This function will change it to reftype="type".

    ```txt
    <pending_xref py:class="True" py:module="tabx.custom" refdomain="py" refspecific="False" reftarget="RowMap" reftype="class">
        <pending_xref_condition condition="resolved">
            RowMap
        <pending_xref_condition condition="*">
            RowMap
    ```
    """
    aliases = get_aliases()
    for node in doctree.traverse(pending_xref):
        if node.get("refdomain") != "py":
            continue
        target = node.get("reftarget")
        reftype = node.get("reftype")

        if target in aliases and reftype != "type":
            if verbose:
                print(f"[xref-typefix] Rewriting :class:`{target}` to :type:`{target}`")
            node["reftype"] = "type"


def fix_reftargets(
    app: Sphinx,
    doctree: nodes.document,
    verbose: bool = False,
) -> None:
    """Fixes reftargets.

    E.g. for tying aliases the reftarget for `Sequence` becomes
    just `Sequence` in both cases.
    By replacing it with collections.abc.Sequence it resolves the link
    correctly.

    <pending_xref py:class="True" py:module="tabx.custom" refdomain="py" refspecific="False" reftarget="Sequence" reftype="class">
        <pending_xref_condition condition="resolved">
            Sequence
        <pending_xref_condition condition="*">
            Sequence

    Credit:
        - https://github.com/khaeru/genno/blob/692b13ae3a365c18b15df914468ec66da5a94876/doc/conf.py#L147-L210
        - https://stackoverflow.com/questions/62293058/how-to-add-objects-to-sphinxs-global-index-or-cross-reference-by-alias
    """
    import typing

    typing.Literal

    reftarget_alias = {
        "^Sequence": ("collections.abc.Sequence", "obj"),
        # reftype obj and not class for Literal
        "^Literal": ("typing.Literal", "obj"),
    }
    for node in doctree.traverse(pending_xref):
        if node.get("refdomain") != "py":
            continue

        target = node.get("reftarget")

        try:
            expr = next(filter(lambda e: re.match(e, target), reftarget_alias))
        except StopIteration:
            continue
        replacement, reftype = reftarget_alias[expr]
        node["reftarget"] = re.sub(expr, replacement, target)
        node["reftype"] = reftype
        if verbose:
            print(
                f"[xref-reftarget-fix] Rewriting reftarget: {target} -> {node['reftarget']}"
            )


def setup(app):
    # Retype types
    verbose = True
    app.connect(
        "doctree-read",
        partial(retype_known_aliases, verbose=verbose),
    )

    app.connect(
        "doctree-read",
        partial(fix_reftargets, verbose=verbose),
    )
