"""
Module for creating tables for descriptive statistics and model output.
"""

from __future__ import annotations

import dataclasses
import itertools as it
import operator
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import chain
from typing import Any, Iterable

from tabx.table import (
    Cmidrule,
    Cmidrules,
    Columns,
    Cell,
    Midrule,
    Row,
    Table,
    TableRow,
    empty_columns,
    empty_cell,
    empty_cells,
    join_columns,
    multirow_column,
    reduce_cells_to_col,
    NumOrStr,
)

__all__ = [
    "DescData",
    "ModelData",
    "ColMap",
    "RowMap",
    "descriptives_table",
    "models_table",
]


type RCMap = dict[tuple[int, int], str]
"""Row/Column map for mapping indices to multirow/multicolumn names."""
type ColMaps = Sequence[ColMap] | ColMap
"""Sequence of ColMap objects or a single ColMap object."""
type RowMaps = Sequence[RowMap] | RowMap
"""Sequence of RowMap objects or a single RowMap object."""


def align_reg_cells(
    *cols: Iterable[RegCell],
    fill_value: NumOrStr = "",
) -> list[tuple[str, list[RegCell]]]:
    if any(not c.name for c in chain.from_iterable(cols)):
        raise ValueError("All RegCells must have a name when aligning")

    all_names = sorted(set(c.name for c in chain.from_iterable(cols)))
    name_to_cells: dict[str, list[RegCell]] = {}

    for name in all_names:
        name_to_cells[name] = [
            RegCell(
                est=Cell(name=name, value=fill_value),
                se=Cell(name=name, value=fill_value),
                name=name,
            )
            for _ in cols
        ]

    for i, col in enumerate(cols):
        for cell in col:
            name_to_cells[cell.name][i] = cell

    return [(name, name_to_cells[name]) for name in all_names]


def align_cells(
    *cols: Iterable[Cell],
    fill_value: NumOrStr = "",
) -> list[tuple[str, list[Cell]]]:
    if any(not c.name for c in chain.from_iterable(cols)):
        raise ValueError("All cells must have a name when aligning")

    all_names = sorted(set(c.name for c in chain.from_iterable(cols)))
    name_to_cells: dict[str, list[Cell]] = {}

    for name in all_names:
        name_to_cells[name] = [Cell(fill_value) for _ in cols]

    for i, col in enumerate(cols):
        for cell in col:
            name_to_cells[cell.name][i] = cell

    return [(name, name_to_cells[name]) for name in all_names]


@dataclass
class ColMap:
    """Mapping of columns to multicolumn header names."""

    mapping: RCMap
    """The underlying mapping of columns to multicolumn header names."""
    include_cmidrule: bool = True
    """Whether to include cmidrule in the header."""


@dataclass
class RowMap:
    """Mapping of rows to multirow labels."""

    mapping: RCMap
    """The underlying mapping of rows to multirow labels"""


@dataclass
class RegCell:
    """A cell in a regression table."""

    est: Cell
    """The estimate cell."""
    se: Cell
    """The standard error cell."""
    name: str = ""
    """The name of the cell."""


@dataclass
class RegRow:
    cells: list[RegCell]
    name: str

    def __repr__(self) -> str:
        return f"RegRow(name={self.name}, #cells={len(self.cells)})"

    def add_cell(self, cell: RegCell):
        if not isinstance(cell, RegCell):
            raise TypeError(f"Cell must be of type RegCell; got {type(cell)}")
        self.cells.append(cell)

    def rows(self) -> tuple[Row, Row]:
        est_cells = [Cell(name=self.name, value=self.name)] + [
            cell.est for cell in self.cells
        ]
        se_cells = [Cell(name="", value="")] + [cell.se for cell in self.cells]
        return Row(cells=est_cells), Row(cells=se_cells)

    def render(self) -> list[str]:
        est_cells = [cell.est for cell in self.cells]
        se_cells = [cell.se for cell in self.cells]
        est_row = f"{self.name} & " + " & ".join(cell.render() for cell in est_cells)
        se_row = " & " + " & ".join(cell.render() for cell in se_cells)
        return [est_row + r" \\", se_row + r" \\"]


@dataclass
class ModelData:
    """Object containing model data for model output tables."""

    variables: list[str]
    """List of variable names."""
    estimates: list[float]
    """List of estimates for the variables."""
    ses: list[float | str]
    """List of standard errors for the variables."""
    name: str
    """Name of the model."""
    extra_data: dict[str, Any] = dataclasses.field(default_factory=dict)
    """Dictionary to hold any extra data associated with the model."""

    def __repr__(self) -> str:
        return f"ModelData(name={self.name}, #variables={len(self.variables)})"

    def __post_init__(self):
        c1 = (l1 := len(self.variables)) != (l2 := len(self.estimates))
        c2 = len(self.variables) != (l3 := len(self.ses))
        if c1 or c2:
            raise ValueError(
                "All lists must have the same length. "
                f"Found: #var={l1}, #est={l2}, #se={l3}"
            )

    @classmethod
    def from_dict(
        cls,
        data: dict,
        v_col: str = "variable",
        est_col: str = "estimates",
        se_col: str = "se",
        name: str = "",
    ) -> "ModelData":
        """Create ModelData from dictionary."""
        extra_data = data.get("extra_data", {})
        return cls(
            variables=data[v_col],
            estimates=data[est_col],
            ses=data[se_col],
            name=name,
            extra_data=extra_data,
        )


@dataclass
class DescData:
    """Object containing data for descriptive statistics tables.

    Some more information here.

    Attributes:
        `variables`: List of variable names.
        `values`: List of values for the variables.
        `name`: Name of the descriptive statistics.
        `extra_data`: Dictionary to hold any extra data.
    """

    variables: list[str]
    """some variable names"""
    values: list[float]
    """some variable names"""
    name: str
    extra_data: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __repr__(self) -> str:
        return f"DescData(name={self.name}, #variables={len(self.values)})"

    @classmethod
    def from_dict(
        cls,
        data: dict,
        var_col: str = "variable",
        val_col: str = "values",
        name: str = "",
    ) -> "DescData":
        """Create DescData from dictionary.

        **Example**:
        ```python
        data = {
            "variable": ["var1", "var2"],
            "values": [1.0, 2.0],
            "extra_data": {"key": "value"},
        }
        desc_data = DescData.from_dict(data)
        print(desc_data)
        ```
        """
        extra_data = data.get("extra_data", {})
        return cls(
            variables=data[var_col],
            values=data[val_col],
            name=name,
            extra_data=extra_data,
        )

    def __post_init__(self):
        c1 = (l1 := len(self.variables)) != (l2 := len(self.values))
        if c1:
            raise ValueError(
                f"All lists must have the same length. Found: #vars={l1}, #vals={l2}"
            )

    @classmethod
    def from_values(
        cls,
        values: Sequence[Sequence[NumOrStr]],
        column_names: list[str],
    ) -> list[DescData]:
        """Construct list of `DescData` objects from a list of values."""
        variable_names = list(map(operator.itemgetter(0), values))
        data = [row[1:] for row in values]
        return [
            DescData.from_dict(
                {
                    "variable": variable_names,
                    "values": list(map(operator.itemgetter(i), data)),
                },
                name=col_name,
            )
            for i, col_name in enumerate(column_names)
        ]


def make_est_col(data: ModelData) -> list[RegCell]:
    """Make column of estimates and standard errors."""
    cells = [
        RegCell(
            est=Cell(name=name, value=f"{est}"),
            se=Cell(
                name="",
                value=f"({se})" if isinstance(se, float) else f"{se}",
            ),
            name=name,
        )
        for name, est, se in zip(data.variables, data.estimates, data.ses)
    ]
    return cells


def make_desc_col(data: DescData) -> list[Cell]:
    """Make column of estimates and standard errors."""
    cells = [
        Cell(name=f"{var}", value=f"{val}")
        for var, val in zip(data.variables, data.values)
    ]
    return cells


def empty_regcell(name: str = "") -> RegCell:
    return RegCell(
        est=Cell(name=name, value=""),
        se=Cell(name=name, value=""),
        name=name,
    )


def find_holes(pairs: list[tuple[tuple[int, int], str]]) -> list[int]:
    """
    Check if holes in the mapping; need to fill those with empty cells.
    """
    intervals = [interval for (interval, _) in pairs]
    holes = [s2 - e1 - 1 for (_, e1), (s2, _) in zip(intervals[:-1], intervals[1:])]
    holes = [0] + holes  # Add 0 for first cell
    return holes


def parse_col_maps(
    col_maps: ColMap,
    n: int,
) -> tuple[Row, Cmidrules] | tuple[Row]:
    """Parses ColMap and returns a row of cells (and cmidrules if specified).

    Args:
        col_maps: ColMap object with mapping of columns to names.
        n: Number of columns in the table.
    """

    max_end = max([end for (_, end) in col_maps.mapping.keys()])
    min_start = min([start for (start, _) in col_maps.mapping.keys()])
    if max_end > n:
        raise ValueError(f"Col map end ({max_end}) exceeds cols ({n}); {col_maps=}")
    pairs = sorted(col_maps.mapping.items(), key=operator.itemgetter(0))
    holes = find_holes(pairs)
    name_cells = [empty_cell()]
    if min_start > 1:
        # prepend empty cells before the first col maps
        name_cells.extend(empty_cells(min_start - 1))
    cmidrules = []
    for pair, hole in zip(pairs, holes):
        (start, end), name = pair
        if hole > 0:
            name_cells.extend(empty_cells(hole))
        name_cells.append(
            Cell(
                name=name,
                value=name,
                multicolumn=end - start + 1,
            )
        )
        cmidrules.append(
            Cmidrule(
                start=start + 1,
                end=end + 1,
                trim="lr",
            )
        )
    # Add fillers if mapping doesn't cover all columns
    ((_, le), _) = pairs[-1]
    if le < n:
        name_cells.extend(empty_cells(n - le))
    row = Row(cells=name_cells)
    if col_maps.include_cmidrule:
        cmidrules = Cmidrules(values=cmidrules)
        return (row, cmidrules)
    return (row,)


def construct_header(
    models: Sequence[ModelData | DescData],
    col_maps: ColMaps | None = None,
    var_name: str = "variable",
    include_midrule: bool = True,
) -> Sequence[TableRow]:
    header = [
        Row(
            cells=[
                Cell(name="", value=var_name),
            ]
            + [Cell(name=f.name, value=f.name) for f in models]
        )
    ]
    out = header
    if col_maps:
        if isinstance(col_maps, ColMap):
            top_h = parse_col_maps(col_maps, n=len(models))
            out = list(top_h) + header
        else:
            top_hs = []
            for dp_map in col_maps:
                top_h = parse_col_maps(dp_map, n=len(models))
                top_hs.extend(top_h)
            out = top_hs + header
    if include_midrule:
        return out + [Midrule()]
    return out


def extra_data_rows(
    models: Sequence[ModelData | DescData],
    order_map: dict[str, int] | None = None,
    fill_value: NumOrStr = "",
) -> list[Row]:
    """
    Args:
        models: List of ModelData or DescData objects.
        order_map:
            Dictionary mapping variable names to their order in the table.
            Higher values indicate later positions in the table.
    """
    if not order_map:
        order_map = dict()
    extra_data = defaultdict(lambda: defaultdict(str))
    extra_vars = set()
    for model in models:
        for k, v in model.extra_data.items():
            extra_data[model.name][k] = v
            extra_vars.update((k,))
    extra_rows = []
    for var in sorted(
        extra_vars,
        key=lambda x: order_map.get(x, float("inf")),
    ):
        row = [Cell(name=var, value=var)]
        for model in models:
            value = model.extra_data.get(var, fill_value)
            row.append(Cell(name=var, value=f"{value}"))
        extra_rows.append(Row(cells=row))
    return extra_rows


@dataclass
class RmParams:
    """
    Attributes:
        n_vars: Number of variables in the table.
        total: Total number of rows in the table.
        header: Header rows of the table.
        extra_rows: Extra rows to be added to the table.
        include_extra: Whether to include extra rows in the table.
        has_header: Whether the table has a header.
        has_extra: Whether the table has extra rows.
        include_midrule: Whether to include midrule(s) in the table.
    """

    n_vars: int
    total: int
    header: Sequence[TableRow]
    extra_rows: list[Row]
    include_extra: bool
    has_header: bool
    has_extra: bool
    include_midrule: bool = True


def handle_rm(rm: RowMap, rmp: RmParams):
    """
    n_vars includes extra variables if specified.
    """
    max_end = max([end for (_, end) in rm.mapping.keys()])
    if max_end > rmp.total:
        raise ValueError(f"Row map end ({max_end}) exceeds rows ({rmp.total})")
    if rmp.has_header:
        pad_before = len(rmp.header)  # Midrule in header usually
    else:
        pad_before = 0
    rm_col = construct_rm_col(rm, rmp, pad_before=pad_before)
    return rm_col


def construct_rm_col(
    rm: RowMap,
    rmp: RmParams,
    pad_before: int = 0,
) -> Columns:
    """Construct row map column to be prepended to the table.

    The logic is to find the holes in the mapping and fill them with empty
    cells. The holes are the gaps between the start and end of the mapping.
    Also, with extra rows (if any), we need to add an extra empty cell for the
    midrule.


    n_vars = 5
    (1, 2): "All vars",
    (4, 5): "Other vars",
    (6, 7): "Extra vars",
    """
    pairs = sorted(rm.mapping.items(), key=operator.itemgetter(0))  # by tuples

    for (start, end), _ in pairs:
        if start <= rmp.n_vars and end > rmp.n_vars:
            raise ValueError(
                f"Row map ({start}, {end}) overlaps with Midrule separating"
                " variables and extra variables. "
                "Row map must be in the range of 1 to n_vars"
                "or n_vars+1 to total."
            )

    holes = find_holes(pairs)
    total = rmp.n_vars + (rmp.total - rmp.n_vars) * rmp.include_extra

    cols = []
    mr_filled = False
    for pair, hole in zip(pairs, holes):
        (start, end), name = pair
        if hole > 0:
            cols.extend(empty_cells(hole))
        if start > rmp.n_vars and not mr_filled:
            cols.extend(empty_cells(1))
            mr_filled = True
        nrows = end - start + 1
        cols.append(multirow_column(name=name, value=name, multirow=nrows))

    if not mr_filled and rmp.include_extra:
        cols.extend(empty_cells(1))

    (_, last_end), _ = pairs[-1]
    if last_end < total:
        # Last end is not for the extra vars
        cols.extend(empty_cells(total - last_end))

    col = reduce_cells_to_col(cols)

    if pad_before > 0:
        col = empty_columns(nrows=pad_before, ncols=1) / col
    col.set_align("l")

    return col


def construct_base(
    rows: Sequence[TableRow],
    objs: Sequence[ModelData] | Sequence[DescData],
    col_maps: ColMaps | None = None,
    row_maps: RowMaps | None = None,
    order_map: dict[str, int] = dict(),
    var_name: str = "",
    include_header: bool = True,
    include_extra: bool = True,
    include_midrule: bool = True,
    fill_value: NumOrStr = "",
) -> Table:
    n_vars = len(rows)
    n_models = len(objs)
    align = "l" + "c" * n_models
    header = construct_header(
        objs,
        col_maps,
        var_name=var_name,
        include_midrule=include_midrule,
    )
    extra_rows = extra_data_rows(objs, order_map=order_map, fill_value=fill_value)
    if include_midrule and extra_rows:
        rows = list(rows) + [Midrule()]
    if extra_rows and include_extra:
        rows = list(rows) + extra_rows
    if include_header:
        rows = list(header) + list(rows)
    cols = Columns(rows=rows, align=align)
    if row_maps:
        rmp = RmParams(
            n_vars=n_vars,
            total=n_vars + len(extra_rows) * include_extra,
            header=header,
            extra_rows=extra_rows,
            include_extra=include_extra,
            include_midrule=include_midrule,
            has_header=include_header,
            has_extra=bool(extra_rows and include_extra),
        )
        if isinstance(row_maps, RowMap):
            rm = row_maps
            col = handle_rm(rm, rmp)
            cols = join_columns([col, cols])
            align = "l" * 2 + "c" * n_models
        else:
            rm_cols = [handle_rm(rm, rmp) for rm in row_maps]
            cols = join_columns(rm_cols + [cols])
            align = "l" * (len(rm_cols) + 1) + "c" * n_models
        cols.align = align
    return Table.from_columns(columns=cols)


def models_table(
    models: Sequence[ModelData],
    col_maps: ColMaps | None = None,
    row_maps: RowMaps | None = None,
    order_map: dict[str, int] = dict(),
    var_name: str = "variable",
    include_extra: bool = True,
    include_header: bool = True,
    fill_value: NumOrStr = "",
) -> Table:
    """Creates a table of parameter estimates and standard errors."""
    est_cols = [make_est_col(model) for model in models]
    aligned = align_reg_cells(*est_cols, fill_value=fill_value)
    rows = sorted(
        [RegRow(cells=cells, name=name) for name, cells in aligned],
        key=lambda x: order_map.get(x.name, float("inf")),
    )
    rows = list(
        it.chain.from_iterable(
            [
                # Flatten [[Row, Row], [Row, Row]] -> [Row, Row, Row, Row]
                # for the estimate, standard error row pairs.
                row.rows()
                for row in rows
            ]
        )
    )
    return construct_base(
        rows=rows,
        objs=models,
        col_maps=col_maps,
        row_maps=row_maps,
        order_map=order_map,
        var_name=var_name,
        include_header=include_header,
        include_extra=include_extra,
        fill_value=fill_value,
    )


def descriptives_table(
    desc_datas: Sequence[DescData],
    col_maps: ColMaps | None = None,
    row_maps: RowMaps | None = None,
    order_map: dict[str, int] = dict(),
    var_name: str = "",
    include_header: bool = True,
    include_extra: bool = True,
    include_midrule: bool = True,
    fill_value: NumOrStr = "",
) -> Table:
    """Create a table of descriptive statistics."""
    cols = [make_desc_col(data) for data in desc_datas]
    aligned = align_cells(*cols, fill_value=fill_value)
    rows = [Row(cells=[Cell(name=name, value=name)] + cells) for name, cells in aligned]
    rows = sorted(
        rows,
        key=lambda x: order_map.get(x.cells[0].name, float("inf")),
    )
    return construct_base(
        rows=rows,
        objs=desc_datas,
        col_maps=col_maps,
        row_maps=row_maps,
        order_map=order_map,
        var_name=var_name,
        include_header=include_header,
        include_extra=include_extra,
        include_midrule=include_midrule,
        fill_value=fill_value,
    )
