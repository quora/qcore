from typing import Any, Callable, Dict, TypeVar

_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])
_SelfT = TypeVar("_SelfT", bound=DebugCounter)

counters: Dict[str, DebugCounter]
def trace(
    enter: bool = ..., exit: bool = ...
) -> Callable[[_CallableT], _CallableT]: ...

class DebugCounter(object):
    def __init__(self, name: str, value: int = ...) -> None: ...
    def increment(self: _SelfT, increment_by: int = ...) -> _SelfT: ...
    def decrement(self: _SelfT, decrement_by: int = ...) -> _SelfT: ...
    def dump(self: _SelfT) -> _SelfT: ...
    def dump_if(
        self: _SelfT, predicate: Callable[[_SelfT], bool], and_break: bool = ...
    ) -> _SelfT: ...
    def dump_every(self: _SelfT, interval_in_seconds: int = ...) -> _SelfT: ...
    def break_if(self: _SelfT, predicate: Callable[[_SelfT], bool]) -> _SelfT: ...

def counter(name: str) -> DebugCounter: ...
def breakpoint() -> None: ...
def hang_me(timeout_secs: int = ...) -> None: ...
def format_stack() -> str: ...
def get_bool_by_mask(source: object, prefix: str) -> bool: ...
def set_by_mask(target: object, prefix: str, value: object) -> None: ...
