# %% [markdown]
# ---
# format: gfm
# ---

# %%
# | echo: true


import tabx
from tabx import utils
from tabx.utils import compile_table, pdf_to_png

C = tabx.Cell
tab = tabx.Table.from_cells(
    [
        [C("A"), C("B"), C("C")],
        [C("A"), C("B"), C("C")],
        [C("A"), C("B"), C("C")],
        [C("A"), C("B"), C("C")],
    ]
)
tab = C("X", multicolumn=3) / tabx.Cmidrule(1, 3) / tab
tab


# %%
# | echo: true
tab.shape


# %%
# | echo: true
tab.shape
print(tab.render())  # Rendered table


# %%
# | echo: true
ce = tabx.empty_columns(6, 1)
ctab = ce | tab | ce
ctab.print()

# %%
# | echo: false
file = compile_table(
    ctab.render(),
    silent=True,
    name="table0",
    output_dir=utils.proj_folder().joinpath("figs"),
)
_ = pdf_to_png(file)

# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/table0.png)


# %%
# | echo: true
rlab = tabx.multirow_column(
    r"\rotatebox[origin=c]{90}{$x = 2$}",
    4,
    pad_before=2,
    align="l",
)
rlab2 = tabx.multirow_column(
    r"\rotatebox[origin=c]{270}{$x = 2$}",
    4,
    pad_before=2,
    align="l",
)
tt = (
    (rlab | tab | rlab2)
    / tabx.Midrule()
    / C("Estimand", multicolumn=5, style="italic")
    / tabx.Cmidrule(2, 4)
    / C(r"$\beta$", multicolumn=5)
)
tt.print()


# %%
# | echo: false
file = compile_table(
    tt.render(),
    silent=True,
    output_dir=utils.proj_folder().joinpath("figs"),
    name="table",
)
_ = pdf_to_png(file)


# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/table.png)
