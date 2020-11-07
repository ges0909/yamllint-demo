import glob
from pathlib import Path

import lark
import pytest
from lark import UnexpectedToken

from parse.pytaf_parser import PytafParser


@pytest.fixture
def parser():
    return PytafParser(debug=True)


def test_grammar(parser):
    tree = parser.parse(
        r"""
    issue: test case id
    before:
        wait:
            input:
                duration: 5
    after:
    steps:
        test step id:
            skip: reason
            flaky: 3
            use: func call
            input:
                param:
                    env: value
            output:
                param1: value
    """
    )
    print("\n" + tree.pretty())


def test_grammar_error(parser):
    try:
        tree = parser.parse(
            r"""
        issue: test case id
        steps:
            test step id:
            
            use: none
    """
        )
        print("\n" + tree.pretty())
    except UnexpectedToken as error:
        print(f"line {error.line} column {error.column}: syntax error: unexpected token '{error.token}'")


def test_script_grammar():
    parser = PytafParser()
    for path in glob.glob("./scripts/*.yaml"):
        with open(str(path), "r") as stream:
            text = stream.read()
            try:
                parser.parse(text=text)
            except lark.UnexpectedToken as error:
                pytest.fail(msg=f"{Path(path).name} line {error.line} column {error.column}, unexpected token", pytrace=False)
