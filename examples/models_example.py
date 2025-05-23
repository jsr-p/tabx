# %% [markdown]
# ---
# format: gfm
# ---

# %%
# | echo: true

import tabx
from tabx import ColMap, utils


m1 = {
    "variable": ["v1", "v2", "v3", "v4", "v5"],
    "estimates": [1, 2, 3, 4, 5],
    "se": [0.1, 0.2, 0.3, 0.4, 0.5],
    "extra_data": {
        r"$n$": 10,
        "FE": r"\checkmark",
    },
}
m2 = {
    "variable": ["e1", "e2", "e3", "e4", "e5"],
    "estimates": [1, 2, -3.34, 4, 5],
    "se": [0.1, 0.2, 0.3, 0.4, 0.5],
    "extra_data": {
        r"$n$": 10,
        "$t$-stat": 2.3,
        "FE": "-",
    },
}
m3 = {
    "variable": ["v1", "e2", "e3", r"$\gamma$"],
    "estimates": [10, 20, 4, 5],
    "se": [0.1, 0.2, 0.3, "0.0400"],
    "extra_data": {
        "FE": r"\checkmark",
    },
}
m4 = {
    "variable": ["v1", "e2", "e3", r"$\gamma$"],
    "estimates": [10, 20, 4, 5],
    "se": [0.1, 0.2, 0.3, "0.0400"],
}
mod1 = tabx.ModelData.from_dict(m1, name="(M1)")
mod2 = tabx.ModelData.from_dict(m2, name="(M2)")
mod3 = tabx.ModelData.from_dict(m3, name="(M3)")
mod4 = tabx.ModelData.from_dict(m4, name="(M4)")
models = [mod1, mod2, mod3, mod4]

variables = (
    ["v1", "v2", "v3", "v4", "v5"] + ["e1", "e2", "e3", "e4", "e5"] + [r"$\gamma$"]
)
order_map = dict(zip(variables, range(len(variables)))) | {
    "session": 0,
    r"$n$": 1,
    "$t$-stat": 2,
}
tab = tabx.models_table(
    models,
    col_maps=ColMap(
        mapping={
            (1, 2): r"\texttt{Outcome1}",
            (3, 4): r"\texttt{Outcome2}",
        }
    ),
    var_name="",
    order_map=order_map,
    fill_value="-",
)


# %%
# | echo: false
file = utils.compile_table(
    tab.render(),
    silent=True,
    output_dir=utils.proj_folder().joinpath("figs"),
    name="models_example",
)
_ = utils.pdf_to_png(file)

# %% [markdown]
# ![image](figs/models_example.png)
