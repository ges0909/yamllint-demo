from typing import Tuple, Optional, NamedTuple

from lark import Lark, UnexpectedToken, Tree
from lark.exceptions import UnexpectedCharacters, GrammarError


class Docstring(NamedTuple):
    summary: str
    args: list
    returns: str
    yields: str
    raises: str
    alias: str
    examples: str


def _string(tree: Tree, key: str) -> str:
    tokens = [token for tree_ in tree.iter_subtrees() if tree_.data == key for token in tree_.children]
    return " ".join([token.value for token in tokens if token.type == "WORD"])


def _arg_list(trees: list[Tree]) -> list[Tuple[str, str, str]]:
    args = []
    for tree in trees:
        args.append(
            (
                " ".join([token.value for token in tree.children if token.type == "ID"]),
                " ".join([token.value for token in tree.children if token.type == "TYPE"]),
                " ".join([token.value for token in tree.children if token.type == "WORD"]),
            )
        )
    return args


class DocstringParser:
    """parse google style docstrings of module level python functions"""

    grammar = r"""
    ?start:         summary args? (returns | yields)? raises? alias? examples?

    summary:        WORD+
    args:           _ARGS COLON params
    returns:        _RETURNS COLON WORD+
    yields:         _YIELDS COLON WORD+
    raises:         _RAISES COLON WORD+
    alias:          _ALIAS COLON WORD+
    examples:       _EXAMPLES COLON WORD+
    
    params:         param+
    param:          ID COLON WORD+
                  | ID BRACKET_OPEN TYPE BRACKET_CLOSE COLON WORD+
    
    _ARGS:          "Args"
    _RETURNS:       "Returns"
    _YIELDS:        "Yields"
    _RAISES:        "Raises"
    _ALIAS:         "Alias"
    _EXAMPLES:      "Examples"
    
    ID:             /[a-zA-Z][a-zA-Z0-9_]*/
    TYPE:           /[a-zA-Z][a-zA-Z0-9_]*/
    COLON:          ":"
    BRACKET_OPEN:   "("
    BRACKET_CLOSE:  ")"
    WORD:           /[a-zA-Z0-9.]+/
 
    WS:             /\s+/
    
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
            # print("\n" + tree.pretty())
        except (GrammarError, UnexpectedCharacters, UnexpectedToken) as error:
            return None, ", ".join(error.args)
        args = [
            param_tree
            for args_tree in tree.iter_subtrees()
            if args_tree.data == "args"
            for params_tree in args_tree.iter_subtrees()
            if params_tree.data == "params"
            for param_tree in params_tree.iter_subtrees()
            if param_tree.data == "param"
        ]
        docstring = Docstring(
            summary=_string(tree, "summary"),
            args=_arg_list(args),
            returns=_string(tree, "returns"),
            yields=_string(tree, "yields"),
            raises=_string(tree, "raises"),
            alias=_string(tree, "alias"),
            examples=_string(tree, "examples"),
        )
        return docstring, None
