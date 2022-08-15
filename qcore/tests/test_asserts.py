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


from collections import defaultdict

from qcore.asserts import (
    assert_eq,
    assert_ge,
    assert_gt,
    assert_is,
    assert_is_not,
    assert_le,
    assert_lt,
    assert_ne,
    assert_unordered_list_eq,
    AssertRaises,
    assert_not_in,
    assert_in,
    assert_dict_eq,
    assert_in_with_tolerance,
    # Strings
    assert_is_substring,
    assert_is_not_substring,
    assert_startswith,
    assert_endswith,
)


def test_assert_eq():
    assert_eq(1, 1)
    assert_eq("abc", "abc")
    assert_eq(None, None)
    assert_eq(1.0004, 1.0005, tolerance=0.001)
    assert_eq(1, 1.0, tolerance=0.001)


def test_assert_eq_failures():
    with AssertRaises(AssertionError):
        assert_eq(1, 2)
    with AssertRaises(AssertionError):
        assert_eq("abc", "abcd")
    with AssertRaises(AssertionError):
        assert_eq(None, 1)
    with AssertRaises(AssertionError):
        assert_eq(1.0004, 1.0005, tolerance=0.00001)
    with AssertRaises(AssertionError):
        assert_eq(1, 1.01, tolerance=0.001)

    # type errors
    with AssertRaises(AssertionError):
        assert_eq("s", 1, tolerance=0.1)
    with AssertRaises(AssertionError):
        assert_eq(None, 1, tolerance=0.1)
    with AssertRaises(AssertionError):
        assert_eq(1, 1, tolerance="s")


def test_assert_ordering():
    # ints
    assert_gt(2, 1)
    with AssertRaises(AssertionError):
        assert_gt(1, 1)
    with AssertRaises(AssertionError):
        assert_gt(0, 1)

    assert_ge(2, 1)
    assert_ge(1, 1)
    with AssertRaises(AssertionError):
        assert_ge(0, 1)

    with AssertRaises(AssertionError):
        assert_lt(2, 1)
    with AssertRaises(AssertionError):
        assert_lt(1, 1)
    assert_lt(0, 1)

    with AssertRaises(AssertionError):
        assert_le(2, 1)
    assert_le(1, 1)
    assert_lt(0, 1)

    # floats (tolerance isn't supported)
    assert_gt(2.5, 1.5)
    with AssertRaises(AssertionError):
        assert_gt(1.5, 1.5)
    with AssertRaises(AssertionError):
        assert_gt(0.5, 1.5)

    assert_ge(2.5, 1.5)
    assert_ge(1.5, 1.5)
    with AssertRaises(AssertionError):
        assert_ge(0.5, 1.5)

    with AssertRaises(AssertionError):
        assert_lt(2.5, 1.5)
    with AssertRaises(AssertionError):
        assert_lt(1.5, 1.5)
    assert_lt(0.5, 1.5)

    with AssertRaises(AssertionError):
        assert_le(2.5, 1.5)
    assert_le(1.5, 1.5)
    assert_lt(0.5, 1.5)

    # strings
    assert_gt("c", "b")
    with AssertRaises(AssertionError):
        assert_gt("b", "b")
    with AssertRaises(AssertionError):
        assert_gt("a", "b")

    assert_ge("c", "b")
    assert_ge("b", "b")
    with AssertRaises(AssertionError):
        assert_ge("a", "b")

    with AssertRaises(AssertionError):
        assert_lt("c", "b")
    with AssertRaises(AssertionError):
        assert_lt("b", "b")
    assert_lt("a", "b")

    with AssertRaises(AssertionError):
        assert_le("c", "b")
    assert_le("b", "b")
    assert_lt("a", "b")


def test_assert_ne():
    assert_ne(1, 2)
    assert_ne("abc", "abcd")
    assert_ne(None, 1)
    assert_ne(1.0004, 1.0005, tolerance=0.00001)
    assert_ne(1, 1.01, tolerance=0.001)


def test_assert_ne_with_failures():
    with AssertRaises(AssertionError):
        assert_ne(1, 1)
    with AssertRaises(AssertionError):
        assert_ne("abc", "abc")
    with AssertRaises(AssertionError):
        assert_ne(None, None)
    with AssertRaises(AssertionError):
        assert_ne(1.0004, 1.0005, tolerance=0.001)
    with AssertRaises(AssertionError):
        assert_ne(1, 1.0, tolerance=0.001)

    # type errors
    with AssertRaises(AssertionError):
        assert_ne("s", 1, tolerance=0.1)
    with AssertRaises(AssertionError):
        assert_ne(None, 1, tolerance=0.1)
    with AssertRaises(AssertionError):
        assert_ne(1, 1, tolerance="s")


def test_assert_is():
    # Assign to val to make the assertion look more prototypical.
    val = None
    assert_is(None, val)
    assert_is(int, type(1))

    with AssertRaises(AssertionError):
        assert_is(None, 1)
    with AssertRaises(AssertionError):
        assert_is(int, type("s"))


def test_assert_is_not():
    assert_is_not(None, 1)
    assert_is_not(int, type("s"))

    # Assign to val to make the assertion look more prototypical.
    val = None
    with AssertRaises(AssertionError):
        assert_is_not(None, val)
    with AssertRaises(AssertionError):
        assert_is_not(int, type(1))


def test_assert_not_in():
    # test truncation of very long strings
    seq = "a" * 1000 + "bbb" + "a" * 1000
    with AssertRaises(AssertionError) as ar:
        assert_not_in("bbb", seq)
    e = ar.expected_exception_found
    assert_eq(
        "'bbb' is in '(truncated) ...%sbbb%s... (truncated)'" % ("a" * 50, "a" * 50),
        str(e),
    )

    # same as above when the match is at index 0
    seq = "a" * 1000
    with AssertRaises(AssertionError) as ar:
        assert_not_in("aaa", seq)
    e = ar.expected_exception_found
    assert_eq("'aaa' is in 'aaa%s... (truncated)'" % ("a" * 50), str(e))


def test_assert_use_ascii_representation():
    non_ascii_string = "Hello سلام"
    with AssertRaises(AssertionError) as ar:
        assert_eq("aaa", non_ascii_string)
    e = ar.expected_exception_found
    assert_eq("'aaa' != 'Hello \\u0633\\u0644\\u0627\\u0645'", str(e))


class SpecificException(Exception):
    pass


class SpecificException2(Exception):
    pass


class TestAssertRaises:
    def test_handles_specific_exceptions(self):
        with AssertRaises(SpecificException, SpecificException2):
            raise SpecificException("foo")

    def test_handles_any_exceptions(self):
        with AssertRaises(Exception):
            raise Exception("foo")

    def test_fails_if_raise_wrong_exception(self):
        with AssertRaises(AssertionError):
            with AssertRaises(SpecificException):
                raise Exception("foo")

    def test_fails_if_exception_not_raised(self):
        try:
            with AssertRaises(ValueError):
                pass
        except AssertionError:
            pass
        else:
            assert False, "expected an exception to be raised"

    def test_handles_multiple_exception_types(self):
        with AssertRaises(IndexError, AssertionError):
            assert False

        with AssertRaises(AssertionError, IndexError):
            print([][0])

        class Assert2(AssertionError):
            pass

        class Index2(IndexError):
            pass

        with AssertRaises(AssertionError, IndexError):
            raise Assert2("foo")

        with AssertRaises(AssertionError, IndexError):
            raise Index2("foo")

    def test_with_extra(self):
        with AssertRaises(AssertionError) as ar:
            with AssertRaises(AssertionError, extra="extra message"):
                pass
        e = ar.expected_exception_found
        assert_in("extra message", str(e))

    def test_no_extra_kwargs(self):
        with AssertRaises(AssertionError):
            with AssertRaises(NotImplementedError, not_valid_kwarg=None):
                pass


def test_complex_assertions():
    with AssertRaises(AssertionError):
        with AssertRaises(AssertionError):
            pass

    with AssertRaises(RuntimeError):
        raise RuntimeError()

    assert_unordered_list_eq([1, 2, 2], [2, 1, 2])
    with AssertRaises(AssertionError):
        try:
            assert_unordered_list_eq([1, 2, 2], [2, 1])
        except AssertionError as e:
            print(repr(e))
            raise


def test_string_assertions():
    assert_is_substring("a", "bca")
    with AssertRaises(AssertionError):
        assert_is_substring("a", "bc")

    assert_is_not_substring("a", "bc")
    with AssertRaises(AssertionError):
        assert_is_not_substring("a", "bca")

    assert_startswith("a", "abc bcd")
    with AssertRaises(AssertionError):
        assert_startswith("b", "abc bcd")

    assert_endswith("d", "abc bcd")
    with AssertRaises(AssertionError):
        assert_endswith("c", "abc bcd")


class ExceptionWithValue(Exception):
    def __init__(self, value):
        self.value = value


def test_assert_error_saves_exception():
    assertion = AssertRaises(ExceptionWithValue)
    with assertion:
        raise ExceptionWithValue(5)
    assert_eq(5, assertion.expected_exception_found.value)


def test_message():
    try:
        assert_is(1, None, message="custom message")
    except AssertionError as e:
        assert_in("custom message", str(e))
    else:
        assert False, "should have thrown assertion error"


def test_extra():
    try:
        assert_eq("thing1", "thing2", extra="something extra")
    except AssertionError as e:
        assert_in("thing1", str(e))
        assert_in("thing2", str(e))
        assert_in("something extra", str(e))
    else:
        assert False, "should have thrown assertion error"


def test_assert_dict_eq():
    assert_dict_eq({"a": 1}, {"a": 1})

    with AssertRaises(AssertionError):
        assert_dict_eq({"a": 1}, {"b": 1})
    with AssertRaises(AssertionError):
        assert_dict_eq({"a": "abc"}, {"a": "xyz"})

    try:
        assert_dict_eq({"a": {"b": {"c": 1}}}, {"a": {"b": {"d": 1}}})
    except AssertionError as e:
        assert_in("'a'->'b'", str(e))
    else:
        assert False, "should have thrown assertion error"

    dd = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    dd["a"]["b"]["c"] = 1
    assert_dict_eq({"a": {"b": {"c": 1}}}, dd)
    assert_dict_eq(dd, {"a": {"b": {"c": 1}}})


def test_assert_in_with_tolerance():
    assert_in_with_tolerance(1, [1, 2, 3], 0)
    with AssertRaises(AssertionError):
        assert_in_with_tolerance(1, [2, 2, 2], 0)
    assert_in_with_tolerance(1, [2, 2, 2], 1)
