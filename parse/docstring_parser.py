from typing import Tuple, Optional, NamedTuple

from lark import Lark, UnexpectedToken
from lark.exceptions import UnexpectedCharacters, GrammarError


class Docstring(NamedTuple):
    description: str
    args: list
    returns: str
    yields: str
    raises: str
    alias: str
    examples: str


class DocstringParser:
    """parse google style docstrings of module level python functions"""

    grammar = r"""
    ?start: description? args? (returns | yields)? raises? alias? examples?

    description: TEXT+
    args: _ARGS ":" TEXT+
    returns: _RETURNS ":" TEXT+
    yields: _YIELDS ":" TEXT+
    raises: _RAISES ":" TEXT+
    alias: _ALIAS ":" TEXT+
    examples: _EXAMPLES ":" TEXT+
    
    // params: TEXT ":" TEST+ params
    
    _ARGS: "Args"
    _RETURNS: "Returns"
    _YIELDS: "Yields"
    _RAISES: "Raises"
    _ALIAS: "Alias"
    _EXAMPLES: "Examples"
    
    TEXT: /.+/
    
    WS: /\s+/
    
    %ignore WS
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
            print("\n" + tree.pretty())
        except (GrammarError, UnexpectedCharacters, UnexpectedToken) as error:
            return None, ", ".join(error.args)
        description = " ".join([t.children[0] for t in tree.iter_subtrees() if t.data == "description"])
        args = [getattr(c, "value", "") for t in tree.iter_subtrees() if t.data == "args" for c in t.children]
        returns = " ".join([t.children[0] for t in tree.iter_subtrees() if t.data == "returns"])
        yields = " ".join([t.children[0] for t in tree.iter_subtrees() if t.data == "yields"])
        raises = " ".join([t.children[0] for t in tree.iter_subtrees() if t.data == "raises"])
        alias = " ".join([t.children[0] for t in tree.iter_subtrees() if t.data == "alias"])
        examples = " ".join([t.children[0] for t in tree.iter_subtrees() if t.data == "examples"])
        docstring = Docstring(
            description=description,
            args=args,
            returns=returns,
            yields=yields,
            raises=raises,
            alias=alias,
            examples=examples,
        )
        return docstring, None
