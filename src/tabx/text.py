from typing import Literal


def bf(s: str):
    """Wrap text in LaTeX \\textbf{} (boldface)."""
    return rf"\textbf{{{s}}}"


def tt(s: str):
    """Wrap text in LaTeX \\texttt{} (typewriter / monospace)."""
    return rf"\texttt{{{s}}}"


def it(s: str):
    """Wrap text in LaTeX \\textit{} (italic)."""
    return rf"\textit{{{s}}}"


def color(s: str, color: str):
    """Wrap text in LaTeX \\textcolor{<color>}{}."""
    return rf"\textcolor{{{color}}}{{{s}}}"


def rotatebox(
    s: str,
    angle: float = 0,
    origin: Literal["l", "r", "b", "c", "t", "B"] = "c",
):
    """Latex rotatebox.

    See https://latexref.xyz/_005crotatebox.html
    """
    return rf"\rotatebox[origin={origin}]{{{angle}}}{{{s}}}"


def parentheses(s: str):
    """Wrap string in parentheses"""
    return f"({s})"


def brackets(s: str):
    """Wrap string in square brackets"""
    return f"[{s}]"
