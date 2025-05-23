# %% [markdown]
# ---
# format: gfm
# ---

# %% [markdown]
# Example from:
# [here](https://nhigham.com/2019/11/19/better-latex-tables-with-booktabs/)

# %%
# | echo: true


import tabx
from tabx import DescData, utils


names = [
    r"\texttt{trigmv}",
    r"\texttt{trig\_expmv}",
    r"\texttt{trig\_block}",
    r"\texttt{expleja}",
]
desc_datas = [
    DescData.from_dict(
        {"variable": names, "values": [11034, 21952, 15883, 11180]},
        name="$mv$",
    ),
    DescData.from_dict(
        {"variable": names, "values": [1.3e-7, 1.3e-7, 5.2e-8, 8.0e-9]},
        name="Rel.~err",
    ),
    DescData.from_dict(
        {"variable": names, "values": [3.9, 6.2, 7.1, 4.3]},
        name="Time",
    ),
    DescData.from_dict(
        {"variable": names, "values": [15846, 31516, 32023, 17348]},
        name="$mv$",
    ),
    DescData.from_dict(
        {"variable": names, "values": [2.7e-11, 2.7e-11, 1.1e-11, 1.5e-11]},
        name="Rel.~err",
    ),
    DescData.from_dict(
        {"variable": names, "values": [5.6, 8.8, 14.0, 6.6]},
        name="Time",
    ),
]
tab = tabx.descriptives_table(
    desc_datas,
    col_maps=tabx.ColMap(
        mapping={
            (1, 3): r"$\text{tol}=u_{\text{single}}$",
            (4, 6): r"$\text{tol}=u_{\text{double}}$",
        }
    ),
    var_name="",
    include_midrule=True,
)
file = utils.compile_table(
    tab.render(),
    silent=True,
    name="booktabs2",
    output_dir=utils.proj_folder().joinpath("figs"),
)
_ = utils.pdf_to_png(file)

# %% [markdown]
# Compiling the table to PDF and converting it to PNG yields:
#
# ![image](figs/booktabs2.png)

# %% [markdown]
# The above is a bit verbose. If you have the data as a list of lists, you can
# use `DescData.from_values` to create the table as follows:

# %%
# | echo: true

column_names = ["$mv$", "Rel.~err", "Time", "$mv$", "Rel.~err", "Time"]
values = [
    ["\\texttt{trigmv}", 11034, 1.3e-07, 3.9, 15846, 2.7e-11, 5.6],
    ["\\texttt{trig\\_expmv}", 21952, 1.3e-07, 6.2, 31516, 2.7e-11, 8.8],
    ["\\texttt{trig\\_block}", 15883, 5.2e-08, 7.1, 32023, 1.1e-11, 14.0],
    ["\\texttt{expleja}", 11180, 8e-09, 4.3, 17348, 1.5e-11, 6.6],
]
desc_datas = DescData.from_values(values, column_names=column_names)
tab_other = tabx.descriptives_table(
    desc_datas,
    col_maps=tabx.ColMap(
        mapping={
            (1, 3): r"$\text{tol}=u_{\text{single}}$",
            (4, 6): r"$\text{tol}=u_{\text{double}}$",
        }
    ),
    var_name="",
    include_midrule=True,
)
print(tab == tab_other)
