from pathlib import Path
from typing import Any, Iterable, cast, MutableMapping, Optional, Dict

from smartquery import lexer, rules
from smartquery.ast_ops import Op
from smartquery.functions import FUNCTIONS
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
        self.lex.paren_count = 0

        self.lex.input(expr)

        while True:
            t = self.lex.token()
            if t is None:
                return
            if t.type == 'NAME':
                yield t.value

    def parse(self, expr: str) -> Op:
        if self.parse_cache is None or expr not in self.parse_cache:
            self.lex.lexpos = 0
            self.lex.lineno = 1
            self.lex.paren_count = 0

            self.lex.ast = None
            self.yacc.parse(input=expr, lexer=self.lex)

            ast = cast(Op, self.lex.ast)

            if self.parse_cache is not None:
                self.parse_cache[expr] = ast

            return ast
        else:
            return self.parse_cache[expr]

    def eval(
        self,
        expr: str,
        names: Dict[str, Any] = None,
        ast_names: Dict[str, Op] = None,
        max_ops_evaluated: int = 100,
    ) -> Any:
        scoped_names = ScopedDict({**FUNCTIONS})
        scoped_names.push_scope(names if names is not None else {})

        ast = self.parse(expr=expr.rstrip())

        if ast is not None:
            state = VMState(names=scoped_names, max_ops_evaluated=max_ops_evaluated)

            if ast_names is not None:
                for k, v in ast_names.items():
                    scoped_names[k] = v.eval(state)

            return ast.eval(state)
        else:
            return None
