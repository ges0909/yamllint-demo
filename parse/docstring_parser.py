from typing import Tuple, Optional, NamedTuple

from lark import Lark, UnexpectedToken, UnexpectedCharacters, Tree


# class Docstring(NamedTuple):
#     args: list
#     returns: str
#     raises: str
#     alias: str


# class Docstring(Transformer):
#     def __init__(self, visit_tokens=True):
#         super().__init__(visit_tokens)
#         self._args = None
#         self._returns = None
#         self._raises = None
#         self._alias = None
#
#     def args(self, tokens):
#         self._args = [t.value for t in tokens if t.value != "Args"]
#
#     def returns(self, tokens):
#         self._returns = [t.value for t in tokens if t.value != "Returns"][0]
#
#     def raises(self, tokens):
#         self._raises = [t.value for t in tokens if t.value != "Raises"][0]
#
#     def alias(self, tokens):
#         self._alias = [t.value for t in tokens if t.value != "ALias"][0]


class FunctionDocstringParser(Lark):
    """parse google style python docstrings"""

    grammar = r"""
    ?start: TEXT+ args? returns? raises? alias?

    args: _ARGS ":" TEXT+ // TEXT ( "(" TEXT ")" )? ":" TEXT+
    returns: _RETURNS ":" TEXT+
    raises: _RAISES ":" TEXT+
    alias: _ALIAS ":" TEXT+
    
    _ARGS: "Args"
    _RETURNS: "Returns"
    _RAISES: "Raises"
    _ALIAS: "Alias"
    TEXT: /.+/
    
    WS: /\s+/
    
    %ignore WS
    """

    def __init__(self, **kwargs):
        super().__init__(
            grammar=self.grammar,
            parser="earley",  # supports rule priority
            # parser="lalr",  # supports terminal priority
            # transformer=DocstringTransformer(),
            **kwargs,
        )

    def parse(self, text: str, **kwargs) -> Tuple[Optional[Tree], Optional[str]]:
        try:
            return super().parse(text=text, **kwargs), None
            # return Docstring().transform(tree), None
        except (UnexpectedCharacters, UnexpectedToken) as error:
            return None, ", ".join(error.args)
