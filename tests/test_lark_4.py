import sys
from typing import Iterator

from lark import Lark, LexError
from lark.lexer import Lexer, Token
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class PytafLexer(Lexer):
    """tokenizes a pytaf doc"""

    def __init__(self, lexer_conf):
        pass

    def lex(self, doc: CommentedMap) -> Iterator[Token]:
        """tokenizes a pytaf doc"""
        for key, value in doc.items():
            line, column = doc.lc.data[key][0], doc.lc.data[key][1]
            if key in ("issue", "markers", "use"):
                yield Token(type_=key.upper(), value=key, line=line, column=column)
                yield Token(type_="STRING", value=value, line=line, column=column)
            elif key in ("input", "output"):
                yield Token(type_=key.upper(), value=key, line=line, column=column)
                yield Token(type_="OBJECT", value=dict(value), line=line, column=column)
            elif key in ("before",):
                yield Token(type_=key.upper(), value=key, line=line, column=column)
                if isinstance(value, CommentedMap):
                    yield from self.lex(doc=value)
                else:
                    raise LexError(f"invalid token '{key}'")
            else:
                yield Token(type_="ID", value=key, line=line, column=column)
                if isinstance(value, CommentedMap):
                    yield from self.lex(doc=value)
                else:
                    raise LexError(f"line {line}, column {column}, invalid token '{key}'")


pytaf_grammar = r"""
start: issue markers? before?

issue: ISSUE STRING
markers: MARKERS STRING
before: BEFORE (ID use? input? output?)+
use: USE STRING
input: INPUT OBJECT+
output: OUTPUT OBJECT+

%declare ID STRING ISSUE MARKERS BEFORE USE INPUT OUTPUT OBJECT
"""

yaml_script = """
issue: test case id
markers: ABC XYZ
before:
  "abc":
    use: func
    input:
      i_param: value
    output:
      o_param: value
"""


def test_grammar():
    try:
        yaml = YAML()
        doc = yaml.load(yaml_script)
        parser = Lark(grammar=pytaf_grammar, parser="lalr", lexer=PytafLexer)
        ast = parser.parse(doc)
        print("\n" + ast.pretty())
    except Exception as error:
        print("\n".join(error.args), file=sys.stderr)
        # raise
