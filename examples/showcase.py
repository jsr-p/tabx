# %% [markdown]
# ---
# format: gfm
# ---

# %%
# | echo: true

from tabx import Cell, Table, Cmidrule, Midrule, multirow_column, multicolumn_row

C = Cell

base = Table.from_cells(
    [
        [C(3.14), C(3.14), C(3.14), C(3.14)],
        [C(1.62), C(1.62), C(1.62), C(1.62)],
        [C(1.41), C(1.41), C(1.41), C(1.41)],
        [C(2.72), C(2.72), C(2.72), C(2.72)],
    ]
)
row_labels = Table.from_cells(
    [
        C(r"$\sigma = 0.1$"),
        C(r"$\sigma = 0.3$"),
        C(r"$\eta = 0.1$"),
        C(r"$\eta = 0.3$"),
    ],
)
header = multicolumn_row(r"$\beta$", 2, pad_before=2) | multicolumn_row(r"$\gamma$", 2)
mr = multirow_column(r"$R_{1}$", 4)
cmrs = Cmidrule(3, 4, "lr") | Cmidrule(5, 6, "lr")
# Stack header on top of Cmidrules; stack row labels onto table from the left
tab = header / cmrs / (mr | row_labels | base)
tab.print()  # Print table to stdout


# %%
# | echo: false

from tabx import utils

r = file = utils.compile_table(
    tab.render(),
    silent=True,
    output_dir=utils.proj_folder().joinpath("figs"),
    name="showcase",
)
_ = utils.pdf_to_png(file)


# %% [markdown]
# Compiling the table and converting to PNG yields:
#
# ![image](figs/showcase.png)


# %%
# | echo: true

# Add some more complexity to the previous table
row_labels2 = Table.from_cells(
    [
        C(r"$\xi = 0.1$"),
        C(r"$\xi = 0.3$"),
        C(r"$\delta = 0.1$"),
        C(r"$\delta = 0.3$"),
    ],
)
header2 = multicolumn_row(r"$\theta$", 2) | multicolumn_row(r"$\mu$", 2)
mr = multirow_column(r"$R_{2}$", 4)
tab2 = mr | row_labels2 | base
concat_tab = (
    # Stack header with Cmidrule above all columns
    (multicolumn_row("All models", 8, pad_before=2) / Cmidrule(3, 10))
    / (
        # Stack tables vertically with Midrule in between
        (tab / Midrule() / tab2)
        # Stack the resulting table horizontally with the one below
        | (
            # Slice tables and stack new header on top
            # Cmidrules start from 1 while no row labels for the right table
            header2
            / (Cmidrule(1, 2, "lr") | Cmidrule(3, 4, "lr"))
            / tab[2:, 2:]  # Previous table sliced
            / Midrule()
            / tab2[:, 2:]  # New table sliced
        )
    )
).set_align(2 * "l" + 8 * "c")
concat_tab.print()

# %%
# | echo: false

from tabx import utils

r = file = utils.compile_table(
    concat_tab.render(),
    silent=True,
    output_dir=utils.proj_folder().joinpath("figs"),
    name="showcase2",
)
_ = utils.pdf_to_png(file)


# %% [markdown]
# Compiling the table and converting to PNG yields:
#
# ![image](figs/showcase2.png)
