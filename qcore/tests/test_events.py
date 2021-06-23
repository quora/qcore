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
from qcore.asserts import (
    AssertRaises,
    assert_eq,
    assert_in,
    assert_is,
    assert_not_in,
    assert_is_instance,
)

from unittest import mock


count = 0


def handler(expected_count, raise_error=False):
    global count
    assert_eq(count, expected_count)
    count += 1
    if raise_error:
        raise NotImplementedError()


def test_events():
    global count
    h0 = lambda: handler(0)
    h1 = lambda: handler(1)
    h2 = lambda: handler(2)
    h0e = lambda: handler(0, True)

    count = 0
    events = qcore.EventHook()
    assert_eq("EventHook()", str(events))
    assert_eq("EventHook()", repr(events))

    events.subscribe(h0)
    assert_eq("EventHook(%r,)" % h0, str(events))
    assert_eq("EventHook(%r,)" % h0, repr(events))

    events()
    assert_eq(count, 1)

    count = 0
    events = qcore.EventHook()
    assert_eq([], list(events))
    events.subscribe(h0)
    events.subscribe(h1)
    assert_eq([h0, h1], list(events))
    assert_in(h0, events)
    assert_in(h1, events)
    assert_not_in(h2, events)

    events()
    assert_eq(count, 2)

    count = 0
    events = qcore.EventHook()
    events.subscribe(h0e)
    events.subscribe(h1)
    try:
        events()
    except BaseException:
        pass
    assert_eq(count, 1)

    count = 0
    events = qcore.EventHook()
    events.subscribe(h0e)
    events.subscribe(h1)
    try:
        events.safe_trigger()
    except BaseException:
        pass
    assert_eq(count, 2)

    count = 0
    events = qcore.EventHook()
    events.subscribe(h0)
    events.subscribe(h1)
    events()
    assert_eq(count, 2)
    count = 0
    events.unsubscribe(h1)
    events()
    assert_eq(count, 1)
    count = 0
    events.unsubscribe(h0)
    events()
    assert_eq(count, 0)

    events = qcore.EventHook()
    events.subscribe(h0)
    events.subscribe(h1)
    events.unsubscribe(h0)
    count = 1
    events()
    assert_eq(count, 2)
    count = 0
    events.unsubscribe(h1)
    events()
    assert_eq(count, 0)

    events = qcore.EventHook()
    events.subscribe(h0)
    events.subscribe(h1)
    events.subscribe(h2)
    events.unsubscribe(h1)
    events.unsubscribe(h0)
    events.unsubscribe(h2)
    count = 0
    events()
    assert_eq(count, 0)


def test_sinking_event_hook():
    def failing_handler():
        raise RuntimeError

    events = qcore.events.SinkingEventHook()
    assert_eq([], list(events))
    events.subscribe(failing_handler)
    assert_eq([], list(events))
    events.unsubscribe(failing_handler)
    assert_eq([], list(events))

    events.trigger()
    events.safe_trigger()
    events()

    assert_not_in(None, events)
    assert_not_in(False, events)
    assert_eq("SinkingEventHook()", str(events))


def test_event_interceptor():
    global count
    count = 0
    hub = qcore.EventHub()

    hub.on_a.trigger()
    hub.on_b.trigger()
    assert_eq(0, count)
    assert_eq([], list(hub.on_a))
    assert_eq([], list(hub.on_b))

    a_handler = lambda: handler(0)
    b_handler = lambda: handler(1)

    with qcore.EventInterceptor(hub, on_a=a_handler, on_b=b_handler):
        assert_eq([a_handler], list(hub.on_a))
        assert_eq([b_handler], list(hub.on_b))

        hub.on_a.trigger()
        hub.on_b.trigger()
        assert_eq(2, count)

    assert_eq([], list(hub.on_a))
    assert_eq([], list(hub.on_b))
    hub.on_a.trigger()
    hub.on_b.trigger()
    assert_eq(2, count)


def test_event_hub():
    h = qcore.EventHub()

    assert_eq(0, len(h))
    assert_eq("EventHub({})", repr(h))

    with AssertRaises(AttributeError):
        h.doesnt_start_with_on

    h_e = h.on_e
    assert_is_instance(h_e, qcore.EventHook)
    assert_eq(1, len(h))
    assert_is(h_e, h["e"])
    assert_eq("EventHub({'e': %r})" % h_e, repr(h))
    assert_is(h, h.safe_trigger("e"))
    assert_is(h, h.trigger("e"))

    h_e.subscribe(lambda: 0)

    assert_in("e", h)
    assert_not_in("f", h)

    h["f"] = None
    assert_is(None, h["f"])
    assert_in("f", h)
    assert_eq(2, len(h))

    del h["f"]
    assert_not_in("f", h)
    assert_eq(1, len(h))

    for k, v in h:
        assert_eq("e", k)
        assert_is(h_e, v)

    def bad_fn(*args):
        raise NotImplementedError()

    m = mock.MagicMock()
    h.on_test.subscribe(bad_fn)
    with AssertRaises(NotImplementedError):
        h.on("test", m).safe_trigger("test", 1)
    m.assert_called_once_with(1)
    m.reset_mock()

    h.off("test", bad_fn).trigger("test", 2, 3)
    m.assert_called_once_with(2, 3)


def test_events_hub_with_source():
    def handler():
        pass

    hook = qcore.EventHook()
    hook.subscribe(handler)
    assert_eq([handler], list(hook))

    hub = qcore.EventHub(source={"on_something": hook})
    assert_eq([handler], list(hub.on_something))


def test_global_events():
    c = len(qcore.events.hub)

    event = "test_global_event_4849tcj5"
    e = qcore.events.hub.get_or_create(event)

    event_fire_args = []

    def event_handler(*args):
        event_fire_args.append(args)

    e.subscribe(event_handler)
    e()

    assert_eq(1, len(event_fire_args))

    del qcore.events.hub[event]
    assert_eq(c, len(qcore.events.hub))


def test_enum_based_event_hub():
    class Events(qcore.Enum):
        work = 1
        sleep = 2

    class MoreEvents(qcore.Enum):
        eat = 3

    class EventHub1(qcore.EnumBasedEventHub):
        __based_on__ = Events
        on_work = qcore.EventHook()
        on_sleep = qcore.EventHook()

    m1 = mock.MagicMock()
    m2 = mock.MagicMock()
    hub1 = EventHub1()
    hub1.on_work.subscribe(m1)
    hub1.on(Events.work, m2).trigger(Events.work)
    m1.assert_called_once_with()
    m2.assert_called_once_with()

    m1.reset_mock()
    m2.reset_mock()
    hub1.on(Events.sleep, lambda: None).trigger(Events.sleep)
    assert_eq(0, m1.call_count)
    assert_eq(0, m2.call_count)

    class EventHub2(qcore.EnumBasedEventHub):
        __based_on__ = [Events, MoreEvents]
        on_work = qcore.EventHook()
        on_sleep = qcore.EventHook()
        on_eat = qcore.EventHook()
        on_some_other_member = None

        def some_method(self):
            pass

    with AssertRaises(AssertionError):

        class BadEventHub3(qcore.EnumBasedEventHub):
            # No __based_on__ = [Events]
            pass

    with AssertRaises(AssertionError):

        class BadEventHub4(qcore.EnumBasedEventHub):
            __based_on__ = [Events, MoreEvents]
            on_work = qcore.EventHook()
            on_eat = qcore.EventHook()

    with AssertRaises(AssertionError):

        class BadEventHub5(qcore.EnumBasedEventHub):
            __based_on__ = [Events, MoreEvents]
            on_work = qcore.EventHook()
            on_sleep = qcore.EventHook()
            on_eat = qcore.EventHook()
            on_bad = qcore.EventHook()

    with AssertRaises(AssertionError):

        class BadEventHub6(qcore.EnumBasedEventHub):
            __based_on__ = Events
            on_work = qcore.EventHook()
            on_sleep = 1

    with AssertRaises(AssertionError):

        class BadEventHub7(qcore.EnumBasedEventHub):
            __based_on__ = [Events, MoreEvents, MoreEvents]  # Duplicate members
            on_work = qcore.EventHook()
            on_sleep = qcore.EventHook()
            on_eat = qcore.EventHook()
