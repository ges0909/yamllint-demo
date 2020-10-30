from dataclasses import dataclass, asdict
from enum import Enum
from typing import Iterator, Optional, List

import pytest
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError


@dataclass
class Indents:
    """keeps indentation levels of pytaf keywords"""

    issue: int
    steps: int
    use: int
    step_id: int = 0


class Type(Enum):
    """represents a token type"""

    KEYWORD = 0
    IDENTIFIER = 1


@dataclass
class Token:
    """represents a token"""

    type: Type
    value: Optional[str]
    line: int
    col: int


def tokenizer(doc: CommentedMap, keywords: List[str]) -> Iterator[Token]:
    """tokenizes a dictionary"""
    for key, value in doc.items():
        line, col = doc.lc.data[key][0], doc.lc.data[key][1]
        yield Token(Type.KEYWORD, key, line, col) if key in keywords else Token(Type.IDENTIFIER, key, line, col)
        if isinstance(value, CommentedMap):
            yield from tokenizer(doc=value, keywords=keywords)
        else:
            yield Token(Type.IDENTIFIER, value, line, col)


def tokenize(doc: CommentedMap, keywords: List[str]) -> List[Token]:
    """collects tokens and returns them as list"""
    tokens = []
    for token in tokenizer(doc=doc, keywords=keywords):
        tokens.append(token)
    return tokens


def check_indents(doc: CommentedMap, indents: Indents) -> List[str]:
    """checks indentation level"""
    errors = []
    for key, value in doc.items():
        if isinstance(value, CommentedMap):
            errors_ = check_indents(doc=value, indents=indents)
            errors.extend(errors_)
        else:
            if key in asdict(indents):
                indent = getattr(indents, key)
                line, column = doc.lc.data[key][0], doc.lc.data[key][1]
                if indent != column:
                    errors.append(f"line {line} expected {indent} actual {column}")
    return errors


yaml_script = """\
issue: "test case"  # 0, 0
                    # 1
steps:              # 2, 0
                    # 3
  1. test step:     # 4, 2
    use: none       # 5, 4
    
  2. test step:     # 7, 2
    use: none       # 8, 4
"""


def test_tokenizer():
    indents = Indents(
        issue=0,
        steps=0,
        use=2,
    )
    try:
        parser = YAML()
        doc = parser.load(yaml_script)
        tokens = tokenize(doc=doc, keywords=list(asdict(indents).keys()))
        assert tokens == [
            Token(type=Type.KEYWORD, value="issue", line=0, col=0),
            Token(type=Type.IDENTIFIER, value="test case", line=0, col=0),
            Token(type=Type.KEYWORD, value="steps", line=2, col=0),
            Token(type=Type.IDENTIFIER, value="1. test step", line=4, col=2),
            Token(type=Type.KEYWORD, value="use", line=5, col=4),
            Token(type=Type.IDENTIFIER, value="none", line=5, col=4),
            Token(type=Type.IDENTIFIER, value="2. test step", line=7, col=2),
            Token(type=Type.KEYWORD, value="use", line=8, col=4),
            Token(type=Type.IDENTIFIER, value="none", line=8, col=4),
        ]
    except ScannerError as error:
        print(f"{error.args[3]}: {error.args[2]}")
        raise
    except ParserError as error:
        print(f"{error.args[3]}: {error.args[2]}")
        raise


def test_idents():
    indents = asdict(
        Indents(
            issue=0,
            steps=0,
            use=4,
        ),
    )
    try:
        parser = YAML()
        doc = parser.load(yaml_script)
        tokens = tokenize(doc=doc, keywords=list(indents.keys()))
        for token in tokens:
            if token.type in indents:
                assert token.col == indents[token.type]
    except ScannerError as error:
        print(f"{error.args[3]}: {error.args[2]}")
        raise
    except ParserError as error:
        print(f"{error.args[3]}: {error.args[2]}")


def test_indents():
    parser = YAML()
    doc = parser.load(yaml_script)
    indent_defs = Indents(issue=0, steps=0, use=4)
    errors = check_indents(doc=doc, indents=indent_defs)
    assert errors == []


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
