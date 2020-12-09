import pytest

from parse.pytaf_parser_2 import PytafParser2


@pytest.fixture
def parser():
    return PytafParser2(debug=True)


def test_pytaf_grammar(parser):
    tree = parser.parse(
        r"""
issue: test case id
markers: mark1 mark2 mark3
"""
    )
    print("\n" + tree.pretty())
