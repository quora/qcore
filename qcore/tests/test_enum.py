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

import json
from qcore.enum import Enum, Flags, IntEnum, EnumValueGenerator
from qcore.asserts import (
    assert_eq, assert_is, assert_ne, assert_raises, assert_in, assert_not_in,
    assert_is_instance
)


class Gender(Enum):
    undefined = 0
    male = 1
    female = 2

    @property
    def opposite(self):
        assert self.is_valid()
        if self.value == 0:
            return Gender.undefined
        return Gender(3 - self.value)


def _assert_equality_both_directions(left, right, not_equal):
    assert_eq(left, right)
    assert_eq(right, left)
    assert_ne(not_equal, right)
    assert_ne(right, not_equal)


def test_gender():
    assert_eq([2, 1], Gender._flag_values)
    assert_eq(3, len(Gender.get_members()))

    _assert_equality_both_directions(0, Gender.undefined, 1)
    _assert_equality_both_directions(1, Gender.male, 2)
    _assert_equality_both_directions(2, Gender.female, 3)

    _assert_equality_both_directions(
        Gender.undefined, Gender.parse('undefined'), Gender.male)
    _assert_equality_both_directions(
        Gender.male, Gender.parse('male'), Gender.female)
    _assert_equality_both_directions(
        Gender.female, Gender.parse('female'), Gender.male)

    _assert_equality_both_directions(
        Gender.undefined, Gender.parse(Gender.undefined), Gender.male)
    _assert_equality_both_directions(
        Gender.male, Gender.parse(Gender.male), Gender.female)
    _assert_equality_both_directions(
        Gender.female, Gender.parse(Gender.female), Gender.male)

    assert_is(None, Gender.parse('na', None))
    assert_raises(lambda: Gender.parse('na'), KeyError)

    assert_eq('undefined', Gender(0).short_name)
    assert_eq('male', Gender(1).short_name)
    assert_eq('female', Gender(2).short_name)

    assert_eq('Gender.female', Gender.female.long_name)
    assert_eq('Female', Gender.female.title)
    assert_eq('test_enum.Gender.female', Gender.female.full_name)

    assert_is(None, Gender.parse('', None))
    assert_is(None, Gender.parse(4, None))
    assert_raises(lambda: Gender.parse(''), KeyError)
    assert_raises(lambda: Gender.parse(4), KeyError)

    assert_eq(str(Gender.male), 'male')
    assert_eq(repr(Gender.male), 'Gender.male')
    assert_eq(str(Gender(5)), 'Gender(5)')
    assert_eq(repr(Gender(5)), 'Gender(5)')


def test_property():
    assert_eq(Gender.undefined.opposite, Gender.undefined)
    assert_eq(Gender.male.opposite, Gender.female)
    assert_eq(Gender.female.opposite, Gender.male)


def test_create():
    def test_exact_gender(cls):
        assert_eq(len(cls.get_members()), 2)
        assert_eq(cls.male, 1)
        assert_eq(cls.female, 2)
        assert_eq(cls.male, Gender.male)
        assert_eq(cls.female, Gender.female)

    class ExactGender(Enum):
        male = Gender.male
        female = Gender.female
    test_exact_gender(ExactGender)

    cls = Enum.create("ExactGender", [
        Gender.male,
        Gender.female,
    ])
    test_exact_gender(cls)

    cls = Enum.create("ExactGender", {
        "male": 1,
        "female": 2,
    })
    test_exact_gender(cls)

    cls = Enum.create("ExactGender", [
        ("male", 1),
        ("female", 2),
    ])
    test_exact_gender(cls)


class Xy(Flags):
    x = 1
    y = 4
    xy = 5


class Xyz(Xy):
    z = 8


class Xyzna(Xyz):
    na = 0


def test_xyz():
    assert_eq([8, 5, 4, 1], Xyz._flag_values)
    assert_eq(3, len(Xy.get_members()))
    assert_eq(4, len(Xyz.get_members()))
    assert_eq(5, len(Xyzna.get_members()))
    assert_eq('[Xyzna.na, Xyzna.x, Xyzna.xy, Xyzna.y, Xyzna.z]',
              str(Xyzna.get_members()))

    assert_eq(0, Xyz.parse(''))
    assert_eq(0, Xyz.parse(0))
    assert_eq(0, Xyzna.parse('na'))
    assert_is(None, Xyz.parse('na', None))

    assert_raises(lambda: Xyz.parse('_'), KeyError)
    assert_raises(lambda: Xyz.parse('x,_'), KeyError)

    assert_eq(4, Xyz.parse('y'))
    assert_eq(4, Xyz.parse(4))

    assert_eq(5, Xyz.parse('xy'))
    assert_eq(5, Xyz.parse('x,y'))

    assert_eq('x', Xyz(1).short_name)
    assert_eq('y', Xyz(4).short_name)
    assert_eq('xy', Xyz(5).short_name)
    assert_eq('z,xy', Xyz(8 | 5).short_name)
    assert_eq('', Xyz(0).short_name)
    assert_eq('na', Xyzna(0).short_name)

    assert_is(None, Xyz.parse(100, None))
    assert_raises(lambda: Xyz.parse(100), KeyError)

    assert_eq('z', str(Xyz.z))
    assert_eq('Xyz.z', repr(Xyz.z))
    assert_eq('xy', str(Xyz.xy))
    assert_eq('Xyz.xy', repr(Xyz.xy))
    assert_eq('z,x', str(Xyz.x | Xyz.z))
    assert_eq("Xyz.parse('z,x')", repr(Xyz.x | Xyz.z))
    assert_eq('Xyz(100)', str(Xyz(100)))
    assert_eq('Xyz(100)', repr(Xyz(100)))


def test_instances():
    assert_eq(0, Gender.undefined)
    assert_eq(1, Gender.male)
    assert_eq(2, Gender.female)

    assert_eq(0, Gender.undefined())
    assert_eq(1, Gender.male())
    assert_eq(2, Gender.female())

    assert_eq(0, Gender.undefined.value)
    assert_eq(1, Gender.male.value)
    assert_eq(2, Gender.female.value)

    assert_eq(Gender(0), Gender.undefined)
    assert_eq(Gender(1), Gender.male)
    assert_eq(Gender(2), Gender.female)
    assert_ne(Gender(3), Gender.female)

    assert Gender(0).is_valid()
    assert not Gender(3).is_valid()

    g0 = Gender.parse(0)
    assert isinstance(g0, Gender)
    assert_eq(0, g0.value)
    g1 = Gender.parse(1)
    assert isinstance(g1, Gender)
    assert_eq(1, g1.value)
    assert_is(None, Gender.parse(4, None))
    assert_raises(lambda: Gender.parse(4), KeyError)
    assert_eq(hash(2), hash(Gender(2)))

    assert_eq('xy', str(Xyz.xy))
    assert_eq('Xyz.xy', repr(Xyz.xy))
    assert_eq('Xyz(1000)', str(Xyz(1000)))
    assert_eq('Xyz(1000)', repr(Xyz(1000)))

    assert_eq(Xyz.xy, Xyz.x | Xyz.y)
    assert_eq(5, Xyz.x | Xyz.y)
    assert_eq(5, Xyz.x | 4)
    assert_eq(5, Xyz.x | Xyz.y)

    assert_eq(Xyz.xy, Xyz.x | Xyz.y)
    assert_eq(8 | 5, Xyz.z | Xyz.xy)

    assert_eq(Xyzna.na, Xyz.x & Xyz.y)

    assert_in(Xyz.x, Xyz.xy)
    assert_in(Xyz.y, Xyz.xy)
    assert_in(Xyz.xy, Xyz.xy)
    assert_not_in(Xyz.z, Xyz.xy)
    assert_not_in(Xyz.z, Xyz.x)
    assert_not_in(Xyz.z, Xyz.y)

    assert_in(Xyz.x(), Xyz.xy)
    assert_in(Xyz.y(), Xyz.xy)
    assert_in(Xyz.xy(), Xyz.xy)
    assert_not_in(Xyz.z(), Xyz.xy)
    assert_not_in(Xyz.z(), Xyz.x)
    assert_not_in(Xyz.z(), Xyz.y)

    assert_in(Xyzna.na, Xyzna.x)
    assert_in(Xyzna.na, Xyzna.y)
    assert_in(Xyzna.na, Xyzna.xy)
    assert_in(Xyzna.na, Xyzna.z)
    assert_in(Xyzna.na, Xyzna.na)

    xyz1 = Xyz.parse('z,xy')
    xyz2 = Xyz.parse('x,y,z')
    xyz3 = Xyz.parse('xy,z')
    xyz4 = Xyz.parse(8 | 5)
    assert isinstance(xyz1, Xyz)
    assert isinstance(xyz2, Xyz)
    assert isinstance(xyz3, Xyz)
    assert isinstance(xyz4, Xyz)
    assert_eq(8 | 5, xyz1.value)
    assert_eq(8 | 5, xyz2.value)
    assert_eq(8 | 5, xyz3.value)
    assert_eq(8 | 5, xyz4.value)
    assert_is(None, Xyz.parse(100, None))
    assert_raises(lambda: Xyz.parse(100), KeyError)

    na1 = Xyz.parse('')
    na2 = Xyzna.parse('na')
    na3 = Xyzna.parse('na')
    assert isinstance(na1, Xyz)
    assert isinstance(na2, Xyzna)
    assert isinstance(na3, Xyzna)
    assert_eq(0, na1)
    assert_eq(0, na2)
    assert_eq(0, na3)


class Python(IntEnum):
    two = 2
    three = 3


def test_intenum():
    assert_is_instance(Python.two, int)
    assert_eq('Python.two', repr(Python.two))
    assert_eq('2', json.dumps(Python.two))


def test_generator():
    enum_generator = EnumValueGenerator()
    assert_eq(1, enum_generator())
    assert_eq(2, enum_generator())

    enum_generator.reset(5)
    assert_eq(5, enum_generator())
    assert_eq(6, enum_generator())


def test_bad_enum():
    def declare_bad_enum():
        class BadEnum(Enum):
            member1 = 1
            member2 = 1

    assert_raises(declare_bad_enum, AssertionError)
