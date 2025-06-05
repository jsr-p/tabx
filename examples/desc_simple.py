# %% [markdown]
# ---
# format: gfm
# ---

# %% [markdown]
# Create descriptive table quickly from a `polars.DataFrame` using `tabx`.

# %%
# | echo: true


import polars as pl
import tabx
from tabx import DescData, utils

data = pl.DataFrame(
    [
        ["$x_1$", -0.44, 1.14, 1.04, 1.12],
        ["$x_2$", 0.58, -0.63, -0.92, 0.74],
        ["$x_3$", 0.64, -1.0, 1.15, 0.78],
        ["$x_4$", -0.43, 1.02, 1.76, -0.68],
        ["$x_5$", 0.1, 0.63, -0.35, -0.21],
        ["$x_6$", 0.06, 0.98, 0.56, -0.25],
        ["$x_7$", -1.49, -1.8, 0.8, -0.23],
        ["$x_8$", -1.91, -1.42, -0.3, 0.25],
    ],
    schema=["variable", "A", "B", "C", "D"],
    orient="row",
)

desc_datas = DescData.from_values(
    data.rows(),
    column_names=data.columns[1:],  # Exclude 'variable' column
    extras=[
        {"n": 10, "misc": 1},
        {"n": 20, "misc": 0},
        {"n": 15, "misc": 1},
    ],
)
tab = tabx.descriptives_table(
    desc_datas,
    col_maps=tabx.ColMap(
        mapping={
            (1, 2): "First",
            (3, 4): "Second",
        }
    ),
    include_midrule=True,
    fill_value="-",
    order_map={"n": 0, "misc": 1},
)
# %%
# | echo: false
file = utils.compile_table(
    tab.render(),
    silent=True,
    name="desc_simple",
    output_dir=utils.proj_folder().joinpath("figs"),
)
_ = utils.pdf_to_png(file)

# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/desc_simple.png)
