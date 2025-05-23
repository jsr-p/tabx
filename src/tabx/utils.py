import shutil
import subprocess
import sys
from pathlib import Path
from typing import Literal

from tabx.table import Table, render_rows

__all__ = [
    "compile_table",
    "pdf_to_png",
    "save_tab",
]


def print_lines(s: str):  # pragma: no cover
    """helper for printing out lines of a table.

    Used in the testing modules.
    """
    print("[")
    for line in s.splitlines():
        print(f"\tr'{line}',")
    print("]")


def compile_table(
    tab: str,
    command: Literal["pdflatex", "lualatex", "xelatex"] = "pdflatex",
    output_dir: str | Path = "/tmp/",
    name: str = "table",
    silent: bool = True,
    extra_preamble: str = "",
):
    """Compile a LaTeX table to PDF."""

    # Ensure pdflatex is available
    if shutil.which(command) is None:
        print(f"Error: {command} is not in PATH.")
        sys.exit(1)

    # Standalone LaTeX document using `booktabs`
    doc = rf"""
\documentclass{{standalone}}
\usepackage{{booktabs}}
\usepackage{{multirow}}
\usepackage{{graphicx}}
\usepackage{{amssymb}}
\usepackage{{array}}
\usepackage{{siunitx}}  % for \num
\usepackage{{colortbl}}  % for \cellcolor
\usepackage[table]{{xcolor}}
{extra_preamble}


\begin{{document}}

{tab}

\end{{document}}
        """

    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    if silent:
        out = subprocess.run(
            [command, f"-jobname={name}", f"-output-directory={output_dir}"],
            input=doc.encode("utf-8"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    else:
        out = subprocess.run(
            [command, f"-jobname={name}", f"-output-directory={output_dir}"],
            input=doc.encode("utf-8"),
            check=True,
        )

    if out.returncode == 0:
        return output_dir.joinpath(f"{name}.pdf")
    raise RuntimeError(
        f"Error compiling table with {command}. Check the output for more details."
    )


def pdf_to_png(file: str | Path) -> Path:
    """Convert a PDF file to PNG using ImageMagick."""
    if shutil.which("magick") is None:
        print("Error: magick is not in PATH.")
        sys.exit(1)

    file = Path(file)
    if not file.exists():
        raise FileNotFoundError(f"PDF file not found: {file}")
    if file.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {file.name}")

    output_file = file.with_suffix(".png")

    subprocess.run(
        [
            "magick",
            "-density",
            "300",
            str(file),
            "-quality",
            "100",
            # remove all metadata from png files s.t.
            # they are smaller *and* don't change on each run
            "-strip",
            "-define",
            "png:exclude-chunk=time",
            "-trim",
            "+repage",
            "-background",
            "white",
            "-alpha",
            "remove",
            str(output_file),
        ],
        check=True,
    )

    return output_file


def save_tab(
    name: str,
    tab: str,
    fp: Path | str,
):  # pragma: no cover
    """Saves a LaTeX table to a file.

    Args:
        name: The name of the file to save.
        tab: The LaTeX table to save.
        fp: The path to the folder where the file will be saved.
    """
    if isinstance(fp, str):
        fp = Path(fp)
    with open(fp.joinpath(name), "w") as f:
        f.write(tab)


def colored_column_spec(
    color: str,
    align: str | None = None,
) -> str:
    """Returns a column spec for a colored column.

    Requires the `xcolor` package.
    """
    if not align:
        align = "c"
    return r">{\columncolor{" + color + r"}}{" + align + r"}"


def render_body_extra(table: Table):  # pragma: no cover
    """Renders the body of a table.

    You can construct your own render function and pass it into
    {py:obj}`<tabx.table.Table.render>`.
    """
    align = table.align
    n = table.ncols
    if not align:
        align = "c" * n
    body = render_rows(table.all_rows())
    body = "\n".join("  " + line for line in body.splitlines())
    return "\n".join(
        [
            r"\begin{tabular}{" + align + "}",
            r"  \toprule",
            body,
            r"  \bottomrule",
            r"\end{tabular}",
        ]
    )


def render_body_simple(table: Table):  # pragma: no cover
    align = table.align
    n = table.ncols
    if not align:
        align = "c" * n
    body = render_rows(table.all_rows())
    return "\n".join(
        [
            r"\begin{tabular}{@{}" + align + r"@{}}",
            body,
            r"\end{tabular}",
        ]
    )


def render_body_no_rules(table: Table):  # pragma: no cover
    align = table.align
    n = table.ncols
    if not align:
        align = "c" * n
    body = render_rows(table.all_rows())
    body = "\n".join("  " + line for line in body.splitlines())
    return "\n".join(
        [
            r"\begin{tabular}{" + align + "}",
            body,
            r"\end{tabular}",
        ]
    )


def proj_folder() -> Path:  # pragma: no cover
    """Returns the project folder."""
    fp = Path(__file__).parents[2]
    if not fp.joinpath("src", "tabx").exists():
        raise FileNotFoundError(
            "Could not find the project folder. "
            "This function only works on the development version when cloning "
            "the repository from github"
        )
    return fp
