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
from qcore.asserts import assert_eq, assert_is_not, AssertRaises


def dump(*args):
    print(repr(args))


def fail(*args):
    raise NotImplementedError()


def test_common():
    o = qcore.MarkerObject("o @ qcore.test_examples")
    assert_is_not(o, qcore.miss)

    o = qcore.dict_to_object({"a": 1, "b": 2})
    assert_eq(o.a, 1)  # Zero overhead!
    assert_eq(o.b, 2)  # Zero overhead!


def test_events():
    e = qcore.EventHook()
    e.subscribe(lambda *args: dump("Handler 1", *args))
    e("argument")

    e.subscribe(lambda: fail("Handler 2"))
    e.subscribe(lambda: dump("Handler 3"))

    with AssertRaises(NotImplementedError):
        e()  # prints 'Handler 1'

    with AssertRaises(NotImplementedError):
        e.safe_trigger()  # prints 'Handler 1', 'Handler 3'

    h = qcore.EventHub()
    h.on_some_event.subscribe(lambda: dump("On some event"))
    h.on_some_other_event.subscribe(lambda: dump("On some other event"))

    h.on_some_event()
    h.on_some_other_event()

    # a.events.hub.on_this_unused_handler.subscribe(lambda: None)
    # qcore.events.hub.on_this_unused_handler.subscribe(lambda: None)
