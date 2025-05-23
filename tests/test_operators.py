import re

import pytest

import tabx
from tabx import table as tabm
from tabx.table import (
    Cmidrule,
    Cmidrules,
    Columns,
    Cell,
    Midrule,
    Row,
    Table,
    empty_cell,
)

ec = tabm.empty_columns
et = tabm.empty_table


def test_truediv_or_objects():
    """
    Here, `+` := `/` or `|`
    Cases:
        Columns + Columns -> Columns
        Table + Columns -> Table
        Columns + Table -> Table

        Rows + Rows -> Rows
        Table + Rows -> Table
        Rows + Table -> Table

        Table + Table -> Table

        Rows + Columns -> Columns
        Columns + Rows -> Columns

    """

    cols = Columns(
        [
            Row(
                [
                    Cell(name="mf", value="1", multirow=3),
                    Cell(name="mf", value="1", multirow=3),
                    Cell(name="x", value="hello"),
                ]
            ),
            Row([empty_cell(), empty_cell(), empty_cell()]),
            Row([empty_cell(), empty_cell(), empty_cell()]),
            tabm.Cmidrule(start=1, end=2, trim="lr"),
            tabm.Midrule(),
        ],
    )

    ec = tabm.empty_columns
    tab = tabm.Table.from_columns(cols)

    # cols | cols -> cols
    assert isinstance(cols | ec(5, 1), Columns)
    assert isinstance(ec(5, 1) | cols, Columns)

    # col | cols -> cols
    # cols | col -> cols
    c = tabm.Column(cols[:, 0].rows)
    assert isinstance(c | ec(5, 1), Columns)
    assert isinstance(c | ec(5, 1), Columns)

    # col(s) | tab -> tab
    # tab | col(s) -> tab
    assert isinstance(ec(5, 1) | tab, Table)
    assert isinstance(tab | ec(5, 1), Table)
    assert isinstance(c | tab, Table)
    assert isinstance(tab | c, Table)

    assert isinstance(tab[:, 1:2] | tab[:, :1], Table)
    assert isinstance(tab[:, 1:2] | tab[:, :1], Table)


def test_columns():
    cols = Columns(
        [
            rows := Row([empty_cell(), empty_cell(), empty_cell()]),
        ],
    )

    assert (cols / Midrule()).rows == [rows, Midrule()]

    assert (Midrule() / cols).rows == [Midrule(), rows]

    assert (cols / Cell("1", multicolumn=3)).rows == [
        rows,
        Row([Cell("1", multicolumn=3)]),
    ]

    tab = tabx.empty_table(2, 3) / tabx.empty_columns(2, 3)
    assert isinstance(tab, Table)

    with pytest.raises(TypeError):
        tabx.empty_columns(2, 3) / 1

    with pytest.raises(TypeError):
        tabx.empty_columns(2, 3) == 1


def test_truediv_or_cells():
    """
    Test `|` and `/` for cells.

    Cases:
        Cell | Cell -> Col(1, 2)
        Cell / Cell -> Col(2, 1)

        Cell | Col(1, 2) -> Col(1, 3)
        Col(1, 2) | Cell  -> Col(1, 3)
        Cell / Col(1, 2) -> Error

        Cell / Col(2, 1) -> Col(3, 1)
        Col(2, 1) / Cell -> Col(3, 1)
        Cell | Col(2, 1) -> Error
    """

    tab = et(21, 2)

    # Test prepend / append cells → Table
    out = tab[:, 0] / Cell("1")
    assert isinstance(out, Table)
    assert out.shape == (22, 1)

    out = Cell("1") / tab[:, 0]
    assert isinstance(out, Table)
    assert out.shape == (22, 1)

    # Test prepend / append cells → Columns
    out = tab[:, 0].columns / Cell("1")
    assert isinstance(out, Columns)
    assert out.shape == (22, 1)

    out = Cell("1") / tab[:, 0].columns
    assert isinstance(out, Columns)
    assert out.shape == (22, 1)

    # Error: mismatched row lengths
    with pytest.raises(ValueError, match="Found unique row lengths: {1, 2}"):
        _ = Cell("1") / ec(2, 2)

    # Error: mismatched column heights
    with pytest.raises(
        ValueError,
        match=re.escape("All columns must have same number of rows. Found: [1, 2]"),
    ):
        _ = Cell("1") | ec(2, 1)

    # Valid cell + columns merge
    out = Cell("1") / ec(2, 1)
    assert isinstance(out, Columns)
    assert out.shape == (3, 1)

    out = ec(2, 1) / Cell("1")
    assert isinstance(out, Columns)
    assert out.shape == (3, 1)

    out = Cell("1") | ec(1, 2)
    assert isinstance(out, Columns)
    assert out.shape == (1, 3)

    out = ec(1, 2) | Cell("1")
    assert isinstance(out, Columns)
    assert out.shape == (1, 3)

    # Valid cell + table merge
    out = Cell("1") / et(2, 1)
    assert isinstance(out, Table)
    assert out.shape == (3, 1)

    out = et(2, 1) / Cell("1")
    assert isinstance(out, Table)
    assert out.shape == (3, 1)

    out = Cell("1") | et(1, 2)
    assert isinstance(out, Table)
    assert out.shape == (1, 3)

    out = et(1, 2) | Cell("1")
    assert isinstance(out, Table)
    assert out.shape == (1, 3)

    # Midrule + cell
    out = Cell("1") / Midrule()
    assert isinstance(out, Columns)
    assert out.shape == (2, 1)

    # Cell and rules
    out = Cell("1") / Midrule()
    assert isinstance(out, Columns)
    assert out.shape == (2, 1)

    out = Cell("1") / Cmidrule(1, 1)
    assert isinstance(out, Columns)
    assert out.shape == (2, 1)

    out = Cell("1", multicolumn=2) / Cmidrule(1, 2)
    assert isinstance(out, Columns)
    assert out.shape == (2, 2)

    out = Cell("1", multicolumn=2) / Cmidrule(1, 2) / et(1, 2)
    assert isinstance(out, Table)
    assert out.shape == (3, 2)

    out = et(1, 2) / Cell("1", multicolumn=2) / Cmidrule(1, 2)
    assert isinstance(out, Table)

    # Cannot concat cell horizontally
    for obj in [
        Midrule(),
        Cmidrule(1, 2),
        Cmidrules([Cmidrule(1, 2), Cmidrule(3, 4)]),
    ]:
        name = type(obj).__name__
        with pytest.raises(
            TypeError,
        ):
            _ = Cell("1") | obj

    # Cell / Cell
    out = Cell("1") / Cell("1")
    assert out.shape == (2, 1)
    assert isinstance(out, Columns)

    with pytest.raises(TypeError):
        _ = Cell("1") / 1

    # Cell / Cell
    out = Cell("1") | Cell("1")
    assert out.shape == (1, 2)
    assert isinstance(out, Columns)

    with pytest.raises(TypeError):
        _ = Cell("1") | 1

    out = Cell("1") | Row([Cell("1")])
    assert len(out) == 2
    assert out.cells == [Cell("1"), Cell("1")]

    out = Row([Cell("1")]) | Cell("1")
    assert len(out) == 2
    assert out.cells == [Cell("1"), Cell("1")]

    out = Cell("1") | [Cell("1"), Cell("1")]
    assert isinstance(out, Columns)


def test_rows():
    row = Row([Cell("1")])
    out = row | row
    assert len(out) == 2
    assert out.cells == [Cell("1"), Cell("1")]

    out = row / row
    assert isinstance(out, Columns)
    assert out.shape == (2, 1)
    assert out.all_rows() == [Row([Cell("1")]), Row([Cell("1")])]

    tab = tabx.empty_table(2, 1)
    out = row / tab
    assert isinstance(out, Table)
    assert out.shape == (3, 1)
    assert out.rows[0].cells == [Cell("1")]

    tab = tabx.empty_columns(2, 1)
    out = row / tab
    assert isinstance(out, Columns)
    assert out.shape == (3, 1)
    assert out.rows[0].cells == [Cell("1")]

    with pytest.raises(
        TypeError,
    ):
        _ = row | tabx.empty_columns(2, 2)

    with pytest.raises(
        TypeError,
    ):
        _ = row / Cell("1")


def test_cmidrule():
    with pytest.raises(
        ValueError,
        match=re.compile("Cmidrules .* overlap"),
    ):
        _ = Cmidrule(1, 2) | Cmidrule(1, 2)

    assert Cmidrule(1, 2) | Cmidrule(3, 4) == Cmidrules(
        [Cmidrule(1, 2), Cmidrule(3, 4)]
    )

    cm = Cmidrule(start=1, end=2)
    cm2 = cm + 2
    assert cm2.start == 3
    assert cm2.end == 4

    cm = Cmidrule(start=3, end=5)
    cm2 = cm - 2
    assert cm2.start == 1
    assert cm2.end == 3

    cm = Cmidrule(start=1, end=2)
    cm2 = cm + (1, 3)
    assert cm2.start == 2
    assert cm2.end == 5

    cm = Cmidrule(start=3, end=5)
    cm2 = cm - (1, 3)
    assert cm2.start == 2
    assert cm2.end == 2

    cm1 = Cmidrule(start=1, end=3)
    with pytest.raises(TypeError):
        cm1 + cm1

    cm1 = Cmidrule(start=1, end=3)
    cm2 = Cmidrule(start=3, end=5)
    with pytest.raises(ValueError, match="overlap"):
        _ = cm1 | cm2

    cm1 = Cmidrule(start=1, end=2)
    cm2 = Cmidrule(start=3, end=5)

    assert (cm1 | cm2).values == [cm1, cm2]
    assert (cm2 | cm1).values == [cm1, cm2]

    cm1 = Cmidrule(start=1, end=2)
    cms = Cmidrules(
        [
            Cmidrule(start=3, end=4),
            Cmidrule(start=5, end=6),
        ]
    )
    assert (cm1 | cms).values == [
        Cmidrule(start=1, end=2, trim="lr"),
        Cmidrule(start=3, end=4, trim="lr"),
        Cmidrule(start=5, end=6, trim="lr"),
    ]

    with pytest.raises(TypeError):
        _ = cm1 | Midrule()

    col = cm1 / Midrule()
    assert col.rows == [cm1, Midrule()]

    col = cm1 / Cell("1", multicolumn=3)

    cm1 = Cmidrule(start=1, end=3)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Cmidrule end (3) must be less than or equal to number of columns (1)"
        ),
    ):
        _ = cm1 / Cell("1")

    cm1 = Cmidrule(start=1, end=3)
    tab = cm1 / tabx.empty_table(2, 3)
    assert tab.shape == (3, 3)
    assert isinstance(tab, Table)

    tab = cm1 / tabx.empty_table(2, 3)
    assert tab.shape == (3, 3)
    assert isinstance(tab, Table)

    cm1 = Cmidrule(start=1, end=3)
    with pytest.raises(TypeError):
        cm1 / 1

    cm1 = Cmidrule(start=1, end=3)
    with pytest.raises(ValueError):
        cm1 = Cmidrule(start=1, end=3) - 1

    with pytest.raises(TypeError):
        cm1 - cm1


def test_cmidrules():
    cmid = Cmidrule(1, 2)
    cmids = Cmidrules([Cmidrule(1, 2), Cmidrule(3, 4)])

    for i in range(4):
        cmd = cmids[i]
        assert cmd.values == [Cmidrule(1, 1)]

    with pytest.raises(IndexError):
        cmids[4]

    assert tabm.standardize_index(-1, len(cmids)) == 3
    assert cmids[4:5].values == []  # slice outside; returns empty

    assert cmids.clen() == 4
    with pytest.raises(IndexError):
        cmids[4]

    with pytest.raises(ValueError):
        cmids | cmid

    cmid = Cmidrule(5, 10)
    assert (cmids | cmid).values == [Cmidrule(1, 2), Cmidrule(3, 4), Cmidrule(5, 10)]

    cmids2 = Cmidrules([Cmidrule(5, 10), Cmidrule(12, 14)])
    assert (cmids | cmids2).values == [
        Cmidrule(1, 2),
        Cmidrule(3, 4),
        Cmidrule(5, 10),
        Cmidrule(12, 14),
    ]

    with pytest.raises(TypeError):
        cmids | Midrule()


def test_midrule():
    mr = Midrule()
    col = mr / Cell("1")
    assert col.shape == (2, 1)
    assert col.rows == [mr, Row([Cell("1")])]

    with pytest.raises(TypeError):
        mr | mr

    tab = Midrule() / tabx.empty_table(2, 1)
    assert tab.rows == [mr, Row([Cell("")]), Row([Cell("")])]

    mr = Midrule()

    with pytest.raises(TypeError, match="wisdom from booktabs"):
        mr / mr


def test_concat():
    tab = tabx.empty_table(2, 1)
    assert tabm.concat([tab, tab], "horizontal") == (tab | tab)
    assert tabm.concat([tab, tab], "vertical") == (tab / tab)

    with pytest.raises(ValueError):
        tabm.concat([tab, tab], "wrong")
