from typing import Any, Optional, Protocol, TypeVar

T = TypeVar('T')


class Castable(Protocol):
    def __call__(self, v: Any) -> T:
        ...


def safe_cast(v: Any, t: Castable) -> Optional[T]:
    return t(v) if v is not None else None
