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

Code inspection helpers.

"""

import functools
import inspect
import six
import sys


def get_original_fn(fn):
    """Gets the very original function of a decorated one."""

    fn_type = type(fn)
    if fn_type is classmethod or fn_type is staticmethod:
        return get_original_fn(fn.__func__)
    if hasattr(fn, 'original_fn'):
        return fn.original_fn
    if hasattr(fn, 'fn'):
        fn.original_fn = get_original_fn(fn.fn)
        return fn.original_fn
    return fn


def get_full_name(src):
    """Gets full class or function name."""

    if hasattr(src, '_full_name_'):
        return src._full_name_
    if hasattr(src, 'is_decorator'):
        # Our own decorator or binder
        if hasattr(src, 'decorator'):
            # Our own binder
            _full_name_ = str(src.decorator)
            # It's a short-living object, so we don't cache result
        else:
            # Our own decorator
            _full_name_ = str(src)
            try:
                src._full_name_ = _full_name_
            except AttributeError:
                pass
            except TypeError:
                pass
    elif hasattr(src, 'im_class'):
        # Bound method
        cls = src.im_class
        _full_name_ = get_full_name(cls) + '.' + src.__name__
        # It's a short-living object, so we don't cache result
    elif hasattr(src, '__module__') and hasattr(src, '__name__'):
        # Func or class
        _full_name_ = ('<unknown module>' if src.__module__ is None else src.__module__) + \
            '.' + src.__name__
        try:
            src._full_name_ = _full_name_
        except AttributeError:
            pass
        except TypeError:
            pass
    else:
        # Something else
        _full_name_ = str(get_original_fn(src))
    return _full_name_


def get_function_call_str(fn, args, kwargs):
    """Converts method call (function and its arguments) to a str(...)-like string."""

    def str_converter(v):
        try:
            return str(v)
        except Exception:
            try:
                return repr(v)
            except Exception:
                return '<n/a str raised>'

    result = get_full_name(fn) + '('
    first = True
    for v in args:
        if first:
            first = False
        else:
            result += ','
        result += str_converter(v)
    for k, v in kwargs.items():
        if first:
            first = False
        else:
            result += ','
        result += str(k) + '=' + str_converter(v)
    result += ")"
    return result


def get_function_call_repr(fn, args, kwargs):
    """Converts method call (function and its arguments) to a repr(...)-like string."""

    result = get_full_name(fn) + '('
    first = True
    for v in args:
        if first:
            first = False
        else:
            result += ','
        result += repr(v)
    for k, v in kwargs.items():
        if first:
            first = False
        else:
            result += ','
        result += str(k) + '=' + repr(v)
    result += ")"
    return result


def getargspec(func):
    """Variation of inspect.getargspec that works for more functions.

    This function works for Cythonized, non-cpdef functions, which expose argspec information but
    are not accepted by getargspec. It also works for Python 3 functions that use annotations, which
    are simply ignoered. However, keyword-only arguments are not supported.

    """
    if inspect.ismethod(func):
        func = func.__func__
    # Cythonized functions have a .__code__, but don't pass inspect.isfunction()
    try:
        code = func.__code__
    except AttributeError:
        raise TypeError('{!r} is not a Python function'.format(func))
    if hasattr(code, 'co_kwonlyargcount') and code.co_kwonlyargcount > 0:
        raise ValueError('keyword-only arguments are not supported by getargspec()')
    args, varargs, varkw = inspect.getargs(code)
    return inspect.ArgSpec(args, varargs, varkw, func.__defaults__)


def is_cython_or_generator(fn):
    """Returns whether this function is either a generator function or a Cythonized function."""
    if hasattr(fn, '__func__'):
        fn = fn.__func__  # Class method, static method
    if inspect.isgeneratorfunction(fn):
        return True
    name = type(fn).__name__
    return \
        name == 'generator' or \
        name == 'method_descriptor' or \
        name == 'cython_function_or_method' or \
        name == 'builtin_function_or_method'


def is_cython_function(fn):
    """Checks if a function is compiled w/Cython."""
    if hasattr(fn, '__func__'):
        fn = fn.__func__  # Class method, static method
    name = type(fn).__name__
    return \
        name == 'method_descriptor' or \
        name == 'cython_function_or_method' or \
        name == 'builtin_function_or_method'


def is_cython_class(cls):
    """Returns whether a class is a Cython extension class."""
    return '__pyx_vtable__' in cls.__dict__


def is_classmethod(fn):
    """Returns whether f is a classmethod."""
    # This is True for bound methods
    if not inspect.ismethod(fn):
        return False
    if not hasattr(fn, '__self__'):
        return False
    im_self = fn.__self__
    # This is None for instance methods on classes, but True
    # for instance methods on instances.
    if im_self is None:
        return False
    # This is True for class methods of new- and old-style classes, respectively
    return isinstance(im_self, six.class_types)


def wraps(
        wrapped,
        assigned=functools.WRAPPER_ASSIGNMENTS,
        updated=functools.WRAPPER_UPDATES):
    """Cython-compatible functools.wraps implementation."""
    if not is_cython_function(wrapped):
        return functools.wraps(wrapped, assigned, updated)
    else:
        return lambda wrapper: wrapper


def get_subclass_tree(cls, ensure_unique=True):
    """Returns all subclasses (direct and recursive) of cls."""
    subclasses = []
    # cls.__subclasses__() fails on classes inheriting from type
    for subcls in type.__subclasses__(cls):
        subclasses.append(subcls)
        subclasses.extend(get_subclass_tree(subcls, ensure_unique))
    return list(set(subclasses)) if ensure_unique else subclasses


def lazy_stack():
    """Return a generator of records for the stack above the caller's frame.

    Equivalent to inspect.stack() but potentially faster because it does not compute info for all
    stack frames.

    As a further optimization, yields raw frame objects instead of tuples describing the frame. To
    get the full information, call inspect.getframeinfo(frame).

    """
    frame = sys._getframe(1)

    while frame:
        yield frame
        frame = frame.f_back
