import tabx

from collections.abc import Sequence

import tabx
from tabx import utils, Table, Cell, Row, table
from tabx import Cell as C
from tabx.table import match_seq
from tabx.utils import compile_table, pdf_to_png


# p 55 not so short guide
tab = Table.from_cells(
    [
        [
            C("left"),
            C(
                """
            Very long paragraph that gets 
            broken into multiple lines.
            """
            ),
        ],
        [
            C("1"),
            C("""
Another one, but shorter."""),
        ],
    ]
).set_align("lp{3cm}")
compile_table(
    (tabx.Toprule(width="1cm") / tab / tabx.Bottomrule(width="1cm")).render(),
    silent=False,
)


# p 56 not so short guide
tab = Table.from_cells(
    [[C(f"{j}") for j in range(i, i + 3)] for i in range(1, 9 + 1, 3)]
).set_align(r"@{a} c @{\hspace{1cm}} c @{|} c @ { b}")
tab.print()
compile_table(
    tab.render(),
    silent=False,
)


tab = Table.from_cells(
    [[C(f"{j}") for j in range(i, i + 3)] for i in range(1, 9 + 1, 3)]
).set_align(r"@{a} c @{\hspace{1cm}} c @{|} c @ { b}")
tab.print()
compile_table(
    tab.render(),
    silent=False,
)


tab = Table.from_cells(
    [[C(f"{j}") for j in range(i, i + 3)] for i in range(1, 9 + 1, 3)]
).set_align(r"@{a} c @{\hspace{1cm}} c @{|} c @ { b}")
cm = tabx.Cmidrule(1, 3, trim="lr", dim="0.2cm")
tab = tab / cm / tab
compile_table(
    tab.render(utils.render_body_extra),
    silent=False,
)


#  TODO: header and inserting rows is weird ; fix!
tab = Table(
    rows=[
        Row([C("Me"), C(":)"), C("Nice")]),
        Row([C("You"), C(":]"), C("Sleek")]),
        Row([C("Your reader"), C(":>"), C("Informative")]),
    ],
    header=[Row([C("Person"), C("Face"), C("Table")])],
    align="lcc",
)
tab = tab.insert_row(tabx.Midrule(), 1)
tab.print()
compile_table(
    tab.render(),
    silent=False,
)

# p 58 not so short guide
tab = Table(
    rows=[
        Row([C("Person"), C("Face"), C("Table")]),
        Row([C("Me"), C(":)"), C("Nice")]),
        Row([C("You"), C(":]"), C("Sleek")]),
        Row(
            [
                C("Your reader"),
                C("Not available", multicolumn=2, colspec="c"),
            ]
        ),
    ],
    align="lll",
)
tab = tab.insert_row(tabx.Midrule(), 1)
tab.print()
compile_table(
    tab.render(),
    silent=True,
)

C("VIPs", multirow=2, vpos="t", width="").render()

# p 58 not so short guide; listing 2.7
tab = Table(
    rows=[
        Row([C(""), C("Reaction", multicolumn=2, colspec="c")]),
        tabx.Cmidrule(2, 3),
        Row([C("Person"), C("Face"), C("Exclamation")]),
        Row([C("VIPs", multirow=2, vpos="t", width="*"), C(":)"), C("Nice")]),
        Row([C(""), C(":]"), C("Sleek")]),
        Row(
            [
                C("Your reader"),
                C("Not available", multicolumn=2, colspec="c"),
            ]
        ),
    ],
    align="lll",
)
tab = tab.insert_row(tabx.Midrule(), 2)
tab.print()
compile_table(
    tab.render(),
    silent=True,
)


tab = Table(
    rows=[
        Row([C(""), C("Reaction", multicolumn=2, colspec="c")]),
        tabx.Cmidrule(2, 3),
        Row([C("Person"), C("Face"), C("Exclamation")]),
        Row([C("VIPs", multirow=2, vpos="t", width="*"), C(":)"), C("Nice")]),
        Row([C(""), C(":]"), C("Sleek")]),
        Row(
            [
                C("Your reader"),
                C("Not available", multicolumn=2, colspec="c"),
            ]
        ),
    ],
    align="lll",
)


tab = Table.from_values(
    [
        [1, 2, 3],
        [1, 2, 3],
        ["hello", "world", "hello"],
    ]
)
tab.print()
compile_table(
    tab.render(),
    silent=True,
)


tab = Table.from_cells(
    cells := [
        [C(""), C("Reaction", multicolumn=2, colspec="c")],
        [C("Person"), C("Face"), C("Exclamation")],
        [C("VIPs", multirow=2, vpos="t", width="*"), C(":)"), C("Nice")],
        [C(""), C(":]"), C("Sleek")],
        [
            C("Your reader"),
            C("Not available", multicolumn=2, colspec="c"),
        ],
    ]
)
compile_table(
    tab.render(),
    silent=True,
)
