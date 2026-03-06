"""
Cli for tabx.

- Use `argparse` to avoid dependencies :=)
- The standard library is an endless pool of fun https://docs.python.org/3/

Examples:

    tabx compile table.tex
    tabx compile table.tex -o out.pdf
    cat table.tex | tabx compile -
    cat table.tex | tabx compile - -o out.pdf
"""

import argparse
import shutil
import sys
from pathlib import Path

from tabx import utils


def check_latex_commands() -> None:
    commands = ["pdflatex", "lualatex", "xelatex"]
    for cmd in commands:
        path = shutil.which(cmd)
        if path:
            print(f"{cmd}: found at {path}")
        else:
            print(f"{cmd}: NOT found")


def check_cmd(args) -> None:
    """Check if LaTeX compilers are available."""
    check_latex_commands()
    sys.exit(0)


def read_table_input(file_arg: str | None) -> tuple[str, Path | None]:
    """
    Returns (content, file_path_if_any)
    """
    if file_arg is None:
        raise SystemExit("compile requires a file argument or '-' for stdin")

    if file_arg == "-":
        if sys.stdin.isatty():
            print("Reading from stdin (Ctrl+D to finish)", file=sys.stderr)
        return sys.stdin.read(), None

    path = Path(file_arg)
    return path.read_text(encoding="utf-8"), path


def compile_cmd(args) -> None:
    tab_content, file_path = read_table_input(args.file)

    if not tab_content.strip():
        print("No LaTeX content provided.", file=sys.stderr)
        sys.exit(1)

    output = args.output
    if output is None:
        if file_path is not None:
            output = file_path.with_suffix(".pdf")
        else:
            output = Path("table.pdf")

    pdf_path = utils.compile_table(
        tab=tab_content,
        file=output,
        command=args.engine,
        silent=not args.verbose,
        extra_preamble=args.extra_preamble,
    )

    print(pdf_path)


def add_compile_subparser(subparsers) -> None:
    parser = subparsers.add_parser("compile", help="Compile a LaTeX table to PDF.")

    parser.add_argument(
        "file",
        help="Input LaTeX file or '-' to read from stdin.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output PDF path (default: derived from input file or 'table.pdf').",
    )

    parser.add_argument(
        "--engine",
        choices=["pdflatex", "lualatex", "xelatex"],
        default="pdflatex",
        help="LaTeX engine to use.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Suppress LaTeX output.",
    )

    parser.add_argument(
        "--extra-preamble",
        type=str,
        default="",
        help="Extra LaTeX preamble content.",
    )

    parser.set_defaults(func=compile_cmd)


def add_check_subparser(subparsers) -> None:
    parser = subparsers.add_parser(
        "check",
        help="Check if LaTeX compilers are available.",
    )
    parser.set_defaults(func=check_cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="tabx CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    add_compile_subparser(subparsers)
    add_check_subparser(subparsers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
