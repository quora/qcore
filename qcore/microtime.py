# Copyright 2016 Quora, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

Helpers for dealing with sub-second time.

Here, time is represented as an integer of microseconds, a.k.a. "Utime".

"""

__all__ = [
    "DAY",
    "HOUR",
    "MICROSECOND",
    "MILLISECOND",
    "MINUTE",
    "MONTH_APPROXIMATE",
    "SECOND",
    "WEEK",
    "YEAR_APPROXIMATE",
    "TimeOffset",
    "Utime",
    "add_time_offset",
    "datetime_as_utime",
    "execute_with_timeout",
    "format_utime_as_iso_8601",
    "get_time_offset",
    "set_time_offset",
    "true_utime",
    "utime",
    "utime_as_datetime",
    "utime_delta",
]


import signal
from functools import wraps
from time import time as _time_in_seconds
from datetime import datetime, timezone
from typing import NewType

from . import inspection
from .helpers import none, empty_tuple, empty_dict
from .errors import TimeoutError, NotSupportedError


Utime = NewType("Utime", int)


MICROSECOND = 1
MILLISECOND = MICROSECOND * 1000
SECOND = MILLISECOND * 1000
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
YEAR_APPROXIMATE = int(DAY * 365.25)
MONTH_APPROXIMATE = int(YEAR_APPROXIMATE // 12)


_offset_utime = 0  # type: Utime


def utime_delta(*, days=0, hours=0, minutes=0, seconds=0):
    """Gets time delta in microseconds.

    Note: Do NOT use this function without keyword arguments.
    It will become much-much harder to add extra time ranges later if positional arguments are used.

    """
    return (days * DAY) + (hours * HOUR) + (minutes * MINUTE) + (seconds * SECOND)


def get_time_offset():
    """Gets the offset applied to time() function result in microseconds."""
    global _offset_utime
    return _offset_utime


def set_time_offset(offset):
    """Sets the offset applied to time() function result in microseconds."""
    global _offset_utime
    _offset_utime = int(offset)


def add_time_offset(offset):
    """Adds specified number of microseconds to the offset applied to time() function result."""
    global _offset_utime
    _offset_utime += int(offset)


class TimeOffset:
    """Temporarily applies specified offset (in microseconds) to time() function result."""

    def __init__(self, offset):
        self.offset = int(offset)

    def __enter__(self):
        global _offset_utime
        _offset_utime += self.offset

    def __exit__(self, typ, value, traceback):
        global _offset_utime
        _offset_utime -= self.offset


def utime():
    """Gets current time in microseconds from the epoch time w/applied offset."""
    return _offset_utime + int(_time_in_seconds() * SECOND)


def true_utime():
    """Gets current time in microseconds from the epoch time."""
    return int(_time_in_seconds() * SECOND)


# ===================================================
# Conversions to/from PY Date-Time
# ===================================================


def utime_as_datetime(utime, *, tz=timezone.utc):
    """Get Python datetime instance for the given microseconds time.

    This time refers to an absolute moment, given as microseconds from Unix Epoch.

    """
    return datetime.fromtimestamp(utime / SECOND, tz=tz)


def datetime_as_utime(dt):
    """Get the microseconds time for given Python datetime instance.

    This time refers to an absolute moment, given as microseconds from Unix Epoch.

    """
    return int(dt.timestamp() * SECOND)


# ===================================================
# Conversions to/from ISO 8601 Date-Time
# ===================================================


def format_utime_as_iso_8601(utime, *, sep="T", drop_subseconds=False, tz=timezone.utc):
    """Get ISO 8601 Time string for the given microseconds time.

    Example output for the default UTC timezone:
    "2022-10-31T18:02:03.123456+00:00"

    """
    timespec = "seconds" if drop_subseconds else "auto"
    return utime_as_datetime(utime, tz=tz).isoformat(sep=sep, timespec=timespec)


# datetime.fromisoformat() is new in Python 3.7.
if hasattr(datetime, "fromisoformat"):

    def iso_8601_as_utime(iso_datetime):
        """Get the microseconds time for given ISO 8601 Time string.

        Example input:
        "2022-11-01T01:02:03.123456+07:00"

        """
        return datetime_as_utime(datetime.fromisoformat(iso_datetime))

    __all__.append("iso_8601_as_utime")


# ===================================================
# Timeout API
# ===================================================


# Windows compatibility stuff
_DEFAULT_SIGNAL_TYPE = signal.SIGALRM if hasattr(signal, "SIGALRM") else None
_DEFAULT_TIMER_TYPE = signal.ITIMER_REAL if hasattr(signal, "ITIMER_REAL") else None


def execute_with_timeout(
    fn,
    args=None,
    kwargs=None,
    timeout=None,
    fail_if_no_timer=True,
    signal_type=_DEFAULT_SIGNAL_TYPE,
    timer_type=_DEFAULT_TIMER_TYPE,
    timeout_exception_cls=TimeoutError,
):
    """
    Executes specified function with timeout. Uses SIGALRM to interrupt it.

    :type fn: function
    :param fn: function to execute

    :type args: tuple
    :param args: function args

    :type kwargs: dict
    :param kwargs: function kwargs

    :type timeout: float
    :param timeout: timeout, seconds; 0 or None means no timeout

    :type fail_if_no_timer: bool
    :param fail_if_no_timer: fail, if timer is nor available; normally it's available only in the
    main thread

    :type signal_type: signalnum
    :param signal_type: type of signal to use (see signal module)

    :type timer_type: signal.ITIMER_REAL, signal.ITIMER_VIRTUAL or signal.ITIMER_PROF
    :param timer_type: type of timer to use (see signal module)

    :type timeout_exception_cls: class
    :param timeout_exception_cls: exception to throw in case of timeout

    :return: fn call result.

    """
    if args is None:
        args = empty_tuple
    if kwargs is None:
        kwargs = empty_dict

    if timeout is None or timeout == 0 or signal_type is None or timer_type is None:
        return fn(*args, **kwargs)

    def signal_handler(signum, frame):
        raise timeout_exception_cls(inspection.get_function_call_str(fn, args, kwargs))

    old_signal_handler = none
    timer_is_set = False
    try:
        try:
            old_signal_handler = signal.signal(signal_type, signal_handler)
            signal.setitimer(timer_type, timeout)
            timer_is_set = True
        except ValueError:
            if fail_if_no_timer:
                raise NotSupportedError(
                    "Timer is not available; the code is probably invoked from outside"
                    " the main thread."
                )
        return fn(*args, **kwargs)
    finally:
        if timer_is_set:
            signal.setitimer(timer_type, 0)
        if old_signal_handler is not none:
            signal.signal(signal_type, old_signal_handler)
