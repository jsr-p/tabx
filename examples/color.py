# %% [markdown]
# ---
# format: gfm
# ---

# %%
# | echo: true

import tabx
from tabx import utils
from tabx.utils import colored_column_spec, compile_table, pdf_to_png
from tabx import ColoredRow, ColoredCell

C = tabx.Cell
CC = ColoredCell
et = tabx.empty_table
CR = ColoredRow
tab = tabx.Table.from_cells(
    [
        [C("A"), CC("B", "yellow"), C("C")],
        [C("A"), CC("B", "green"), C("C")],
        [C("A"), CC("X", "orange"), C("C")],
        [C("A"), C("B"), C("C")],
    ]
)
tab = C("X", multicolumn=3) / tabx.Cmidrule(1, 3) / tab
tab = (tab / tabx.empty_table(3, 3)).set_align(
    colored_column_spec("blue", "c")
    + colored_column_spec("magenta", "c")
    + colored_column_spec("purple", "r")
)
subtab = tabx.Table.from_cells(
    [
        [
            CC("H", "red"),
            CC("E", "green"),
            CC("L", "blue"),
            CC("L", "orange"),
            CC("O", "yellow"),
        ]
        for _ in range(5)
    ]
)
subtab = et(2, 5) / subtab / et(2, 5)
tab = (
    tab
    | subtab
    | tabx.multirow_column(
        r"\rotatebox[origin=c]{270}{Greetings}",
        7,
        pad_before=2,
    )
)
tab.print()

# %%
# | echo: false
file = compile_table(
    r := tab.render(),
    silent=True,
    extra_preamble=r"""
% Define some colors
\definecolor{Gray}{gray}{0.85}
\definecolor{LightCyan}{rgb}{0.88,1,1}
    """,
    output_dir=utils.proj_folder().joinpath("figs"),
    name="color0",
)
_ = pdf_to_png(file)

# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/color0.png)
