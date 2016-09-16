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

from qcore.microtime import utime_delta, execute_with_timeout, TimeOffset
import qcore
from qcore.asserts import AssertRaises, assert_eq, assert_ne, assert_le

import time


def test_utime_delta_combines_dates_hours_minutes_and_seconds():
    delta = utime_delta(days=1, hours=1, minutes=1, seconds=1)
    assert_eq(qcore.DAY + qcore.HOUR + qcore.MINUTE + qcore.SECOND, delta)


def test_utime_delta_does_not_allow_positional_arguments():
    with AssertRaises(TypeError):
        utime_delta(1, 2, seconds=3)


def test_execute_with_timeout():
    def run_forever():
        while True:
            time.sleep(0.1)

    def run_quickly():
        pass

    with AssertRaises(qcore.TimeoutError):
        execute_with_timeout(run_forever, timeout=0.2)
    execute_with_timeout(run_quickly, timeout=None)


def test_time_offset():
    time_before_offset = qcore.utime()
    with TimeOffset(qcore.HOUR):
        time_during_offset = qcore.utime()
    time_after_offset = qcore.utime()

    assert_eq(time_before_offset, time_after_offset, tolerance=qcore.MINUTE)
    assert_ne(time_before_offset, time_during_offset, tolerance=qcore.MINUTE)
    assert_le(time_after_offset, time_during_offset)
