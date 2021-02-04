from pathlib import Path
from typing import Any, Iterable, cast, MutableMapping, Optional

from smartquery import lexer, rules
from smartquery.ast_ops import Op
from smartquery.ply import lex, yacc
from smartquery.scoped_dict import ScopedDict
from smartquery.vm_state import VMState


class SqParser:
    def __init__(self, parse_cache: Optional[MutableMapping[str, Op]] = None):
        output_dir = str(Path(__file__).parent / 'gen')

        self.parse_cache = parse_cache

        self.lex = lex.lex(
            module=lexer,
            optimize=True,
            debug=False,
            outputdir=output_dir)

        self.yacc = yacc.yacc(
            module=rules,
            optimize=True,
            debug=False,
            outputdir=output_dir)

    def list_names(self, expr: str) -> Iterable[str]:
        self.lex.lexpos = 0
        self.lex.lineno = 1

        self.lex.input(expr)

        while True:
            t = self.lex.token()
            if t is None:
                return
            if t.type == 'NAME':
                yield t.value

    def parse(self, expr: str) -> Op:
        self.lex.lexpos = 0
        self.lex.lineno = 1

        self.lex.ast = None
        self.yacc.parse(input=expr, lexer=self.lex)
        return cast(Op, self.lex.ast)

    def eval(self, expr: str, names: dict = None, max_ops_evaluated: int = 100) -> Any:
        scoped_names = ScopedDict(names if names is not None else {})

        if self.parse_cache is None or expr not in self.parse_cache:
            ast = self.parse(expr=expr)
            if self.parse_cache is not None:
                self.parse_cache[expr] = ast
        else:
            ast = self.parse_cache[expr]

        if ast is not None:
            state = VMState(names=scoped_names, max_ops_evaluated=max_ops_evaluated)
            return ast.eval(state)
        else:
            return None
