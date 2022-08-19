from types import TracebackType
from typing import (
    Any,
    Callable,
    Container,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

_Numeric = Union[int, float, complex]

def assert_is(
    expected: Any,
    actual: Any,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_is_not(
    expected: Any,
    actual: Any,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_is_instance(
    value: Any,
    types: Union[Type[Any], Tuple[Union[Type[Any], Tuple[Any, ...]], ...]],
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_eq(
    expected: Any,
    actual: Any,
    message: Optional[str] = ...,
    tolerance: Optional[_Numeric] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_dict_eq(
    expected: Dict[Any, Any],
    actual: Dict[Any, Any],
    number_tolerance: Optional[_Numeric] = ...,
    dict_path: List[Any] = ...,
) -> None: ...
def assert_ne(
    expected: Any,
    actual: Any,
    message: Optional[str] = ...,
    tolerance: Optional[_Numeric] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_gt(
    expected: Any,
    actual: Any,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_ge(
    expected: Any,
    actual: Any,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_lt(
    expected: Any,
    actual: Any,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_le(
    expected: Any,
    actual: Any,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_in(
    expected: Any,
    actual: Container[Any],
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_not_in(
    expected: Any,
    actual: Container[Any],
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_in_with_tolerance(
    expected: Any,
    actual: Container[Any],
    tolerance: _Numeric,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_unordered_list_eq(
    expected: Iterable[Any], actual: Iterable[Any], message: Optional[str] = ...
) -> None: ...
def assert_raises(
    fn: Callable[[], Any], *expected_exception_types: Type[BaseException]
) -> None: ...

class AssertRaises:
    expected_exception_types: Set[Type[BaseException]]
    expected_exception_found: Any
    extra: Optional[str]
    def __init__(
        self,
        *expected_exception_types: Type[BaseException],
        extra: Optional[object] = ...,
    ) -> None: ...
    def __enter__(self) -> AssertRaises: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool: ...

# ===================================================
# Strings
# ===================================================

def assert_is_substring(
    substring: str,
    subject: str,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_is_not_substring(
    substring: str,
    subject: str,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_startswith(
    prefix: str,
    subject: str,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
def assert_endswith(
    suffix: str,
    subject: str,
    message: Optional[str] = ...,
    extra: Optional[object] = ...,
) -> None: ...
