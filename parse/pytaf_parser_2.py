from lark.lark import Lark


class PytafParser2(Lark):
    """parse pytaf script"""

    grammar = r"""
    start: issue markers? NL*
    
    issue: NL* "issue" WS* ":" WS* VALUE
    markers: NL+ "markers" WS* ":" WS* VALUE
    
    before: NL+ "before" WS* ":" WS* _step*
    after: NL+ "after" WS* ":" WS* _step*
    steps: NL+ "steps" WS* ":" WS* step+
    _step: NL+ INDENT ID ":" WS* use? input? output?
    step: NL+ INDENT ID  ":" WS* markers? before? after? input? output?
    use: NL+ INDENT~2 "use" WS* ":" WS* VALUE
    input: NL+ INDENT~2 "input" WS* ":" WS* param+
    output: NL+ INDENT~2 "output" WS* ":" param+
    param: OBJECT
    
    ID: /[^:]+/
    VALUE: /[^:\n]+/
    INDENT: "  "
    OBJECT: (NL+ INDENT INDENT INDENT /.+/)
    COMMENT: /#[^\n]*/
 
    %import common.WS_INLINE -> WS
    %import common.NEWLINE -> NL
    %ignore COMMENT
    """

    def __init__(self, **kwargs):
        super().__init__(
            grammar=self.grammar,
            parser="lalr",
            **kwargs,
        )

    def parse(self, text: str, **kwargs):
        return super().parse(
            text=text,
            **kwargs,
        )
