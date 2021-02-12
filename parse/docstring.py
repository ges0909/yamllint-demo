from collections import ChainMap
from dataclasses import dataclass, field
from typing import Tuple, Optional

from lark import Lark, UnexpectedToken, Transformer
from lark.exceptions import UnexpectedCharacters, GrammarError


@dataclass
class Docstring:
    summary: str = ""
    description: str = ""
    args: list[str] = field(default_factory=[])
    returns: str = ""
    yields: str = ""
    raises: list[str] = field(default_factory=[])
    alias: str = ""
    examples: str = ""


class DocstringTransformer(Transformer):
    @staticmethod
    def to_string(tokens, type_: str):
        return " ".join([token.value for token in tokens if token.type == type_])

    @staticmethod
    def start(children):
        return dict(ChainMap(*children[::-1]))

    def summary(self, tokens):
        return {"summary": self.to_string(tokens, type_="WORD")}

    def description(self, tokens):
        return {"description": self.to_string(tokens, type_="WORD")}

    @staticmethod
    def args(children):
        return {"args": [child for child in children if isinstance(child, tuple)]}

    def arg(self, tokens):
        return (
            self.to_string(tokens, type_="NAME"),
            self.to_string(tokens, type_="TYPE"),
            self.to_string(tokens, type_="WORD"),
        )

    def returns(self, tokens):
        return {
            "returns": (
                self.to_string(tokens, type_="TYPE"),
                self.to_string(tokens, type_="WORD"),
            )
        }

    def yields(self, tokens):
        return {
            "yields": {
                "type": self.to_string(tokens, type_="TYPE"),
                "word": self.to_string(tokens, type_="WORD"),
            }
        }

    @staticmethod
    def raises(children):
        return {"raises": [child for child in children if isinstance(child, tuple)]}

    def error(self, tokens):
        return (
            self.to_string(tokens, type_="TYPE"),
            self.to_string(tokens, type_="WORD"),
        )

    def alias(self, tokens):
        return {"alias": self.to_string(tokens, type_="WORD")}

    def examples(self, tokens):
        return {"examples": self.to_string(tokens, type_="WORD")}


class DocstringParser:
    """parse google style docstrings of module level python functions"""

    grammar = r"""
    ?start:         summary description? args? (returns | yields)? raises? alias? examples?

    summary:        WORD+ "\n"
    description:    WORD+
    args:           _ARGS COLON arg+
    returns:        _RETURNS COLON TYPE COLON WORD+
    yields:         _YIELDS COLON TYPE COLON WORD+
    raises:         _RAISES COLON error+
    alias:          _ALIAS COLON WORD+
    examples:       _EXAMPLES COLON WORD+
    
    arg:            NAME COLON WORD+
                  | NAME BRACKET_OPEN TYPE BRACKET_CLOSE COLON WORD+
                  
    error:          TYPE COLON WORD+
    
    _ARGS:          "Args"
    _RETURNS:       "Returns"
    _YIELDS:        "Yields"
    _RAISES:        "Raises"
    _ALIAS:         "Alias"
    _EXAMPLES:      "Examples"
    
    NAME:           /[a-zA-Z][a-zA-Z0-9_]*/
    TYPE:           /[a-zA-Z][a-zA-Z0-9_]*/
    COLON:          ":"
    BRACKET_OPEN:   "("
    BRACKET_CLOSE:  ")"
    WORD:           /[a-zA-Z0-9.`,>=()]+/
 
    WS:             /\s+/
    
    %ignore         WS
    """

    @staticmethod
    def parse(text: str, **kwargs) -> Tuple[Optional[Docstring], Optional[str]]:
        try:
            parser = Lark(
                grammar=DocstringParser.grammar,
                parser="earley",  # supports rule priority
                # parser="lalr",  # supports terminal priority
                **kwargs,
            )
            tree = parser.parse(text=text, **kwargs)
            # print("\n" + tree.pretty())
            transformed = DocstringTransformer().transform(tree)
        except (GrammarError, UnexpectedCharacters, UnexpectedToken) as error:
            return None, ", ".join(error.args)
        return Docstring(**transformed), None
