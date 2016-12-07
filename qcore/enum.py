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

from __future__ import unicode_literals
__doc__ = """

Enum implementation.

"""

__all__ = ['Enum', 'EnumType', 'EnumValueGenerator', 'Flags', 'IntEnum']

import inspect
import six
import sys

from . import helpers
from . import inspection

_no_default = helpers.MarkerObject(u'no_default @ enums')


class EnumType(type):
    """Metaclass for all enum types."""

    def __init__(cls, what, bases=None, dict=None):
        super(EnumType, cls).__init__(what, bases, dict)
        cls.process()

    def __contains__(self, k):
        return k in self._value_to_name

    def __len__(self):
        return len(self._members)

    def __iter__(self):
        return iter(self._members)

    def __call__(self, value, default=_no_default):
        """Instantiating an Enum always produces an existing value or throws an exception."""
        return self.parse(value, default=default)

    def process(self):
        name_to_member = {}
        value_to_member = {}
        value_to_name = {}
        flag_values = []
        members = []
        for k, v in list(inspect.getmembers(self)):
            # ensure that names are unicode, even in py2
            if isinstance(k, bytes):
                k = k.decode('ascii')
            if isinstance(type(v), EnumType):
                v = v.value  # For inherited members
            if isinstance(v, six.integer_types):
                assert v not in value_to_member, \
                    'Duplicate enum value: %s (class: %s).' % \
                    (v, inspection.get_full_name(self))
                member = self._make_value(v)

                name_to_member[k] = member
                value_to_member[v] = member
                value_to_name[v] = k
                if v != 0:
                    flag_values.append(v)

                members.append(member)
        self._name_to_member = name_to_member
        self._value_to_member = value_to_member
        self._value_to_name = value_to_name
        self._flag_values = list(reversed(sorted(flag_values)))
        self._members = sorted(members, key=lambda m: m.value)
        for m in members:
            setattr(self, m.short_name, m)

    def _make_value(self, value):
        """Instantiates an enum with an arbitrary value."""
        member = self.__new__(self, value)
        member.__init__(value)
        return member


class EnumBase(six.with_metaclass(EnumType)):
    _name_to_member = {}
    _value_to_member = {}
    _value_to_name = {}
    _flag_values = []
    _members = []

    def __init__(self, value):
        self.value = int(value)

    @property
    def short_name(self):
        """Returns the enum member's name, like "foo"."""
        raise NotImplementedError

    @property
    def long_name(self):
        """Returns the enum member's name including the class name, like "MyEnum.foo"."""
        return '%s.%s' % (self.__class__.__name__, self.short_name)

    @property
    def title(self):
        """Returns the enum member's name in title case, like "FooBar" for MyEnum.foo_bar."""
        return self.short_name.replace('_', ' ').title()

    @property
    def full_name(self):
        """Returns the enum meber's name including the module, like "mymodule.MyEnum.foo"."""
        return '%s.%s' % (self.__class__.__module__, self.long_name)

    def is_valid(self):
        raise NotImplementedError

    def assert_valid(self):
        if not self.is_valid():
            raise _create_invalid_value_error(self.__class__, self.value)

    def __int__(self):
        return self.value

    def __call__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        if self.is_valid():
            return self.short_name
        else:
            return '%s(%s)' % (self.__class__.__name__, self.value)

    def __repr__(self):
        if self.is_valid():
            return self.__class__.__name__ + '.' + self.short_name
        else:
            return '%s(%s)' % (self.__class__.__name__, self.value)

    @classmethod
    def get_names(cls):
        """Returns the names of all members of this enum."""
        return [m.short_name for m in cls._members]

    @classmethod
    def get_members(cls):
        return cls._members

    @classmethod
    def create(cls, name, members):
        """Creates a new enum type based on this one (cls) and adds newly
        passed members to the newly created subclass of cls.

        This method helps to create enums having the same member values as
        values of other enum(s).

        :param name: name of the newly created type
        :param members: 1) a dict or 2) a list of (name, value) tuples
                        and/or EnumBase instances describing new members
        :return: newly created enum type.

        """
        NewEnum = type(name, (cls,), {})

        if isinstance(members, dict):
            members = members.items()
        for member in members:
            if isinstance(member, tuple):
                name, value = member
                setattr(NewEnum, name, value)
            elif isinstance(member, EnumBase):
                setattr(NewEnum, member.short_name, member.value)
            else:
                assert False, (
                    "members must be either a dict, " +
                    "a list of (name, value) tuples, " +
                    "or a list of EnumBase instances.")

        NewEnum.process()

        # needed for pickling to work (hopefully); taken from the namedtuple implementation in the
        # standard library
        try:
            NewEnum.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass

        return NewEnum

    @classmethod
    def parse(cls, value, default=_no_default):
        """Parses a value into a member of this enum."""
        raise NotImplementedError


class Enum(EnumBase):
    def is_valid(self):
        return self.value in self._value_to_member

    @property
    def short_name(self):
        self.assert_valid()
        return self._value_to_name[self.value]

    @classmethod
    def parse(cls, value, default=_no_default):
        """Parses an enum member name or value into an enum member.

        Accepts the following types:
        - Members of this enum class. These are returned directly.
        - Integers. If there is an enum member with the integer as a value, that member is returned.
        - Strings. If there is an enum member with the string as its name, that member is returned.
        For integers and strings that don't correspond to an enum member, default is returned; if
        no default is given the function raises KeyError instead.

        Examples:

        >>> class Color(Enum):
        ...     red = 1
        ...     blue = 2
        >>> Color.parse(Color.red)
        Color.red
        >>> Color.parse(1)
        Color.red
        >>> Color.parse('blue')
        Color.blue

        """
        if isinstance(value, cls):
            return value
        elif isinstance(value, six.integer_types) and not isinstance(value, EnumBase):
            e = cls._value_to_member.get(value, _no_default)
        else:
            e = cls._name_to_member.get(value, _no_default)
        if e is _no_default or not e.is_valid():
            if default is _no_default:
                raise _create_invalid_value_error(cls, value)
            return default
        return e


class Flags(EnumBase):
    def is_valid(self):
        value = self.value
        for v in self._flag_values:
            if (v | value) == value:
                value ^= v
        return value == 0

    @property
    def short_name(self):
        self.assert_valid()
        result = []
        l = self.value
        for v in self._flag_values:
            if (v | l) == l:
                l ^= v
                result.append(self._value_to_name[v])
        if not result:
            if 0 in self._value_to_name:
                return self._value_to_name[0]
            else:
                return ''
        return ','.join(result)

    @classmethod
    def parse(cls, value, default=_no_default):
        """Parses a flag integer or string into a Flags instance.

        Accepts the following types:
        - Members of this enum class. These are returned directly.
        - Integers. These are converted directly into a Flags instance with the given name.
        - Strings. The function accepts a comma-delimited list of flag names, corresponding to
          members of the enum. These are all ORed together.

        Examples:

        >>> class Car(Flags):
        ...     is_big = 1
        ...     has_wheels = 2
        >>> Car.parse(1)
        Car.is_big
        >>> Car.parse(3)
        Car.parse('has_wheels,is_big')
        >>> Car.parse('is_big,has_wheels')
        Car.parse('has_wheels,is_big')

        """
        if isinstance(value, cls):
            return value
        elif isinstance(value, int):
            e = cls._make_value(value)
        else:
            if not value:
                e = cls._make_value(0)
            else:
                r = 0
                for k in value.split(','):
                    v = cls._name_to_member.get(k, _no_default)
                    if v is _no_default:
                        if default is _no_default:
                            raise _create_invalid_value_error(cls, value)
                        else:
                            return default
                    r |= v.value
                e = cls._make_value(r)
        if not e.is_valid():
            if default is _no_default:
                raise _create_invalid_value_error(cls, value)
            return default
        return e

    def __contains__(self, item):
        item = int(item)
        if item == 0:
            return True
        return item == (self.value & item)

    def __or__(self, other):
        return self.__class__(self.value | int(other))

    def __and__(self, other):
        return self.__class__(self.value & int(other))

    def __xor__(self, other):
        return self.__class__(self.value ^ int(other))

    def __repr__(self):
        if self.is_valid():
            name = self.short_name
            if ',' in name:
                return "%s.parse('%s')" % (self.__class__.__name__, self.short_name)
            else:
                return self.__class__.__name__ + '.' + self.short_name
        else:
            return '%s(%s)' % (self.__class__.__name__, self.value)


class IntEnum(int, Enum):
    """Enum subclass that offers more compatibility with int."""

    def __repr__(self):
        return Enum.__repr__(self)


class EnumValueGenerator(object):
    def __init__(self, start=1):
        self._next_value = start

    def reset(self, start=1):
        self._next_value = start

    def next(self):
        result = self._next_value
        self._next_value += 1
        return result

    def __call__(self):
        return self.next()

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._next_value)


# Private part

def _create_invalid_value_error(cls, value):
    return KeyError(
        "Invalid %s value: %r" % (inspection.get_full_name(cls), value))
