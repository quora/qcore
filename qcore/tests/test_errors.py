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

import sys
import traceback

from qcore import errors
from qcore.asserts import assert_in


def test_errors():
    def f1():
        assert 0, "holy moly"

    def raise_later(e):
        errors.reraise(e)

    def f2():
        try:
            f1()
        except AssertionError as e:
            prepared_e = errors.prepare_for_reraise(e)
        else:
            assert False, "f1 should have raised AssertionError"
        raise_later(prepared_e)

    try:
        f2()
    except AssertionError:
        formatted = traceback.format_tb(sys.exc_info()[2])
        formatted_message = "".join(formatted)
        assert_in("holy moly", formatted_message)
        assert_in("f1", formatted_message)
    else:
        assert False, "f2 should have raised AssertionError"
