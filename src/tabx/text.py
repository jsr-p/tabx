def bf(s: str):
    return rf"\textbf{{{s}}}"


def tt(s: str):
    return rf"\texttt{{{s}}}"


def it(s: str):
    return rf"\textit{{{s}}}"


def color(color: str, s: str):
    return rf"\textcolor{{{color}}}{{{s}}}"
