from typing import Iterator, Union

from lark import Lark, LexError
from lark.lexer import Lexer, Token
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class PytafLexer(Lexer):
    """tokenize pytaf script"""

    keywords = (
        "issue",
        "markers",
        "before",
        "after",
        "steps",
        "skip",
        "flaky",
        "use",
        "input",
        "output",
        "assign",
        "env",
        "file",
        "scan",
    )

    def __init__(self, lexer_conf):
        pass

    def lex(self, doc: Union[CommentedMap, str], line=0, column=0, context=None, level=1) -> Iterator[Token]:
        if isinstance(doc, CommentedMap):
            if context in ("input", "output"):
                yield Token(type_="OBJECT", value=doc, line=line, column=column)
            else:
                for key, value in doc.items():
                    line, column = doc.lc.data[key][0], doc.lc.data[key][1]
                    token_type = key.upper() if key in self.keywords else "VALUE"
                    yield Token(type_=token_type, value=key, line=line, column=column)
                    if level == 3 and key in ("input", "output"):
                        context = key
                    if value:  # avoid 'None'
                        yield from self.lex(doc=value, line=line, column=column, context=context, level=level + 1)
        elif isinstance(doc, str):
            yield Token(type_="VALUE", value=doc, line=line, column=column)
        else:
            raise LexError(f"line {line})", f"column {column}", f"invalid token '{doc}'")


class PytafParser(Lark):
    """parse pytaf script"""

    grammar = r"""
    start: issue markers? before? after? steps

    issue: ISSUE VALUE
    markers: MARKERS VALUE
    before: BEFORE step+
    after: AFTER step+
    steps: STEPS step+
    step: VALUE skip? markers? flaky? before? after? use? input? output?
    skip: SKIP VALUE*
    flaky: FLAKY VALUE
    use: USE VALUE
    input: INPUT input_parameter+
    input_parameter: OBJECT
    output: OUTPUT output_parameter+
    output_parameter: OBJECT

    %declare VALUE OBJECT ISSUE MARKERS BEFORE AFTER STEPS SKIP FLAKY USE INPUT OUTPUT ASSIGN ENV FILE SCAN
    """

    def __init__(self):
        super(PytafParser, self).__init__(
            grammar=self.grammar,
            parser="lalr",
            propagate_positions=True,
            lexer=PytafLexer,
        )

    def parse(self, text: str, **kwargs):
        yaml = YAML()
        text = yaml.load(text)
        return super().parse(text=text, **kwargs)
