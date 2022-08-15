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

import qcore
from qcore.asserts import AssertRaises, assert_is_substring, assert_is, assert_eq
from qcore.debug import get_bool_by_mask, set_by_mask
from unittest import mock


def test_hang_me_does_not_throw():
    qcore.debug.hang_me(0)
    with mock.patch("time.sleep") as mock_sleep:
        qcore.debug.hang_me(1)
        mock_sleep.assert_called_once_with(1)
        mock_sleep.reset_mock()
        qcore.debug.hang_me()
        mock_sleep.assert_called_once_with(10000)


def test_hange_me_handles_exception():
    with mock.patch("time.sleep") as mock_sleep:
        mock_sleep.side_effect = RuntimeError
        with AssertRaises(RuntimeError):
            qcore.debug.hang_me()
        mock_sleep.side_effect = KeyboardInterrupt
        qcore.debug.hang_me()


def test_format_stack():
    def foo():
        return qcore.debug.format_stack()

    st = foo()
    assert_is_substring("in foo\n", st)


def test_debug_counter():
    counter = qcore.debug.counter("test_debug_counter")
    counter_again = qcore.debug.counter("test_debug_counter")

    assert_is(counter, counter_again)
    counter.increment(5)
    assert_eq("DebugCounter('test_debug_counter', value=5)", str(counter))
    assert_eq("DebugCounter('test_debug_counter', value=5)", repr(counter))

    counter.decrement(3)
    assert_eq("DebugCounter('test_debug_counter', value=2)", str(counter))
    assert_eq("DebugCounter('test_debug_counter', value=2)", repr(counter))


def test_bool_by_mask():
    class MaskObject:
        def __init__(self):
            self.TEST_MASK_1 = False
            self.TEST_MASK_2 = True

    m = MaskObject()
    assert_is(True, get_bool_by_mask(m, "ABC"))
    assert_is(False, get_bool_by_mask(m, "TEST_MASK"))
    assert_is(False, get_bool_by_mask(m, "TEST_MASK_1"))
    assert_is(True, get_bool_by_mask(m, "TEST_MASK_2"))

    set_by_mask(m, "TEST_", True)
    assert_is(True, get_bool_by_mask(m, "TEST_MASK"))
    assert_is(True, get_bool_by_mask(m, "TEST_MASK_1"))
    assert_is(True, get_bool_by_mask(m, "TEST_MASK_2"))

    set_by_mask(m, "TEST_MASK_2", False)
    assert_is(True, get_bool_by_mask(m, "ABC"))
    assert_is(False, get_bool_by_mask(m, "TEST_MASK"))
    assert_is(True, get_bool_by_mask(m, "TEST_MASK_1"))
    assert_is(False, get_bool_by_mask(m, "TEST_MASK_2"))
