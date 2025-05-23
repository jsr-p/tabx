import re

import pytest

import tabx
from tabx import table as tabm
from tabx import utils
from tabx.table import (
    Cmidrule,
    Cmidrules,
    Columns,
    Cell,
    Midrule,
    Row,
    empty_cell,
    slice_cells,
)

ec = tabm.empty_columns
et = tabm.empty_table


def test_multirow_cell_slicing():
    """
    - slicing columns and an element is a multirow cell
        - done (make tests)
    """

    cells = [
        tabm.empty_cell(),
        Cell(name="mf", value="1", multirow=3),
        Cell(name="mf", value="1", multirow=6),
    ]

    assert slice_cells(cells, slice(0, 1), len_measure="row") == [tabm.empty_cell()]

    assert slice_cells(cells, slice(0, 4), len_measure="row") == cells[:2]

    assert slice_cells(cells, slice(0, 5), len_measure="row") == [
        tabm.empty_cell(),
        Cell(name="mf", value="1", multirow=3),
        Cell(name="mf", value="1", multirow=1),
    ]

    # Larger slices picks out more of the multirow
    for i in range(6):
        assert slice_cells(cells, slice(0, 5 + i), len_measure="row") == [
            tabm.empty_cell(),
            Cell(name="mf", value="1", multirow=3),
            Cell(name="mf", value="1", multirow=1 + i),
        ]


def test_row():
    # Row has to be a sequence of cells
    with pytest.raises(TypeError):
        Row([1])
    with pytest.raises(TypeError):
        Row(Cell(name="mf", value="1", multirow=3))

    row = Row(
        [
            Cell(name="mf", value="1", multirow=3),
            Cell(name="mf", value="1", multirow=3),
            Cell(name="mf", value="1", multirow=3),
        ]
    )

    assert row[0] == row[-3]
    assert row[1] == row[-2]
    assert row[2] == row[-1]

    with pytest.raises(IndexError):
        row[3]

    assert tabm.index_to_slice(0, [0, 1]) == slice(0, 1)
    assert tabm.index_to_slice(2, [0, 1, 2]) == slice(2, 3)

    with pytest.raises(IndexError):
        _ = tabm.index_to_slice(3, [0, 1, 2])

    assert tabm.index_to_slice(-1, [0, 1, 2]) == slice(2, 3)
    assert tabm.index_to_slice(-2, [0, 1, 2]) == slice(1, 2)
    assert tabm.index_to_slice(-3, [0, 1, 2]) == slice(0, 1)


def test_misc_slices():
    assert tabm.slices_from_indices([0, 1, 2, 4, 5]) == [slice(0, 3), slice(4, 6)]
    assert tabm.slices_from_indices([]) == []

    assert tabm.slices_from_indices([0, 1]) == [slice(0, 2)]


def test_len_rows():
    assert tabm.len_rows(
        [
            Row([Cell(name="a", value="1"), Cell(name="b", value="2")]),
            Row([Cell(name="a", value="1"), Cell(name="b", value="2")]),
        ]
    ) == {2}

    assert tabm.len_rows(
        [
            Row(
                [
                    Cell(name="a", value="1"),
                    Cell(name="b", value="2"),
                    Cell(name="b", value="2"),
                ]
            ),
            Row([Cell(name="a", value="1"), Cell(name="b", value="2")]),
        ]
    ) == {3, 2}


def test_validate_column_rows():
    tabm.validate_column_rows(
        rows=[
            Row([Cell(name="mf", value="1", multirow=3)]),
            Row([empty_cell()]),
            Row([empty_cell()]),
        ]
    )

    with pytest.raises(
        ValueError, match="found 2 following cells of which 1 is empty."
    ):
        tabm.validate_column_rows(
            rows=[
                Row([Cell(name="mf", value="1", multirow=3)]),
                Row([empty_cell()]),
                Row([empty_cell()]),
                Row([Cell(name="mf", value="1", multirow=3)]),
                Row([empty_cell()]),
                Row([Cell(name="mf", value="1", multirow=3)]),
            ]
        )

    with pytest.raises(ValueError, match="found 1 following cell of which 1 is empty."):
        tabm.validate_column_rows(
            rows=[
                Row([Cell(name="mf", value="1", multirow=3)]),
                Row([empty_cell()]),
            ]
        )

    with pytest.raises(ValueError, match="found 0 following cell of which 0 is empty."):
        tabm.validate_column_rows(
            rows=[
                Row([Cell(name="mf", value="1", multirow=3)]),
            ]
        )


def test_validate_rows():
    rows = [
        # Row([Cell(name="mf", value="1", multirow=3)]),
        # Row([empty_cell()]),
        # Row([empty_cell()]),
        Cmidrule(start=1, end=2),
        cms := Cmidrules(
            [
                Cmidrule(start=1, end=2),
                cm := Cmidrule(start=3, end=4),
            ]
        ),
        Midrule(),
    ]

    assert tabm.validate_rows(rows) == 4  # Cmidrules
    assert tabm.validate_rows(rows[:1]) == 2  # Cmidrule
    assert tabm.validate_rows(rows[-1:]) == 1  # Midrule


def test_cmidrules_concat():
    col = tabm.Column(
        rows=[
            Row([Cell(name="mf", value="1", multirow=3)]),
            Row([empty_cell()]),
            Row([empty_cell()]),
            tabm.Cmidrule(start=1, end=1),
        ]
    )

    scol = tabm.join_columns([col, col])[-1]
    val = scol.rows[0]
    assert isinstance(val, tabm.Cmidrules)
    assert val.values == [
        tabm.Cmidrule(start=1, end=1),
        tabm.Cmidrule(start=2, end=2),
    ]

    cols = tabm.Columns(
        [
            Row(
                [
                    Cell(name="mf", value="1", multirow=3),
                    Cell(name="mf", value="1", multirow=3),
                ]
            ),
            Row([empty_cell(), empty_cell()]),
            Row([empty_cell(), empty_cell()]),
            tabm.Cmidrule(start=1, end=2),
        ],
    )

    scol = tabm.join_columns([cols, cols])[-1]
    val = scol.rows[0]
    assert isinstance(val, tabm.Cmidrules)
    assert val.values == [
        Cmidrule(start=1, end=2, trim="lr"),
        Cmidrule(start=3, end=4, trim="lr"),
    ]


def test_cmidrule_slice():
    cm = Cmidrule(1, 3)
    assert cm[0:1] == Cmidrule(1, 1)
    assert cm[1:2] == Cmidrule(2, 2)
    assert cm[2:3] == Cmidrule(3, 3)
    assert cm[1:3] == Cmidrule(2, 3)
    assert cm[:] == Cmidrule(1, 3)

    cm = Cmidrule(3, 5)
    sl = slice(None, None, None)
    assert cm.__getitem__(sl, standardize=False) == cm
    assert cm.__getitem__(sl, standardize=True) == cm - 2

    for i in range(2, 5):
        assert cm[i] == Cmidrule(1, 1)

    with pytest.raises(IndexError):
        cm[1]  # Out of bounds
    with pytest.raises(IndexError):
        cm[5]  # Out of bounds


def test_multicolumn_cell_slicing():
    cells = [
        empty_cell(),
        Cell(name="mf", value="1", multicolumn=3),
        Cell(name="mf", value="1", multicolumn=6),
    ]

    # refuse step size larger than 1
    with pytest.raises(ValueError):
        tabm.slice_cells(cells, slice(0, 4, 2))

    assert slice_cells(cells, slice(0, 1)) == [tabm.empty_cell()]

    assert slice_cells(cells, slice(0, 4)) == [
        empty_cell(),
        Cell(name="mf", value="1", multicolumn=3),
    ]

    # Larger slices picks out more of the multicolumn
    for i in range(1, 7):
        assert slice_cells(cells, slice(0, 4 + i)) == [
            empty_cell(),
            Cell(name="mf", value="1", multicolumn=3),
            Cell(name="mf", value="1", multicolumn=i),
        ]

    assert Row(cells)[:].cells == cells
    assert Row(cells)[:].cells == cells


def test_cmidrules_slice():
    cmids = Cmidrules(
        [
            Cmidrule(1, 3),
            Cmidrule(4, 5),
        ]
    )

    # Regular slice
    assert cmids.__getitem__(slice(2, 3 + 1)).values == [
        Cmidrule(start=3, end=3, trim="lr"),
        Cmidrule(start=4, end=4, trim="lr"),
    ]

    with pytest.raises(
        ValueError,
        match=re.compile("Cmidrules .* overlap"),
    ):
        #  NOTE: Expected behavior for individual cmidrules when standardizing
        # but with Cmidrules when slicing we *don't* want to standardize.

        # Standardize each to be individual modular components
        assert cmids.__getitem__(slice(2, 3 + 1), True).values == [
            Cmidrule(start=1, end=1, trim=""),
            Cmidrule(start=1, end=1, trim=""),
        ]

    # Standardize by minimum of slice
    assert cmids.__getitem__(slice(2, 3 + 1), standardize=2).values == [
        Cmidrule(start=1, end=1, trim="lr"),
        Cmidrule(start=2, end=2, trim="lr"),
    ]

    # Older tests
    cmidrules = tabm.Cmidrules(
        [
            tabm.Cmidrule(start=1, end=4),
            tabm.Cmidrule(start=6, end=8),
        ]
    )

    assert cmidrules[0].values == [
        Cmidrule(start=1, end=1),
    ]

    assert cmidrules[:4].values == [
        Cmidrule(start=1, end=4),
    ]

    # Still only first cmidrule
    assert cmidrules[:5].values == [
        Cmidrule(start=1, end=4),
    ]

    # From i = 6, ..., 8 picks out
    for i in range(6, 9 + 1):
        assert cmidrules[:i].values == [
            Cmidrule(start=1, end=4),
            Cmidrule(start=6, end=min(i, 8)),
        ]


def test_column():
    rows = [
        Row([Cell(name="mf", value="1", multirow=3)]),
        Row([empty_cell()]),
        Row([empty_cell()]),
        tabm.Cmidrule(start=1, end=1),
    ]
    col = tabm.Column(rows)
    assert col.ncols == 1
    assert tabm.len_rows(col.rows) == {1}

    cols = tabm.join_columns([col])
    assert cols.ncols == 1
    assert tabm.len_rows(cols.rows) == {1}

    cols = tabm.join_columns([col, col, col])
    assert cols.ncols == 3

    rows = [
        Row([Cell(name="mf", value="1", multirow=3)]),
        Row([empty_cell()]),
        Row([empty_cell()]),
        tabm.Cmidrule(start=2, end=3),
    ]
    with pytest.raises(ValueError):
        col = tabm.Column(rows)

    col = tabx.empty_columns(3, 1)

    with pytest.raises(IndexError, match="Index 1 out of bounds"):
        col[0, 1]

    with pytest.raises(ValueError):
        col[[1]]


def test_multirow_cell():
    """

    - Link empty cell to multirow class
    - Whe slicing from below we remove empty cell and detach it from multirow
    and decrease multirow by 1
    - slicing from above switch multi with its next empty cell and remove that
    one and subtract 1 from mr, repeat until multirow empty then continue

    Invariant when placing in several rows (i.e. in columns):
        - MultirowCell always precedes its MrEmptyCells
        - MultirowCell with multirow=n has n - 1 trailing MrEmptyCells
        - Slice from above
        - Slice from below
        - Index inside MR return MR with multirow=1 and its value if index
        happens inside the MultirowCell or its MrEmptyCells
    """

    from tabx.table import EmptyCell, MrEmptyCell, MultirowCell

    assert isinstance(EmptyCell(), Cell)
    assert isinstance(MultirowCell(name="foo", value="bar", multirow=3), Cell)
    assert isinstance(MrEmptyCell(), Cell)

    mr = MultirowCell(name="foo", value="bar", multirow=3)
    mr.add_empty_cell(f1 := MrEmptyCell(name="mr"))
    mr.add_empty_cell(f2 := MrEmptyCell(name="mr"))
    array = [[mr], [f1], [f2]]

    assert tabm.slice_array(array, slice(0, 1)) == [
        [MultirowCell(name="foo", value="bar", multirow=1)]
    ]

    assert tabm.slice_array(array, slice(0, 2)) == [
        [MultirowCell(name="foo", value="bar", multirow=2)],
        [f1],
    ]

    assert tabm.slice_array(array, slice(0, 3)) == [
        [MultirowCell(name="foo", value="bar", multirow=3)],
        [f1],
        [f2],
    ]

    assert tabm.slice_array(array, slice(1, 2)) == [
        [MultirowCell(name="foo", value="bar", multirow=1)],
    ]

    assert tabm.slice_array(array, slice(2, 3)) == [
        [MultirowCell(name="foo", value="bar", multirow=1)],
    ]

    assert tabm.slice_array(array, slice(1, 3)) == [
        [MultirowCell(name="foo", value="bar", multirow=2)],
        [f1],
    ]

    mr = MultirowCell(name="foo", value="bar", multirow=3)
    mr.add_empty_cell(f1 := MrEmptyCell(name="mr"))
    mr.add_empty_cell(f2 := MrEmptyCell(name="mr"))
    mr2 = MultirowCell(name="foo", value="bar", multirow=2)
    mr2.add_empty_cell(f3 := MrEmptyCell(name="mr"))

    # Multi-dimensional i.e. multiple multirows inside array at different
    # places
    array = [
        [mr, EmptyCell(name="mr")],
        [f1, mr2],
        [f2, f3],
    ]

    assert tabm.slice_array(array, slice(0, 1)) == [
        [
            MultirowCell(name="foo", value="bar", multirow=1),
            EmptyCell(name="mr"),
        ],
    ]

    assert tabm.slice_array(array, slice(0, 2)) == [
        [
            MultirowCell(name="foo", value="bar", multirow=2),
            EmptyCell(name="mr"),
        ],
        [
            MrEmptyCell(name="mr"),
            MultirowCell(name="foo", value="bar", multirow=1),
        ],
    ]

    assert tabm.slice_array(array, slice(1, 2)) == [
        [
            MultirowCell(name="foo", value="bar", multirow=1),
            MultirowCell(name="foo", value="bar", multirow=1),
        ],
    ]

    assert tabm.slice_array(array, slice(1, 3)) == [
        [
            MultirowCell(name="foo", value="bar", multirow=2),
            MultirowCell(name="foo", value="bar", multirow=2),
        ],
        [
            MrEmptyCell(name="mr"),
            MrEmptyCell(name="mr"),
        ],
    ]

    assert tabm.slice_array(array, slice(2, 3)) == [
        [
            MultirowCell(name="foo", value="bar", multirow=1),
            MultirowCell(name="foo", value="bar", multirow=1),
        ],
    ]

    assert tabm.slice_array(array, slice(0, 3)) == [
        [
            MultirowCell(name="foo", value="bar", multirow=3),
            EmptyCell(name="mr"),
        ],
        [
            MrEmptyCell(name="mr"),
            MultirowCell(name="foo", value="bar", multirow=2),
        ],
        [
            MrEmptyCell(name="mr"),
            MrEmptyCell(name="mr"),
        ],
    ]


def test_slices_columns():
    cols = Columns(
        [
            Row(
                [
                    Cell(name="mf", value="1", multirow=3),
                    Cell(name="mf", value="1", multirow=3),
                ]
            ),
            Row([empty_cell(), empty_cell()]),
            Row([empty_cell(), empty_cell()]),
            tabm.Cmidrule(start=1, end=2, trim="lr"),
            tabm.Midrule(),
        ],
    )

    cols.print()

    # Slicing multirow cells for [0, 1) just returns non-multirow cell
    assert tabm.slice_rows_vertical(cols, slice(0, 1)).render().splitlines() == [
        r"1 & 1 \\",
    ]
    # Slicing multirow cells for [0, 2) returns multirow-cell with multirow=2
    # with trailing empty cell
    assert tabm.slice_rows_vertical(cols, slice(0, 2)).render().splitlines() == [
        r"\multirow{2}{*}{1} & \multirow{2}{*}{1} \\",
        r" &  \\",
    ]
    # etc
    assert tabm.slice_rows_vertical(cols, slice(0, 3)).render().splitlines() == [
        r"\multirow{3}{*}{1} & \multirow{3}{*}{1} \\",
        r" &  \\",
        r" &  \\",
    ]

    assert tabm.slice_rows_vertical(cols, slice(0, None)).render().splitlines() == [
        r"\multirow{3}{*}{1} & \multirow{3}{*}{1} \\",
        r" &  \\",
        r" &  \\",
        r"\cmidrule(lr){1-2}",
        r"\midrule",
    ]

    assert tabm.slice_rows_vertical(cols, slice(0, 3)) == cols[:3]

    assert tabm.slice_rows_vertical(cols, slice(0, 0)) == Columns(rows=[], align="c")

    assert tabm.slice_rows_vertical(cols, slice(1, 1)) == Columns(rows=[], align="c")

    # Horizontal slicing
    assert tabm.slice_rows_horizontal(cols, slice(0, 1)).render().splitlines() == [
        r"\multirow{3}{*}{1} \\",
        r" \\",
        r" \\",
        r"\cmidrule(lr){1-1}",
        r"\midrule",
    ]

    with pytest.raises(IndexError):
        _ = tabm.slice_rows_horizontal(cols, slice(0, 0))

    assert tabm.slice_rows_horizontal(cols, slice(0, None)) == cols

    utils.print_lines(cols[:, :1].render())

    cmids = Cmidrules(
        values=[
            Cmidrule(start=1, end=2),
            Cmidrule(start=3, end=3),
        ]
    )
    rows = [Row([Cell(name="mf", value="1", multicolumn=3)]), cmids, Midrule()]
    cols = Columns(rows)
    cols.print_rows()
    print(cols.render())

    tabm.slice_rows_horizontal(cols, slice(2, None)).print_rows()


def test_slice_table():
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

    cols[:, 0]

    tab = tabm.Table.from_columns(cols)[:2, :2]
    print(tab.render())
