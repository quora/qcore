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

Helpers for debugging.

"""

import inspect
import time
import types
import traceback

from . import inspection


counters = {}
globals()["counters"] = counters


def trace(enter=False, exit=True):
    """
    This decorator prints entry and exit message when
    the decorated method is called, as well as call
    arguments, result and thrown exception (if any).

    :param enter: indicates whether entry message should be printed.
    :param exit: indicates whether exit message should be printed.
    :return: decorated function.

    """
    def decorate(fn):
        @inspection.wraps(fn)
        def new_fn(*args, **kwargs):
            name = fn.__module__ + '.' + fn.__name__
            if enter:
                print('%s(args = %s, kwargs = %s) <-' % (name, repr(args), repr(kwargs)))
            try:
                result = fn(*args, **kwargs)
                if exit:
                    print('%s(args = %s, kwargs = %s) -> %s' % (
                        name,
                        repr(args),
                        repr(kwargs),
                        repr(result),
                    ))
                return result
            except Exception as e:
                if exit:
                    print('%s(args = %s, kwargs = %s) -> thrown %s' % (
                        name,
                        repr(args),
                        repr(kwargs),
                        str(e),
                    ))
                raise
        return new_fn
    return decorate


class DebugCounter(object):
    def __init__(self, name, value=0):
        self.name = name
        self.value = value
        self.last_dump_time = 0
        counters[name] = self

    def increment(self, increment_by=1):
        self.value += increment_by
        return self

    def decrement(self, decrement_by=1):
        self.value -= decrement_by
        return self

    def dump(self):
        self.last_dump_time = time.time()
        print('debug: ' + str(self))
        return self

    def dump_if(self, predicate, and_break=False):
        if predicate(self):
            self.dump()
            if and_break:
                breakpoint()
        return self

    def dump_every(self, interval_in_seconds=1):
        if self.last_dump_time + interval_in_seconds < time.time():
            self.dump()
        return self

    def break_if(self, predicate):
        if predicate(self):
            breakpoint()
        return self

    def __str__(self):
        return "DebugCounter(%s, value=%d)" % (repr(self.name), self.value)

    def __repr__(self):
        return self.__str__()


def counter(name):
    global counters
    if name in counters:
        return counters[name]
    else:
        return DebugCounter(name)


def breakpoint():
    print('Breakpoint reached.')


def hang_me(timeout_secs=10000):
    """Used for debugging tests."""
    print('Sleeping. Press Ctrl-C to continue...')
    try:
        time.sleep(timeout_secs)
    except KeyboardInterrupt:
        print('Done sleeping')


def format_stack():
    return ''.join(traceback.format_stack())


def get_bool_by_mask(source, prefix):
    result = True
    for k in dir(source):
        v = getattr(source, k, None)
        if k.startswith(prefix) and type(v) is bool:
            result = result and v
    return result


def set_by_mask(target, prefix, value):
    for k in dir(target):
        v = getattr(target, k, None)
        if k.startswith(prefix) and not inspect.isfunction(v):
            try:
                setattr(target, k, value)
            except AttributeError:
                pass
