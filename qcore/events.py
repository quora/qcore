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

Event pub/sub routines.

"""

import inspect

from .enum import EnumType, EnumBase
from .errors import prepare_for_reraise, reraise


class EventHook:
    """This type allows to implement event pattern.

    Allowed operations on EventHook objects:

    * hook.subscribe(handler)  # subscribe
    * hook.unsubscribe(handler)  # unsubscribe (requires O(handlerCount)!)
    * hook(...)  # invokes all event handlers
    * hook.trigger(...) # another way to raise the event
    * hook.safe_trigger(...) # definitely invokes all event handlers and raises
                             # the first thrown exception (if any)

    """

    def __init__(self, handlers=None):
        """Constructor."""
        self.handlers = handlers if handlers is not None else []

    def subscribe(self, handler):
        """Adds a new event handler."""
        assert callable(handler), "Invalid handler %s" % handler
        self.handlers.append(handler)

    def unsubscribe(self, handler):
        """Removes an event handler."""
        self.handlers.remove(handler)

    def safe_trigger(self, *args):
        """*Safely* triggers the event by invoking all its
        handlers, even if few of them raise an exception.

        If a set of exceptions is raised during handler
        invocation sequence, this method rethrows the first one.

        :param args: the arguments to invoke event handlers with.

        """
        error = None
        # iterate over a copy of the original list because some event handlers
        # may mutate the list
        for handler in list(self.handlers):
            try:
                handler(*args)
            except BaseException as e:
                if error is None:
                    prepare_for_reraise(e)
                    error = e
        if error is not None:
            reraise(error)

    def trigger(self, *args):
        """Triggers the event by invoking all its handlers
        with provided arguments.

        .. note::
            If one of event handlers raises an exception,
            other handlers won't be invoked by this method.

        :param args: the arguments to invoke event handlers with.

        """
        for handler in list(self.handlers):
            handler(*args)

    def __call__(self, *args):
        """A shortcut to trigger method.

        .. note::
            If one of event handlers raises an exception,
            other handlers won't be invoked by this method.

        :param args: the arguments to invoke event handlers with.

        """
        self.trigger(*args)

    def __contains__(self, item):
        """Checks whether this set contains the specified event handler."""
        return item in self.handlers

    def __iter__(self):
        """Iterates through all registered event handlers."""
        for handler in self.handlers:
            yield handler

    def __str__(self):
        """Gets the string representation of this object."""
        return "EventHook" + repr(tuple(self.handlers))

    def __repr__(self):
        """Gets the ``repr`` representation of this object."""
        return self.__str__()


class SinkingEventHook(EventHook):
    """An implementation of EventHook that actually does nothing.
    This type allows to implement a simple performance
    optimization for ConstFuture, ErrorFuture and similar
    classes, since they never raise their events.

    """

    def subscribe(self, handler):
        """Does nothing."""
        return self

    def unsubscribe(self, handler):
        """Does nothing."""
        return self

    def safe_trigger(self, *args):
        """Does nothing."""
        return

    def trigger(self, *args):
        """Does nothing."""
        return

    def __call__(self, *args):
        """Does nothing."""
        return

    def __contains__(self, item):
        """Always returns False."""
        return False

    def __iter__(self):
        """Returns empty generator."""
        return iter([])

    def __str__(self):
        """Gets the string representation of this object."""
        return "SinkingEventHook()"


sinking_event_hook = SinkingEventHook()
globals()["sinking_event_hook"] = sinking_event_hook


class EventInterceptor:
    """A context object helping to temporarily intercept
    a set of events on an object exposing a set of event hooks.

    """

    def __init__(self, source, **events):
        """
        Constructor.

        :param source: the object exposing a set of event hook properies
        :param events: a set of event_hook_name=event_handler pairs specifying
                       which events to intercept.
        """
        self.source = source
        self.events = events

    def __enter__(self):
        """Starts event interception."""
        source = self.source
        for name, handler in self.events.items():
            hook = getattr(source, name)
            hook.subscribe(handler)

    def __exit__(self, typ, value, traceback):
        """Stops event interception."""
        source = self.source
        for name, handler in self.events.items():
            hook = getattr(source, name)
            hook.unsubscribe(handler)


class EventHub:
    """Provides named event hooks on demand.

    Use properties (or keys) of this object to access
    named event hooks created on demand (i.e. on the first
    access attempt).

    """

    def __init__(self, source=None):
        """Constructor.

        :param source: ``dict`` with initial set of named event hooks.

        """
        if source is not None:
            self.__dict__ = source

    def on(self, event, handler):
        """Attaches the handler to the specified event.

        @param event: event to attach the handler to. Any object can be passed
                      as event, but string is preferable. If qcore.EnumBase
                      instance is passed, its name is used as event key.
        @param handler: event handler.
        @return: self, so calls like this can be chained together.

        """
        event_hook = self.get_or_create(event)
        event_hook.subscribe(handler)
        return self

    def off(self, event, handler):
        """Detaches the handler from the specified event.

        @param event: event to detach the handler to. Any object can be passed
                      as event, but string is preferable. If qcore.EnumBase
                      instance is passed, its name is used as event key.
        @param handler: event handler.
        @return: self, so calls like this can be chained together.

        """
        event_hook = self.get_or_create(event)
        event_hook.unsubscribe(handler)
        return self

    def trigger(self, event, *args):
        """Triggers the specified event by invoking EventHook.trigger under the hood.

        @param event: event to trigger. Any object can be passed
                      as event, but string is preferable. If qcore.EnumBase
                      instance is passed, its name is used as event key.
        @param args: event arguments.
        @return: self, so calls like this can be chained together.

        """
        event_hook = self.get_or_create(event)
        event_hook.trigger(*args)
        return self

    def safe_trigger(self, event, *args):
        """Safely triggers the specified event by invoking
        EventHook.safe_trigger under the hood.

        @param event: event to trigger. Any object can be passed
                      as event, but string is preferable. If qcore.EnumBase
                      instance is passed, its name is used as event key.
        @param args: event arguments.
        @return: self, so calls like this can be chained together.

        """
        event_hook = self.get_or_create(event)
        event_hook.safe_trigger(*args)
        return self

    def get_or_create(self, event):
        """Gets or creates a new event hook for the specified event (key).

        This method treats qcore.EnumBase-typed event keys specially:
        enum_member.name is used as key instead of enum instance
        in case such a key is passed.

        Note that on/off/trigger/safe_trigger methods rely on this method,
        so you can pass enum members there as well.

        """
        if isinstance(event, EnumBase):
            event = event.short_name
        return self.__dict__.setdefault(event, EventHook())

    def __getattr__(self, key):
        """Gets or creates a new event hook with the specified name.
        Calls get_or_create under the hood.

        Specified key must start with ``on_`` prefix; this prefix is
        trimmed when key is passed to self.get_or_create.

        """
        if key.startswith("on_"):
            return self.get_or_create(key[3:])
        else:
            raise AttributeError(key)

    def __contains__(self, item):
        """Checks if there is an event hook with the specified name."""
        return item in self.__dict__

    def __len__(self):
        """Gets the count of created event hooks."""
        return len(self.__dict__)

    def __getitem__(self, item):
        """Gets the event hook with the specified name."""
        return self.__dict__[item]

    def __setitem__(self, key, value):
        """Sets the event hook by its name."""
        self.__dict__[key] = value

    def __delitem__(self, key):
        """Removes the event hook with the specified name."""
        del self.__dict__[key]

    def __iter__(self):
        """Iterates over all (name, event_hook) pairs."""
        return iter(self.__dict__.items())

    def __repr__(self):
        """Gets the ``repr`` representation of this object."""
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)

    # Needed bcz of a six bug: https://github.com/benjaminp/six/issues/252
    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        return {}


class EnumBasedEventHubType(type):
    """Metaclass for enum-based event hubs.

    Asserts that all enum members are defined in class and vice versa.

    """

    def __init__(cls, what, bases=None, dict=None):
        super().__init__(what, bases, dict)
        if cls.__name__ == "NewBase" and cls.__module__ == "six" and not dict:
            # some versions of six generate an intermediate class that is created without a
            # __based_on__
            return
        assert dict is not None and "__based_on__" in dict, (
            "__based_on__ = [EnumA, EnumB] class member "
            "must be used to subclass EnumBasedEventHub"
        )
        based_on = cls.__based_on__
        if isinstance(based_on, EnumType):
            based_on = [based_on]

        cls_member_names = set()
        for k, v in inspect.getmembers(cls):
            if not k.startswith("on_"):
                continue
            if not isinstance(v, EventHook):
                continue
            cls_member_names.add(k[3:])

        enum_members = {}
        for enum_type in based_on:
            for member in enum_type.get_members():
                name = member.short_name
                assert (
                    name not in enum_members
                ), "Two enum members share the same name: %r and %r " % (
                    member,
                    enum_members[name],
                )
                enum_members[name] = member
        enum_member_names = set(enum_members.keys())

        for name in enum_member_names:
            assert name in cls_member_names, (
                "Member %r is declared in one of enums, "
                + "but %r is not declared in class."
            ) % (name, "on_" + name)
        for name in cls_member_names:
            assert name in enum_member_names, (
                "Member %r is declared in class, "
                + "but %r is not declared in any of enum(s)."
            ) % ("on_" + name, name)
            # Members are removed from class, since EventHub anyway creates
            # similar instance members
            delattr(cls, "on_" + name)

    # Needed bcz of a six bug: https://github.com/benjaminp/six/issues/252
    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        return {}


class EnumBasedEventHub(EventHub, metaclass=EnumBasedEventHubType):
    __based_on__ = []


hub = EventHub()  # Default global event hub
