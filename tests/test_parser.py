import pytest
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError


ReservedWords = (
    "issue",
    "steps",
    "use",
)


def tokenizer(doc):
    """tokenizes dict"""
    for key, value in doc.items():
        line, col = doc.lc.data[key][0], doc.lc.data[key][1]
        yield (key, None, line, col) if key in ReservedWords else ("<ident>", key, line, col)
        if isinstance(value, CommentedMap):
            yield from tokenizer(value)
        else:
            yield "<ident>", value, line, col


def tokenize(doc):
    """collects tokens"""
    tokens = []
    for token in tokenizer(doc):
        tokens.append(token)
    return tokens


yaml_script = """\
issue: "test case"  # 0, 0
                    # 1
steps:              # 2, 0
                    # 3
  1. test step:     # 4, 2
    use: none       # 5, 4
"""


def test_tokenizer():
    try:
        parser = YAML()
        doc = parser.load(yaml_script)
        tokens = tokenize(doc)
        assert tokens == [
            ("issue", None, 0, 0),
            ("<ident>", "test case", 0, 0),
            ("steps", None, 2, 0),
            ("<ident>", "1. test step", 4, 2),
            ("use", None, 5, 4),
            ("<ident>", "none", 5, 4),
        ]
    except ScannerError as error:
        print(f"{error.args[3]}: {error.args[2]}")


@pytest.mark.skip
def test_scanner_error():
    parser = YAML()
    with pytest.raises(ScannerError):
        parser.load(yaml_script)
    # except ScannerError as error:
    #     print(f"{error.args[3]}: {error.args[2]}")


@pytest.mark.skip
def test_parser_error():
    parser = YAML()
    with pytest.raises(ParserError):
        parser.load(yaml_script)
