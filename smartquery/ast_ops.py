from abc import ABC
from dataclasses import dataclass
from decimal import Decimal as Decimal_
from typing import Any, List

import copy

from smartquery.custom_types import Decimal
from smartquery.exceptions import ParserError, OpsExecutionLimitExceededError
from smartquery.functions import _dict_key_cast
from smartquery.utils import safe_cast
from smartquery.vm_state import VMState


NUMERIC_TYPES = (Decimal_, int, float)


class Op(ABC):
    def eval(self, state: VMState):
        state.ops_evaluated += 1
        if state.ops_evaluated >= state.max_ops_evaluated:
            raise OpsExecutionLimitExceededError(f'Ops execution limit exceeded: {state.max_ops_evaluated}')


@dataclass
class NoOp(Op):
    pass


@dataclass
class ValueOp(Op):
    v: Any

    def eval(self, state: VMState):
        super().eval(state)
        return self.v


@dataclass
class CodeOp(Op):
    lines: List[Op]

    def eval(self, state: VMState):
        super().eval(state)

        res = None
        for line in self.lines:
            res = line.eval(state)

        return res


@dataclass
class BinOp(Op):
    op: str
    op1: Op
    op2: Op

    def eval(self, state: VMState):
        super().eval(state)

        op1 = self.op1.eval(state)

        if self.op != 'and' and self.op != 'or':
            op2 = self.op2.eval(state)
        else:
            op2 = None

        if self.op == '+':
            if isinstance(op1, str) and not isinstance(op2, str):
                op2 = str(op2)
            return op1 + op2
        elif self.op == '-':
            return op1 - op2
        elif self.op == '*':
            if not isinstance(op1, NUMERIC_TYPES) or not isinstance(op2, NUMERIC_TYPES):
                raise ParserError(f'Can\'t multiply non-numbers')

            return Decimal(op1) * Decimal(op2)
        elif self.op == '**':
            # explicitly cast to Decimal to avoid powering of big integers
            return Decimal(op1) ** Decimal(op2)
        elif self.op == '/':
            return op1 / op2

        elif self.op == '==':
            return op1 == op2
        elif self.op == '!=':
            return op1 != op2
        elif self.op == '>':
            return op1 > op2
        elif self.op == '<':
            return op1 < op2
        elif self.op == '>=':
            return op1 >= op2
        elif self.op == '<=':
            return op1 <= op2
        elif self.op == 'not in':
            return op1 not in op2
        elif self.op == 'in':
            return op1 in op2

        elif self.op == 'and':
            return op1 and self.op2.eval(state)
        elif self.op == 'or':
            return op1 or self.op2.eval(state)

        raise ParserError(f'Unsupported binary operation: {self.op}')


@dataclass
class UnaryOp(Op):
    op: str
    op1: Op

    def eval(self, state: VMState):
        super().eval(state)

        op1 = self.op1.eval(state)

        if self.op == '-':
            return -op1

        if self.op == 'not':
            return not op1


@dataclass
class AssignOp(Op):
    name: str
    value: Op

    def eval(self, state: VMState):
        super().eval(state)

        value = self.value.eval(state)
        state.names[self.name] = copy.deepcopy(value)
        return None


@dataclass
class ShortOp(Op):
    name: str
    op: str
    value: Op

    def eval(self, state: VMState):
        super().eval(state)

        value = copy.deepcopy(self.value.eval(state))

        if self.op == '+=':
            state.names[self.name] += value
        elif self.op == '-=':
            state.names[self.name] -= value
        elif self.op == '*=':
            state.names[self.name] *= value
        elif self.op == '/=':
            state.names[self.name] /= value
        else:
            raise ParserError(f'Unsupported short op: {self.op}')

        return None


@dataclass
class NameOp(Op):
    name: str

    def eval(self, state: VMState):
        super().eval(state)

        try:
            value = state.names[self.name]
        except LookupError:
            raise ParserError(f'Undefined variable {self.name}')

        return value


@dataclass
class IfExprOp(Op):
    cond: Op
    op1: Op
    op2: Op

    def eval(self, state: VMState):
        super().eval(state)

        cond = self.cond.eval(state)
        return self.op1.eval(state) if cond else self.op2.eval(state)


@dataclass
class SliceOp(Op):
    start: Op = ValueOp(None)
    stop: Op = ValueOp(None)
    step: Op = ValueOp(None)

    def eval(self, state: VMState):
        super().eval(state)

        return slice(
            safe_cast(self.start.eval(state), int),
            safe_cast(self.stop.eval(state), int),
            safe_cast(self.step.eval(state), int),
        )


@dataclass
class CallOp(Op):
    name: str
    args: list

    def eval(self, state: VMState):
        super().eval(state)

        args = [
            arg.eval(state) for arg in self.args
        ]
        try:
            f = state.names[self.name]
        except LookupError:
            raise ParserError(f'Undefined function {self.name}')

        return f(*args)


@dataclass
class DictOp(Op):
    d: List[tuple]

    def eval(self, state: VMState):
        super().eval(state)

        return {
            _dict_key_cast(k.eval(state)): v.eval(state) for k, v in self.d
        }


@dataclass
class LambdaOp(Op):
    args: List[NameOp]
    expr: Op

    def eval(self, state: VMState):
        super().eval(state)

        def f(*args):
            with state.names.make_scope({
                k.name: v for k, v in zip(self.args, args)
            }):
                return self.expr.eval(state)

        return f
