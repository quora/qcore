import sys
from datetime import datetime, timezone, tzinfo
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    NewType,
    Optional,
    SupportsInt,
    Type,
    TypeVar,
)
from types import TracebackType

_T = TypeVar("_T")

Utime = NewType("Utime", int)

MICROSECOND: Utime
MILLISECOND: Utime
SECOND: Utime
MINUTE: Utime
HOUR: Utime
DAY: Utime
WEEK: Utime
YEAR_APPROXIMATE: Utime
MONTH_APPROXIMATE: Utime

def utime_delta(
    *, days: int = ..., hours: int = ..., minutes: int = ..., seconds: int = ...
) -> Utime: ...
def get_time_offset() -> Utime: ...
def set_time_offset(offset: SupportsInt) -> None: ...
def add_time_offset(offset: SupportsInt) -> None: ...

class TimeOffset:
    """Temporarily applies specified offset (in microseconds) to time() function result."""

    def __init__(self, offset: SupportsInt) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        typ: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...

def utime() -> Utime: ...
def true_utime() -> Utime: ...

# ===================================================
# Conversions to/from PY Date-Time
# ===================================================

def utime_as_datetime(utime: Utime, *, tz: tzinfo = timezone.utc) -> datetime: ...
def datetime_as_utime(dt: datetime) -> Utime: ...

# ===================================================
# Conversions to/from ISO 8601 Date-Time
# ===================================================

def format_utime_as_iso_8601(
    utime: Utime,
    *,
    sep: str = "T",
    drop_subseconds: bool = False,
    tz: tzinfo = timezone.utc,
) -> str: ...

# datetime.fromisoformat() is new in Python 3.7.
if sys.version_info >= (3, 7):
    def iso_8601_as_utime(iso_datetime: str) -> Utime: ...

# ===================================================
# Timeout API
# ===================================================

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
