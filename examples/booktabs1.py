# %% [markdown]
# ---
# format: gfm
# ---

# %% [markdown]
# Example from:
# [here](https://lazyscientist.wordpress.com/2021/07/23/make-better-tables-in-latex-using-booktabs/)

# %%
# | echo: true

import tabx
from tabx import DescData, utils, Cmidrule


column_names = ["{A}", "{B}", "{C}", "{D}", "{Avg}"]
values = [
    ["Density (g/mL)", 1.1, 1.04, 1.05, 1.109, 1.07],
    ["Mass (g)", 1.399, 1.32, 1.328, 1.408, 1.364],
    ["Mass w/ Precipitate (g)", 13.443, 13.401, 13.348, "{---}", 13.397],
    ["Mass AgCl (\\num{e-2} g)", 9.0, 9.2, 8.7, "{---}", 8.9],
    ["Moles AgCl (\\num{e-4} mol", 6.28, 6.42, 6.08, "{---}", 6.5],
]
desc_datas = DescData.from_values(values, column_names=column_names)
tab = (
    tabx.descriptives_table(
        desc_datas,
        col_maps=tabx.ColMap(mapping={(1, 4): r"Test Tubes"}),
        var_name="Qty of Sample",
        include_midrule=False,
    )
    .insert_row(
        Cmidrule(1, 1, "r") | Cmidrule(2, 5, "rl") | Cmidrule(6, 6, "l"),
        index=3,
    )
    .set_align("l" + 5 * "S")
)
file = utils.compile_table(
    tab.render(),
    silent=True,
    name="booktabs1",
    output_dir=utils.proj_folder().joinpath("figs"),
)
_ = utils.pdf_to_png(file)


# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/booktabs1.png)
