"""
Cli for tabx.

- Use `argparse` to avoid dependencies :=)
- The standard library is an endless pool of fun https://docs.python.org/3/
"""

import argparse
import sys
from pathlib import Path
from tabx import utils
import shutil


def check_latex_commands():
    commands = ["pdflatex", "lualatex", "xelatex"]
    for cmd in commands:
        path = shutil.which(cmd)
        if path:
            print(f"{cmd}: found at {path}")
        else:
            print(f"{cmd}: NOT found")


def check_cmd(args):
    """Check if LaTeX compilers are available."""
    check_latex_commands()
    sys.exit(0)


def compile_cmd(args):
    tab_content = ""
    if args.file:
        tab_content = args.file.read_text()
    elif args.stdin:
        if sys.stdin.isatty():
            print("Reading from stdin (press Ctrl+D to finish):", file=sys.stderr)
        tab_content = sys.stdin.read()
    if not tab_content:
        print(
            "No content provided. Please provide a file or input via stdin.",
            file=sys.stderr,
        )
        sys.exit(1)

    pdf_path = utils.compile_table(
        tab=tab_content,
        command=args.command,
        output_dir=args.output_dir,
        name=args.name,
        silent=args.silent,
        extra_preamble=args.extra_preamble,
    )

    print(f"Compiled PDF saved to: {pdf_path}")


def add_compile_subparser(subparsers):
    parser = subparsers.add_parser("compile", help="Compile a LaTeX table to PDF.")

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--file", type=Path, help="Path to file containing LaTeX table."
    )
    input_group.add_argument(
        "--stdin", action="store_true", help="Read LaTeX table from stdin."
    )

    parser.add_argument(
        "--command",
        choices=["pdflatex", "lualatex", "xelatex"],
        default="pdflatex",
        help="LaTeX engine to use (default: pdflatex).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory for output PDF (default: cwd).",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="table",
        help="Base name for output file (default: table).",
    )
    parser.add_argument("--silent", action="store_true", help="Suppress LaTeX output.")
    parser.add_argument(
        "--extra-preamble", type=str, default="", help="Extra LaTeX preamble content."
    )

    parser.set_defaults(func=compile_cmd)


def add_check_subparser(subparsers):
    parser = subparsers.add_parser(
        "check", help="Check if LaTeX compilers are available."
    )
    parser.set_defaults(func=check_cmd)


def main():
    parser = argparse.ArgumentParser(description="tabx CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_compile_subparser(subparsers)
    add_check_subparser(subparsers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
