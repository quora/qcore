from typing import (
    Any,
    ContextManager,
    Dict,
    Generic,
    List,
    Optional,
    Text,
    Tuple,
    Type,
    TypeVar,
)
from types import TracebackType

from .disallow_inheritance import DisallowInheritance as DisallowInheritance

_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)

empty_tuple: Tuple[Any, ...]
empty_list: List[Any]
empty_dict: Dict[Any, Any]

def true_fn() -> bool: ...
def false_fn() -> bool: ...

class MarkerObject:
    name: Text
    def __init__(self, name: Text) -> None: ...

none: MarkerObject
miss: MarkerObject
same: MarkerObject
unspecified: MarkerObject

class EmptyContext:
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None: ...

empty_context: EmptyContext

class CythonCachedHashWrapper(Generic[_T_co]):
    def __init__(self, value: _T_co) -> None: ...
    def value(self) -> _T_co: ...
    def hash(self) -> int: ...
    def __call__(self) -> _T_co: ...

CachedHashWrapper = CythonCachedHashWrapper

class ScopedValue(Generic[_T]):
    def __init__(self, default: _T) -> None: ...
    def get(self) -> _T: ...
    def set(self, value: _T) -> None: ...
    def override(self, value: _T) -> ContextManager[None]: ...
    def __call__(self) -> _T: ...

class _PropertyOverrideContext:
    def __init__(self, target: object, property_name: str, value: object) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None: ...

override = _PropertyOverrideContext

def ellipsis(source: str, max_length: int) -> str: ...
def safe_str(source: object, max_length: int = ...) -> str: ...
def safe_repr(source: object, max_length: int = ...) -> str: ...
def dict_to_object(source: Dict[str, Any]) -> Any: ...
def copy_public_attrs(source_obj: object, dest_obj: object) -> None: ...
def object_from_string(name: Text) -> Any: ...
def catchable_exceptions(exceptions: object) -> bool: ...
