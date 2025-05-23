# %% [markdown]
# ---
# format: gfm
# ---

# %% [markdown]
# **Great Tables table**
#
# Construct a table from its components as shown in in [Great Tables
# ](https://posit-dev.github.io/great-tables/articles/intro.html)


# %%
# | echo: true


"""
See: https://posit-dev.github.io/great-tables/articles/intro.html
"""

import tabx

from tabx import Table, table, Cmidrule, Midrule
from tabx import Cell as C
from tabx.table import multicolumn_row, multirow_column
from tabx.utils import compile_table, render_body_no_rules, pdf_to_png


vals = [[j for j in range(i, i + 3)] for i in range(1, 9 + 1, 3)]
colsums = [sum(col) for col in zip(*vals)]
table_body = Table.from_values(vals + [colsums])
stub = table.Column.from_values(
    ["Row label", "Row label", "Row label", "Summary label"]
)
stubhead_label = multirow_column(
    "Stubhead label",
    multirow=3,
    vpos="c",
    vmove="3pt",
)
col_labels1 = (
    # spanner label
    C("Spanner label", multicolumn=2)
    / Cmidrule(1, 2, trim="lr")
    # column labels
    / (C(r"\shortstack{Column\\Label}") | C(r"\shortstack{Column\\Label}"))
)
col_labels2 = multirow_column(
    r"\shortstack{Column\\Label}",
    # "Column label",
    multirow=3,
    vpos="c",
    vmove="3pt",
)
col_labels = col_labels1 | col_labels2
footnotes = multicolumn_row("footnotes", multicolumn=4, colspec="c")
sourcenotes = multicolumn_row("sourcenotes", multicolumn=4, colspec="c")
title = multicolumn_row("Some very long title", multicolumn=4, colspec="c")
subtitle = multicolumn_row("Some very long subtitle", multicolumn=4, colspec="c")
tab = (
    (title / subtitle)
    / Midrule()
    / (stubhead_label | col_labels)
    / (C("Row group label") | [C("-"), C("-"), C("-")])
    / (stub | table_body)
    / Midrule()
    / (footnotes / sourcenotes)
).set_align("lccc")


# %%
# | echo: false
file = compile_table(
    tab.render(),
    silent=True,
    name="great_tables",
    output_dir=tabx.utils.proj_folder().joinpath("figs"),
)
_ = pdf_to_png(file)


# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/great_tables.png)


# %% [markdown]
# ---
# **Annotated table**
#
# Annotate the table as shown in in [Great Tables
# docs](https://posit-dev.github.io/great-tables/articles/intro.html)

# %%
# | echo: true

# Remove midrules and annotate the table's components
# Midrules will span the annotations; hence we remove them
tab = (
    (title / subtitle)
    / (stubhead_label | col_labels)
    / (C("Row group label") | [C("-"), C("-"), C("-")])
    / (stub | table_body)
    / (footnotes / sourcenotes)
).set_align("lccc")
annotations_left = (
    multirow_column(r"\large \shortstack{TABLE\\HEADER}", 2, vpos="c")
    / multirow_column(r"\large \shortstack{STUB\\HEAD}", 3, vpos="c")
    # add 1 for row group label
    / multirow_column(r"\large STUB", 4 + 1, vpos="c")
    / tabx.empty_columns(2, 1)
)
annotations_right = (
    tabx.empty_columns(2, 1)
    / multirow_column(r"\large \shortstack{COLUMN\\LABELS}", 3, vpos="c")
    / multirow_column(r"\large \shortstack{TABLE\\BODY}", 4 + 1, vpos="c")
    / multirow_column(r"\large \shortstack{TABLE\\FOOTER}", 2, vpos="c")
)
annotations_top = multicolumn_row(
    r"\LARGE The Components of a Table", multicolumn=6, colspec="c"
)
annotated_tab = (
    annotations_top / Cmidrule(2, 5) / (annotations_left | tab | annotations_right)
)

# %%
# | echo: false
file = compile_table(
    annotated_tab.render(render_body_no_rules),
    silent=True,
    name="great_tables_annotated",
    output_dir=tabx.utils.proj_folder().joinpath("figs"),
)
_ = pdf_to_png(file)

# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/great_tables_annotated.png)
