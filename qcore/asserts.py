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

__all__ = [
    'assert_is', 'assert_is_not', 'assert_is_instance', 'assert_eq', 'assert_dict_eq', 'assert_ne',
    'assert_gt', 'assert_ge', 'assert_lt', 'assert_le', 'assert_in',
    'assert_not_in', 'assert_in_with_tolerance', 'assert_is_substring', 'assert_is_not_substring',
    'assert_unordered_list_eq', 'assert_raises', 'AssertRaises'
]


# The unittest.py testing framework checks for this variable in a module to
# filter out stack frames from that module from the test output, in order to
# make the output more concise.
# __unittest = 1


import six
import traceback

from .inspection import get_full_name


_number_types = six.integer_types + (float, complex)


def _assert_fail_message(message, expected, actual, comparison_str, extra):
    if message:
        return message
    if extra:
        return '%r %s %r (%s)' % (expected, comparison_str, actual, extra)
    return '%r %s %r' % (expected, comparison_str, actual)


def assert_is(expected, actual, message=None, extra=None):
    """Raises an AssertionError if expected is not actual."""
    assert expected is actual, _assert_fail_message(message, expected, actual, 'is not', extra)


def assert_is_not(expected, actual, message=None, extra=None):
    """Raises an AssertionError if expected is actual."""
    assert expected is not actual, _assert_fail_message(message, expected, actual, 'is', extra)


def assert_is_instance(value, types, message=None, extra=None):
    """Raises an AssertionError if value is not an instance of type(s)."""
    assert isinstance(value, types), _assert_fail_message(message, value, types,
                                                          'is not an instance of', extra)


def assert_eq(expected, actual, message=None, tolerance=None, extra=None):
    """Raises an AssertionError if expected != actual.

    If tolerance is specified, raises an AssertionError if either
    - expected or actual isn't a number, or
    - the difference between expected and actual is larger than the tolerance.

    """
    if tolerance is None:
        assert expected == actual, _assert_fail_message(message, expected, actual, '!=', extra)
    else:
        assert isinstance(tolerance, _number_types), \
            'tolerance parameter to assert_eq must be a number: %r' % tolerance
        assert isinstance(expected, _number_types) and isinstance(actual, _number_types), \
            'parameters must be numbers when tolerance is specified: %r, %r' % (expected, actual)

        diff = abs(expected - actual)
        assert diff <= tolerance, _assert_fail_message(message, expected, actual,
                                                       'is more than %r away from' % tolerance,
                                                       extra)


def _dict_path_string(path):
    if len(path) == 0:
        return '(root)'
    return '->'.join(map(repr, path))


def assert_dict_eq(expected, actual, number_tolerance=None, dict_path=[]):
    """Asserts that two dictionaries are equal, producing a custom message if they are not."""
    assert_is_instance(expected, dict)
    assert_is_instance(actual, dict)

    expected_keys = set(expected.keys())
    actual_keys = set(actual.keys())
    assert expected_keys <= actual_keys, "Actual dict at %s is missing keys: %r" % (
            _dict_path_string(dict_path), expected_keys - actual_keys)
    assert actual_keys <= expected_keys, "Actual dict at %s has extra keys: %r" % (
            _dict_path_string(dict_path), actual_keys - expected_keys)

    for k in expected_keys:
        key_path = dict_path + [k]
        assert_is_instance(
            actual[k],
            type(expected[k]),
            extra="Types don't match for %s" % _dict_path_string(key_path)
        )
        assert_is_instance(
            expected[k],
            type(actual[k]),
            extra="Types don't match for %s" % _dict_path_string(key_path)
        )

        if isinstance(actual[k], dict):
            assert_dict_eq(
                expected[k], actual[k], number_tolerance=number_tolerance, dict_path=key_path)
        elif isinstance(actual[k], _number_types):
            assert_eq(expected[k], actual[k],
                      extra="Value doesn't match for %s" % _dict_path_string(key_path),
                      tolerance=number_tolerance)
        else:
            assert_eq(expected[k], actual[k],
                      extra="Value doesn't match for %s" % _dict_path_string(key_path))


def assert_ne(expected, actual, message=None, tolerance=None, extra=None):
    """Raises an AssertionError if expected == actual.

    If tolerance is specified, raises an AssertionError if either
    - expected or actual isn't a number, or
    - the difference between expected and actual is smaller than the tolerance.

    """
    if tolerance is None:
        assert expected != actual, _assert_fail_message(message, expected, actual, '==', extra)
    else:
        assert isinstance(tolerance, _number_types), \
            'tolerance parameter to assert_eq must be a number: %r' % tolerance
        assert isinstance(expected, _number_types) and isinstance(actual, _number_types), \
            'parameters must be numbers when tolerance is specified: %r, %r' % (expected, actual)

        diff = abs(expected - actual)
        assert diff > tolerance, _assert_fail_message(message, expected, actual,
                                                      'is less than %r away from' % tolerance,
                                                      extra)


def assert_gt(left, right, message=None, extra=None):
    """Raises an AssertionError if left_hand <= right_hand."""
    assert left > right, _assert_fail_message(message, left, right, '<=', extra)


def assert_ge(left, right, message=None, extra=None):
    """Raises an AssertionError if left_hand < right_hand."""
    assert left >= right, _assert_fail_message(message, left, right, '<', extra)


def assert_lt(left, right, message=None, extra=None):
    """Raises an AssertionError if left_hand >= right_hand."""
    assert left < right, _assert_fail_message(message, left, right, '>=', extra)


def assert_le(left, right, message=None, extra=None):
    """Raises an AssertionError if left_hand > right_hand."""
    assert left <= right, _assert_fail_message(message, left, right, '>', extra)


def assert_in(obj, seq, message=None, extra=None):
    """Raises an AssertionError if obj is not in seq."""
    assert obj in seq, _assert_fail_message(message, obj, seq, 'is not in', extra)


def assert_not_in(obj, seq, message=None, extra=None):
    """Raises an AssertionError if obj is in iter."""
    # for very long strings, provide a truncated error
    if isinstance(seq, six.string_types) and obj in seq and len(seq) > 200:
        index = seq.find(obj)
        start_index = index - 50
        if start_index > 0:
            truncated = '(truncated) ...'
        else:
            truncated = ''
            start_index = 0
        end_index = index + len(obj) + 50
        truncated += seq[start_index:end_index]
        if end_index < len(seq):
            truncated += '... (truncated)'
        assert False, _assert_fail_message(message, obj, truncated, 'is in', extra)
    assert obj not in seq, _assert_fail_message(message, obj, seq, 'is in', extra)


def assert_in_with_tolerance(obj, seq, tolerance, message=None, extra=None):
    """Raises an AssertionError if obj is not in seq using assert_eq cmp."""
    for i in seq:
        try:
            assert_eq(obj, i, tolerance=tolerance, message=message, extra=extra)
            return
        except AssertionError:
            pass
    assert False, _assert_fail_message(message, obj, seq, 'is not in', extra)


def assert_is_substring(substring, subject, message=None, extra=None):
    """Raises an AssertionError if substring is not a substring of subject."""
    assert \
        (subject is not None) and \
        (substring is not None) and \
        (subject.find(substring) != -1), \
        _assert_fail_message(message, substring, subject, 'is not in', extra)


def assert_is_not_substring(substring, subject, message=None, extra=None):
    """Raises an AssertionError if substring is a substring of subject."""
    assert \
        (subject is not None) and \
        (substring is not None) and \
        (subject.find(substring) == -1), \
        _assert_fail_message(message, substring, subject, 'is in', extra)


def assert_unordered_list_eq(expected, actual, message=None):
    """Raises an AssertionError if the objects contained
    in expected are not equal to the objects contained
    in actual  without regard to their order.

    This takes quadratic time in the umber of elements in actual; don't use it for very long lists.

    """
    missing_in_actual = []
    missing_in_expected = list(actual)
    for x in expected:
        try:
            missing_in_expected.remove(x)
        except ValueError:
            missing_in_actual.append(x)

    if missing_in_actual or missing_in_expected:
        if not message:
            message = '%r not equal to %r; missing items: %r in expected, %r in actual.' % (
                expected, actual, missing_in_expected, missing_in_actual)
        assert False, message


def assert_raises(fn, *expected_exception_types):
    """Raises an AssertionError if calling fn does not raise one of the expected_exception-types."""
    with AssertRaises(*expected_exception_types):
        fn()


class AssertRaises(object):
    """With-context that asserts that the code within the context raises the specified exception."""
    def __init__(self, *expected_exception_types, **kwargs):
        # when you don't specify the exception expected, it's easy to write buggy tests that appear
        # to pass but actually throw an exception different from the expected one
        assert len(expected_exception_types) >= 1, \
            'You must specify the exception type when using AssertRaises'
        self.expected_exception_types = set(expected_exception_types)
        self.expected_exception_found = None
        self.extra = kwargs.pop('extra', None)
        assert_eq({}, kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type in self.expected_exception_types:
            # Return True to suppress the Exception if the type matches. For details,
            # see: http://docs.python.org/release/2.5.2/lib/typecontextmanager.html

            self.expected_exception_found = exc_val
            return True

        for t in self.expected_exception_types:
            if isinstance(exc_val, t):
                self.expected_exception_found = exc_val
                return True

        expected = ', '.join(map(get_full_name, self.expected_exception_types))

        if exc_type is None:
            message = "No exception raised, but expected: %s" % expected
            if self.extra is not None:
                message += ' (%s)' % self.extra
        else:
            template = '{TYPE}: {VAL} is raised, but expected: {EXPECTED}{EXTRA_STR}\n\n{STACK}'
            message = template.format(
                TYPE=get_full_name(exc_type),
                VAL=exc_val,
                EXPECTED=expected,
                STACK=''.join(traceback.format_tb(exc_tb)),
                EXTRA_STR=(' (%s)' % self.extra) if self.extra is not None else '',
            )
        raise AssertionError(message)
