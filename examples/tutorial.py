# %% [markdown]
# ---
# format: gfm
# ---

# %% [markdown]
# ### Cell, Table, and concatenation

# %%
# | echo: true

from tabx import Cell
from tabx import utils

# %% [markdown]
# The most basic object is a `Cell`

# %%
# | echo: true
cell = Cell("1")
cell

# %% [markdown]
# Rendering a cell returns it values as a `str`

# %%
# | echo: true
cell.render()

# %%
# | echo: true
cell = Cell(r"$\alpha$")
cell.render()

# %% [markdown]
# Cells can be concatenated with other cells.
# Concatenating three cells horizontally with the `|` operator
# yields a `Table` object of dimension (1, 3)

# %%
# | echo: true
tab = Cell("1") | Cell("2") | Cell("3")
tab

# %% [markdown]
# Rendering this yields a `str` with the three cells concatenated wrapped inside a `tabular` environment ready to be used in a LaTeX document.

# %%
# | echo: true
tab.render()


# %% [markdown]
# Can also be done vertically with the `/` operator yielding a `Table` object of
# dimension (3, 1)

# %%
# | echo: true
tab_other = Cell("1") / Cell("2") / Cell("3")
tab_other


# %% [markdown]
# We can concatenate a `Table` horizontally to stack the tables above each
# other. This is done using the `/` operator.


# %%
# | echo: true
stacked_tab = tab / tab
stacked_tab

# %% [markdown]
# And we can concatenate another table onto it from below and then the other
# from the right

# %%
# | echo: true
stacked_tab2 = (stacked_tab / tab) | tab_other
stacked_tab2


# %% [markdown]
# To print out how the table looks like, we can use the `print` method; this
# does not return anything but prints out the object to the console.

# %%
# | echo: true
stacked_tab2.print()

# %% [markdown]
# Say we want some columns name onto this table.
# This can be done:

# %%
# | echo: true
stacked_tab3 = (Cell("A") | Cell("B") | Cell("C") | Cell("D")) / stacked_tab2
stacked_tab3.print()

# %% [markdown]
# Maybe we want a `Midrule` underneath the column names.
# This can be done as:

# %%
# | echo: true
from tabx import Midrule

stacked_tab3 = (
    (Cell("A") | Cell("B") | Cell("C") | Cell("D")) / Midrule() / stacked_tab2
)
stacked_tab3.print()

# %% [markdown]
# Let add some variable names on the left side.
# We can construct a column as:

# %%
# | echo: true
row_labels = (
    # The header row and Midrule row shouldn't get a label hence empty cells
    Cell("") / Cell("") / Cell("Var1") / Cell("Var2") / Cell("Var3")
)
stacked_tab3 = row_labels | stacked_tab3
stacked_tab3.print()

# %% [markdown]
# If you have a LaTeX compiler in your path, you can compile the table to a PDF
# and convert it to a PNG using `tabx.utils.compile_table` and
# `tabx.utils.pdf_to_png` respectively.

# %%
# | echo: true
file = utils.compile_table(
    stacked_tab2.render(),
    silent=True,
    name="tutorial",
    output_dir=utils.proj_folder().joinpath("figs"),
)
_ = utils.pdf_to_png(file)

# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/tutorial.png)


# %% [markdown]
# ---
# ### Slicing tables
# Tables can be sliced like numpy arrays.

# %%
# | echo: true
# Slice out the row label column
sliced_tab = stacked_tab3[:, 1:]
sliced_tab

# %%
# | echo: true
sliced_tab.print()


# %% [markdown]
# Lets concatenate the sliced table to the original table, add a header above
# the columns of each concatenated table and two  `Cmidrule`s between to
# distinguish the two tables.

# %%
# | echo: true
from tabx import Cmidrule

tab = (
    # Add a header row; one empty cell for the row label column
    (Cell("") | Cell("Table 1", multicolumn=4) | Cell("Table 2", multicolumn=4))
    # Insert Cmidrules after columns
    / (Cmidrule(2, 5, trim="lr") | Cmidrule(6, 9, trim="lr"))
    # Stack header row and Cmidrules above the concatenated tables
    / (stacked_tab3 | sliced_tab)
    # Left align the first column and center the rest
    .set_align("l" + "c" * 8)
)
tab.print()
file = utils.compile_table(
    tab.render(),
    silent=True,
    name="tutorial2",
    output_dir=utils.proj_folder().joinpath("figs"),
)
_ = utils.pdf_to_png(file)

# %% [markdown]
# ![image](figs/tutorial2.png)


# %% [markdown]
# Okay let's have some fun.
# We'll slice out the upper part of the previous table, concatenate the sliced
# table onto it from below and then concatenate a column of multirow labels on
# the left.
# Let's see it in action instead of the just read word salad:

# %%
# | echo: true
from tabx import empty_table

multirow_labels = (
    empty_table(3, 1)
    / Midrule()
    # A multirow label spanning 3 rows should be followed by 2 empty cells
    / (Cell("Label 1", multirow=3) / empty_table(2, 1))
    / Midrule()
    / (Cell("Label 2", multirow=3) / empty_table(2, 1))
)
tab_new = multirow_labels | (tab / tab[3:, :])
tab_new.print()
file = utils.compile_table(
    tab_new.render(),
    silent=True,
    name="tutorial3",
    output_dir=utils.proj_folder().joinpath("figs"),
)
_ = utils.pdf_to_png(file)

# %% [markdown]
# ![image](figs/tutorial3.png)

# %%
# | echo: true

from tabx import Table

# Renders the table body without the tabular environment
print(tab_new.render_body())

# %% [markdown]
# ### Custom render function
# A custom rendering function can be used to render the body of a table.

# %%
# | echo: true


def render_body_simple(table: Table):
    if not (align := table.align):
        align = "c" * table.ncols
    return "\n".join(
        [
            r"\begin{tabular}{" + align + r"}",
            table.render_body(),
            r"\end{tabular}",
        ]
    )


print(tab_new.render(custom_render=render_body_simple))

# %% [markdown]
# ### Utility functions
# The function `empty_table` is convienient for creating empty cells of
# dimension (nrows, ncols) as fillers.

# %%
# | echo: true
n, m = 3, 5
empty_table(n, m)

# %% [markdown]
# The notation for the multirow cells above is a bit verbose.
# The function `multirow_column` is a wrapper for creating a multirow column with padding before and after the multirow cell.

# %%
# | echo: true
from tabx import multirow_column

mr = multirow_column("Label1", multirow=3, pad_before=2, pad_after=2)
print(mr)

# %%
# | echo: true
mr.print()

# %% [markdown]
# We can write the `multirow_labels` column from before as:

# %%
# | echo: true


multirow_labels_succ = (
    # A multirow label spanning 3 rows should be followed by 2 empty cells
    empty_table(3, 1)
    / Midrule()
    / multirow_column("Label 1", multirow=3)
    / Midrule()
    / multirow_column("Label 2", multirow=3)
)

print(multirow_labels_succ.rows == multirow_labels.rows)
