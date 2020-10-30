import pytest
from lark import Lark
from lark.exceptions import UnexpectedEOF

script_grammar = r"""
start: issue markers? before?

issue: "issue" ":" STRING
markers: "markers" ":" STRING
before: "before" ":" ( use? input? )+
use: INDENT "use" ":" STRING
input: INDENT "input" ":"

INDENT: "  "
STRING: /[^:\n]/+ | "\"" /[^:\n]/+ "\"" | "\'" /[^:\n]/+ "\'"
COMMENT: "#" /[^?]/*

%import common.NEWLINE

%ignore NEWLINE
%ignore COMMENT
"""

yaml_script = """
issue: test case id
markers: a b
before:
  use: abc
  input:
"""


def test_grammar():
    parser = Lark(grammar=script_grammar)
    ast = parser.parse(yaml_script)
    print("\n" + ast.pretty())
