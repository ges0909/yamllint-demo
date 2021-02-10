import pytest

from parse.docstring_parser import DocstringParser


@pytest.fixture
def parser():
    return DocstringParser()


# param1: The [JMESpath](https://jmespath.org) query.


def test_parse_google_style_function_docstring(parser):
    sample = r"""Applies a query to the output of the test step in execution and returns the result.

        Args:
            param1: The JMESpath query.
            param2 (str): An other param.

        Returns:
            The search result.

        Raises:
            An assertion exception if the query returns no result.
            
        Alias:
            what ever you want to call
        """
    docstring, error = DocstringParser.parse(text=sample)

    assert error is None, error
    assert docstring is not None

    assert docstring.summary == "Applies a query to the output of the test step in execution and returns the result."
    assert docstring.args == [
        ("param1", "", "The JMESpath query."),
        ("param2", "str", "An other param."),
    ]
    assert docstring.returns == "The search result."
    assert docstring.yields == ""
    assert docstring.raises == "An assertion exception if the query returns no result."
    assert docstring.alias == "what ever you want to call"
    assert docstring.examples == ""
