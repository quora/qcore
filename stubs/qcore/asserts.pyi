from types import TracebackType
from typing import (
    Callable,
    Container,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

_Numeric = Union[int, float, complex]
def assert_is(
    expected: object,
    actual: object,
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_is_not(
    expected: object,
    actual: object,
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_is_instance(
    value: object,
    types: Union[type, Tuple[Union[type, Tuple], ...]],
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_eq(
    expected: object,
    actual: object,
    message: Optional[str] = ...,
    tolerance: Optional[_Numeric] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_dict_eq(
    expected: Dict[object, object],
    actual: Dict[object, object],
    number_tolerance: Optional[_Numeric] = ...,
    dict_path: List[object] = ...,
) -> None: ...
def assert_ne(
    expected: object,
    actual: object,
    message: Optional[str] = ...,
    tolerance: Optional[_Numeric] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_gt(
    expected: object,
    actual: object,
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_ge(
    expected: object,
    actual: object,
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_lt(
    expected: object,
    actual: object,
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_le(
    expected: object,
    actual: object,
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_in(
    expected: object,
    actual: Container[object],
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_not_in(
    expected: object,
    actual: Container[object],
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_in_with_tolerance(
    expected: object,
    actual: Container[object],
    tolerance: _Numeric,
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_is_substring(
    substring: str,
    subject: str,
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_is_not_substring(
    substring: str,
    subject: str,
    message: Optional[str] = ...,
    extra: Optional[str] = ...,
) -> None: ...
def assert_unordered_list_eq(
    expected: Iterable[object], actual: Iterable[object], message: Optional[str] = ...
) -> None: ...
def assert_raises(
    fn: Callable[[], object], *expected_exception_types: Type[BaseException]
) -> None: ...

class AssertRaises(object):
    """With-context that asserts that the code within the context raises the specified exception."""
    def __init__(
        self, *expected_exception_types: Type[BaseException], extra: Optional[str] = ...
    ) -> None: ...
    def __enter__(self) -> AssertRaises: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool: ...
