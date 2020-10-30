import pytest
from lark import Lark
from lark.exceptions import UnexpectedEOF

script_grammar = r"""
start: issue markers? before?

issue: "issue" ":" STRING
markers: "markers" ":" STRING
before: "before" ":" ( use? input? )+
use: "use" ":" STRING
input: "input" ":" INPUT_PARAMS
assign: "assign" ":" STRING
env: "env" ":"
file: "file" ":"
scan: "scan" ":"

COMMENT: "#" /[^\n]/*
STRING : /[^:\n]/+ | "\"" /[^:\n]/+ "\"" | "\'" /[^:\n]/+ "\'"
ID: /[^:]/+

%import common.WS

%ignore WS
%ignore COMMENT
"""

yaml_script = """
issue: test case id
markers: a b
before:
  use: abc
  input:
    param1: value
    param2:
      assign: value 
"""


def test_grammar():
    parser = Lark(grammar=script_grammar)
    ast = parser.parse(yaml_script)
    print("\n" + ast.pretty())
