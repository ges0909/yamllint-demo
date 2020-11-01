import pytest
from lark import Tree, Token, LexError

from parse.pytaf_parser import PytafParser


@pytest.fixture
def parser():
    return PytafParser()


# issue


def test_issue(parser):
    tree = parser.parse(r"issue: abc")
    assert tree == Tree(
        "start",
        [Tree("issue", [Token("ISSUE", "issue"), Token("VALUE", "abc")])],
    )


def test_issue_without_id_raises_error(parser):
    with pytest.raises(LexError):
        parser.parse(r"issue:")


def test_issue_with_array_arg_raises_error(parser):
    with pytest.raises(LexError):
        parser.parse(r"issue: [abc]")


# markers


def test_markers(parser):
    tree = parser.parse(
        r"""
    issue: abc
    markers: abc"""
    )
    assert tree == Tree(
        "start",
        [
            Tree("issue", [Token("ISSUE", "issue"), Token("VALUE", "abc")]),
            Tree("markers", [Token("MARKERS", "markers"), Token("VALUE", "abc")]),
        ],
    )


# before


# after


# skip


def test_skip(parser):
    tree = parser.parse(
        r"""
    issue: test case id
    steps:
        test step id:
            skip:
    """
    )
    print("\n" + tree.pretty())


def test_skip_2(parser):
    tree = parser.parse(
        r"""
    issue: test case id
    steps:
        test step id:
            skip: reason
    """
    )
    print("\n" + tree.pretty())


# flaky


# input


def test_input(parser):
    tree = parser.parse(
        r"""
    issue: test case id
    steps:
        test step id:
            use: func call
            input:
                param1: value
                param2:
                    assign: value
                param3:
                    env: value
                param4:
                    file: path
                param5:
                    scan: query
    """
    )
    print("\n" + tree.pretty())


# output


def test_output(parser):
    tree = parser.parse(
        r"""
    issue: test case id
    steps:
        test step id:
            use: func call
            output:
                param1: value
                param2:
                    assign: value
                param3:
                    env: value
                param4:
                    file: path
                param5:
                    scan: query
    """
    )
    print("\n" + tree.pretty())
