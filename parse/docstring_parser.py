from typing import Tuple, Optional, NamedTuple

from lark import Lark, UnexpectedToken, Tree
from lark.exceptions import UnexpectedCharacters, GrammarError


class Docstring(NamedTuple):
    description: str
    args: list
    returns: str
    yields: str
    raises: str
    alias: str
    examples: str


def _string(tree: Tree, key: str) -> str:
    tokens = [token for tree_ in tree.iter_subtrees() if tree_.data == key for token in tree_.children]
    return " ".join([getattr(token, "value", "") for token in tokens])


def _list(trees: list[Tree]) -> list[str]:
    results = []
    for tree in trees:
        tokens = [token for token in tree.children]
        results.append(" ".join([getattr(token, "value", "") for token in tokens]))
    return results


class DocstringParser:
    """parse google style docstrings of module level python functions"""

    grammar = r"""
    ?start: description args? (returns | yields)? raises? alias? examples?

    description: WORD+
    args: _ARGS ":" params
    returns: _RETURNS ":" WORD+
    yields: _YIELDS ":" WORD+
    raises: _RAISES ":" WORD+
    alias: _ALIAS ":" WORD+
    examples: _EXAMPLES ":" WORD+
    
    params: param+
    param: ID ":" WORD+
         | ID "(" TYPE ")" ":" WORD+
    
    _ARGS: "Args"
    _RETURNS: "Returns"
    _YIELDS: "Yields"
    _RAISES: "Raises"
    _ALIAS: "Alias"
    _EXAMPLES: "Examples"
    
    ID: /[a-zA-Z][a-zA-Z0-9_]*/
    TYPE: /[a-zA-Z][a-zA-Z0-9_]*/
    WORD: /[a-zA-Z0-9.]+/
 
    WS: /\s+/
    
    %ignore WS
    """

    @staticmethod
    def parse(text: str, **kwargs) -> Tuple[Optional[Docstring], Optional[str]]:
        # tokens = []
        try:
            parser = Lark(
                # lexer="standard",
                # lexer="contextual",
                grammar=DocstringParser.grammar,
                parser="earley",  # supports rule priority
                # parser="lalr",  # supports terminal priority
                # lexer_callbacks={"TEXT": tokens.append},
                **kwargs,
            )
            tree = parser.parse(text=text, **kwargs)
            # print("\n" + tree.pretty())
        except (GrammarError, UnexpectedCharacters, UnexpectedToken) as error:
            return None, ", ".join(error.args)
        params = [
            param_tree
            for args_tree in tree.iter_subtrees()
            if args_tree.data == "args"
            for params_tree in args_tree.children
            if params_tree.data == "params"
            for param_tree in params_tree.children
        ]
        docstring = Docstring(
            description=_string(tree, "description"),
            args=_list(params),
            returns=_string(tree, "returns"),
            yields=_string(tree, "yields"),
            raises=_string(tree, "raises"),
            alias=_string(tree, "alias"),
            examples=_string(tree, "examples"),
        )
        return docstring, None
