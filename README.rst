*****
qcore
*****

``qcore`` is a library of common utility functions used at Quora. It is used to
abstract out common functionality for other Quora libraries like `asynq <https://github.com/quora/asynq>`_.

Its component modules are discussed below. See the docstrings in the code
itself for more detail.

qcore.asserts
-------------

When a normal Python assert fails, it only indicates that there was a failure,
not what the bad values were that caused the assert to fail. This module
provides rich assertion helpers that automatically produce better error
messages. For example:

.. code-block:: python

    >>> from qcore.asserts import assert_eq
    >>> assert 5 == 2 * 2
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AssertionError
    >>> assert_eq(5, 2 * 2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "qcore/asserts.py", line 82, in assert_eq
        assert expected == actual, _assert_fail_message(message, expected, actual, '!=', extra)
    AssertionError: 5 != 4

Similar methods are provided by the standard library's ``unittest`` package,
but those are tied to the ``TestCase`` class instead of being standalone
functions.

qcore.caching
-------------

This provides helpers for caching data. Some examples include:

.. code-block:: python

    from qcore.caching import cached_per_instance, lazy_constant

    @lazy_constant
    def some_function():
        # this will only be executed the first time some_function() is called;
        # afterwards it will be cached
        return expensive_computation()

    class SomeClass:
        @cached_per_instance()
        def some_method(self, a, b):
            # for any instance of SomeClass, this will only be executed once
            return expensive_computation(a, b)

qcore.debug
-----------

This module provides some helpers useful for debugging Python. Among others, it
includes the ``@qcore.debug.trace()`` decorator, which can be used to trace
every time a function is called.

qcore.decorators
----------------

This module provides an abstraction for class-based decorators that supports
transparently decorating functions, methods, classmethods, and staticmethods
while also providing the option to add additional custom attributes. For
example, it could be used to provide a caching decorator that adds a ``.dirty``
attribute to decorated functions to dirty their cache:

.. code-block:: python

    from qcore.decorators import DecoratorBase, DecoratorBinder, decorate

    class CacheDecoratorBinder(DecoratorBinder):
        def dirty(self, *args):
            if self.instance is None:
                return self.decorator.dirty(*args)
            else:
                return self.decorator.dirty(self.instance, *args)

    class CacheDecorator(DecoratorBase):
        binder_cls = CacheDecoratorBinder

        def __init__(self, *args):
            super().__init__(*args)
            self._cache = {}

        def dirty(self, *args):
            try:
                del self._cache[args]
            except KeyError:
                pass

        def __call__(self, *args):
            try:
                return self._cache[args]
            except KeyError:
                value = self.fn(*args)
                self._cache[args] = value
                return value

    cached = decorate(CacheDecorator)

qcore.enum
----------

This module provides an abstraction for defining enums. You can define an enum
as follows:

.. code-block:: python

    from qcore.enum import Enum

    class Color(Enum):
        red = 1
        green = 2
        blue = 3

qcore.errors
------------

This module provides some commonly useful exception classes and helpers for
reraising exceptions from a different place.

qcore.events
------------

This provides an abstraction for registering events and running callbacks.
Example usage:

.. code-block:: python

    >>> from qcore.events import EventHook
    >>> event = EventHook()
    >>> def callback():
    ...     print('callback called')
    ...
    >>> event.subscribe(callback)
    >>> event.trigger()
    callback called

qcore.helpers
-------------

This provides a number of small helper functions.

qcore.inspectable_class
-----------------------

This provides a base class that automatically provides hashing, equality
checks, and a readable ``repr()`` result. Example usage:

.. code-block:: python

    >>> from qcore.inspectable_class import InspectableClass
    >>> class Pair(InspectableClass):
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    ...
    >>> Pair(1, 2)
    Pair(a=1, b=2)
    >>> Pair(1, 2) == Pair(1, 2)
    True

qcore.inspection
----------------

This provides functionality similar to the standard ``inspect`` module. Among
others, it includes the ``get_original_fn`` function, which extracts the
underlying function from a ``qcore.decorators``-decorated object.

qcore.microtime
---------------

This includes helpers for dealing with time, represented as an integer number
of microseconds since the Unix epoch.

qcore.testing
-------------

This provides helpers to use in unit tests. Among others, it provides an
``Anything`` object that compares equal to any other Python object.
