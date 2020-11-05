from typing import Iterator, Union

from lark import Lark, UnexpectedInput
from lark.lexer import Lexer, Token
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class PytafLexer(Lexer):
    """tokenize pytaf script"""

    indents = {
        "issue": (0,),
        "markers": (0, 4),
        "before": (0, 4),
        "after": (0, 4),
        "steps": (0,),
        "skip": (4,),
        "skip_env": (4,),
        "flaky": (4,),
        "use": (4,),
        "input": (4,),
        "output": (4,),
    }

    def __init__(self, lexer_conf):
        pass

    def lex(self, doc: Union[CommentedMap, str], indent=0) -> Iterator[Token]:
        for key, value in doc.items():
            line, column = doc.lc.data[key][0] + 1, doc.lc.data[key][1] + 1
            token_type = key.upper() if key in self.indents.keys() and indent in self.indents[key] else "VALUE"
            yield Token(type_=token_type, value=key, line=line, column=column)
            if key in ("input", "output") and indent in self.indents[key]:
                yield Token(type_="OBJECT", value=value, line=line, column=column)
            elif isinstance(value, CommentedMap):
                yield from self.lex(doc=value, indent=indent + 2)
            elif value:
                yield Token(type_="VALUE", value=value, line=line, column=column)


class PytafParser(Lark):
    """parse pytaf script"""

    grammar = r"""
    start: issue markers? before? after? steps

    issue: ISSUE VALUE
    markers: MARKERS VALUE
    before: BEFORE step+
    after: AFTER step+
    steps: STEPS step+
    step: VALUE skip_env? skip? markers? flaky? before? after? use? input? output?
    skip_env: SKIP_ENV VALUE
    skip: SKIP VALUE*
    flaky: FLAKY VALUE
    use: USE VALUE
    input: INPUT parameter+
    output: OUTPUT parameter+
    parameter: OBJECT
    
    %declare VALUE OBJECT INVALID ISSUE MARKERS BEFORE AFTER STEPS SKIP_ENV SKIP FLAKY USE INPUT OUTPUT
    """

    def __init__(self, **kwargs):
        super(PytafParser, self).__init__(
            grammar=self.grammar,
            parser="lalr",
            lexer=PytafLexer,
            **kwargs
        )

    def parse(self, text: str, **kwargs):
        yaml = YAML()
        text = yaml.load(stream=text)
        return super().parse(text=text, **kwargs)
