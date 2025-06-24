import operator

import pytest

import tabx
from tabx import Cell, Row, custom, utils
from tabx.custom import ColMap, RegCell, RegRow, RowMap


def test_align():
    with pytest.raises(
        ValueError,
        match="All cells must have a name when aligning",
    ):
        _ = custom.align_cells(
            [
                tabx.Cell("1", name="1"),
                tabx.Cell("1", name="1"),
                tabx.Cell("1"),
            ]
        )

    assert custom.align_cells(
        [
            tabx.Cell("1", name="2"),
            tabx.Cell("1", name="3"),
            tabx.Cell("1", name="1"),
        ]
    ) == [
        ("1", [Cell(name="1", value="1", multirow=1, multicolumn=1)]),
        ("2", [Cell(name="2", value="1", multirow=1, multicolumn=1)]),
        ("3", [Cell(name="3", value="1", multirow=1, multicolumn=1)]),
    ]

    assert custom.align_cells(
        [
            tabx.Cell("1", name="2"),
            tabx.Cell("1", name="3"),
            tabx.Cell("1", name="1"),
        ],
        [
            tabx.Cell("1", name="2"),
            tabx.Cell("1", name="3"),
            tabx.Cell("1", name="4"),
            tabx.Cell("1", name="1"),
        ],
    ) == [
        (
            "1",
            [
                Cell(name="1", value="1", multirow=1, multicolumn=1),
                Cell(name="1", value="1", multirow=1, multicolumn=1),
            ],
        ),
        (
            "2",
            [
                Cell(name="2", value="1", multirow=1, multicolumn=1),
                Cell(name="2", value="1", multirow=1, multicolumn=1),
            ],
        ),
        (
            "3",
            [
                Cell(name="3", value="1", multirow=1, multicolumn=1),
                Cell(name="3", value="1", multirow=1, multicolumn=1),
            ],
        ),
        (
            "4",
            [
                Cell(name="", value="", multirow=1, multicolumn=1),
                Cell(name="4", value="1", multirow=1, multicolumn=1),
            ],
        ),
    ]

    with pytest.raises(
        ValueError,
        match="All RegCells must have a name when aligning",
    ):
        _ = custom.align_reg_cells(
            [
                RegCell(est=Cell(value="1"), se=Cell("1"), name="1"),
                RegCell(est=Cell(value="1"), se=Cell("1"), name="2"),
                RegCell(est=Cell(value="1"), se=Cell("1")),
            ]
        )

    assert custom.align_reg_cells(
        [
            RegCell(est=Cell(value="1"), se=Cell("1"), name="1"),
            RegCell(est=Cell(value="1"), se=Cell("1"), name="2"),
            RegCell(est=Cell(value="1"), se=Cell("1"), name="3"),
        ]
    ) == [
        (
            "1",
            [
                RegCell(est=Cell(value="1"), se=Cell("1"), name="1"),
            ],
        ),
        (
            "2",
            [
                RegCell(est=Cell(value="1"), se=Cell("1"), name="2"),
            ],
        ),
        (
            "3",
            [
                RegCell(est=Cell(value="1"), se=Cell("1"), name="3"),
            ],
        ),
    ]


def test_regrow():
    regrow = RegRow(
        cells=(
            cells := [
                RegCell(est=Cell("1"), se=Cell("1"), name="1"),
                RegCell(est=Cell("1"), se=Cell("1"), name="2"),
                RegCell(est=Cell("1"), se=Cell("1"), name="3"),
            ]
        ),
        name="1",
    )

    assert regrow.cells == cells
    assert repr(regrow) == "RegRow(name=1, #cells=3)"
    assert len(regrow.render()) == 2

    assert isinstance(regrow.rows()[0], Row)
    assert isinstance(regrow.rows()[1], Row)

    regrow.add_cell(
        RegCell(est=Cell("1"), se=Cell("1"), name="4"),
    )

    with pytest.raises(TypeError):
        _ = regrow.add_cell(tabx.Cell("1"))

    assert len(regrow.cells) == 4
    assert regrow.cells[-1] == RegCell(est=Cell("1"), se=Cell("1"), name="4")


def test_model_data():
    md1 = tabx.ModelData(
        variables=list("abcde"),
        estimates=[1, 2, 3, 4, 5],
        ses=[1, 2, 3, 4, 5],
        name="M1",
    )

    assert repr(md1) == "ModelData(name=M1, #variables=5)"

    with pytest.raises(ValueError):
        _ = tabx.ModelData(
            variables=list("abcde"),
            estimates=[1, 2, 3, 4, 5],
            ses=[1, 2, 3, 4, 5, 6],
            name="M1",
        )

    with pytest.raises(ValueError):
        _ = tabx.ModelData(
            variables=list("abcdef"),
            estimates=[1, 2, 3, 4, 5],
            ses=[1, 2, 3, 4, 5],
            name="M1",
        )

    m1 = {
        "variable": ["v1", "v2", "v3", "v4", "v5"],
        "estimates": [1, 2, 3, 4, 5],
        "se": [0.1, 0.2, 0.3, 0.4, 0.5],
        "extra_data": {
            r"$n$": 10,
            "session": 1,
        },
    }
    mod1 = tabx.ModelData.from_dict(m1, name="(M1)")
    assert mod1.extra_data == {
        r"$n$": 10,
        "session": 1,
    }

    assert len(col := custom.make_est_col(mod1)) == 5
    assert all(isinstance(f, RegCell) for f in col)
    assert [f.est.name for f in col] == ["v1", "v2", "v3", "v4", "v5"]
    assert [f.est.value for f in col] == [f"{i}" for i in range(1, 6)]


def test_model_table():
    m1 = {
        "variable": ["v1", "v2", "v3", "v4", "v5"],
        "estimates": [1, 2, 3, 4, 5],
        "se": [0.1, 0.2, 0.3, 0.4, 0.5],
        "extra_data": {
            r"$n$": 10,
            "session": 1,
        },
    }
    mod1 = tabx.ModelData.from_dict(m1, name="(M1)")

    tab = custom.models_table(
        models=[mod1, mod1],
        col_maps=ColMap(
            mapping={
                (1, 2): "All vars",
            },
            include_cmidrule=False,
        ),
        order_map={
            "v1": 0,
            "v2": 1,
            "v3": 2,
            "v4": 3,
            "v5": 4,
            r"$n$": 5,
            "session": 6,
        },
    )

    assert tab.render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{All vars} \\",
        r"   & (M1) & (M1) \\",
        r"  \midrule",
        r"  v1 & 1 & 1 \\",
        r"   & (0.1) & (0.1) \\",
        r"  v2 & 2 & 2 \\",
        r"   & (0.2) & (0.2) \\",
        r"  v3 & 3 & 3 \\",
        r"   & (0.3) & (0.3) \\",
        r"  v4 & 4 & 4 \\",
        r"   & (0.4) & (0.4) \\",
        r"  v5 & 5 & 5 \\",
        r"   & (0.5) & (0.5) \\",
        r"  \midrule",
        r"  $n$ & 10 & 10 \\",
        r"  session & 1 & 1 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    tab = custom.models_table(
        models=[mod1, mod1],
        col_maps=ColMap(
            mapping={
                (1, 2): "All vars",
            },
            include_cmidrule=False,
        ),
        order_map={
            "v1": 0,
            "v2": 1,
            "v3": 2,
            "v4": 3,
            "v5": 4,
            r"$n$": 5,
            "session": 6,
        },
        var_name="variable",
    )
    assert tab.render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{All vars} \\",
        r"  variable & (M1) & (M1) \\",
        r"  \midrule",
        r"  v1 & 1 & 1 \\",
        r"   & (0.1) & (0.1) \\",
        r"  v2 & 2 & 2 \\",
        r"   & (0.2) & (0.2) \\",
        r"  v3 & 3 & 3 \\",
        r"   & (0.3) & (0.3) \\",
        r"  v4 & 4 & 4 \\",
        r"   & (0.4) & (0.4) \\",
        r"  v5 & 5 & 5 \\",
        r"   & (0.5) & (0.5) \\",
        r"  \midrule",
        r"  $n$ & 10 & 10 \\",
        r"  session & 1 & 1 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    tab = custom.models_table(
        models=[mod1, mod1],
        col_maps=ColMap(
            mapping={
                (1, 2): "All vars",
            },
            include_cmidrule=False,
        ),
        order_map={
            "v1": 0,
            "v2": 1,
            "v3": 2,
            "v4": 3,
            "v5": 4,
            r"$n$": 5,
            "session": 6,
        },
        var_name="",
    )
    assert tab.render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{All vars} \\",
        r"   & (M1) & (M1) \\",
        r"  \midrule",
        r"  v1 & 1 & 1 \\",
        r"   & (0.1) & (0.1) \\",
        r"  v2 & 2 & 2 \\",
        r"   & (0.2) & (0.2) \\",
        r"  v3 & 3 & 3 \\",
        r"   & (0.3) & (0.3) \\",
        r"  v4 & 4 & 4 \\",
        r"   & (0.4) & (0.4) \\",
        r"  v5 & 5 & 5 \\",
        r"   & (0.5) & (0.5) \\",
        r"  \midrule",
        r"  $n$ & 10 & 10 \\",
        r"  session & 1 & 1 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]


def test_desc_data():
    dd1 = tabx.DescData(
        variables=list("abcde"),
        values=[1, 2, 3, 4, 5],
        name="M1",
    )

    assert repr(dd1) == "DescData(name=M1, #variables=5)"

    with pytest.raises(ValueError):
        _ = tabx.DescData(
            variables=list("abcdef"),
            values=[1, 2, 3, 4, 5],
            name="M1",
        )

    m1 = {
        "variable": ["v1", "v2", "v3", "v4", "v5"],
        "estimates": [1, 2, 3, 4, 5],
        "se": [0.1, 0.2, 0.3, 0.4, 0.5],
        "extra_data": {
            r"$n$": 10,
            "session": 1,
        },
    }
    mod1 = tabx.ModelData.from_dict(m1, name="(M1)")
    assert mod1.extra_data == {
        r"$n$": 10,
        "session": 1,
    }

    m1 = {
        "variable": ["v1", "v2", "v3", "v4", "v5"],
        "values": [1.0, 2.0, 3, 4.0, 5],
        "extra_data": {
            r"$n$": 10,
            "session": 1,
        },
    }
    mod1 = tabx.DescData.from_dict(m1, name="y")
    assert mod1.extra_data == {
        r"$n$": 10,
        "session": 1,
    }

    col = custom.make_desc_col(mod1)
    assert len(col) == 5
    assert all(isinstance(f, Cell) for f in col)
    assert [f.name for f in col] == ["v1", "v2", "v3", "v4", "v5"]
    assert [f.value for f in col] == ["1.0", "2.0", "3", "4.0", "5"]


def test_desc_data_from_values():
    import polars as pl
    import tabx
    from tabx import DescData

    data = pl.DataFrame(
        [
            ["$x_1$", -0.44, 1.14],
            ["$x_2$", 0.58, -0.63],
            ["$x_3$", 0.64, -1.0],
        ],
        schema=["variable", "A", "B"],
        orient="row",
    )
    desc_datas = DescData.from_values(
        data.rows(),
        column_names=data.columns[1:],  # Exclude 'variable' column
    )
    tab = tabx.descriptives_table(
        desc_datas,
        col_maps=tabx.ColMap(mapping={(1, 2): "First"}),
        include_midrule=True,
        fill_value="-",
    )

    assert tab.render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{First} \\",
        r"  \cmidrule(lr){2-3}",
        r"   & A & B \\",
        r"  \midrule",
        r"  $x_1$ & -0.44 & 1.14 \\",
        r"  $x_2$ & 0.58 & -0.63 \\",
        r"  $x_3$ & 0.64 & -1.0 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    desc_datas = DescData.from_values(
        data.rows(),
        column_names=data.columns[1:],  # Exclude 'variable' column
        extras=[
            {"n": 10, "misc": 1},
            {"n": 20, "misc": 0},
        ],
    )
    tab = tabx.descriptives_table(
        desc_datas,
        col_maps=tabx.ColMap(mapping={(1, 2): "First"}),
        include_midrule=True,
        fill_value="-",
        order_map={"n": 0, "misc": 1},
    )
    assert tab.render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{First} \\",
        r"  \cmidrule(lr){2-3}",
        r"   & A & B \\",
        r"  \midrule",
        r"  $x_1$ & -0.44 & 1.14 \\",
        r"  $x_2$ & 0.58 & -0.63 \\",
        r"  $x_3$ & 0.64 & -1.0 \\",
        r"  \midrule",
        r"  n & 10 & 20 \\",
        r"  misc & 1 & 0 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]


def test_model_data_from_values():
    import polars as pl
    import tabx
    from tabx import ModelData

    data = pl.DataFrame(
        [
            ["$x_1$", -0.44, 1.14, 1.04, 1.12],
            ["$x_2$", 0.58, -0.63, -0.92, 0.74],
            ["$x_3$", 0.64, -1.0, 1.15, 0.78],
        ],
        schema=["variable", "ests1", "ses1", "ests2", "ses2"],
        orient="row",
    )
    model_datas = ModelData.from_values(
        data.rows(),
        model_names=["M1", "M2"],
    )
    tab = tabx.models_table(
        model_datas,
        col_maps=tabx.ColMap(mapping={(1, 2): "OLS"}),
        include_midrule=True,
        fill_value="-",
        var_name="",
    )

    assert tab.render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{OLS} \\",
        r"  \cmidrule(lr){2-3}",
        r"   & M1 & M2 \\",
        r"  \midrule",
        r"  $x_1$ & -0.44 & 1.04 \\",
        r"   & (1.14) & (1.12) \\",
        r"  $x_2$ & 0.58 & -0.92 \\",
        r"   & (-0.63) & (0.74) \\",
        r"  $x_3$ & 0.64 & 1.15 \\",
        r"   & (-1.0) & (0.78) \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    model_datas = ModelData.from_values(
        data.rows(),
        model_names=["M1", "M2"],
        extras=[
            {"n": 10, "misc": 1},
            {"n": 20, "misc": 0},
        ],
    )
    tab = tabx.models_table(
        model_datas,
        col_maps=tabx.ColMap(mapping={(1, 2): "OLS"}),
        include_midrule=True,
        fill_value="-",
        var_name="",
        order_map={"misc": 0, "n": 1},
    )
    assert tab.render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{OLS} \\",
        r"  \cmidrule(lr){2-3}",
        r"   & M1 & M2 \\",
        r"  \midrule",
        r"  $x_1$ & -0.44 & 1.04 \\",
        r"   & (1.14) & (1.12) \\",
        r"  $x_2$ & 0.58 & -0.92 \\",
        r"   & (-0.63) & (0.74) \\",
        r"  $x_3$ & 0.64 & 1.15 \\",
        r"   & (-1.0) & (0.78) \\",
        r"  \midrule",
        r"  misc & 1 & 0 \\",
        r"  n & 10 & 20 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    with pytest.raises(ValueError):
        model_datas = ModelData.from_values(
            data.rows(),
            model_names=["M1"],
            extras=[
                {"n": 10, "misc": 1},
                {"n": 20, "misc": 0},
            ],
        )


def test_header():
    m1 = {
        "variable": ["v1", "v2", "v3", "v4", "v5"],
        "values": [1.0, 2.0, 3, 4.0, 5],
        "extra_data": {
            r"$n$": 10,
            "session": 1,
        },
    }
    mod1 = tabx.DescData.from_dict(m1, name="y")
    # Header
    header = custom.construct_header(
        [mod1, mod1, mod1],
        ColMap(
            mapping={
                (1, 1): "All vars",
            },
            include_cmidrule=False,
        ),
    )

    assert header[0].cells == [
        Cell(name="", value="", multirow=1, multicolumn=1),
        Cell(name="All vars", value="All vars", multirow=1, multicolumn=1),
        Cell(name="", value="", multirow=1, multicolumn=1),
        Cell(name="", value="", multirow=1, multicolumn=1),
    ]
    assert header[1].cells == [
        Cell(name="", value="variable", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
    ]
    assert header[2] == tabx.Midrule()

    # cmap with multiple keys
    header = custom.construct_header(
        [mod1, mod1, mod1, mod1],
        ColMap(
            mapping={
                (1, 2): "Some vars",
                (2, 4): "Other vars",
            },
            include_cmidrule=False,
        ),
    )
    assert header[0].cells == [
        Cell(name="", value="", multirow=1, multicolumn=1),
        Cell(name="Some vars", value="Some vars", multirow=1, multicolumn=2),
        Cell(name="Other vars", value="Other vars", multirow=1, multicolumn=3),
    ]
    assert header[1].cells == [
        Cell(name="", value="variable", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
    ]
    assert header[2] == tabx.Midrule()

    # multiple cmaps
    header = custom.construct_header(
        [mod1, mod1, mod1, mod1],
        [
            ColMap(
                mapping={
                    (1, 4): "All vars",
                },
                include_cmidrule=False,
            ),
            ColMap(
                mapping={
                    (1, 2): "Some vars",
                    (2, 4): "Other vars",
                },
                include_cmidrule=False,
            ),
        ],
    )
    assert header[0].cells == [
        Cell(name="", value="", multirow=1, multicolumn=1),
        Cell(name="All vars", value="All vars", multirow=1, multicolumn=4),
    ]
    assert header[1].cells == [
        Cell(name="", value="", multirow=1, multicolumn=1),
        Cell(name="Some vars", value="Some vars", multirow=1, multicolumn=2),
        Cell(name="Other vars", value="Other vars", multirow=1, multicolumn=3),
    ]
    assert header[2].cells == [
        Cell(name="", value="variable", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
    ]
    assert header[3] == tabx.Midrule()

    # No colmaps
    header = custom.construct_header(
        [mod1, mod1, mod1, mod1],
    )
    assert header[0].cells == [
        Cell(name="", value="variable", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=1),
    ]
    assert header[1] == tabx.Midrule()


def test_extra_data_rows():
    m1 = {
        "variable": ["v1", "v2", "v3", "v4", "v5"],
        "values": [1.0, 2.0, 3, 4.0, 5],
        "extra_data": {
            "n": 10,
            "session": 1,
        },
    }
    mod1 = tabx.DescData.from_dict(m1, name="y")

    rows = custom.extra_data_rows([mod1], order_map={"n": 1, "session": 0})
    assert rows[0].cells == [
        Cell(name="session", value="session", multirow=1, multicolumn=1),
        Cell(name="session", value="1", multirow=1, multicolumn=1),
    ]
    assert rows[1].cells == [
        Cell(name="n", value="n", multirow=1, multicolumn=1),
        Cell(name="n", value="10", multirow=1, multicolumn=1),
    ]

    rows = custom.extra_data_rows([mod1], order_map={"n": 0, "session": 1})
    assert rows[1].cells == [
        Cell(name="session", value="session", multirow=1, multicolumn=1),
        Cell(name="session", value="1", multirow=1, multicolumn=1),
    ]
    assert rows[0].cells == [
        Cell(name="n", value="n", multirow=1, multicolumn=1),
        Cell(name="n", value="10", multirow=1, multicolumn=1),
    ]


def test_col_maps():
    cm1 = ColMap(
        mapping={
            (1, 5): "All vars",
        },
        include_cmidrule=False,
    )
    cm2 = ColMap(
        mapping={
            (1, 3): r"\texttt{Pubs}",
            (4, 5): r"\texttt{C3}",
        },
        include_cmidrule=False,
    )

    (row,) = custom.parse_col_maps(cm1, 5)
    assert row.cells == [
        # Padding for names
        Cell(name="", value="", multirow=1, multicolumn=1),
        # All vars heading
        Cell(name="All vars", value="All vars", multirow=1, multicolumn=5),
    ]

    cm2 = ColMap(
        mapping={
            (1, 5): "All vars",
        },
        include_cmidrule=True,
    )
    (row, cmr) = custom.parse_col_maps(cm2, 5)
    assert isinstance(cmr, tabx.Cmidrules)
    assert isinstance(row, Row)
    assert cmr.values == [tabx.Cmidrule(start=2, end=6, trim="lr")]

    with pytest.raises(ValueError):
        _ = custom.parse_col_maps(cm1, 4)  # 5 > 4; not enough columns

    cm3 = ColMap(
        mapping={
            (1, 3): "y",
            (5, 7): "z",
        },
        include_cmidrule=False,
    )
    (row,) = custom.parse_col_maps(cm3, 9)

    assert row.cells == [
        # padding name
        Cell(name="", value="", multirow=1, multicolumn=1),
        Cell(name="y", value="y", multirow=1, multicolumn=3),
        # padding for hole in between middle
        Cell(name="", value="", multirow=1, multicolumn=1),
        Cell(name="z", value="z", multirow=1, multicolumn=3),
        # padding while map doesn't fit all columns
        Cell(name="", value="", multirow=1, multicolumn=1),
        Cell(name="", value="", multirow=1, multicolumn=1),
    ]


def test_row_maps():
    rm1 = RowMap(
        mapping={
            (1, 5): "All vars",
        },
    )
    rmp = custom.RmParams(
        n_vars=5,
        total=6,
        header=[],
        extra_rows=[],
        include_extra=False,
        has_header=False,
        has_extra=False,
    )

    rm_col = custom.construct_rm_col(rm1, rmp)

    assert rm_col.shape == (5, 1)
    assert (
        rm_col.render()
        == r"""\multirow{5}{*}{All vars} \\
 \\
 \\
 \\
 \\"""
    )

    rm_col = custom.handle_rm(rm1, rmp)
    assert rm_col.shape == (5, 1)
    assert (
        rm_col.render()
        == r"""\multirow{5}{*}{All vars} \\
 \\
 \\
 \\
 \\"""
    )

    with pytest.raises(ValueError):
        rm1 = RowMap(
            mapping={
                (1, 5): "All vars",
            },
        )
        rmp = custom.RmParams(
            n_vars=5,
            total=4,  # RowMap exceeds total rows
            header=[],
            extra_rows=[],
            include_extra=False,
            has_header=False,
            has_extra=False,
        )
        rm_col = custom.handle_rm(rm1, rmp)

    rm1 = RowMap(
        mapping={
            (1, 5): "All vars",
        },
    )
    rmp = custom.RmParams(
        n_vars=5,
        total=5,  # RowMap exceeds total rows
        header=[Row([Cell("header")])],
        extra_rows=[],
        include_extra=False,
        has_header=True,
        has_extra=False,
    )
    rm_col = custom.handle_rm(rm1, rmp)
    assert rm_col.shape == (6, 1)
    assert rm_col.render().splitlines() == [
        r" \\",
        r"\multirow{5}{*}{All vars} \\",
        r" \\",
        r" \\",
        r" \\",
        r" \\",
    ]

    # Holes
    rm1 = RowMap(
        mapping={
            (1, 2): "All vars",
            (4, 5): "Other vars",
            (6, 7): "Extra vars",
        },
    )
    rmp = custom.RmParams(
        n_vars=5,  # 5 vars
        total=7,  # 2 extra variables
        header=[],
        extra_rows=[Row([Cell("extra")]), Row([Cell("extra")])],
        include_extra=True,
        has_header=False,
        has_extra=True,
    )
    rm_col = custom.construct_rm_col(rm1, rmp)
    assert rm_col.render().splitlines() == [
        r"\multirow{2}{*}{All vars} \\",
        r" \\",
        r" \\",
        r"\multirow{2}{*}{Other vars} \\",
        r" \\",
        r" \\",
        r"\multirow{2}{*}{Extra vars} \\",
        r" \\",
    ]

    # check for holes in mappings; one hole between first and second
    pairs = sorted(rm1.mapping.items(), key=operator.itemgetter(0))
    holes = custom.find_holes(pairs)
    assert holes == [0, 1, 0]

    # Holes
    rm1 = RowMap(
        mapping={
            (1, 2): "All vars",
        },
    )
    rmp = custom.RmParams(
        n_vars=5,  # 5 vars
        total=7,  # 2 extra variables
        header=[],
        extra_rows=[Row([Cell("extra")]), Row([Cell("extra")])],
        include_extra=True,
        has_header=False,
        has_extra=True,
    )
    rm_col = custom.construct_rm_col(rm1, rmp)
    assert rm_col.render().splitlines() == [
        r"\multirow{2}{*}{All vars} \\",
        r" \\",
        r" \\",
        r" \\",
        r" \\",
        r" \\",
        r" \\",
        r" \\",
    ]


def test_base():
    m1 = {
        "variable": ["v1", "v2", "v3", "v4", "v5"],
        "values": [1.0, 2.0, 3, 4.0, 5],
        "extra_data": {
            r"$n$": 10,
            "session": 1,
        },
    }
    mod1 = tabx.DescData.from_dict(m1, name="y")

    cols = [custom.make_desc_col(m) for m in [mod1, mod1]]
    aligned = custom.align_cells(*cols)
    rows = [Row(cells=[Cell(name=name, value=name)] + cells) for name, cells in aligned]
    order_map = {
        "v1": 0,
        "v2": 1,
        "v3": 2,
        "v4": 3,
        "v5": 4,
        r"$n$": 5,
        "session": 6,
    }

    rows = sorted(
        rows,
        key=lambda x: order_map.get(x.cells[0].name, float("inf")),
    )
    base = custom.construct_base(
        rows=rows,
        objs=[mod1, mod1],
        col_maps=ColMap(
            mapping={
                (1, 2): "All vars",
            },
            include_cmidrule=False,
        ),
        order_map=order_map,
    )

    # 1 variable name column, 2 model columns
    assert base.shape == (11, 3)
    assert base.render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{All vars} \\",
        r"   & y & y \\",
        r"  \midrule",
        r"  v1 & 1.0 & 1.0 \\",
        r"  v2 & 2.0 & 2.0 \\",
        r"  v3 & 3 & 3 \\",
        r"  v4 & 4.0 & 4.0 \\",
        r"  v5 & 5 & 5 \\",
        r"  \midrule",
        r"  $n$ & 10 & 10 \\",
        r"  session & 1 & 1 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    # Same as above
    base = custom.descriptives_table(
        desc_datas=[mod1, mod1],
        col_maps=ColMap(
            mapping={
                (1, 2): "All vars",
            },
            include_cmidrule=False,
        ),
        order_map={
            "v1": 0,
            "v2": 1,
            "v3": 2,
            "v4": 3,
            "v5": 4,
            r"$n$": 5,
            "session": 6,
        },
    )
    # 1 variable name column, 2 model columns
    assert base.shape == (11, 3)
    assert base.render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{All vars} \\",
        r"   & y & y \\",
        r"  \midrule",
        r"  v1 & 1.0 & 1.0 \\",
        r"  v2 & 2.0 & 2.0 \\",
        r"  v3 & 3 & 3 \\",
        r"  v4 & 4.0 & 4.0 \\",
        r"  v5 & 5 & 5 \\",
        r"  \midrule",
        r"  $n$ & 10 & 10 \\",
        r"  session & 1 & 1 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    assert custom.descriptives_table(
        desc_datas=[mod1, mod1],
        col_maps=ColMap(
            mapping={
                (1, 2): "All vars",
            },
            include_cmidrule=False,
        ),
        order_map={
            "v1": 0,
            "v2": 1,
            "v3": 2,
            "v4": 3,
            "v5": 4,
            r"$n$": 5,
            "session": 6,
        },
    ).render().splitlines() == [
        r"\begin{tabular}{@{}lcc@{}}",
        r"  \toprule",
        r"   & \multicolumn{2}{c}{All vars} \\",
        r"   & y & y \\",
        r"  \midrule",
        r"  v1 & 1.0 & 1.0 \\",
        r"  v2 & 2.0 & 2.0 \\",
        r"  v3 & 3 & 3 \\",
        r"  v4 & 4.0 & 4.0 \\",
        r"  v5 & 5 & 5 \\",
        r"  \midrule",
        r"  $n$ & 10 & 10 \\",
        r"  session & 1 & 1 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    base = custom.construct_base(
        rows=rows,
        objs=[mod1, mod1],
        col_maps=ColMap(
            mapping={
                (1, 2): "All vars",
            },
            include_cmidrule=False,
        ),
        row_maps=RowMap(
            mapping={
                (1, 2): "All vars",
                (4, 5): "Other vars",
                (6, 7): "Extra vars",
            },
        ),
        order_map={
            "v1": 0,
            "v2": 1,
            "v3": 2,
            "v4": 3,
            "v5": 4,
            r"$n$": 5,
            "session": 6,
        },
    )
    assert base.render().splitlines() == [
        r"\begin{tabular}{@{}llcc@{}}",
        r"  \toprule",
        r"   &  & \multicolumn{2}{c}{All vars} \\",
        r"   &  & y & y \\",
        r"  \midrule",
        r"  \multirow{2}{*}{All vars} & v1 & 1.0 & 1.0 \\",
        r"   & v2 & 2.0 & 2.0 \\",
        r"   & v3 & 3 & 3 \\",
        r"  \multirow{2}{*}{Other vars} & v4 & 4.0 & 4.0 \\",
        r"   & v5 & 5 & 5 \\",
        r"  \midrule",
        r"  \multirow{2}{*}{Extra vars} & $n$ & 10 & 10 \\",
        r"   & session & 1 & 1 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    with pytest.raises(ValueError):
        base = custom.construct_base(
            rows=rows,
            objs=[mod1, mod1],
            col_maps=ColMap(
                mapping={
                    (1, 2): "All vars",
                },
                include_cmidrule=False,
            ),
            row_maps=[
                RowMap(
                    mapping={
                        # Row map overlaps with midrule
                        (1, 7): "All data",
                    },
                ),
                RowMap(
                    mapping={
                        (1, 5): "Experiment 1",
                        (6, 7): "Experiment 2",
                    },
                ),
            ],
            include_header=True,
        )


def test_row_maps_extra():
    m1 = {
        "variable": ["v1", "v2", "v3", "v4", "v5"],
        "values": [1.0, 2.0, 3, 4.0, 5],
        "extra_data": {
            r"$n$": 10,
            "session": 1,
        },
    }
    mod1 = tabx.DescData.from_dict(m1, name="y")

    cols = [custom.make_desc_col(m) for m in [mod1, mod1]]
    aligned = custom.align_cells(*cols)
    rows = [Row(cells=[Cell(name=name, value=name)] + cells) for name, cells in aligned]
    order_map = {
        "v1": 0,
        "v2": 1,
        "v3": 2,
        "v4": 3,
        "v5": 4,
        r"$n$": 5,
        "session": 6,
    }
    rows = sorted(
        rows,
        key=lambda x: order_map.get(x.cells[0].name, float("inf")),
    )
    base = custom.construct_base(
        rows=rows,
        objs=[mod1, mod1],
        col_maps=ColMap(
            mapping={
                (1, 2): "All vars",
            },
            include_cmidrule=False,
        ),
        order_map=order_map,
    )

    base = custom.construct_base(
        rows=rows,
        objs=[mod1, mod1],
        col_maps=ColMap(
            mapping={
                (1, 2): "All vars",
            },
            include_cmidrule=False,
        ),
        row_maps=[
            RowMap(
                mapping={
                    # Row map overlaps with midrule
                    (1, 5): "All data",
                },
            ),
            RowMap(
                mapping={
                    (1, 2): "Experiment 1",
                    (3, 5): "Experiment 2",
                },
            ),
        ],
        include_header=True,
        order_map=order_map,
    )
    assert base.render().splitlines() == [
        r"\begin{tabular}{@{}lllcc@{}}",
        r"  \toprule",
        r"   &  &  & \multicolumn{2}{c}{All vars} \\",
        r"   &  &  & y & y \\",
        r"  \midrule",
        r"  \multirow{5}{*}{All data} & \multirow{2}{*}{Experiment 1} & v1 & 1.0 & 1.0 \\",
        r"   &  & v2 & 2.0 & 2.0 \\",
        r"   & \multirow{3}{*}{Experiment 2} & v3 & 3 & 3 \\",
        r"   &  & v4 & 4.0 & 4.0 \\",
        r"   &  & v5 & 5 & 5 \\",
        r"  \midrule",
        r"   &  & $n$ & 10 & 10 \\",
        r"   &  & session & 1 & 1 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    # Some row map stuff

    m1 = tabx.ModelData(
        **{
            "variables": ["C1", "C2", "C3"],
            "estimates": [-0.27, -0.03, -0.02],
            "ses": [0.96, 1.0, 1.0],
            "name": "01",
            "extra_data": {},
        }
    )
    m2 = tabx.ModelData(
        **{
            "variables": ["C1", "C2", "C3"],
            "estimates": [-0.6, -0.54, -0.52],
            "ses": [0.8, 0.84, 0.85],
            "name": "O2",
            "extra_data": {},
        }
    )

    tab = tabx.models_table(
        [m1, m2],
        var_name="",
        row_maps=[tabx.RowMap({(1, 3): "All"})],
        include_extra=False,
    ).render()
    tab2 = tabx.models_table(
        [m1, m2],
        var_name="",
        row_maps=[tabx.RowMap({(1, 3): "All"})],
        include_extra=True,
    ).render()

    test_lines = [
        r"\begin{tabular}{@{}llcc@{}}",
        r"  \toprule",
        r"   &  & 01 & O2 \\",
        r"  \midrule",
        r"  \multirow{3}{*}{All} & C1 & -0.27 & -0.6 \\",
        r"   &  & (0.96) & (0.8) \\",
        r"   & C2 & -0.03 & -0.54 \\",
        r"   &  & (1.0) & (0.84) \\",
        r"   & C3 & -0.02 & -0.52 \\",
        r"   &  & (1.0) & (0.85) \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    assert tab.splitlines() == test_lines
    assert tab2.splitlines() == test_lines

    test_lines2 = [
        r"\begin{tabular}{@{}llcc@{}}",
        r"  \toprule",
        r"   &  & 01 & O2 \\",
        r"  \midrule",
        r"  \multirow{3}{*}{All} & C1 & -0.27 & -0.6 \\",
        r"   &  & (0.96) & (0.8) \\",
        r"   & C2 & -0.03 & -0.54 \\",
        r"   &  & (1.0) & (0.84) \\",
        r"   & C3 & -0.02 & -0.52 \\",
        r"   &  & (1.0) & (0.85) \\",
        r"  \midrule",
        r"   & N & 100 & 100 \\",
        r"  \bottomrule",
        r"\end{tabular}",
    ]

    m1 = tabx.ModelData(
        **{
            "variables": ["C1", "C2", "C3"],
            "estimates": [-0.27, -0.03, -0.02],
            "ses": [0.96, 1.0, 1.0],
            "name": "01",
            "extra_data": {"N": 100},
        }
    )
    m2 = tabx.ModelData(
        **{
            "variables": ["C1", "C2", "C3"],
            "estimates": [-0.6, -0.54, -0.52],
            "ses": [0.8, 0.84, 0.85],
            "name": "O2",
            "extra_data": {"N": 100},
        }
    )
    for ie, tlines in zip([False, True], [test_lines, test_lines2]):
        tab = tabx.models_table(
            [m1, m2],
            var_name="",
            row_maps=[tabx.RowMap({(1, 3): "All"})],
            include_extra=ie,
        )
        assert tab.render().splitlines() == tlines, tlines
