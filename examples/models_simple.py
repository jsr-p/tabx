# %% [markdown]
# ---
# format: gfm
# ---

# %% [markdown]
# Create model table quickly from a `polars.DataFrame` using `tabx`.
# We assume the columns are stacked as pairs of estimates and standard errors
# for each model.

# %%
# | echo: true


import polars as pl
import tabx
from tabx import ModelData, utils

data = pl.DataFrame(
    [
        ["$x_1$", -0.44, 1.14, 1.04, 1.12, 0.56, 0.98, -0.25, -0.21],
        ["$x_2$", 0.58, -0.63, -0.92, 0.74, 0.45, -0.67, 0.33, 0.12],
        ["$x_3$", 0.64, -1.0, 1.15, 0.78, 0.34, -0.89, 0.22, 0.44],
        ["$x_4$", -0.43, 1.02, 1.76, -0.68, 0.22, 0.45, 0.11, -0.33],
        ["$x_5$", 0.1, 0.63, -0.35, -0.21, 0.15, 0.33, -0.12, 0.44],
        ["$x_6$", 0.06, 0.98, 0.56, -0.25, 0.12, 0.44, 0.22, -0.11],
        ["$x_7$", -1.49, -1.8, 0.8, -0.23, 0.67, 0.55, 0.33, -0.44],
        ["$x_8$", -1.91, -1.42, -0.3, 0.25, 0.33, 0.22, 0.11, -0.55],
    ],
    schema=[
        "variable",
        "ests1",
        "ses1",
        "ests2",
        "ses2",
        "ests3",
        "ses3",
        "ests4",
        "ses4",
    ],
    orient="row",
)

desc_datas = ModelData.from_values(
    data.rows(),
    model_names=["M1", "M2", "M3", "M4"],  # Exclude 'variable' column
    extras=[
        {"n": 10, "misc": 1},
        {"n": 20, "misc": 0},
        {"n": 50, "optimizer": "sgd"},
        {"n": 25, "optimizer": "sgd"},
    ],
)
tab = tabx.models_table(
    desc_datas,
    col_maps=tabx.ColMap(mapping={(1, 2): "OLS", (3, 4): "Logistic"}),
    include_midrule=True,
    fill_value="-",
    var_name="",
    order_map={"n": 0, "misc": 1, "optimizer": 2},
)
# %%
# | echo: false
file = utils.compile_table(
    tab.render(),
    silent=True,
    name="model_simple",
    output_dir=utils.proj_folder().joinpath("figs"),
)
_ = utils.pdf_to_png(file)

# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/model_simple.png)

# %% [markdown]
# The downside of this approach is that the estimates and standard errors in
# each row are for the same variable. For the case with many models and many
# variables the dictionary passing approach is more flexible.
