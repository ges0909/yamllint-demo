import json
from pathlib import Path
from typing import Iterator, Union, Dict, Any, Tuple

from lark import Lark, Tree
from lark.exceptions import UnexpectedToken
from lark.lexer import Lexer, Token
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError


class PytafParserError(Exception):
    def __init__(self, path: str, line: int, column: int, text: str):
        self.path = path
        self.line = line
        self.column = column
        self.text = text


class PytafLexer(Lexer):
    """tokenize pytaf script"""

    indents = {
        "issue": (0,),
        "markers": (0, 4),
        "parameterize": (4,),
        "foreach": (4,),
        "before": (0, 4),
        "after": (0, 4),
        "steps": (0,),
        "skip": (4,),
        "skip_env": (4,),
        "flaky": (4,),
        "scope": (4, 8),
        "use": (4, 8),
        "input": (4, 8),
        "output": (4, 8),
    }

    def __init__(self, lexer_conf):
        pass

    def lex(self, doc: Union[CommentedMap, str], indent=0) -> Iterator[Token]:
        for key, value in doc.items():
            line, column = doc.lc.data[key][0] + 1, doc.lc.data[key][1] + 1
            type_ = key.upper() if key in self.indents.keys() and indent in self.indents[key] else "ID"
            yield Token(type_=type_, value=key, line=line, column=column)
            if key in ("parameterize", "foreach", "input", "output") and indent in self.indents[key]:
                yield Token(type_="OBJECT", value=json.dumps(value), line=line, column=column)
            elif isinstance(value, CommentedMap):
                yield from self.lex(doc=value, indent=indent + 2)
            elif value:
                yield Token(type_="VALUE", value=value, line=line, column=column)


class PytafParser(Lark):
    """parse pytaf script"""

    grammar = r"""
    start: issue markers? before? after? steps

    issue: ISSUE VALUE
    markers: MARKERS VALUE*
    before: BEFORE _step*
    after: AFTER _step*
    steps: STEPS step+
    _step: ID scope? use? input? output?
    step: ID skip_env? skip? markers? flaky? parameterize? before? after? use? input? output?
    skip_env: SKIP_ENV VALUE
    skip: SKIP VALUE*
    flaky: FLAKY VALUE
    parameterize: (PARAMETERIZE | FOREACH) OBJECT
    scope: SCOPE VALUE
    use: USE VALUE
    input: INPUT param+
    output: OUTPUT param+
    param: OBJECT
    
    %declare ID VALUE OBJECT ISSUE MARKERS PARAMETERIZE FOREACH BEFORE AFTER STEPS SKIP_ENV SKIP FLAKY SCOPE USE INPUT OUTPUT
    """

    def __init__(self, **kwargs):
        super(PytafParser, self).__init__(
            grammar=self.grammar,
            parser="lalr",
            lexer=PytafLexer,
            **kwargs,
        )

    def parse(self, path: str, **kwargs) -> Tuple[Dict[str, Any], Tree]:
        yaml = YAML()
        try:
            with open(path, "r") as stream:
                instance = yaml.load(stream=stream)  # yaml parser
                tree = super().parse(text=instance, **kwargs)  # pytaf parser
                return instance, tree
        except (ScannerError, ParserError) as error:
            raise PytafParserError(
                path=Path(path).name,  # error.problem_mark.name,
                line=error.problem_mark.line,
                column=error.problem_mark.column,
                text=f"yaml error, {error.context} {error.problem}",
            ) from None
        except UnexpectedToken as error:
            raise PytafParserError(
                path=Path(path).name,
                line=error.line,
                column=error.column,
                text=f"parser error, unexpected token '{error.token.value}' (token type {error.token.type})",
            ) from None
