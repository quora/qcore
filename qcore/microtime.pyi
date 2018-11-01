from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Optional,
    SupportsInt,
    Type,
    TypeVar,
)
from types import TracebackType

_T = TypeVar("_T")

MICROSECOND: int
MILLISECOND: int
SECOND: int
MINUTE: int
HOUR: int
DAY: int
WEEK: int
YEAR_APPROXIMATE: int
MONTH_APPROXIMATE: int

def utime_delta(
    *, days: int = ..., hours: int = ..., minutes: int = ..., seconds: int = ...
) -> int: ...
def get_time_offset() -> int: ...
def set_time_offset(offset: SupportsInt) -> None: ...
def add_time_offset(offset: SupportsInt) -> None: ...

class TimeOffset(object):
    """Temporarily applies specified offset (in microseconds) to time() function result."""

    def __init__(self, offset: SupportsInt) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        typ: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...

def utime() -> int: ...
def true_utime() -> int: ...
def execute_with_timeout(
    fn: Callable[..., _T],
    args: Optional[Iterable[Any]] = ...,
    kwargs: Optional[Mapping[str, Any]] = ...,
    timeout: Optional[float] = ...,
    fail_if_no_timer: bool = ...,
    signal_type: int = ...,
    timer_type: int = ...,
    timeout_exception_cls: Type[BaseException] = ...,
) -> _T: ...
