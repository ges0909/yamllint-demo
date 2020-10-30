import pytest
from lark import Lark
from lark.exceptions import UnexpectedEOF

script_grammar = r"""
start: "issue" ":" WORD+ markers? before? after? steps

markers: "markers" ":" WORD+
before: "before" ":" WORD+ ":" input? output?
after: "after" ":" input? output?
input: "input" ":"
output: "output" ":"

steps: "steps" ":" step+
step: (NUMBER WORD+) ":" markers? skip? flaky? parameterize? before? after? use? input? output?

skip: "skip" ":" WORD*
flaky: "flaky" ":" NUMBER
parameterize: "parameterize" ":" WORD+
use: "use" ":" WORD+

COMMENT: "#" /[^\n]/*

%import common.WS
%import common.WORD
%import common.NUMBER

%ignore WS
%ignore COMMENT
"""

yaml_script = """
issue: test case id
markers: a
steps:

    1 test step id:
      markers: b c
      skip: reason to skip # comment
      flaky: 3
      parameterize:
        param:
          env: x.y.z
        param2: 1
      before:
        "a. before step"
          input:
          output:
      after:
        input:
      use: function call
      input:
      output:
    
    # next test step 
    
    2 test step id:
"""


def test_grammar():
    try:
        parser = Lark(grammar=script_grammar, parser="lalr")
        ast = parser.parse(yaml_script)
        print(ast.pretty())
    except Exception as error:
        print("\n".join(error.args))
        raise


@pytest.mark.skip
def test_unexpected_eof():
    with pytest.raises(UnexpectedEOF):
        parser = Lark(grammar=script_grammar)
        parser.parse("Hello, World")
