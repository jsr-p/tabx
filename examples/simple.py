# %% [markdown]
# ---
# format: gfm
# ---

# %%
# | echo: true

import tabx
from tabx import ColMap, RowMap

tab = tabx.simple_table(
    values=[
        [3.14, 3.14, 3.14, 3.14],
        [1.62, 1.62, 1.62, 1.62],
        [1.41, 1.41, 1.41, 1.41],
        [2.72, 2.72, 2.72, 2.72],
    ],
    col_maps=[ColMap({(1, 2): r"$\beta$", (3, 4): r"$\gamma$"})],
    row_maps=[
        RowMap({(1, 4): r"$R_{1}$"}),
        RowMap(
            {
                (1, 1): r"$\sigma = 0.1$",
                (2, 2): r"$\sigma = 0.3$",
                (3, 3): r"$\eta = 0.1$",
                (4, 4): r"$\eta = 0.3$",
            }
        ),
    ],
)

# %%
# | echo: false
r = file = tabx.compile_table(
    tab.render(),
    silent=True,
    output_dir=tabx.utils.proj_folder().joinpath("figs"),
    name="simple",
)
_ = tabx.utils.pdf_to_png(file)

# %% [markdown]
# Compiling the table and converting to PNG yields:
#
# ![image](figs/simple.png)
#
# equivalent to the image from the [Showcase](#showcase).
