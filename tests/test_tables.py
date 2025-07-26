import re

import pytest

import tabx
import tabx.table as tabm
from tabx import Cell, Cmidrule, Cmidrules, Columns, Midrule, Row
from tabx.table import interval_conditions


def test_cell():
    F = Cell

    with pytest.raises(ValueError):
        _ = F("1", multicolumn=2, multirow=2)

    assert F("1", style="bold").render() == r"\textbf{1}"
    assert F("1", style="italic").render() == r"\textit{1}"
    assert F("1", style="math").render() == r"$1$"
    assert F("1", style="none").render() == "1"

    with pytest.raises(ValueError):
        _ = F("1", multicolumn=1, multirow=1, style="random").render()

    assert F("1", multicolumn=2).render() == r"\multicolumn{2}{c}{1}"
    assert F("1", multicolumn=2, colspec="r").render() == r"\multicolumn{2}{r}{1}"


def test_utils():
    rows = [
        Row([Cell(name="mf", value="1", multicolumn=3)]),
        Cmidrules(
            values=[
                Cmidrule(start=1, end=2),
                Cmidrule(start=3, end=3),
            ]
        ),
        Midrule(),
    ]

    assert tabm.len_rows(rows) == {3}

    assert tabm.len_rows([Cmidrule(start=1, end=2)]) == set()
    assert (
        tabm.len_rows(
            [
                Cmidrule(start=1, end=2),
                Cmidrule(start=3, end=3),
                Midrule(),
            ]
        )
        == set()
    )

    assert tabm.len_rows([Row([Cell(name="mf", value="1", multicolumn=3)])]) == {3}


def test_columns():
    out = Columns(
        [
            cm1 := Cmidrule(start=1, end=2),
            cm2 := Cmidrule(start=3, end=3),
            Midrule(),
        ]
    )
    assert out.shape == (3, 3)

    col = Columns(
        [
            Row([Cell(name="mf", value="1", multicolumn=3)]),
            Cmidrule(start=1, end=2),
            Midrule(),
        ]
    )

    out = col / Cmidrule(start=1, end=3)
    assert out.shape == (4, 3)

    with pytest.raises(ValueError):
        Cell(name="mf", value="1", multicolumn=0)

    with pytest.raises(ValueError):
        Cell(name="mf", value="1", multirow=0)

    col = Columns(
        rows := [
            Row([Cell(name="mf", value="1", multicolumn=3)]),
            Cmidrule(start=1, end=2),
            Midrule(),
        ]
    )
    ncol = col.insert_row(row=Midrule(), index=0)
    assert ncol.rows[0] == Midrule()
    assert ncol.rows[1:] == rows

    ncol = col.insert_row(row=Midrule(), index=-1)
    assert ncol.rows[-2:] == [Midrule(), Midrule()]

    nb = col.nrows
    with pytest.raises(IndexError):
        ncol = col.insert_row(row=Midrule(), index=nb + 1)

    ncol = col.insert_row(row=Midrule(), index=nb - 1)

    assert (
        col.insert_row(row=Midrule(), index=nb - 1)
        # inserting at last place equal to append
        == col.append_row(row=Midrule())
    )

    with pytest.raises(TypeError):
        col.append_row(row=1)
    with pytest.raises(TypeError):
        col.prepend_row(row=1)

    with pytest.raises(TypeError):
        col.insert_row(row=1, index=1)

    # with pytest.raises(ValueError):
    #     col.set_align("c")

    assert repr(col) == "Columns(nrows=3, ncols=3)"

    col = Columns(
        rows := [
            Row([Cell(name="mf", value="1", multicolumn=3)]),
            Cmidrule(start=1, end=2),
            Midrule(),
        ]
    )

    with pytest.raises(TypeError):
        col | 1


def test_columns_from_cells():
    F = tabx.Cell

    c1 = tabx.Columns.from_cells(
        cells := [
            F("A"),
            F("A"),
            F("A"),
            F("A"),
        ]
    )

    assert c1.shape == (4, 1)
    assert c1.render().splitlines() == [
        r"A \\",
        r"A \\",
        r"A \\",
        r"A \\",
    ]
    assert tabx.Table.from_cells(cells).columns == c1

    c2 = tabx.Columns.from_cells(
        [
            [F("A"), F("B")],
            [F("A"), F("B")],
            [F("A"), F("B")],
            [F("A"), F("B")],
        ]
    )
    assert c2.shape == (4, 2)
    assert c2.render().splitlines() == [
        r"A & B \\",
        r"A & B \\",
        r"A & B \\",
        r"A & B \\",
    ]

    with pytest.raises(TypeError):
        c3 = tabx.Columns.from_cells(
            [
                F("A"),
                1,  # typerror
                F("A"),
                F("A"),
            ]
        )


def test_join_columns():
    out = Columns(
        [
            cm1 := Cmidrule(start=1, end=2),
            cm2 := Cmidrule(start=3, end=3),
            Midrule(),
        ]
    )
    assert out.shape == (3, 3)

    with pytest.raises(
        ValueError,
        match=re.escape("All columns must have same number of rows. Found: [2, 3]"),
    ):
        tabm.join_columns([out, tabm.empty_columns(2, 2)])

    with pytest.raises(TypeError):
        tabm.join_columns([out, Cmidrule(start=1, end=2)])

    with pytest.raises(
        ValueError, match="Row cells must be empty when mixing Cmidrule and Row"
    ):
        _ = tabm.join_columns(
            [
                Columns(
                    [
                        Row([Cell(name="mf", value="1", multicolumn=3)]),
                        Row([Cell(name="mf", value="1", multicolumn=3)]),
                        Midrule(),
                    ]
                ),
                Columns(
                    [
                        Cmidrule(start=1, end=2),
                        Cmidrule(start=3, end=3),
                        Midrule(),
                    ]
                ),
            ]
        )

    with pytest.raises(
        ValueError, match="Row cells must be empty when mixing Midrule and Row"
    ):
        _ = tabm.join_columns(
            [
                Columns(
                    [
                        Row([Cell(name="mf", value="1", multicolumn=3)]),
                    ]
                ),
                Columns(
                    [
                        Midrule(),
                    ]
                ),
            ]
        )

    with pytest.raises(
        ValueError, match="Row cells must be empty when mixing Cmidrules and Row"
    ):
        _ = tabm.join_columns(
            [
                Columns(
                    [
                        Row([Cell(name="mf", value="1", multicolumn=3)]),
                    ]
                ),
                Columns(
                    [
                        Cmidrules(
                            [
                                Cmidrule(start=1, end=2),
                                Cmidrule(start=3, end=5),
                            ]
                        ),
                    ]
                ),
            ]
        )

    # Concatenate cmidrules
    out = tabm.join_columns(
        [
            Columns(
                [
                    Cmidrules(
                        [
                            Cmidrule(start=1, end=2),
                            Cmidrule(start=3, end=5),
                        ]
                    ),
                ]
            ),
            Columns(
                [
                    Cmidrules(
                        [
                            Cmidrule(start=1, end=4),
                        ]
                    ),
                ]
            ),
        ]
    )
    assert out.shape == (1, 9)
    cmid = out.rows[0]
    assert cmid.values == [
        Cmidrule(start=1, end=2, trim="lr"),
        Cmidrule(start=3, end=5, trim="lr"),
        Cmidrule(start=6, end=9, trim="lr"),
    ]


def test_join_rows():
    row = Row([Cell(name="mf", value="1", multicolumn=3)])

    with pytest.raises(TypeError):
        _ = tabm.join_rows([row, row])

    cols = tabm.join_rows([Columns([row]), Columns([row])])
    assert cols.shape == (2, 3)
    assert cols.rows == [row, row]

    with pytest.raises(ValueError):
        _ = tabm.join_rows(
            [
                cols,
                Columns([Row([Cell(name="mf", value="1", multicolumn=2)])]),
            ]
        )


def test_cmidrule():
    cms = Cmidrules(
        [
            Cmidrule(start=1, end=2),
            Cmidrule(start=3, end=4),
        ]
    )
    assert cms.start == 1
    assert cms.end == 4

    with pytest.raises(ValueError):
        _ = Cmidrule(start=0, end=2)

    with pytest.raises(ValueError):
        _ = Cmidrule(start=3, end=2)

    cm = Cmidrule(start=1, end=2)
    with pytest.raises(TypeError):
        _ = cm == 1


def test_validate_rows():
    """
    Test function to validate rows.
    """

    rows = [
        Row([Cell(name="mf", value="1", multicolumn=3)]),
        Cmidrules(
            values=[
                Cmidrule(start=1, end=2),
                Cmidrule(start=3, end=3),
            ]
        ),
        Midrule(),
    ]

    with pytest.raises(TypeError):  # Wrong type
        tabm.validate_rows(rows + [1])

    with pytest.raises(TypeError):  # Wrong type
        tabm.validate_rows(Row([Cell("1")]))

    assert tabm.validate_rows([]) == 0

    assert tabm.len_rows([]) == set()

    assert tabm.validate_rows([Row([Cell("1")])]) == 1
    assert tabm.validate_rows([Row([Cell("1", multicolumn=3)])]) == 3
    assert tabm.validate_rows([Row([Cell("1", multicolumn=10)])]) == 10

    with pytest.raises(TypeError):  # Wrong type
        tabm.validate_rows([Midrule(), 1])

    assert tabm.validate_rows([Midrule(), Cmidrule(start=1, end=3)]) == 3

    assert tabm.validate_rows([Midrule(), Cmidrule(start=1, end=3)]) == 3
    assert tabm.validate_rows([Midrule(), Midrule()]) == 1


def test_table_others():
    tab = tabx.empty_table(2, 2)
    subtab = tab[2:]
    assert subtab.shape == (0, 0)

    with pytest.raises(ValueError):
        _ = subtab.render()


def test_interval_conditions():
    ic = interval_conditions((0, 1), (0, 2))
    assert ic.condition == "right"

    ic = interval_conditions(interval=(-1, 3), slice_=(-3, 2))
    assert ic.condition == "left"

    ic = interval_conditions((-1, 3), (-0, 2))
    assert ic.condition == "center"

    # Completely before
    assert interval_conditions((10, 20), (0, 9)).condition == "none"
    # Touches from left
    assert interval_conditions((10, 20), (5, 10)).condition == "none"
    # Left overlap
    assert interval_conditions((10, 20), (5, 15)).condition == "left"
    # Fully inside
    assert interval_conditions((10, 20), (12, 18)).condition == "center"
    # Equal
    assert interval_conditions((10, 20), (10, 20)).condition == "center"
    # Right overlap
    assert interval_conditions((10, 20), (15, 25)).condition == "right"
    # Touches from right
    assert interval_conditions((10, 20), (20, 25)).condition == "none"
    # Completely after
    assert interval_conditions((10, 20), (21, 30)).condition == "none"
    # Slice spans entire interval
    assert interval_conditions((10, 20), (5, 25)).condition == "center"

    interval_conditions((10, 5), (2, 3))  # invalid: start > end


def test_color():
    c1 = tabx.empty_columns(3, 1) / tabx.Midrule()
    c2 = tabx.empty_columns(3, 1) / tabx.table.ColoredRow("blue")
    with pytest.raises(ValueError):
        c1 | c2

    c1 = tabx.empty_columns(3, 1) / tabx.table.ColoredRow("grey")
    c2 = tabx.empty_columns(3, 1) / tabx.table.ColoredRow("blue")
    with pytest.raises(
        ValueError,
        match="Cannot have multiple ColoredRows in same row",
    ):
        c1 | c2


def test_insert_rows():
    """test inserting rows"""

    def test_tab():
        return tabx.Table.from_values(
            [
                [1, 2, 3],
                [1, 2, 3],
                [1, 2, 3],
            ]
        )

    # every other row is a Midrule
    tab = test_tab()
    tab = tab.insert_row(tabx.Midrule(), 3)
    tab = tab.insert_row(tabx.Midrule(), 2)
    tab = tab.insert_row(tabx.Midrule(), 1)
    tab = tab.insert_row(tabx.Midrule(), 0)
    for i, row in enumerate(tab.rows):
        if i % 2 == 0:
            assert isinstance(row, tabx.Midrule)

    # every other row is a Midrule
    tab = test_tab()
    tab = tab.insert_rows(
        [
            tabx.Midrule(),
            tabx.Midrule(),
            tabx.Midrule(),
            tabx.Midrule(),
        ],
        [0, 1, 2, 3],
    )
    for i, row in enumerate(tab.rows):
        if i % 2 == 0:
            assert isinstance(row, tabx.Midrule)

    # insert Midrule at every position
    for i in range(3 + 1):
        tab = test_tab()
        tab = tab.insert_row(tabx.Midrule(), i)
        assert isinstance(tab.rows[i], tabx.Midrule)
