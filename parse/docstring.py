from collections import ChainMap
from dataclasses import dataclass, field
from typing import Tuple, Optional, Union

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
    def words_to_str(tokens, type_: str) -> str:
        return " ".join([token.value for token in tokens if token.type == type_])

    @staticmethod
    def start(
        children: list,
    ) -> dict[str, Union[str, tuple[str, str], tuple[str, str, str]]]:
        return dict(ChainMap(*children[::-1]))  # reduce list of dicts to single dict

    def summary(self, tokens: list) -> dict[str, str]:
        return {"summary": self.words_to_str(tokens, type_="WORD")}

    def description(self, tokens: list) -> dict[str, str]:
        return {"description": self.words_to_str(tokens, type_="WORD")}

    @staticmethod
    def args(children: list) -> dict[str, list[tuple[str, str, str]]]:
        return {"args": [child for child in children if isinstance(child, tuple)]}

    def arg(self, tokens: list) -> tuple[str, str, str]:
        return (
            self.words_to_str(tokens, type_="NAME"),
            self.words_to_str(tokens, type_="TYPE"),
            self.words_to_str(tokens, type_="WORD"),
        )

    def returns(self, tokens: list) -> dict[str, tuple[str, str]]:
        return {
            "returns": (
                self.words_to_str(tokens, type_="TYPE"),
                self.words_to_str(tokens, type_="WORD"),
            )
        }

    def yields(self, tokens: list) -> dict[str, tuple[str, str]]:
        return {
            "yields": (
                self.words_to_str(tokens, type_="TYPE"),
                self.words_to_str(tokens, type_="WORD"),
            )
        }

    @staticmethod
    def raises(children: list) -> dict[str, list[tuple[str, str]]]:
        return {"raises": [child for child in children if isinstance(child, tuple)]}

    def error(self, tokens: list) -> tuple[str, str]:
        return (
            self.words_to_str(tokens, type_="TYPE"),
            self.words_to_str(tokens, type_="WORD"),
        )

    def alias(self, tokens: list) -> dict[str, str]:
        return {"alias": self.words_to_str(tokens, type_="WORD")}

    def examples(self, tokens: list) -> dict[str, str]:
        return {"examples": self.words_to_str(tokens, type_="WORD")}


class DocstringParser(Lark):
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
    WORD:           /[a-zA-Z0-9.`,>=()\[\]\/]+/
 
    WS:             /\s+/
    
    %ignore         WS
    """

    def __init__(self, **kwargs):
        super().__init__(
            grammar=self.grammar,
            parser="earley",  # supports rule priority
            # parser="lalr",  # supports terminal priority
            **kwargs,
        )

    def parse(self, text: str, **kwargs) -> Tuple[Optional[Docstring], Optional[str]]:
        try:
            tree = super().parse(text=text, **kwargs)
            # print("\n" + tree.pretty())
            transformed = DocstringTransformer().transform(tree)
            return Docstring(**transformed), None
        except (GrammarError, UnexpectedCharacters, UnexpectedToken) as error:
            return None, ", ".join(error.args)
