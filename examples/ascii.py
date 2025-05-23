# %% [markdown]
# ---
# format: gfm
# ---

# %%
# | echo: true

"""
ASCII art tables.
"""

from functools import reduce

import pyfiglet

import tabx
from tabx import Cell, utils
from tabx.utils import render_body_simple


def get_lines(c: str):
    return [c for c in c.splitlines() if c]


def parse_c(c: str):
    if c == "_":
        return r"\_"
    if c == "|":
        return r"\textbar"
    if c == "\\":
        return r"\textbackslash"
    if c == "<":
        return r"\textless"
    if c == ">":
        return r"\textgreater"
    return c


def get_table(s: str):
    parts = get_lines(s)
    max_len = max([len(p) for p in parts])
    rows = []
    for p in parts:
        row = []
        lp = len(p)
        diff = max_len - lp
        for c in p:
            row.append(Cell(value=parse_c(c), style="bold"))
        for _ in range(diff):  # pad differences
            row.append(tabx.empty_cell())
        rows.append(tabx.Row(row))
    return tabx.Table(rows)


p1 = pyfiglet.figlet_format("t")
p2 = pyfiglet.figlet_format("a")
p3 = pyfiglet.figlet_format("b")
p4 = pyfiglet.figlet_format("x")

cols = [
    get_table(p1),
    get_table(p2),
    get_table(p3),
    get_table(p4),
]

ec = tabx.empty_columns

tab = get_table(p1) | get_table(p2) | get_table(p3) | get_table(p4)
file = utils.compile_table(
    tab.render(),
    silent=True,
    output_dir=utils.proj_folder().joinpath("figs"),
    name="ascii1",
)
_ = utils.pdf_to_png(file)

# %% [markdown]
# ![image](figs/ascii1.png)


# %%
# | echo: true


words = []
for word in ["LaTeX", "tables", "in", "Python"]:
    word_cols = []
    for c in word:
        word_cols.append(get_table(pyfiglet.figlet_format(c)))
    words.append(reduce(lambda x1, x2: x1 | x2, word_cols))
extra = (words[0] | ec(6, 1) | words[1]) / (
    ec(6, 7) | words[2] | ec(6, 3) | words[3] | ec(6, 7)
)
top = ec(6, 21) | tab | ec(6, 21)

r = file = utils.compile_table(
    (top / extra).render(render_body_simple),
    silent=True,
    output_dir=utils.proj_folder().joinpath("figs"),
    name="ascii2",
)
_ = utils.pdf_to_png(file)


# %% [markdown]
# ![image](figs/ascii2.png)
