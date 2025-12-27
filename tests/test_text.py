import re

import pytest

import tabx
from tabx import text


def test_basic_wrappers():
    assert text.bf("hello") == r"\textbf{hello}"
    assert text.tt("code") == r"\texttt{code}"
    assert text.it("emph") == r"\textit{emph}"


def test_color_wrapper():
    assert text.color("warn", "red") == r"\textcolor{red}{warn}"


def test_empty_strings():
    assert text.bf("") == r"\textbf{}"
    assert text.tt("") == r"\texttt{}"
    assert text.it("") == r"\textit{}"
    assert text.color("", "") == r"\textcolor{}{}"


def test_rotatebox():
    assert text.rotatebox("abc") == r"\rotatebox[origin=c]{0}{abc}"
    assert text.rotatebox("abc", angle=90) == r"\rotatebox[origin=c]{90}{abc}"
    assert (
        text.rotatebox("abc", angle=45, origin="l") == r"\rotatebox[origin=l]{45}{abc}"
    )
