"""
tabx - compose LaTeX tables using booktabs in Python
"""

from tabx import custom, table, utils
from tabx.custom import (
    ColMap,
    DescData,
    ModelData,
    RowMap,
    descriptives_table,
    models_table,
    simple_table,
)
from tabx.table import (
    Bottomrule,
    Cell,
    Cmidrule,
    Cmidrules,
    ColoredCell,
    ColoredRow,
    Columns,
    Midrule,
    Row,
    Table,
    Toprule,
    concat,
    empty_cell,
    empty_cells,
    empty_columns,
    empty_table,
    filled_columns,
    filled_table,
    multicolumn_row,
    multirow_column,
)
from tabx.utils import (
    compile_table,
    pdf_to_png,
    print_lines,
    save_table,
)

__all__ = [
    # most relevant
    "Cell",
    "ColoredCell",
    "Columns",
    "Table",
    "Row",
    "Cmidrule",
    "Cmidrules",
    "Toprule",
    "Midrule",
    "Bottomrule",
    "ColoredRow",
    # table
    "empty_columns",
    "empty_cell",
    "empty_cells",
    "empty_table",
    "filled_columns",
    "filled_table",
    "multirow_column",
    "multicolumn_row",
    # custom
    "DescData",
    "ModelData",
    "ColMap",
    "RowMap",
    "descriptives_table",
    "models_table",
    "simple_table",
    # utils
    "print_lines",
    "compile_table",
    "pdf_to_png",
    "save_table",
    # modules
    "custom",
    "table",
    "utils",
]

__version__ = "0.3.0"
