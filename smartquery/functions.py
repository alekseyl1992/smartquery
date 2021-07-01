from typing import Any, Callable, Iterable, Union, Optional, List, Dict

import functools

import copy
import math
import random

from decimal import Decimal as Decimal_

import regex

from smartquery.custom_types import Decimal
from smartquery.exceptions import ParserError


REGEX_TIMEOUT = 0.05
MAX_ARRAY_SIZE = 10000
CAST_DICT_KEYS_TO_STRINGS = True  # for JSON serialisation compatability


def pretty(value: Any, sep=...) -> str:
    if isinstance(value, dict):
        if sep is ...:
            sep = '\n'

        return sep.join([f'{k}: {v}' for k, v in value.items()])
    elif isinstance(value, list):
        if sep is ...:
            sep = ', '

        return sep.join([str(v) for v in value])
    elif isinstance(value, Decimal_):
        if sep is ...:
            sep = ' '

        value = str(value)
        no_minus_value = value if value[0] != '-' else value[1:]
        no_minus_value_len = len(no_minus_value)
        if no_minus_value_len < 5:
            return value

        chunks: List[str] = []
        for i in range(0, no_minus_value_len, 3):
            id_from = no_minus_value_len - i - 3
            if id_from < 0:
                id_from = 0

            chunks.insert(0, no_minus_value[id_from: no_minus_value_len - i])

        if no_minus_value == value:
            return sep.join(chunks)
        else:
            return f'-{sep.join(chunks)}'
    else:
        return str(value)


def keys(value: Any) -> list:
    return list(value.keys())


def values(value: Any) -> list:
    return list(value.values())


def items(value: Any) -> list:
    return list(value.items())


def _sum(value: Any) -> Any:
    if isinstance(value, list):
        return sum(value)
    else:
        return value


def _get(container: Any, key: Any, default=None) -> Any:
    key = _key_cast(container, key)
    return container.get(key, default)


def _key_cast(container: Any, key: Any) -> Any:
    if isinstance(container, dict):
        return _dict_key_cast(key)
    else:
        return _list_key_cast(key)


def _list_key_cast(key: Any) -> Any:
    if isinstance(key, Decimal_):
        return int(key)

    return key


def _dict_key_cast(key: Any) -> Any:
    if CAST_DICT_KEYS_TO_STRINGS:
        return str(key)
    else:
        if isinstance(key, Decimal_):
            return int(key)

    return key


def _get_item(container: Any, key: Any) -> Any:
    key = _key_cast(container, key)

    try:
        return container[key]
    except LookupError:
        raise ParserError(f'Key error \'{key}\'')


def _del(container: Any, key: Any) -> Any:
    key = _key_cast(container, key)

    if isinstance(container, dict):
        if key in container:
            del container[key]
    else:
        if len(container) > key:
            del container[key]


def _set(container: Any, key: Any, value: Any) -> Any:
    _check_array_size(container)

    key = _key_cast(container, key)

    container[key] = copy.deepcopy(value)
    return value


def _set_with_op(container: Any, key: Any, op: str, value: Any) -> Any:
    _check_array_size(container)

    key = _key_cast(container, key)
    value = copy.deepcopy(value)

    if op == '+=':
        container[key] += value
    elif op == '-=':
        container[key] -= value
    elif op == '*=':
        container[key] *= value
    elif op == '/=':
        container[key] /= value
    else:
        raise ParserError(f'Unsupported short op: {op}')

    return value


def _map(container: Any, f: Callable) -> Any:
    if isinstance(container, (list, str)):
        return [
            f(v) for v in container
        ]
    elif isinstance(container, dict):
        return [
            f(k, v) for k, v in container.items()
        ]

    raise ParserError(f'{container} is not a string, list or dict')


def _filter(container: Any, f: Callable) -> Any:
    if isinstance(container, list):
        return list(filter(f, container))

    raise ParserError(f'{container} is not a list')


def _reduce(container: Any, f: Callable) -> Any:
    if isinstance(container, Iterable):
        return functools.reduce(f, container)

    raise ParserError(f'{container} is not an Iterable')


def _enumerate(container: Any) -> list:
    return list(enumerate(container))


def _shuffle(container: Any) -> list:
    copied = copy.copy(container)
    random.shuffle(copied)
    return copied


def _index_of(container: list, value: Any) -> Optional[int]:
    try:
        return container.index(value)
    except ValueError:
        return None


def _split(s: str, sep=' ', max_split: int = -1):
    return s.split(sep, maxsplit=int(max_split))


def _replace(s: str, old: str, new: str, count: int = -1):
    return s.replace(old, new, int(count))


def _join(container: list, sep='\n'):
    return sep.join(map(str, container))


def _rand(*args):
    if len(args) == 0:
        return Decimal(random.random())
    elif len(args) == 1 and isinstance(args[0], list):
        return random.choice(args[0])
    elif len(args) == 2:
        min_ = args[0]
        max_ = args[1]
        return Decimal(random.randint(min_, max_))

    raise ParserError(f'Not supported rand() params: {args}')


def _parse_flags(flags_str: Optional[str]):
    if not flags_str:
        return 0

    flags_str = flags_str.lower()

    flags = 0
    if 'i' in flags_str:
        flags |= regex.I

    if 'm' in flags_str:
        flags |= regex.M

    if 's' in flags_str:
        flags |= regex.S

    return flags


def _match(s: str, pattern: str, flags_str: str = None):
    flags = _parse_flags(flags_str)
    m = regex.search(pattern, s, flags=flags, timeout=REGEX_TIMEOUT)
    if m is None:
        return None

    return m.group(0)


def _match_groups(s: str, pattern: str, flags_str: str = None):
    flags = _parse_flags(flags_str)
    m = regex.search(pattern, s, flags=flags, timeout=REGEX_TIMEOUT)
    if m is None:
        return None

    return [m.group(0), *m.groups()]


def _match_all(s: str, pattern: str, flags_str: str = None):
    flags = _parse_flags(flags_str)
    return regex.findall(pattern, s, flags=flags, timeout=REGEX_TIMEOUT)


def _push(arr: list, v: Any):
    _check_array_size(arr)
    return arr.append(v)


def _insert(arr: list, i: Any, v: Any):
    _check_array_size(arr)
    return arr.insert(int(i), v)


def _remove(container: Union[list, dict], v: Any):
    try:
        if isinstance(container, list):
            container.remove(v) if v in container else None
        else:
            if v in container:
                del container[v]
    except IndexError as e:
        raise ParserError(str(e))


def _pop(arr: list, i: Optional[int] = None):
    try:
        return arr.pop(int(i)) if i is not None else arr.pop()
    except IndexError as e:
        raise ParserError(str(e))


def _sorted(container: Union[list, dict], key: Any = None, reverse: bool = False):
    if isinstance(container, dict):
        if isinstance(key, Callable):  # type: ignore
            return dict(sorted(
                container.items(),
                key=lambda p: key(p[0], p[1]), reverse=reverse))  # type: ignore
        else:
            return dict(sorted(container.items(), key=key, reverse=reverse))
    else:
        return list(sorted(container, key=key, reverse=reverse))


def _reversed(container: Union[list, str]):
    if isinstance(container, str):
        return ''.join(reversed(container))
    else:
        return list(reversed(container))


def _check_array_size(arr: Union[list, dict]):
    if len(arr) >= MAX_ARRAY_SIZE:
        raise ParserError(f'Array size overflow: {MAX_ARRAY_SIZE}')


FUNCTIONS: Dict[str, Callable] = {
    'len': len,
    'int': lambda v: Decimal(int(v)),
    'float': lambda v: Decimal(float(v)),
    'str': str,
    'dict': dict,
    'list': lambda *args: [*args],

    # strings
    'startswith': str.startswith,
    'endswith': str.endswith,
    'lower': str.lower,
    'upper': str.upper,
    'strip': str.strip,
    'replace': _replace,

    # re
    'match': _match,
    'match_groups': _match_groups,
    'match_all': _match_all,

    # dicts
    'pretty': pretty,
    'keys': keys,
    'values': values,
    'items': items,
    'sum': _sum,
    'get': _get,
    '__getitem__': _get_item,
    '__delitem__': _del,
    '__setitem__': _set,
    '__setitem_with_op__': _set_with_op,

    'map': _map,
    'filter': _filter,
    'reduce': _reduce,
    'join': _join,
    'split': _split,

    # math:
    'round': lambda v, nd=None: Decimal(str(round(v, int(nd) if nd is not None else None))),
    'floor': lambda *args: Decimal(str(math.floor(*args))),
    'ceil': lambda *args: Decimal(str(math.ceil(*args))),
    'abs': lambda v: Decimal(abs(v)),
    'min': min,
    'max': max,
    'rand': _rand,

    # list ops:
    'push': _push,
    'pop': _pop,
    'insert': _insert,
    'remove': _remove,

    'sorted': _sorted,
    'reversed': _reversed,
    'enumerate': _enumerate,
    'shuffle': _shuffle,
    'index_of': _index_of,
}
