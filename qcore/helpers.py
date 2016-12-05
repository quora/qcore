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

Various small helper classes and routines.

"""

import inspect
import six
import warnings

from . import inspectable_class

# export it here for backward compatibility
from .disallow_inheritance import DisallowInheritance


empty_tuple = ()
empty_list = []
empty_dict = {}
globals()['empty_tuple'] = empty_tuple
globals()['empty_list'] = empty_list
globals()['empty_dict'] = empty_dict


def true_fn():
    return True


def false_fn():
    return False


class MarkerObject(object):
    """Replaces None in cases when None value is also expected.
    Used mainly by caches to describe a cache miss.

    """
    def __init__(self, name):
        if isinstance(name, six.binary_type):
            if six.PY2:
                warnings.warnpy3k('MarkerObject does not support bytes names in Python 3')
                name = name.decode('utf-8')
            else:
                raise TypeError("name must be str, not bytes")
        self.name = name

    if six.PY2:
        def __str__(self):
            return unicode(self).encode('utf-8')

        def __unicode__(self):
            return self.name
    else:
        def __str__(self):
            return self.name

    def __repr__(self):
        return self.name

none = MarkerObject(u'none')
miss = MarkerObject(u'miss')
same = MarkerObject(u'same')
unspecified = MarkerObject(u'unspecified')
globals()['none'] = none
globals()['miss'] = miss
globals()['same'] = same
globals()['unspecified'] = unspecified


class EmptyContext(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __repr__(self):
        return 'qcore.empty_context'

empty_context = EmptyContext()
globals()['empty_context'] = empty_context


class CythonCachedHashWrapper(object):
    def __init__(self, value):
        self._value = value
        self._hash = hash(value)

    def value(self):
        return self._value

    def hash(self):
        return self._hash

    def __call__(self):
        return self._value

    def __hash__(self):
        return self._hash

    def __richcmp__(self, other, op):
        # Cython way of implementing comparison operations
        if op == 2:
            return (
                self() == other()
                if isinstance(other, CachedHashWrapper)
                else self() == other)
        elif op == 3:
            return not (
                self() == other()
                if isinstance(other, CachedHashWrapper)
                else self() == other)
        else:
            raise NotImplementedError('only == and != are supported')

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._value)


CachedHashWrapper = CythonCachedHashWrapper
globals()['CachedHashWrapper'] = CythonCachedHashWrapper
if hasattr(CythonCachedHashWrapper, '__richcmp__'):
    # This isn't Cython, so we must add eq and ne to make it work w/o Cython
    class PythonCachedHashWrapper(CachedHashWrapper):
        def __eq__(self, other):
            return (
                self._value == other._value
                if isinstance(other, CachedHashWrapper)
                else self._value == other)

        def __ne__(self, other):
            return not (
                self._value == other._value
                if isinstance(other, CachedHashWrapper)
                else self._value == other)

        # needed in Python 3 because this class overrides __eq__
        def __hash__(self):
            return self._hash

    CachedHashWrapper = PythonCachedHashWrapper
    globals()['CachedHashWrapper'] = PythonCachedHashWrapper


class ScopedValue(object):
    def __init__(self, default):
        self._value = default

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

    def override(self, value):
        """Temporarily overrides the old value with the new one."""
        if self._value is not value:
            return _ScopedValueOverrideContext(self, value)
        else:
            return empty_context

    def __call__(self):
        """Same as get."""
        return self._value

    def __str__(self):
        return 'ScopedValue(%s)' % (self._value,)

    def __repr__(self):
        return 'ScopedValue(%r)' % (self._value,)


class _ScopedValueOverrideContext(object):
    def __init__(self, target, value):
        self._target = target
        self._value = value
        self._old_value = None

    def __enter__(self):
        self._old_value = self._target._value
        self._target._value = self._value

    def __exit__(self, exc_type, exc_value, tb):
        self._target._value = self._old_value


class _PropertyOverrideContext(object):
    def __init__(self, target, property_name, value):
        self._target = target
        self._property_name = property_name
        self._value = value
        self._old_value = None

    def __enter__(self):
        self._old_value = getattr(self._target, self._property_name)
        setattr(self._target, self._property_name, self._value)

    def __exit__(self, exc_type, exc_value, tb):
        setattr(self._target, self._property_name, self._old_value)

override = _PropertyOverrideContext
globals()['override'] = override


def ellipsis(source, max_length):
    """Truncates a string to be at most max_length long."""
    if max_length == 0 or len(source) <= max_length:
        return source
    return source[:max(0, max_length - 3)] + '...'


def safe_str(source, max_length=0):
    """Wrapper for str() that catches exceptions."""
    try:
        return ellipsis(str(source), max_length)
    except Exception as e:
        return ellipsis("<n/a: str(...) raised %s>" % e, max_length)


def safe_repr(source, max_length=0):
    """Wrapper for repr() that catches exceptions."""
    try:
        return ellipsis(repr(source), max_length)
    except Exception as e:
        return ellipsis("<n/a: repr(...) raised %s>" % e, max_length)


def dict_to_object(source):
    """Returns an object with the key-value pairs in source as attributes."""
    target = inspectable_class.InspectableClass()
    for k, v in source.items():
        setattr(target, k, v)
    return target


def copy_public_attrs(source_obj, dest_obj):
    """Shallow copies all public attributes from source_obj to dest_obj.

    Overwrites them if they already exist.

    """
    for name, value in inspect.getmembers(source_obj):
        if not any(name.startswith(x) for x in ['_', 'func', 'im']):
            setattr(dest_obj, name, value)


def object_from_string(st):
    """Creates a Python class or function from its fully qualified name.

    :param st: A fully qualified name of a class or a function.
    :return: A function or class object.

    This method is used by serialization code to create a function or class
    from a fully qualified name.

    """
    pos = st.rfind('.')
    if pos < 0:
        raise ValueError('Invalid function or class name %s' % st)
    module_name = st[:pos]
    func_name = st[pos + 1:]
    mod = __import__(module_name, fromlist=[func_name], level=0)
    return getattr(mod, func_name)


def catchable_exceptions(exceptions):
    """Returns True if exceptions can be caught in the except clause.

    The exception can be caught if it is an Exception type or a tuple of
    exception types.

    """
    if isinstance(exceptions, type) and issubclass(exceptions, BaseException):
        return True

    if (isinstance(exceptions, tuple) and exceptions and
            all(issubclass(it, BaseException) for it in exceptions)):
        return True

    return False
