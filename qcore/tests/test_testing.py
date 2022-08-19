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

from qcore.asserts import assert_eq, assert_is, AssertRaises
from qcore.testing import (
    Anything,
    decorate_all_test_methods,
    decorate_func_or_method_or_class,
    GreaterEq,
    disabled,
    TEST_PREFIX,
)


def test_Anything():
    assert_eq(Anything, None)
    assert_eq(Anything, [])
    assert_eq(None, Anything)
    assert_eq([], Anything)
    assert not (Anything != None)
    assert not (Anything != [])
    assert not (None != Anything)
    assert not ([] != Anything)
    assert_eq("<Anything>", repr(Anything))


def test_GreaterEq():
    assert_eq(GreaterEq(2), 3)
    assert_eq(GreaterEq(2), 2)
    assert not GreaterEq(2) != 3
    assert not GreaterEq(2) != 2

    with AssertRaises(AssertionError):
        assert_eq(GreaterEq(3), 2)

    assert_eq("<GreaterEq(3)>", repr(GreaterEq(3)))


def _check_disabled(fn):
    try:
        from nose.plugins.skip import SkipTest
    except ImportError:
        assert_is(None, fn())
    else:
        with AssertRaises(SkipTest):
            fn()


def test_disabled():
    @disabled
    def fn():
        pass

    _check_disabled(fn)

    @disabled
    class TestCls:
        def test_method(self):
            return marker

        def normal_method(self):
            return marker

    _check_disabled(TestCls().test_method)
    assert_is(marker, TestCls().normal_method())

    class TestCls2:
        def test_method(self):
            return marker

        @disabled
        def test_method_disabled(self):
            return marker

        def normal_method(self):
            return marker

    assert_is(marker, TestCls2().test_method())
    _check_disabled(TestCls2().test_method_disabled)
    assert_is(marker, TestCls2().normal_method())

    with AssertRaises(AssertionError):
        disabled(None)


def normal_method(self):
    pass


marker = object()
test_method_name = TEST_PREFIX + "_method"
test_member_name = TEST_PREFIX + "_member"


def decorator(method):
    return marker


def _get_decoratable_class():
    class Cls:
        pass

    Cls.normal_method = normal_method

    test_method = lambda self: None
    setattr(Cls, test_method_name, test_method)
    assert_eq(test_method.__get__(None, Cls), getattr(Cls, test_method_name))

    setattr(Cls, test_member_name, "not a method")
    return Cls


def _assert_is_decorated(new_cls, cls):
    assert_is(new_cls, cls)
    assert_eq(normal_method.__get__(None, new_cls), new_cls.normal_method)
    assert_is(marker, getattr(new_cls, test_method_name))
    assert_eq("not a method", getattr(new_cls, test_member_name))


def test_decorate_all_test_methods():
    cls = _get_decoratable_class()
    new_cls = decorate_all_test_methods(decorator)(cls)
    _assert_is_decorated(new_cls, cls)


def test_decorate_func_or_method_or_class():
    cls = _get_decoratable_class()
    new_cls = decorate_func_or_method_or_class(decorator)(cls)
    _assert_is_decorated(new_cls, cls)

    assert_is(marker, decorate_func_or_method_or_class(decorator)(normal_method))

    with AssertRaises(AssertionError):
        decorate_func_or_method_or_class(decorator)(None)
