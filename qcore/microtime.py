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

__doc__ = """

Helpers for dealing with time.

Assume that time is represented as an integer of microseconds.

"""

__all__ = [
    'MICROSECOND',
    'MILLISECOND',
    'SECOND',
    'MINUTE',
    'HOUR',
    'DAY',
    'WEEK',
    'YEAR_APPROXIMATE',
    'MONTH_APPROXIMATE',
    'utime_delta',
    'get_time_offset',
    'set_time_offset',
    'add_time_offset',
    'TimeOffset',
    'utime',
    'true_utime',
    'execute_with_timeout',
]

from functools import wraps
import signal
from time import time as _time

from . import inspection
from .helpers import none, empty_tuple, empty_dict
from .errors import TimeoutError, NotSupportedError


MICROSECOND = 1
MILLISECOND = MICROSECOND * 1000
SECOND = MILLISECOND * 1000
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
YEAR_APPROXIMATE = int(DAY * 365.25)
MONTH_APPROXIMATE = int(YEAR_APPROXIMATE // 12)

_time_offset = 0  # In microseconds (us)


def _keyword_arguments_only(fn):
    @wraps(fn)
    def new_fn(**kwargs):
        return fn(**kwargs)
    return new_fn


@_keyword_arguments_only
def utime_delta(days=0, hours=0, minutes=0, seconds=0):
    """Gets time delta in microseconds.

    Note: Do NOT use this function without keyword arguments.
    It will become much-much harder to add extra time ranges later if positional arguments are used.

    """
    return (days * DAY) + (hours * HOUR) + (minutes * MINUTE) + (seconds * SECOND)


def get_time_offset():
    """Gets the offset applied to time() function result in microseconds."""
    global _time_offset
    return _time_offset


def set_time_offset(offset):
    """Sets the offset applied to time() function result in microseconds."""
    global _time_offset
    _time_offset = int(offset)


def add_time_offset(offset):
    """Adds specified number of microseconds to the offset applied to time() function result."""
    global _time_offset
    _time_offset += int(offset)


class TimeOffset(object):
    """Temporarily applies specified offset (in microseconds) to time() function result."""
    def __init__(self, offset):
        self.offset = int(offset)

    def __enter__(self):
        global _time_offset
        _time_offset += self.offset

    def __exit__(self, typ, value, traceback):
        global _time_offset
        _time_offset -= self.offset


def utime():
    """Gets current time in microseconds from the epoch time w/applied offset."""
    return _time_offset + int(_time() * 1000000)


def true_utime():
    """Gets current time in microseconds from the epoch time."""
    return int(_time() * 1000000)


# Windows compatibility stuff
_default_signal_type = signal.SIGALRM if hasattr(signal, 'SIGALRM') else None
_default_timer_type = signal.ITIMER_REAL if hasattr(signal, 'ITIMER_REAL') else None


def execute_with_timeout(fn, args=None, kwargs=None, timeout=None,
                         fail_if_no_timer=True,
                         signal_type=_default_signal_type,
                         timer_type=_default_timer_type,
                         timeout_exception_cls=TimeoutError):
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
                    "Timer is not available; the code is probably invoked from outside the main "
                    "thread.")
        return fn(*args, **kwargs)
    finally:
        if timer_is_set:
            signal.setitimer(timer_type, 0)
        if old_signal_handler is not none:
            signal.signal(signal_type, old_signal_handler)
