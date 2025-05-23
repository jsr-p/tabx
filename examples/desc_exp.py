# %% [markdown]
# ---
# format: gfm
# ---

# %%
# | echo: true


import tabx
from tabx import ColMap, RowMap, utils


m1 = {
    "variable": ["v1", "v2", "v3", "v4", "v5"],
    "values": [1.0, 2.0, 3, 4.0, 5],
    "extra_data": {
        r"$n$": 10,
        "session": 1,
    },
}
m2 = {
    "variable": ["e1", "e2", "e3", "e4", "Something"],
    "values": [1, 2, 3, 4, 5],
    "extra_data": {
        r"$n$": 10,
        "tstat": 2.3,
        "session": 2,
    },
}
m3 = {
    "variable": ["v1", "e2", "e3", r"$\gamma$"],
    "values": [10, 20, 4, 5],
    "se": [0.1, 0.2, 0.3, "0.0400"],
}

mod1 = tabx.DescData.from_dict(m1, name=r"\texttt{Outcome1}")
mod2 = tabx.DescData.from_dict(m2, name=r"\texttt{Outcome2}")
mod3 = tabx.DescData.from_dict(m3, name=r"\texttt{Outcome3}")
descs = [mod1, mod2, mod3, mod1, mod2, mod3]

variables = (
    ["Something", "v2", "v3", "v4", "v5"]
    + ["e1", "e2", "e3", "e4", "e5"]
    + [r"$\gamma$"]
)
order_map = dict(zip(variables, range(len(variables)))) | {
    "session": 0,
    r"$n$": 1,
    "tstat": 2,
}


tab = tabx.descriptives_table(
    descs,
    col_maps=[
        ColMap(
            mapping={
                (1, 6): r"Full experiment",
            },
            include_cmidrule=True,
        ),
        ColMap(
            mapping={
                (1, 3): r"Col group 1",
                (4, 6): r"Col group 2",
            },
            include_cmidrule=True,
        ),
    ],
    order_map=order_map,
    include_header=True,
    include_extra=True,
    row_maps=[
        RowMap(
            {
                (1, 11): r"All",
            }
        ),
        RowMap(
            {
                (1, 6): r"Row group 1",
                (7, 11): r"Row group 2",
            }
        ),
    ],
    fill_value="-",
)
# %%
# | echo: false
file = utils.compile_table(
    tab.render(),
    silent=True,
    output_dir=utils.proj_folder().joinpath("figs"),
    name="desc_example",
)
_ = utils.pdf_to_png(file)

# %% [markdown]
# ![image](figs/desc_example.png)
