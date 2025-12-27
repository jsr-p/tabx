from typing import Literal


def bf(s: str):
    return rf"\textbf{{{s}}}"


def tt(s: str):
    return rf"\texttt{{{s}}}"


def it(s: str):
    return rf"\textit{{{s}}}"


def color(s: str, color: str):
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
