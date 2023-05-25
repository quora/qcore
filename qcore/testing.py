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

Module with assertion helpers.

The advantages of using a method like

   assert_eq(expected, actual)

instead of

   assert expected == actual

include:

1 - On failures, assert_eq prints an informative message of the actual
    values compared (e.g. AssertionError: 1 != 2) for free, which makes it
    faster and easier to iterate on tests.
2 - In the context of refactors, basic asserts incorrectly shift the burden of
    adding printouts and writing good test code to people refactoring code
    rather than the person who initially wrote the code.

"""

__all__ = ["Anything", "GreaterEq"]


# The unittest.py testing framework checks for this variable in a module to
# filter out stack frames from that module from the test output, in order to
# make the output more concise.
# __unittest = 1


import functools
import inspect

TEST_PREFIX = "test"


class _Anything:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __repr__(self):
        return "<Anything>"

    def __hash__(self):
        return 0


Anything = _Anything()


class GreaterEq:
    """Greater than or equal to some value.

    For example, assert_eq(GreaterEq(2), 3) and assert_eq(GreaterEq(2), 2) succeed,
    while assert_eq(GreaterEq(3), 2) fails.
    Useful if only equality asserts are supported or if we need to
    check inequality in a subfield as part of an assert_eq on an object that contains it.
    """

    def __init__(self, val):
        self.val = val

    def __eq__(self, other):
        return other >= self.val

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<GreaterEq({})>".format(self.val)


def disabled(func_or_class):
    """Decorator to disable a test.

    Ensures that nose skips the test and that neither the test's setup nor
    teardown is executed.

    """

    def decorate_func(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                from nose.plugins.skip import SkipTest
            except ImportError:
                return None  # do nothing, the test will show up as passed
            else:
                raise SkipTest

        return wrapper

    def decorate_class(class_):
        class_.setup = class_.teardown = lambda self: None
        return decorate_all_test_methods(decorate_func)(class_)

    if inspect.isfunction(func_or_class):
        return decorate_func(func_or_class)
    elif inspect.isclass(func_or_class):
        return decorate_class(func_or_class)
    else:
        assert False, "Must be used as a function or class decorator"


def decorate_all_test_methods(decorator):
    """Decorator to apply another decorator to all test methods of a class."""

    # in python 3, unbound methods are just functions, so we also need to check for functions
    def predicate(member):
        return inspect.ismethod(member) or inspect.isfunction(member)

    def wrapper(cls):
        for name, m in inspect.getmembers(cls, predicate):
            if name.startswith(TEST_PREFIX):
                setattr(cls, name, decorator(m))
        return cls

    return wrapper


decorate_all_test_methods.__test__ = False


def decorate_func_or_method_or_class(decorator):
    """Applies a decorator to a function, method, or all methods of a class.

    This is a decorator that is applied to a decorator to allow a
    function/method decorator to be applied to a class and have it act on all
    test methods of the class.

    """

    def decorate(func_or_class):
        if inspect.isclass(func_or_class):
            return decorate_all_test_methods(decorator)(func_or_class)
        elif inspect.isfunction(func_or_class):
            return decorator(func_or_class)
        else:
            assert False, "Target of decorator must be function or class"

    return decorate


decorate_func_or_method_or_class.__test__ = False
