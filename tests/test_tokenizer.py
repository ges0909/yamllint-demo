from dataclasses import dataclass, asdict
from typing import Iterator, Dict, Optional, List

import pytest
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError


@dataclass
class Indents:
    """keeps identation levels of pytaf keywords"""

    issue: int
    steps: int
    use: int


@dataclass
class Token:
    """represents a token"""

    type: str
    value: Optional[str]
    line: int
    col: int


def tokenizer(doc, keywords: List[str]) -> Iterator[Token]:
    """tokenizes dict"""
    for key, value in doc.items():
        line, col = doc.lc.data[key][0], doc.lc.data[key][1]
        yield Token(key, None, line, col) if key in keywords else Token("<ident>", key, line, col)
        if isinstance(value, CommentedMap):
            yield from tokenizer(doc=value, keywords=keywords)
        else:
            yield Token("<ident>", value, line, col)


def tokenize(doc, keywords: List[str]) -> List[Token]:
    """collects tokens and returns them as list"""
    tokens = []
    for token in tokenizer(doc=doc, keywords=keywords):
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
    idents = Indents(
        issue=0,
        steps=0,
        use=2,
    )
    try:
        parser = YAML()
        doc = parser.load(yaml_script)
        tokens = tokenize(doc=doc, keywords=list(asdict(idents).keys()))
        assert tokens == [
            Token(type="issue", value=None, line=0, col=0),
            Token(type="<ident>", value="test case", line=0, col=0),
            Token(type="steps", value=None, line=2, col=0),
            Token(type="<ident>", value="1. test step", line=4, col=2),
            Token(type="use", value=None, line=5, col=4),
            Token(type="<ident>", value="none", line=5, col=4),
        ]
    except ScannerError as error:
        print(f"{error.args[3]}: {error.args[2]}")
        raise
    except ParserError as error:
        print(f"{error.args[3]}: {error.args[2]}")
        raise


def test_idents():
    idents = asdict(
        Indents(
            issue=0,
            steps=0,
            use=4,
        ),
    )
    try:
        parser = YAML()
        doc = parser.load(yaml_script)
        tokens = tokenize(doc=doc, keywords=list(idents.keys()))
        for token in tokens:
            if token.type in idents:
                assert token.col == idents[token.type]
    except ScannerError as error:
        print(f"{error.args[3]}: {error.args[2]}")
        raise
    except ParserError as error:
        print(f"{error.args[3]}: {error.args[2]}")


def test_asdict_raises_type_error():
    with pytest.raises(TypeError):
        asdict(Indents)  # asdict() should be called on dataclass instances


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
