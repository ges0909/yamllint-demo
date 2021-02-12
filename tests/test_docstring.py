import pytest

from parse.docstring import DocstringParser


@pytest.fixture
def parser():
    return DocstringParser()


# param1: The [JMESpath](https://jmespath.org) query.


def test_parse_google_style_function_docstring(parser):
    sample = r"""Summary line.

        Extended description of function.
        
    Args:
        arg1: Description of arg1
        arg2 (str): Description of arg2

    Returns:
        bool: Description of return value

    Raises:
        AttributeError: The ``Raises`` section is a list of all exceptions
            that are relevant to the interface.
        ValueError: If `arg2` is equal to `arg1`.
        
    Alias:
        what ever you want to call
        
    Examples:
        Examples should be written in doctest format, and should illustrate how
        to use the function.

        >>> a=1
        >>> b=2
        >>> func(a,b)
        True

        """
    docstring, error = DocstringParser.parse(text=sample)

    assert error is None, error
    assert docstring is not None

    assert docstring.summary == "Summary line."
    assert docstring.description == "Extended description of function."
    assert docstring.args == [
        ("arg1", "", "Description of arg1"),
        ("arg2", "str", "Description of arg2"),
    ]
    assert docstring.returns == ("bool", "Description of return value")
    assert docstring.yields == ""
    assert docstring.raises == [
        ("AttributeError", "The ``Raises`` section is a list of all exceptions that are relevant to the interface."),
        ("ValueError", "If `arg2` is equal to `arg1`."),
    ]
    assert docstring.alias == "what ever you want to call"
    assert (
        docstring.examples
        == "Examples should be written in doctest format, and should illustrate how to use the function. >>> a=1 >>> b=2 >>> func(a,b) True"
    )
