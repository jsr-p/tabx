from __future__ import annotations

import dataclasses
import dataclasses as dc
import itertools as it
import operator
from abc import ABC, abstractmethod
from collections import abc
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
from functools import reduce
from itertools import chain
from typing import (
    Callable,
    Iterable,
    Literal,
    Self,
    TypeVar,
    assert_never,
    cast,
    overload,
)

__all__ = [
    "Cmidrule",
    "Cmidrules",
    "Columns",
    "ColoredRow",
    "empty_columns",
    "empty_cell",
    "empty_cells",
    "empty_table",
    "Cell",
    "filled_columns",
    "filled_table",
    "Midrule",
    "Toprule",
    "Bottomrule",
    "multirow_column",
    "multicolumn_row",
    "Row",
    "Rule",
    "Table",
    "concat",
]


@dataclass
class Cell:
    """
    A cell in a table with optional formatting and spanning behavior.

    Represents a single value in a table, optionally spanning multiple columns
    or rows, and supporting LaTeX-style rendering (e.g., math mode, bold,
                                                   italic).

    ### Attributes

    :value: The displayed value in the table cell.
    - name: An optional identifier or key for the cell (used internally).
    - `style`: Text style for LaTeX rendering: 'math', 'bold', 'italic', or
    'none'.
    - `multicolumn`: Number of columns this cell spans.
    - `colspec`: Alignment of multicolumn text ('l', 'c', or 'r').
    - `multirow`: Number of rows this cell spans.
    - `width`: Width specification for multirow cells (LaTeX syntax, e.g.,
                                                     '*', '2cm').

    Raises:
    - ValueError: If both multicolumn and multirow are greater than 1.


    {lineno-start=1 emphasize-lines="2,3"}
    ```python
    from tabx import Cell
    print(Cell("1"))
    print(Cell("1"))
    print(Cell("1"))
    print(Cell("1"))
    ```

    \\multirow[〈vpos〉]{〈nrows〉}{〈width〉}[〈vmove〉]{〈text〉}
    """

    value: NumOrStr
    name: str = dc.field(
        default="",
        init=True,
        repr=True,
        metadata={"help": "The name of the cell, used for identification."},
    )
    style: Literal["math", "bold", "italic", "none"] = "none"
    multicolumn: int = 1
    colspec: Literal["l", "c", "r"] = "c"
    multirow: int = 1
    vpos: Literal["c", "t", "b", ""] = ""  # vertical position for multirow
    vmove: str = ""  # vertical move for multirow
    width: str = "*"  # for multirow width ("*", "2cm", etc.)

    def __repr__(self) -> str:
        if self.name:
            return f'Cell(name="{self.name}", value="{self.value}", multirow={self.multirow}, multicolumn={self.multicolumn})'
        return f'Cell(value="{self.value}", multirow={self.multirow}, multicolumn={self.multicolumn})'

    def __post_init__(self):
        if self.multicolumn <= 0:
            raise ValueError("Cannot have multicolumn <= 0")
        if self.multirow <= 0:
            raise ValueError("Cannot have multirow <= 0")

        if self.multicolumn > 1 and self.multirow > 1:
            raise ValueError(
                "Cell cannot be both multicolumn and multirow at the same time."
            )

    def __len__(self) -> int:
        if self.multicolumn > 1:
            return self.multicolumn
        return 1

    def clen(self) -> int:
        """Return the number of rows in a column this cell occupies."""
        return self.multirow

    def is_multirow(self) -> bool:
        """Return True if this cell is a multirow cell."""
        return self.multirow > 1

    def is_multicolumn(self) -> bool:
        """Return True if this cell is a multicolumn cell."""
        return self.multicolumn > 1

    def is_empty(self) -> bool:
        """Return True if this cell is empty."""
        return not self.value

    def render(self) -> str:
        text = str(self.value)

        match self.style:
            case "math":
                text = r"$" + text + r"$"
            case "bold":
                text = r"\textbf{" + text + "}"
            case "italic":
                text = r"\textit{" + text + "}"
            case "none":
                pass
            case _:
                raise ValueError(f"Unknown style: {self.style}")

        # Apply multicolumn
        if self.multicolumn > 1:
            text = (
                r"\multicolumn{"
                + str(self.multicolumn)
                + "}{"
                + self.colspec
                + "}{"
                + text
                + "}"
            )

        # Apply multirow
        if self.multirow > 1:
            # \\multirow[〈vpos〉]{〈nrows〉}{〈width〉}[〈vmove〉]{〈text〉}
            parts = [
                f"[{self.vpos}]" if self.vpos else "",
                f"{{{str(self.multirow)}}}",
                f"{{{self.width}}}" if self.width else "",
                f"[{self.vmove}]" if self.vmove else "",
                f"{{{text}}}",
            ]
            text = r"\multirow" + "".join(parts)

        return text

    def __truediv__(self: Self, other):
        if isinstance(other, (Table, Columns)):
            return other.prepend_row(Row([self]))
        if isinstance(other, Cell):
            return Table([Row([self]), Row([other])])
        if isinstance(other, (Cmidrule, Cmidrules, Midrule)):
            return Table([Row([self]), other])
        raise TypeError(
            f"unsupported operand type(s) for /: '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )

    @overload
    def __or__(self: Self, other: Row) -> Row: ...
    @overload
    def __or__(self: Self, other: Cell) -> Table: ...

    @overload
    def __or__(self: Self, other: Sequence[Cell]) -> Table: ...

    def __or__(self: Self, other):
        if isinstance(other, (Cmidrule, Cmidrules, Midrule)):
            raise TypeError(
                f"unsupported operand type(s) for |: '{type(self).__name__}' "
                f"and '{type(other).__name__}'"
            )
        if isinstance(other, Table):
            return Columns([Row([self])]) | other
        if isinstance(other, Columns):
            return Table.from_columns(Columns([Row([self])])) | other
        if isinstance(other, Cell):
            return Table([Row([self, other])])
        if match_seq(other, type_=Cell) == "seq":
            other = cast(list[Cell], other)
            return Table([Row([self])]) | Table([Row(other)])
        if isinstance(other, Row):
            return Row([self] + list(other.cells))
        raise TypeError(
            f"unsupported operand type(s) for |: '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )


class ColoredCell(Cell):
    """A colored `Cell`.

    Requires the `xcolor` package in LaTeX.
    """

    def __init__(
        self,
        value: str,
        color: str,
        name: str = "",
        multicolumn: int = 1,
        multirow: int = 1,
    ):
        super().__init__(
            name=name, value=value, multicolumn=multicolumn, multirow=multirow
        )
        self.color = color

    def __repr__(self) -> str:
        if self.name:
            return f"ColoredCell(name={self.name}, color={self.color})"
        return f"ColoredCell(color={self.color})"

    def render(self) -> str:
        return r"\cellcolor{" + self.color + "}" + super().render()


class EmptyCell(Cell):
    def __init__(self, name: str = ""):
        super().__init__(name=name, value="", multicolumn=1, multirow=1)

    def __repr__(self) -> str:
        if self.name:
            return f"EmptyCell(name={self.name})"
        return "EmptyCell()"

    def render(self) -> str:
        return ""


class Placeholder(Cell):
    def __init__(self, name: str = ""):
        super().__init__(name=name, value="", multicolumn=1, multirow=1)

    def __repr__(self) -> str:
        return f"PlaceholderCell(name={self.name})"

    def render(self) -> str:
        return ""


class MrEmptyCell(Cell):
    def __init__(self, name: str = "", mr: MultirowCell | None = None):
        super().__init__(name=name, value="", multicolumn=1, multirow=1)
        self.mr = mr

    def __repr__(self) -> str:
        if self.name:
            return f"MrEmptyCell(name={self.name})"
        return "MrEmptyCell()"

    def link(self, mr: MultirowCell):
        self.mr = mr

    def unlink(self):
        if not isinstance(self.mr, MultirowCell):
            raise ValueError("Cannot unlink unlinked MrEmptyCell")
        self.mr.decrease()
        self.mr = None

    def render(self) -> str:
        return ""


class MultirowCell(Cell):
    def __init__(
        self,
        value: NumOrStr,
        multirow: int,
        name: str = "",
        vpos: Literal["c", "t", "b", ""] = "c",
        vmove: str = "",
        width: str = "",
        style: Literal["math", "bold", "italic", "none"] = "none",
    ):
        super().__init__(
            name=name,
            value=value,
            multirow=multirow,
            vpos=vpos,
            vmove=vmove,
            width=width,
            style=style,
        )

        self.empty_cells = []

    @classmethod
    def from_cell(cls, cell: Cell):
        return cls(
            name=cell.name,
            value=cell.value,
            multirow=cell.multirow,
            vpos=cell.vpos,
            vmove=cell.vmove,
            width=cell.width,
            style=cell.style,
        )

    def __repr__(self) -> str:
        return f"MultirowCell(name={self.name}, value={self.value}, multirow={self.multirow})"

    def add_empty_cell(self, empty_cell: MrEmptyCell):
        self.empty_cells.append(empty_cell)
        empty_cell.link(self)

    def decrease(self):
        self.multirow -= 1

    # Hashing into dict based on id of object but equality just based on
    # values of attributes.
    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return (
            isinstance(other, MultirowCell)
            and self.name == other.name
            and self.value == other.value
            and self.multirow == other.multirow
        )


def multirow_column(
    value: str,
    multirow: int,
    name: str = "",
    vpos: Literal["c", "t", "b", ""] = "",
    vmove: str = "",
    width: str = "*",
    style: Literal["math", "bold", "italic", "none"] = "none",
    pad_before: int = 0,
    pad_after: int = 0,
    align: str = "c",
) -> Columns:
    """Creates a column with a multirow cell and empty cells."""
    mrf = MultirowCell(
        name=name,
        value=value,
        multirow=multirow,
        vpos=vpos,
        vmove=vmove,
        width=width,
        style=style,
    )
    ecells = []
    for _ in range(multirow - 1):
        f = MrEmptyCell()
        mrf.add_empty_cell(f)
        ecells.append(f)
    col = Columns(rows=[Row([mrf])] + [Row([f]) for f in ecells], align=align)
    if pad_before > 0:
        col = empty_columns(pad_before, 1) / col
    if pad_after > 0:
        col = col / empty_columns(pad_after, 1)
    return col


def multicolumn_row(
    value: str,
    multicolumn: int,
    name: str = "",
    colspec: Literal["l", "c", "r"] = "c",
    pad_before: int = 0,
    pad_after: int = 0,
) -> Row:
    """Creates a row with a multicolumn cell and empty cells."""
    cell = Cell(
        value=value,
        multicolumn=multicolumn,
        name=name,
        colspec=colspec,
    )
    return Row(empty_cells(pad_before) + [cell] + empty_cells(pad_after))


def slice_range_cmidrule(index: slice, cm: Cmidrule):
    idx_start = 0  # Full interval
    idx_stop = index.stop
    if not index.stop:
        idx_stop = cm.end
    return range(idx_start, idx_stop)


def range_to_interval(r: range):
    return min(r), max(r)


class Cmidrule:
    """A LaTeX cmidrule.

    Up to tree we go, this works in the docs:

    ```{literalinclude} ../../../../examples/ex2.py
    :start-after: start example 1
    :end-before: end example 1
    ```

    ```{include} ../../../../examples/doctestex.md
    ```
    """

    def __init__(
        self,
        start: int,
        end: int,
        trim: str = "lr",
        dim: str = "",
    ):
        if start > end:
            raise ValueError(f"Start ({start}) must be less than end ({end})")
        if start < 1 or end < 1:
            raise ValueError(f"Start ({start}) and end ({end}) must be >= 1")
        self.start = start
        self.end = end
        self.trim = trim
        self.rule = r"\cmidrule"
        self.dim = dim

    def __repr__(self) -> str:
        return f"Cmidrule(start={self.start}, end={self.end}, lr={self.trim})"

    def __eq__(self, other):
        if not isinstance(other, Cmidrule):
            raise TypeError()
        return (self.start, self.end, self.trim) == (other.start, other.end, other.trim)

    @property
    def interval(self) -> tuple[int, int]:
        """
        Cmidrules are 1-indexed in latex and right-inclusive.

        """
        return (self.start - 1, self.end)

    @property
    def interval_range(self) -> range:
        return range(*self.interval)

    def __getitem__(
        self,
        index: int | slice,
        standardize: bool | int | None = None,
    ) -> Cmidrule:
        """
        Cmidrules are 1-indexed in latex and right-inclusive.
        """

        interval = self.interval
        interval_range = self.interval_range

        if isinstance(index, int):
            if index not in interval_range:
                raise IndexError(
                    f"Index {index} out of bounds for {self} with {self.interval_range=}"
                )
            return Cmidrule(start=1, end=1, trim=self.trim)

        slice_range = slice_range_cmidrule(index, self)

        # slice
        slice_idc = slice_range[index]

        if not slice_idc:
            raise IndexError(
                f"Index out of range: {slice_range=}; {index=}; {slice_idc=}"
            )

        start_slice, end_slice = min(slice_idc), max(slice_idc)
        interval_slice = (start_slice, end_slice + 1)
        cond = interval_conditions(interval, interval_slice)

        if standardize and isinstance(standardize, bool):
            std_base = max(start_slice, 1, self.start - 1)
        elif standardize and isinstance(standardize, int):
            std_base = standardize
            pass
        else:
            std_base = 0

        match cond.condition:
            case "center" | "left" | "right":
                start = cond.start + 1
                end = cond.end
                if standardize:
                    start -= std_base
                    end -= std_base
                return Cmidrule(
                    # add one to convert back to 1-index
                    start=start,
                    end=end,
                    trim=self.trim,
                )
            case "none":
                raise ValueError(
                    "Index out of range; overlap='none'; "
                    f"{interval=}; {slice_range=}; {index=}; {slice_idc=}"
                )

    def __add__(self, other: int | tuple[int, int]) -> Cmidrule:
        """
        Add an offset to a Cmidrule, returning a new Cmidrule.
        Supports:
          - int: shifts both start and end by the same amount
          - tuple[int, int]: shifts start and end independently
        """
        if isinstance(other, int):
            start = self.start + other
            end = self.end + other
        elif isinstance(other, tuple):
            dstart, dend = other
            start = self.start + dstart
            end = self.end + dend
        else:
            raise TypeError(f"Unsupported type: {type(other)}")
        if start < 1 or end < 1:
            raise ValueError(f"Out of bounds {start=}, {end=}")
        return Cmidrule(start=start, end=end, trim=self.trim)

    def __sub__(self, other: Cmidrule | int | tuple[int, int]):
        """
        Adding two Cmidrules should result in a Cmidrules object.

        We shouldn't return a Cmidrule object because often we have.
        """
        if isinstance(other, int):
            return self + (-other)
        elif isinstance(other, tuple):
            dstart, dend = other
            return self + (-dstart, -dend)
        else:
            raise TypeError(f"{type(other)}")

    def __or__(self, other):
        if isinstance(other, Cmidrule):
            if overlap := (
                set(range(self.start, self.end + 1))
                & set(range(other.start, other.end + 1))
            ):
                raise ValueError(f"Cmidrules overlap: {overlap=}")
            elif self.end < other.start:
                return Cmidrules([self, other])
            elif self.start > other.end:
                return Cmidrules([other, self])
        if isinstance(other, Cmidrules):
            return Cmidrules([self] + other.values)
        raise TypeError(
            f"unsupported operand type(s) for |: '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )

    @overload
    def __truediv__(self: Self, other: Table) -> Table: ...

    @overload
    def __truediv__(self: Self, other) -> Table: ...

    def __truediv__(self: Self, other):
        if isinstance(other, (Table, Columns)):
            return other.prepend_row(self)
        if isinstance(other, Cell):
            return Table([self, Row([other])])
        if isinstance(other, (Cmidrule, Cmidrules, Midrule)):
            return Table([self, other])
        raise TypeError()

    def __len__(self):
        return 1

    def clen(self) -> int:
        return self.end - self.start + 1

    def rlen(self) -> int:
        return 1

    def dlen(self) -> int:
        return self.end - self.start

    def render_base(self) -> str:
        if self.trim and self.dim:
            return f"{self.rule}[{self.dim}]({self.trim}){{{self.start}-{self.end}}}"
        if self.trim:
            return f"{self.rule}({self.trim}){{{self.start}-{self.end}}}"
        return f"{self.rule}{{{self.start}-{self.end}}}"

    def render(self) -> str:
        r"""Cmidrule doesn't need a latex newline `\\`"""
        base = self.render_base()
        return base


@dataclass
class Cmidrules:
    """A collection of Cmidrules."""

    values: list[Cmidrule]

    start: int = dataclasses.field(init=False)
    end: int = dataclasses.field(init=False)

    def __repr__(self) -> str:
        return f"Cmidrules(#cmidrules={len(self.values)})"

    def __len__(self) -> int:
        return sum(cmidrule.clen() for cmidrule in self.values)

    def render(self) -> str:
        return "\n".join(cmidrule.render_base() for cmidrule in self.values)

    def __post_init__(self):
        # check overlap
        for cm1, cm2 in it.combinations(self.values, 2):
            cond = interval_conditions(cm1.interval, cm2.interval)
            if not cond.condition == "none":
                raise ValueError(f"Cmidrules {cm1=} and {cm2=} overlap.")
        if self.values:  # Else empty cmidrule
            self.start = min(self.values, key=operator.attrgetter("start")).start
            self.end = max(self.values, key=operator.attrgetter("end")).end
            self.values = sorted(self.values, key=operator.attrgetter("start"))

    def clen(self) -> int:
        max_end = max(self.values, key=operator.attrgetter("end")).end
        min_start = min(self.values, key=operator.attrgetter("start")).start
        return max_end - min_start + 1

    def __getitem__(
        self,
        index: int | slice,
        standardize: bool | int | None = None,
    ) -> Cmidrules:
        """
        Cmidrules are 1-indexed in latex
        """

        if isinstance(index, int):
            index = standardize_index(index, len(self))

        cmids = []
        for cmidrule in self.values:
            try:
                cmids.append(cmidrule.__getitem__(index, standardize=standardize))
            except (ValueError, IndexError):
                pass
        if not cmids and isinstance(index, slice):
            return Cmidrules([])
        return Cmidrules(values=cmids)

    def print(self):
        print(f"[{', '.join([str(c) for c in self.values])}]")

    def __or__(self, other):
        if isinstance(other, Cmidrule):
            return Cmidrules(self.values + [other])
        if isinstance(other, Cmidrules):
            return Cmidrules(self.values + other.values)
        raise TypeError(
            f"unsupported operand type(s) for |: '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )

    @overload
    def __truediv__(self: Self, other: Table) -> Table: ...

    @overload
    def __truediv__(self: Self, other) -> Table: ...

    def __truediv__(self: Self, other):
        if isinstance(other, (Table, Columns)):
            return other.prepend_row(self)
        if isinstance(other, Cell):
            return Table([self, Row([other])])
        if isinstance(other, (Cmidrule, Cmidrules, Midrule)):
            return Table([self, other])
        raise TypeError(
            f"unsupported operand type(s) for /: '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )


class Rule(ABC):
    """Base class rules."""

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __len__(self):
        return 1

    def clen(self) -> int:
        """
        If Midrule only element in rows then it is 1 column.
        """
        return 1

    @abstractmethod
    def render(self) -> str:
        """
        Return the LaTeX code representation of the rule.
        Must be implemented by subclasses.
        """
        pass

    def __getitem__(self, _) -> Self:
        return self

    def __truediv__(self, other: Table | Columns):
        if isinstance(other, Cell):
            return Columns([self, Row([other])])
        if isinstance(other, (Table, Columns)):
            return other.prepend_row(self)
        if isinstance(other, Rule):
            raise TypeError(
                "Recall wisdom from booktabs docs: '2. Never use double rules.'"
                f"Got '{type(other).__name__}"
            )
        raise TypeError()


@dataclass
class Midrule(Rule):
    """A LaTeX midrule."""

    def __repr__(self) -> str:
        return "Midrule"

    def render(self) -> str:
        # r"\midrule" doesn't need a latex newline `\\`
        return r"\midrule"


@dataclass
class Bottomrule(Rule):
    """A LaTeX bottomrule."""

    width: str = ""

    def __repr__(self) -> str:
        return "Bottomrule"

    def render(self) -> str:
        # r"\midrule" doesn't need a latex newline `\\`
        if self.width:
            return r"\bottomrule[" + self.width + "]"
        return r"\bottomrule"


@dataclass
class Toprule(Rule):
    """A LaTeX toprule."""

    width: str = ""

    def __repr__(self) -> str:
        return "Toprule"

    def render(self) -> str:
        if self.width:
            return r"\toprule[" + self.width + "]"
        return r"\toprule"


class ColoredRow(Rule):
    """Colored Row.

    Stack it above a row in a `Table` to color the row.

    Requires the [xcolor](https://ctan.org/pkg/xcolor?lang=en)
    Latex package.

    Examples:

    ```python
    from tabx import Table, Row, ColoredRow
    tab = Table.from_cells([[1, 2, 3], [4, 5, 6]])
    tab = ColoredRow("red") / tab
    ```

    ![table](../../figs/color_red_simple.png)
    """

    def __init__(self, color: str):
        self.color = color
        super().__init__()

    def __repr__(self) -> str:
        return f"ColoredRow(color={self.color})"

    def render(self) -> str:
        return r"\rowcolor{" + self.color + "}"


@dataclass
class IntervalCondition:
    start: int
    end: int
    condition: Literal["left", "center", "right", "none"]

    def diff(self):
        """Return the difference between start and end."""
        return self.end - self.start


def interval_conditions(
    interval: tuple[int, int],
    slice_: tuple[int, int],
) -> IntervalCondition:
    """Determine how `slice_` overlaps with `interval` (both inclusive).

    Returns:
        IntervalCondition with the overlapping segment and label:
        - "left": overlaps from the left
        - "center": fully inside interval
        - "right": overlaps from the right
        - "none": no overlap
    """

    i_start, i_end = interval
    s_start, s_end = slice_

    match (s_start < i_start, s_end > i_end, s_start >= i_end, s_end <= i_start):
        case (_, _, True, _) | (_, _, _, True):
            return IntervalCondition(0, 0, "none")
        case (True, False, False, False):
            return IntervalCondition(i_start, s_end, "left")
        case (False, True, False, False):
            return IntervalCondition(s_start, i_end, "right")
        case (True, True, False, False):
            return IntervalCondition(i_start, i_end, "center")
        case (False, False, False, False):
            return IntervalCondition(s_start, s_end, "center")
        case _:  # pragma: no cover
            assert_never("Unreachable case in interval_conditions")


def is_subint(a: tuple[int, int], b: tuple[int, int]) -> bool:
    """Check if a is a subinterval of b."""
    return a[0] >= b[0] and a[1] <= b[1]


LenMeasure = Literal["column", "row"]


def slice_cells(
    cells: Sequence[Cell], sl: slice, len_measure: LenMeasure = "column"
) -> Sequence[Cell]:
    """
    Slices cells.

    """
    if (sl.step or 1) > 1:  # Hack for getattr not having default value option
        raise ValueError(
            "Step size larger than 1 not allowed, you maniac. "
            "Go outside and get some fresh air."
        )

    start, stop = sl.start, sl.stop

    if (isinstance(start, int) and isinstance(stop, int)) and (start == stop):
        # e.g. degenerate slice(0, 0), slice(1, 1) etc..

        return []

    if len_measure == "column":
        lens = [len(f) for f in cells]
    else:
        lens = [f.clen() for f in cells]

    if not isinstance(start, int):
        start = 0
    if not isinstance(stop, int):
        stop = sum(lens)  # 0-indexed

    cs = cumsum(lens)
    idc_s = [0] + cs[:-1]
    idcs = [(s, s + e) for s, e in zip(idc_s, lens)]
    idc_to_f = {idc: i for i, idc in enumerate(idcs)}

    # Get the cells that are in the slice
    slice_cells = []
    for idc, i in idc_to_f.items():
        f = cells[i]
        is_mc, is_mr = f.is_multicolumn(), f.is_multirow()
        if is_subint(idc, (start, stop)):
            # Cell is inside slice interval
            slice_cells.append(f)
        elif is_mc or is_mr:
            istart, istop = idc
            ic = interval_conditions((istart, istop), (start, stop))
            match ic.condition:
                case "center" | "left" | "right":
                    if is_mc:
                        slice_cells.append(
                            Cell(
                                name=f.name,
                                value=f.value,
                                multicolumn=ic.diff(),
                            )
                        )
                    elif is_mr:
                        slice_cells.append(
                            Cell(
                                name=f.name,
                                value=f.value,
                                multirow=ic.diff(),
                            )
                        )
                case "none":
                    pass
    return slice_cells


def is_contiguous(idc_rest: list[int]):
    return all(e - s == 1 for s, e in zip(idc_rest[:-1], idc_rest[1:]))


def slices_from_indices(indices: list[int]) -> list[slice]:
    """Convert sorted list of indices into minimal list of contiguous slices."""
    if not indices:
        return []

    slices = []
    start = prev = indices[0]

    for i in indices[1:]:
        if i == prev + 1:
            prev = i
        else:
            slices.append(slice(start, prev + 1))
            start = prev = i
    slices.append(slice(start, prev + 1))
    return slices


def slice_from_set(rest: set[int]) -> slice | list[slice]:
    idc_rest = sorted(list(rest))
    if not rest:
        return slice(0, 0)
    if len(idc_rest) == 1:
        (val,) = idc_rest
        return slice(val, val + 1)

    if is_contiguous(idc_rest):
        return slice(min(idc_rest), max(idc_rest) + 1)  # Including max

    # Non-contiguous parts; slice was inside array; e.g.
    # slice array[2:4] and full array array[0:6]
    return slices_from_indices(idc_rest)


def slice_array(array: list[list[Cell]], sl: slice) -> list[list[Cell]]:
    array = deepcopy(array)  # If we slice multiple times in repl

    # Slice array
    idc = list(range(len(array)))
    idc_sl = idc[sl]
    idc_rest = set(idc) - set(idc_sl)

    # Elements that weren't sliced
    sl_rest = slice_from_set(idc_rest)

    if isinstance(sl_rest, list):
        rest = [subarr for slr in sl_rest for subarr in array[slr]]
    else:
        rest = array[sl_rest]

    selected = array[sl]

    # Check if elements in the non-selected parts are part of a multirow
    # - if emptycell then we unlink it
    # - if multirowcell we add it to dict for further logic below
    mr_map: dict[MultirowCell, list[tuple[MrEmptyCell, int, int]]] = dict()
    for i, row in enumerate(rest):
        for ele in row:
            if isinstance(ele, MrEmptyCell):
                ele.unlink()
            if isinstance(ele, MultirowCell):
                mr_map[ele] = []

    # Slice from above rows[2:] logic where multirow in rows[:2] and its
    # empty cells inside rows[2:].
    # Find mrempty cells in the selected slice and add them to the mr_map
    # if their multirow has been removed by the slice
    for i, row in enumerate(selected):
        for j, ele in enumerate(row):
            if isinstance(ele, MrEmptyCell):
                if ele.mr is not None and ele.mr in mr_map:
                    mr_map[ele.mr].append((ele, i, j))

    # Swap non-selected multirows with its first empty cell in the
    # selected part and unlink the cell.
    for k in mr_map:
        vals = mr_map[k]
        if vals:
            vals = sorted(vals, key=operator.itemgetter(1))
            cell, i, j = min(vals, key=operator.itemgetter(1))
            selected[i][j] = k
            cell.unlink()

    return array[sl]


def slice_rows_horizontal(cols: Columns | Table, sl: slice):
    """Slices each row in the columns by `sl`.

    Corresponds to a slice across columns i.e. cols[:, n:m]
    in familiar numpy notation.
    """
    rows = cols.all_rows()
    sliced_rows = []
    for row in rows:
        if isinstance(row, (Cmidrule, Cmidrules)):
            # If sl.start is None we slice whole range from left hence no
            # standardization
            sliced_rows.append(row.__getitem__(sl, standardize=sl.start))
        else:
            sliced_rows.append(row[sl])
    if isinstance(cols, Table):
        return Table.from_columns(columns=Columns(rows=sliced_rows))
    return Columns(rows=sliced_rows)


def slice_rows_vertical(cols: Columns | Table, sl: slice):
    """
    Slices the columns by `sl` and returns a new Columns object.

    Corresponds to a slice cols[n:m] across rows in familiar numpy notation.
    """
    if (sl.start and sl.stop) and (sl.start == sl.stop):
        ecols = Columns(rows=[], align="c")
        if isinstance(ecols, Table):
            return Table.from_columns(ecols)
        return ecols
    rows = cols.all_rows()
    array = []
    orig = dict()
    idc = list(range(len(rows)))
    for i, row in enumerate(rows):
        if isinstance(row, Row):
            array.append(row.cells)
        else:
            array.append([Placeholder() for _ in range(cols.ncols)])
            orig[i] = row

    new_rows = []
    slices = slice_array(array, sl)
    for idx, cells in zip(idc[sl], slices):
        if idx in orig:
            new_rows.append(orig[idx])
        else:
            new_rows.append(Row(cells=cells))

    if isinstance(cols, Table):
        return Table.from_columns(columns=Columns(new_rows, align=cols.align))
    return Columns(new_rows, align=cols.align)


def index_to_slice(index: int, values: Sequence) -> slice:
    idc = list(range(len(values)))
    try:
        index = idc[index]
    except IndexError:
        raise IndexError(f"Index {index} out of bounds with {idc=} and{values=}")
    return slice(index, index + 1)


def standardize_index(index: int, n: int):
    return list(range(n))[index]


@dataclass
class Row:
    """A row in a table.

    Consists of a sequence of `Cell` objects.
    """

    cells: Sequence[Cell]

    def __post_init__(self):
        if not (
            isinstance(self.cells, abc.Sequence)
            and all(isinstance(f, Cell) for f in self.cells)
        ):
            raise TypeError(
                "Cells must be a sequence of Cell objects."
                f" Got {self.cells=} of types {[type(f) for f in self.cells]}"
            )

    def __repr__(self) -> str:
        return f"Row(#cells={len(self.cells)})"

    def __len__(self) -> int:
        return sum(len(cell) for cell in self.cells)

    def __getitem__(self, index: int | slice) -> Row:
        cells = self.cells
        if isinstance(index, slice):
            return Row(cells=slice_cells(cells, index, "column"))
        sl = index_to_slice(index, cells)
        return Row(cells=slice_cells(cells, sl, "column"))

    def __setitem__(self, index: int, cell: Cell):
        self.cells = list(self.cells)  # Sequence doesn't allow setitem
        self.cells[index] = cell

    def render(self) -> str:
        return " & ".join(cell.render() for cell in self.cells) + r" \\"

    def __truediv__(self, other):
        if isinstance(other, TableRow_):
            return Columns([self, other])
        if isinstance(other, Table | Columns):
            return other.prepend_row(self)
        raise TypeError(
            f"unsupported operand type(s) for /: '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )

    def __or__(self: Self, other):
        if isinstance(other, Row):
            return Row(list(self.cells) + list(other.cells))
        if isinstance(other, Cell):
            return Row(list(self.cells) + [other])
        raise TypeError(
            f"unsupported operand type(s) for |: '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )


# type alias notation >= 3.12
type TableRow = Row | Cmidrule | Cmidrules | Rule
TableRow_ = (Row, Cmidrule, Cmidrules, Rule)
type NumOrStr = int | float | str


def len_rows(rows: Iterable[TableRow]) -> set[int]:
    """Counts the number of cells in each row.

    - Midrules don't count towards #cells in a given row.
        - Cmidrule, Cmidrules, and Midrule
        - This is the reason for their __len__ returning 0.
    - Applying `len` to a Cell measures how many columns it occupies.
      If it is a multicolumn cell, it will count as that many columns.
    """
    return set(
        [len(row) for row in rows if not isinstance(row, (Cmidrule, Cmidrules, Rule))]
    )


def render_rows(rows: Iterable[TableRow]) -> str:
    """Renders a sequence of `TableRow` objects to a LaTeX table body."""
    return "\n".join(row.render() for row in rows)


def int_idx_to_slice(n: int, index: int):
    """
    Handles negative index by delegating to usual python indexing.
    """
    index = list(range(n))[index]
    sl = slice(index, index + 1)
    return sl


def validate_rows(rows: Sequence[TableRow]):
    """
    Returns the length of the rows i.e. the number of columns.
    Raises ValueError if the rows are not of the same length.
    """
    if not rows:
        return 0

    if not isinstance(rows, abc.Sequence):
        raise TypeError(f"Rows must be a Sequence of TableRow objects; got {rows=}")

    if not all(isinstance(row, TableRow_) for row in rows):
        raise TypeError(
            f"All elements of rows must be TableRow instances; got {
                [type(row) for row in rows]
            }"
        )

    s = len_rows(rows)

    if len(s) > 1:
        raise ValueError(
            f"All rows must have same #cells i.e. columns differ."
            f" Found unique row lengths: {s}"
        )

    if len(s) == 0:  # Empty column or only (c)midrules
        if all(isinstance(r, Midrule) for r in rows):
            return 1
        elif all(isinstance(r, (Cmidrule, Cmidrules, Midrule)) for r in rows):
            rows = cast(Sequence[Cmidrule | Cmidrules | Midrule], rows)
            min_start = min(
                r.start for r in rows if isinstance(r, (Cmidrule, Cmidrules))
            )
            max_end = max(r.end for r in rows if isinstance(r, (Cmidrule, Cmidrules)))
            return max_end - min_start + 1

    # Unique single element which is the number of columns
    ncols = list(s)[0]
    return ncols


def is_type_seq(seq, type_: type = int):
    return (
        isinstance(seq, Sequence)
        and len(seq) > 0
        and all(isinstance(i, type_) for i in seq)
    )


def is_seq_of_type_seq(seq, type_: type = int):
    return (
        isinstance(seq, Sequence)
        and len(seq) > 0
        and all(is_type_seq(i, type_) for i in seq)
    )


type SequenceKind = Literal["seq", "seq_of_seq", "other"]


def match_seq(x, type_) -> SequenceKind:
    """Matches x and returns the type of sequence.

    - "seq": Sequence of type
    - "seq_of_seq": Sequence of sequences of type
    - "other": Other type
    """
    match x:
        case Sequence() if is_type_seq(x, type_):
            return "seq"
        case Sequence() if is_seq_of_type_seq(x, type_):
            return "seq_of_seq"
        case _:
            return "other"


class Rows:
    values: Sequence[TableRow]
    ncols: int
    nrows: int

    def __post_init__(self): ...


class Columns:
    """Columns class for LaTeX tables.

    This is the base of the `Table` object.
    """

    ncols: int
    """Number of columns in the table."""
    nrows: int
    """Number of rows in the table."""
    rows: Sequence[TableRow]
    """List of rows in the table."""
    align: str = ""
    """Alignment string of columns"""

    def __init__(self, rows: Sequence[TableRow], align: str = ""):
        self.rows = rows
        self.align = align

        self.__post_init__()

    def __post_init__(self):
        # ncols
        ncols = validate_rows(self.rows)
        if not ncols:
            # empty columns
            ncols = 0
        self.ncols = ncols
        self.nrows = len(self.rows)

        if not self.align:
            self.align = "c" * self.ncols

        # Validate rows in columns; linking multirows and their cells
        validate_column_rows(self.rows)
        validate_cmidrules(self)

    def __repr__(self) -> str:
        return f"Columns(nrows={self.nrows}, ncols={self.ncols})"

    def __len__(self) -> int:
        return self.nrows

    def render(self) -> str:
        body = render_rows(self.rows)
        return body

    def set_align(self, align: str):
        """Set the alignment of the columns.

        Hard to validate as e.g. with colored columns the alignment
        string becomes long and verbose.
        """
        self.align = align
        return self

    def all_rows(self) -> Sequence[TableRow]:
        """Return all rows"""
        return self.rows

    def total_rows(self) -> int:
        """Return total number of rows, including header."""
        return len(self.rows)

    def print_rows(self):
        rows = self.all_rows()
        for i, row in enumerate(rows, start=1):
            if isinstance(row, Row):
                row_str = ", ".join([str(f) for f in row.cells])
            elif isinstance(row, Cmidrules):
                row_str = ", ".join([str(c) for c in row.values])
            else:
                row_str = str(row)
            print(f"Row: {i}: [{row_str}]")

    @property
    def shape(self) -> tuple[int, int]:
        """Return the shape of the table."""
        return self.nrows, self.ncols

    def print(self):
        print(self.render())

    def prepend_row(self, row: TableRow):
        """Prepend a row."""
        if not isinstance(row, TableRow_):
            raise TypeError(f"Row must be a TableRow object; got {type(row)}")
        return Columns(rows=[row] + list(self.rows), align=self.align)

    def append_row(self, row: TableRow):
        """Append a row"""
        if not isinstance(row, TableRow_):
            raise TypeError(f"Row must be a TableRow object; got {type(row)}")
        return Columns(rows=list(self.rows) + [row], align=self.align)

    def insert_row(self, row: TableRow, index: int):
        """Insert a row at index."""
        if not isinstance(row, TableRow_):
            raise TypeError(f"Row must be a TableRow object; got {type(row)}")
        index = list(range(self.nrows))[index]
        return Columns(
            rows=list(self.rows[:index]) + [row] + list(self.rows[index:]),
            align=self.align,
        )

    @classmethod
    def from_cells(
        cls,
        cells: Sequence[Cell] | Sequence[Sequence[Cell]],
    ):
        """Create a Column from a sequence of cells."""
        match match_seq(cells, type_=Cell):
            case "seq":
                cells = cast(Sequence[Cell], cells)
                return cls(
                    rows=[Row([cell]) for cell in cells],
                )
            case "seq_of_seq":
                cells = cast(Sequence[Sequence[Cell]], cells)
                return cls(
                    rows=[Row([cell for cell in row]) for row in cells],
                )
            case "other":
                raise TypeError(
                    f"Cells must be a sequence of Cell objects or a "
                    f"sequence of sequence of Cell objects; got {cells=}"
                )

    @classmethod
    def from_values(
        cls,
        values: Sequence[NumOrStr] | Sequence[Sequence[NumOrStr]],
    ):
        """Create a Column from a sequence of values.


        Values could be str, int, float.
        """
        if any(isinstance(val, TableRow_) for val in values):
            raise ValueError("Cannot pass TableRow_ as value")
        match match_seq(values, type_=(int, float, str)):
            case "seq":
                values = cast(Sequence[NumOrStr], values)
                return cls(
                    rows=[Row([Cell(str(value))]) for value in values],
                )
            case "seq_of_seq":
                values = cast(Sequence[Sequence[NumOrStr]], values)
                return cls(
                    rows=[Row([Cell(str(value)) for value in row]) for row in values],
                )
            case "other":
                raise TypeError(
                    f"Cells must be a sequence of objects or a "
                    f"sequence of sequence of objects; got {values=}"
                )

    def __getitem__(
        self,
        index: int | slice | tuple[slice | int, slice | int],
    ) -> Columns:
        if isinstance(index, int):
            sl = self._save_index_to_slice(index, self.nrows)
            return slice_rows_vertical(self, sl)
        if isinstance(index, slice):
            return slice_rows_vertical(self, index)
        if isinstance(index, tuple) and len(index) == 2:
            idx_row, idx_column = index
            # handle case of either being an integer
            if isinstance(idx_row, int):
                idx_row = self._save_index_to_slice(idx_row, self.nrows)
            if isinstance(idx_column, int):
                idx_column = self._save_index_to_slice(idx_column, self.ncols)
            # Slice and return
            cols = slice_rows_vertical(self, idx_row)
            return slice_rows_horizontal(cols, idx_column)
        raise ValueError(f"Index {index} not valid")

    def _save_index_to_slice(self, index: int, n: int):
        try:
            slice = int_idx_to_slice(n, index)
        except IndexError:
            raise IndexError(f"Index {index} out of bounds for {n}")
        else:
            return slice

    @overload
    def __or__(self: Self, other: Table) -> Table: ...

    # (col | tab) | tab -> tab

    @overload
    def __or__(self: Self, other) -> Self: ...

    # tab | cols -> tab; cols | cols -> cols

    def __or__(self: Columns | Table, other):
        """Overload `|`"""
        if isinstance(other, Cell):
            other = Columns([Row([other])])  # delegate to Columns below
        if isinstance(other, Table):
            cols = join_columns([self, other])
            return Table.from_columns(cols)
        if isinstance(other, Columns):
            cols = join_columns([self, other])
            if isinstance(self, Table):
                return Table.from_columns(cols)
            return cols
        raise TypeError(
            f"unsupported operand type(s) for |: '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )

    @overload
    def __truediv__(self: Self, other: Table) -> Table: ...

    # (col | tab) | tab -> tab

    @overload
    def __truediv__(self: Self, other) -> Self: ...

    # tab | cols -> tab; cols | cols -> cols

    def __truediv__(self: Columns | Table, other):
        """Overload `/`"""
        if isinstance(other, Cell):
            return self.append_row(Row([other]))
        if isinstance(other, (Rule, Row, Cmidrule, Cmidrules)):
            return self.append_row(other)
        if isinstance(other, Table):
            cols = join_rows([self, other])
            return Table.from_columns(cols)
        if isinstance(other, Columns):
            cols = join_rows([self, other])
            if isinstance(self, Table):
                return Table.from_columns(cols)
            return cols
        raise TypeError(
            f"unsupported operand type(s) for /: '{type(self).__name__}' "
            f"and '{type(other).__name__}'"
        )

    def __eq__(self, other):
        if not isinstance(other, Columns):
            raise TypeError()
        equal_rows = all(
            [r1 == r2 for r1, r2 in zip(self.all_rows(), other.all_rows())]
        )
        equal_dim = (self.nrows, self.ncols) == (other.nrows, other.ncols)
        return equal_rows and equal_dim


class Column(Columns):
    def __init__(
        self,
        rows: Sequence[TableRow],
        align: str | None = None,
    ):
        if not align:
            align = "c"
        if len(align) > 1:
            raise ValueError(
                f"Column alignment must be a single character. Found: {align}"
            )
        super().__init__(rows=rows, align=align)
        if self.ncols != 1:
            raise ValueError(f"Column must have exactly 1 column. Found: {self.ncols}")
        validate_column_rows(rows)

    def __len__(self) -> int:
        """Return the number of rows in the column.

        Everything counts as a row, including (c)midrules.
        """
        return len(self.rows)

    def __repr__(self) -> str:
        return f"Column(#rows={len(self.rows)}, n={self.ncols})"


class Table(Columns):
    """Table class for LaTeX tables.

    This is the main class for creating LaTeX tables.
    Implementation wise a `Table` is a `Columns` object with some extras
    functionality.
    """

    def __init__(self, rows: Sequence[TableRow], align: str = ""):
        super().__init__(rows=rows, align=align)

    @classmethod
    def from_columns(
        cls,
        columns: Columns,
    ):
        """Create a Table from rows."""
        return cls(rows=columns.rows, align=columns.align)

    @property
    def columns(self) -> Columns:
        """Return the columns of the table."""
        return Columns(rows=self.rows, align=self.align)

    def __getitem__(
        self,
        index: int | slice | tuple[int | slice, int | slice],
    ) -> Table:
        result = super().__getitem__(index)
        return Table.from_columns(result)

    def __repr__(self):
        return f"Table(nrows={self.nrows}, ncols={self.ncols})"

    def render(
        self,
        custom_render: Callable[..., str] | None = None,
        *args,
        **kwargs,
    ):
        """Render the table to a LaTeX string.

        It wraps the table in a tabular environment by default.
        If `custom_render` is provided, it will be used to render the table.
        """
        if self.ncols == 0 or self.nrows == 0:
            raise ValueError("Cannot render empty table")
        if custom_render is not None:
            return custom_render(self, *args, **kwargs)
        body = render_rows(self.rows)
        return render_body(body, n=self.ncols, align=self.align)

    def render_body(self) -> str:
        """Render the body of the table without the tabular environment."""
        return render_rows(self.rows)

    def prepend_row(self, row: TableRow):
        """Prepend a row."""
        return Table.from_columns(super().prepend_row(row))

    def append_row(self, row: TableRow):
        """add a row."""
        return Table.from_columns(super().append_row(row))

    def insert_row(self, row: TableRow, index: int):
        """insert a row."""
        return Table.from_columns(super().insert_row(row, index))

    def print(
        self,
        custom_render: Callable[..., str] | None = None,
    ):
        print(self.render(custom_render))

    @classmethod
    def from_cells(
        cls,
        cells: Sequence[Cell] | Sequence[Sequence[Cell]],
    ):
        out = Columns.from_cells(cells)
        return cls.from_columns(out)

    @classmethod
    def from_values(
        cls,
        values: Sequence[NumOrStr] | Sequence[Sequence[NumOrStr]],
    ):
        """
        Construct Table from values.
        """
        out = Columns.from_values(values)
        return cls.from_columns(out)


def empty_columns(nrows: int, ncols: int):
    """Create empty columns with `nrows` and `ncols`."""
    return Columns(
        rows=[Row(empty_cells(ncols)) for _ in range(nrows)],
        align="c" * ncols,
    )


def filled_columns(nrows: int, ncols: int, value: str, **kwargs):
    """Creates columns with `nrows` and `ncols` filled with `value`."""
    return Columns(
        rows=[Row([Cell(value, **kwargs) for _ in range(ncols)]) for _ in range(nrows)],
    )


def empty_table(nrows: int, ncols: int):
    """Create an empty table with `nrows` and `ncols`."""
    return Table.from_columns(empty_columns(nrows, ncols))


def filled_table(nrows: int, ncols: int, value: str, **kwargs):
    """Creates a table with `nrows` and `ncols` filled with `value`."""
    return Table.from_columns(filled_columns(nrows, ncols, value, **kwargs))


def reduce_cells_to_col(cells: list[Cell | Columns]) -> Columns:
    out = reduce(lambda x, y: x / y, cells)
    out = cast(Columns, out)
    return out


def reduce_horizontal(values):
    """
    Cannot use this with multirow cells while they should be linked
    across the table.
    """
    if isinstance(values, TableRow_):
        return values
    if all(isinstance(r, Cell) for r in values):
        values = cast(Sequence[Cell], values)
        return reduce(lambda x, y: x | y, values)
    raise ValueError(f"Invalid {values=}")


def validate_next_cells_mr(
    next_cells: Sequence[Cell],
    clen: int,
):
    if not (n_empty := sum([f.is_empty() for f in next_cells])) == clen - 1:
        nf = len(next_cells)
        raise ValueError(
            f"Multirow cell with #rows={clen} should always be "
            f"followed by {clen - 1} empty cells, but found "
            f"{nf} following cell{'s' if nf > 1 else ''} of"
            f" which {n_empty}"
            f" {'are' if n_empty > 1 else 'is'} empty."
            f"\nCells: {next_cells}"
        )


def tot_visited_to_cell_idx(tot_visited: int, row: Row):
    """Helper to get the correct cell from the row.

    Notes:
    pick out next cells corresponding to column j
    >>> f.cells
    [
        Cell(name="", value="sourcenotes", multirow=1, multicolumn=4),
        EmptyCell(name=)

    ]
    Want index map:
        {0: 0, 1: 0, 2: 0, 3: 0, 4: 1}
    i.e. first 4 indices maps to the multicolumn cell and the last index
    maps to the empty cell.
    """
    cells = row.cells
    lens = cumsum([len(f) for f in cells])
    idc_pairs = list(zip([0] + lens, lens))
    idx_to_cell_idx = {
        i: j for j, pair in zip(range(len(cells)), idc_pairs) for i in range(*pair)
    }
    return idx_to_cell_idx[tot_visited]


def validate_multirow_cell(
    cell: Cell,
    row: Row,
    rows: Sequence[TableRow],
    i: int,
    j: int,
    tot_visited: int,
):
    """Validates multirow cell.

    Args:
        cell: The cell to validate.
        row: The row containing the cell.
        rows: The rows in the table.
        i: The index of the row.
        j: The index of the cell in the row.
        tot_visited: The total length of the row visited so far.
    """
    clen = cell.clen()
    ni = i + 1
    f_rows = [r for r in rows[ni : ni + clen - 1]]
    if not all(isinstance(r, (Row, Cmidrule, Cmidrules)) for r in f_rows):
        raise ValueError(
            "Row with multirow cell must be followed by "
            f"rows with empty cells. Found {f_rows}"
        )

    next_cells = []
    for f in f_rows:
        if isinstance(f, Row):
            # pick out cell from correct column if e.g. multicolumns
            next_cells.append(f.cells[tot_visited_to_cell_idx(tot_visited, f)])
        if isinstance(f, (Cmidrule, Cmidrules)):
            next_cells.append(MrEmptyCell())
    validate_next_cells_mr(next_cells, clen)

    # cast to multirowcell and link trailing emptycells
    if not isinstance(cell, MultirowCell):
        cell = MultirowCell.from_cell(cell)

    for ncell, f_row in zip(next_cells, f_rows):
        # Need to link empty cells to multirow
        if not isinstance(ncell, MrEmptyCell):
            ncell = MrEmptyCell()
            ncell.link(cell)
        elif ncell.mr is cell:
            # ncell not linked to multirow; link it
            ncell.link(cell)
        if isinstance(f_row, Row):
            # insert linked cell in row; don't do it for Cmidrule(s)
            # insert at correct `tot_visited` place; not just `j` for
            # the #element in the row
            f_row[tot_visited_to_cell_idx(tot_visited, f_row)] = ncell
    # insert multirowcell in row
    row[j] = cell


def validate_column_rows(rows: Sequence[TableRow]):
    """Validates rows in a single column.

    I.e. all rows have one TableRow element.
    """
    for i, row in enumerate(rows):
        if isinstance(row, Row):
            tot_visited = 0
            for j, cell in enumerate(row.cells):
                if cell.is_multirow():
                    validate_multirow_cell(cell, row, rows, i, j, tot_visited)
                tot_visited += cell.__len__()  # e.g. multicolumn cell


def render_body(
    body: str,
    n: int,
    align: str | None = None,
):
    if not align:
        align = "@{}" + "c" * n + "{}@"
    body = "\n".join("  " + line for line in body.splitlines())
    return "\n".join(
        [
            r"\begin{tabular}{@{}" + align + "@{}}",
            r"  \toprule",
            body,
            r"  \bottomrule",
            r"\end{tabular}",
        ]
    )


def check_cmidrule(cmidrule: Cmidrule, n: int):
    if cmidrule.end > n:
        raise ValueError(
            f"Cmidrule end ({cmidrule.end}) must be less than or equal to "
            f"number of columns ({n})"
        )


def validate_cmidrules(columns: Columns):
    # Check cmidrules are within table
    for row in columns.all_rows():
        if isinstance(row, Cmidrule):
            check_cmidrule(row, columns.ncols)
        elif isinstance(row, Cmidrules):
            for cmidrule in row.values:
                check_cmidrule(cmidrule, columns.ncols)


def empty_cell() -> Cell:
    """Create an empty `Cell`."""
    return Cell(name="", value="")


def empty_cells(n: int) -> list[Cell]:
    """Create a list of `n` empty `Cell` objects."""
    return [empty_cell() for _ in range(n)]


def cumsum(lst: list[int]) -> list[int]:
    """Return cumulative sum of a list."""
    return list(it.accumulate(lst))


T = TypeVar("T")


def flatten(lst: Sequence[Sequence[T]]) -> Sequence[T]:
    """Flatten a list of lists."""
    return list(it.chain.from_iterable(lst))


def cmidrules_ns(all_cols: Sequence[Columns | Column]):
    all_n = cumsum([c.ncols for c in all_cols])
    return [0] + [n for n in all_n[:-1]]  # First col shouldn't be displaced


def update_cmidrules(
    cmidrules: list[tuple[int, Cmidrule]],
    cmid_ns: list[int],
) -> Cmidrules:
    ncmidrules: list[Cmidrule] = []
    for j, cmidrule in cmidrules:
        cmidrule = deepcopy(cmidrule)
        d = cmidrule.dlen()
        n = cmid_ns[j]
        new_start = cmidrule.start + n
        cmidrule.start = new_start
        cmidrule.end = new_start + d
        ncmidrules.append(cmidrule)
    return Cmidrules(values=ncmidrules)


def check_empty_cells(rows: Iterable[TableRow]):
    cells = [
        f
        for f in chain.from_iterable(
            [row.cells for row in rows if isinstance(row, Row)]
        )
    ]
    return all(not f.value for f in cells)


def join_rows(all_cols: list[Columns]):
    if not all(isinstance(c, Columns) for c in all_cols):
        raise TypeError(
            f"All columns must be Columns objects; got {[type(c) for c in all_cols]}"
        )
    if not len(r := set(c.ncols for c in all_cols)) == 1:
        raise ValueError(
            f"All columns must have same number of columns to join rows. Found: {r}"
        )
    new_rows = []
    for col in all_cols:
        new_rows.extend(col.all_rows())
    align = all_cols[0].align
    return Columns(rows=new_rows, align=align)


def join_columns(all_cols: Sequence[Columns | Column]):
    if not all(isinstance(c, Columns) for c in all_cols):
        raise TypeError(
            f"All columns must be Columns objects; got {[type(c) for c in all_cols]}"
        )
    if not len(r := set(c.total_rows() for c in all_cols)) == 1:
        raise ValueError(
            f"All columns must have same number of rows. Found: {sorted(r)}"
        )
    all_cols = [
        # e.g. when concatenating same column multiple times with multirow
        # inside we need to deepcopy object for linking to work
        deepcopy(col)
        for col in all_cols
    ]
    new_rows = []
    new_n = sum([c.ncols for c in all_cols])
    cmid_ns = cmidrules_ns(all_cols)
    new_align = "".join([c.align for c in all_cols])
    for i, group in enumerate(zip(*[c.all_rows() for c in all_cols], strict=True)):
        match group:
            case [*rows] if all(isinstance(x, Row) for x in rows):
                rows = cast(list[Row], rows)
                new_row = Row(
                    cells=[f for f in chain.from_iterable([row.cells for row in rows])]
                )
                new_rows.append(new_row)
            case [*rows] if all(isinstance(x, Cmidrule) for x in rows):
                rows = cast(list[Cmidrule], rows)
                new_cmidrule = update_cmidrules(
                    [(j, r) for j, r in enumerate(rows)],
                    cmid_ns,
                )
                new_rows.append(new_cmidrule)
            case [*rows] if all(isinstance(x, (Cmidrule, Row)) for x in rows):
                # Cmidrules and rows; assert cells empty and return cmidrules
                # Also have to update cmidrule start and end
                rows = cast(list[TableRow], rows)
                if not check_empty_cells(rows):
                    raise ValueError(
                        "Row cells must be empty when mixing Cmidrule and Row"
                    )
                new_cmidrule = update_cmidrules(
                    [(j, r) for j, r in enumerate(rows) if isinstance(r, Cmidrule)],
                    cmid_ns,
                )
                new_rows.append(new_cmidrule)
            case [*rows] if all(isinstance(x, ColoredRow) for x in rows):
                rows = cast(list[ColoredRow], rows)
                if len(rows) > 1:
                    raise ValueError("Cannot have multiple ColoredRows in same row.")
                (row,) = rows
                new_rows.append(row)
            case [*rows] if all(isinstance(x, Midrule) for x in rows):
                new_rows.append(Midrule())
            case [*rows] if all(isinstance(x, Rule) for x in rows):
                is_color = any([isinstance(x, ColoredRow) for x in rows])
                is_midrule = any([isinstance(x, Midrule) for x in rows])
                if is_color and is_midrule:
                    raise ValueError("Cannot mix ColoredRow and Midrule in same row.")
                if is_midrule:
                    new_rows.append(Midrule())
            case [*rows] if all(isinstance(x, (Row, Rule)) for x in rows):
                rows = cast(list[TableRow], rows)
                if not check_empty_cells(rows):
                    raise ValueError(
                        "Row cells must be empty when mixing Midrule and Row"
                    )
                rows_rule = [r for r in rows if isinstance(r, Rule)]
                if len(rows_rule) == 1:
                    (rule,) = rows_rule
                    new_rows.append(rule)
            case [*rows] if all(isinstance(x, (Cmidrules, Row)) for x in rows):
                # Same as for single cmidrule
                rows = cast(list[TableRow], rows)
                if not check_empty_cells(rows):
                    raise ValueError(
                        "Row cells must be empty when mixing Cmidrules and Row"
                    )
                all_cmids = []
                for j, r in enumerate(rows):
                    if isinstance(r, Cmidrules):
                        for cmid in r.values:
                            # idx j for correct displacement
                            # if multiple cmidrules they need same displacement
                            # based on the Columns object they came from.
                            all_cmids.append((j, cmid))
                new_cmidrule = update_cmidrules(all_cmids, cmid_ns)
                new_rows.append(new_cmidrule)
            case _:  # pragma: no cover
                raise ValueError("All rows must be of same type (Row or Cmidrule)")
    return Columns(rows=new_rows, align=new_align)


def concat(
    tables: list[Table],
    how: Literal["vertical", "horizontal"] = "vertical",
):
    """Concatenates tables.

    See also the operator overloading syntax.

    ```python
    >>> concat([table1, table2]) == table1 | table2
    True
    ```

    Args:
        tables: List of tables to concatenate.
        how: How to concatenate the tables.

    Returns:
        A new table with the concatenated rows or columns.
    """
    match how:
        case "vertical":
            # Concatenate rows
            new_cols = join_rows([t.columns for t in tables])
            return Table.from_columns(columns=new_cols)
        case "horizontal":
            # Concatenate columns
            new_cols = join_columns([t.columns for t in tables])
            return Table.from_columns(columns=new_cols)
        case _:
            raise ValueError(f"Invalid {how=}")
