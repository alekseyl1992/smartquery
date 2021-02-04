from dataclasses import dataclass, field

from smartquery.scoped_dict import ScopedDict


@dataclass
class VMState:
    names: ScopedDict = field(default_factory=lambda: ScopedDict({}))
    ops_evaluated: int = 0

    max_ops_evaluated: int = 100
