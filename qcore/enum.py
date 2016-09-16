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

Enum implementation.

"""

__all__ = ['Enum', 'EnumType', 'EnumValueGenerator', 'Flags']

import inspect
import six

from . import helpers
from . import inspection

_no_default = helpers.MarkerObject('no_default @ enums')


class EnumType(type):
    """Metaclass for all enum types."""

    def __init__(cls, what, bases=None, dict=None):
        super(EnumType, cls).__init__(what, bases, dict)
        EnumType.process(cls)

    @staticmethod
    def process(cls):
        name_to_value = {}
        value_to_name = {}
        flag_values = []
        members = []
        for k, v in list(inspect.getmembers(cls)):
            if isinstance(type(v), EnumType):
                v = v.value  # For inherited members
            if isinstance(v, int):
                assert v not in value_to_name, \
                    'Duplicate enum value: %s (class: %s).' % \
                    (v, inspection.get_full_name(cls))
                name_to_value[k] = v
                value_to_name[v] = k
                if v != 0:
                    flag_values.append(v)
                members.append(cls(v))
        cls._name_to_value = name_to_value
        cls._value_to_name = value_to_name
        cls._flag_values = list(reversed(sorted(flag_values)))
        cls._members = members
        for m in members:
            setattr(cls, value_to_name[m.value], m)


class EnumBase(six.with_metaclass(EnumType)):
    _name_to_value = {}
    _value_to_name = {}
    _flag_values = []
    _members = []

    def __init__(self, value):
        self.value = int(value)

    @property
    def short_name(self):
        """Returns the enum member's name, like "foo"."""
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        class NewEnum(cls):
            pass

        NewEnum.__name__ = name
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

        EnumType.process(NewEnum)
        return NewEnum


class Enum(EnumBase):
    def is_valid(self):
        return self.value in self._value_to_name

    @property
    def short_name(self):
        self.assert_valid()
        return self._value_to_name[self.value]

    @classmethod
    def parse(cls, value, default=_no_default):
        if isinstance(value, cls):
            return value
        elif isinstance(value, six.integer_types):
            e = cls(value)
        else:
            e = cls._name_to_value.get(value, _no_default)
            if e is _no_default:
                if default is _no_default:
                    raise _create_invalid_value_error(cls, value)
                return default
            else:
                e = cls(e)
        if not e.is_valid():
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
        if isinstance(value, int):
            e = cls(value)
        else:
            if not value:
                e = cls(0)
            else:
                r = 0
                for k in value.split(','):
                    v = cls._name_to_value.get(k, _no_default)
                    if v is _no_default:
                        if default is _no_default:
                            raise _create_invalid_value_error(cls, value)
                        else:
                            return default
                    r |= v
                e = cls(r)
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
                return '%s.parse(%r)' % (self.__class__.__name__, self.short_name)
            else:
                return self.__class__.__name__ + '.' + self.short_name
        else:
            return '%s(%s)' % (self.__class__.__name__, self.value)


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
        "Invalid %s value: %s" % (inspection.get_full_name(cls), value))
