from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, List

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


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


def test_indents():
    parser = YAML()
    doc = parser.load(yaml_script)
    indent_defs = Indents(issue=0, steps=0, use=4)
    errors = check_indents(doc=doc, indents=indent_defs)
    assert errors == []


defs = {
    "issue": None,
    "markers": None,
    "before": {
        "[\\w]+": {
            "use": None,
            "input": [
                {"[\\w]+": None}
            ],
            "output": [
                {"[\\w]+": None}
            ],
        }
    },
    "after": {
        "use": {},
        "input": {},
        "output": {},
    },
    "steps": {"<ident>": {"skip": {}, "markers": {}, "flaky": {}, "use": {}}},
}
