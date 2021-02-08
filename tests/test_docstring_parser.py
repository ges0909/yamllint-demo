import pytest


@pytest.fixture
def parser():
    from parse.docstring_parser import FunctionDocstringParser

    return FunctionDocstringParser()


def test_parse_google_style_function_docstring(parser):
    sample = r"""Applies a query to the output of the test step in execution and returns the result.

        Args:
            param1 (str): The [JMESpath](https://jmespath.org) query.
            param2 (str): An other param

        Returns:
            The search result.

        Raises:
            An assertion exception if the query returns no result.
            
        Alias:
            what ever you want to call
        """
    tree, error = parser.parse(text=sample)

    print("\n" + tree.pretty())

    assert tree is not None
    assert error is None

    alias_tokens = [tree_.children for tree_ in tree.iter_subtrees() if tree_.data == "alias"]
    assert alias_tokens[0][0].value == "what ever you want to call"
