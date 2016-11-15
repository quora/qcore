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

Base classes and helpers for decorators.

"""

__all__ = [
    'DecoratorBinder',
    'DecoratorBase',
    'decorate',
    'deprecated',
    'convert_result',
    'retry',
    'decorator_of_context_manager',
]

# make sure qcore is still importable if this module has not been compiled with Cython and Cython
# is not installed
try:
    from cython import compiled
except ImportError:
    compiled = False

import functools
import inspect
from six.moves import xrange
import sys
import time

from . import inspection


class DecoratorBinder(object):
    def __init__(self, decorator, instance=None):
        self.decorator = decorator
        self.instance = instance

    def name(self):
        return self.decorator.name()

    def is_decorator(self):
        return True

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            return self.decorator(*args, **kwargs)
        else:
            return self.decorator(self.instance, *args, **kwargs)

    def __str__(self):
        if self.instance is None:
            return '<%s unbound>' % str(self.decorator)
        else:
            return '<%s bound to %s>' % (str(self.decorator), str(self.instance))

    def __repr__(self):
        return self.__str__()

    # This awkward implementation is necessary so that binders can be compared for equality across
    # Cythonized and non-Cythonized Python 2 and 3. In pure-Python compiled classes, Cython only
    # supports overriding __richcmp__, not __eq__ (https://github.com/cython/cython/issues/690),
    # but if __eq__ is defined it throws an error.
    if compiled:
        def __richcmp__(self, other, op):
            """Compare objects for equality (so we can run tests that do an equality check)."""
            if op in (2, 3): # ==, !=
                if self.__class__ is other.__class__ and self.decorator == other.decorator and \
                        self.instance == other.instance:
                    equal = True
                else:
                    equal = False
                return equal if op == 2 else not equal
            else:
                return NotImplemented

    def __hash__(self):
        return hash(self.decorator) ^ hash(self.instance)


if not compiled:
    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.decorator == other.decorator and \
            self.instance == other.instance
    DecoratorBinder.__eq__ = __eq__
    del __eq__


class DecoratorBase(object):
    binder_cls = DecoratorBinder

    def __init__(self, fn):
        if hasattr(fn, '__func__'):  # Class method, static method
            self.type = type(fn)
            fn = fn.__func__
        elif hasattr(fn, 'is_decorator'):  # Decorator
            self.type = fn.type
        else:
            self.type = None
        self.fn = fn
        _update_wrapper(self, fn)

    def name(self):
        raise NotImplementedError()

    def is_decorator(self):
        return True

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()

    def __get__(self, owner, cls):
        if self.type is staticmethod:
            return self
        # unbound method being acccessed directly on the class
        if owner is None and self.type is not classmethod:
            return self.binder_cls(self)
        return self.binder_cls(self, cls if self.type is classmethod else owner)

    def __str__(self):
        return self.name() + ' ' + inspection.get_full_name(self.fn)

    def __repr__(self):
        return self.__str__()

    def __reduce__(self):
        # For pickling. We assume that the decorated function is available in its module's global
        # scope. Alternatively, we could supply type(self) and the decorator class's __init__
        # arguments, but that runs into "it's not the same object" errors from Pickle.
        return (_reduce_impl, (self.__module__, self.__name__,))


# We use wrappers of Cython extension classes here to enable
# Python features like adding new properties for decorators.
_wrappers = {}


def decorate(decorator_cls, *args, **kwargs):
    """Creates a decorator function that applies the decorator_cls that was passed in."""
    global _wrappers

    wrapper_cls = _wrappers.get(decorator_cls, None)
    if wrapper_cls is None:
        class PythonWrapper(decorator_cls):
            pass

        wrapper_cls = PythonWrapper
        wrapper_cls.__name__ = decorator_cls.__name__ + 'PythonWrapper'
        _wrappers[decorator_cls] = wrapper_cls

    def decorator(fn):
        wrapped = wrapper_cls(fn, *args, **kwargs)
        _update_wrapper(wrapped, fn)
        return wrapped

    return decorator


def deprecated(replacement_description):
    """States that method is deprecated.

    :param replacement_description: Describes what must be used instead.
    :return: the original method with modified docstring.

    """
    def decorate(fn_or_class):
        if isinstance(fn_or_class, type):
            pass  # Can't change __doc__ of type objects
        else:
            try:
                fn_or_class.__doc__ = 'This API point is obsolete. %s\n\n%s' % (
                    replacement_description,
                    fn_or_class.__doc__,
                )
            except AttributeError:
                pass  # For Cython method descriptors, etc.
        return fn_or_class
    return decorate


def convert_result(converter):
    """Decorator that can convert the result of a function call."""
    def decorate(fn):
        @inspection.wraps(fn)
        def new_fn(*args, **kwargs):
            return converter(fn(*args, **kwargs))
        return new_fn
    return decorate


def retry(exception_cls, max_tries=10, sleep=0.05):
    """Decorator for retrying a function if it throws an exception.

    :param exception_cls: an exception type or a parenthesized tuple of exception types
    :param max_tries: maximum number of times this function can be executed. Must be at least 1.
    :param sleep: number of seconds to sleep between function retries

    """

    assert max_tries > 0

    def with_max_retries_call(delegate):
        for i in xrange(0, max_tries):
            try:
                return delegate()
            except exception_cls:
                if i + 1 == max_tries:
                    raise
                time.sleep(sleep)

    def outer(fn):
        is_generator = inspect.isgeneratorfunction(fn)

        @functools.wraps(fn)
        def retry_fun(*args, **kwargs):
            return with_max_retries_call(lambda: fn(*args, **kwargs))

        @functools.wraps(fn)
        def retry_generator_fun(*args, **kwargs):
            def get_first_item():
                results = fn(*args, **kwargs)
                for first_result in results:
                    return [first_result], results
                return [], results

            cache, generator = with_max_retries_call(get_first_item)

            for item in cache:
                yield item

            for item in generator:
                yield item

        if not is_generator:
            # so that qcore.inspection.get_original_fn can retrieve the original function
            retry_fun.fn = fn
            return retry_fun
        else:
            retry_generator_fun.fn = fn
            return retry_generator_fun
    return outer


def decorator_of_context_manager(ctxt):
    """Converts a context manager into a decorator.

    This decorator will run the decorated function in the context of the
    manager.

    :param ctxt: Context to run the function in.
    :return: Wrapper around the original function.

    """
    def decorator_fn(*outer_args, **outer_kwargs):
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                with ctxt(*outer_args, **outer_kwargs):
                    return fn(*args, **kwargs)
            return wrapper
        return decorator

    if getattr(ctxt, '__doc__', None) is None:
        msg = 'Decorator that runs the inner function in the context of %s'
        decorator_fn.__doc__ = msg % ctxt
    else:
        decorator_fn.__doc__ = ctxt.__doc__
    return decorator_fn


def _update_wrapper(wrapper, wrapped):
    if hasattr(wrapped, '__module__'):
        wrapper.__module__ = wrapped.__module__
    if hasattr(wrapped, '__name__'):
        wrapper.__name__ = wrapped.__name__
    if hasattr(wrapped, '__doc__'):
        wrapper.__doc__ = wrapped.__doc__


def _reduce_impl(module, name):
    try:
        module = sys.modules[module]
        return getattr(module, name)
    except (KeyError, AttributeError):
        raise TypeError(
            'Cannot pickle decorated function %s.%s, failed to find it' % (module, name))
