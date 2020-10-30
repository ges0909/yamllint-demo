from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, List

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


def check_indents(doc: CommentedMap, column=0) -> List[str]:
    """checks indentation level"""
    errors = []
    for key, value in doc.items():
        if isinstance(value, CommentedMap):
            errors_ = check_indents(doc=value, column=column + 2)
            errors.extend(errors_)
        else:
            line, col = doc.lc.data[key][0], doc.lc.data[key][1]
            if column == 0:
                if key not in ("issue", "markers", "before", "after", "steps"):
                    errors.append(f"line {line} key {key} expected {column} actual {col}")
    return errors


yaml_script = """\
issue: "test case"
    steps:
    1. test step:
        use: none
"""


def test_indents():
    parser = YAML()
    doc = parser.load(yaml_script)
    errors = check_indents(doc=doc)
    assert errors == []
