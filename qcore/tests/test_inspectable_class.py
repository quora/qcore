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

from qcore.asserts import assert_eq, assert_ne
from qcore import InspectableClass


class OldStyleClass:
    pass


class SimpleObjectWithDictComparison(InspectableClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class OidObject(InspectableClass):
    def __init__(self, oid):
        self.oid = oid


class ObjectWithExcludedAttributes(InspectableClass):
    _excluded_attributes = {"attr1"}

    def __init__(self, attr1, attr2):
        self.attr1 = attr1
        self.attr2 = attr2


class ObjectWithSlots(InspectableClass):
    __slots__ = ("oid",)

    def __init__(self, oid):
        self.oid = oid


class TestObjectWithDictComparison:
    def _check_repr_and_str(self, expected, obj):
        assert_eq(expected, repr(obj))
        assert_eq(expected, str(obj))

    def test_compare_objects(self):
        assert_eq(SimpleObjectWithDictComparison(), SimpleObjectWithDictComparison())
        assert_eq(
            SimpleObjectWithDictComparison(foo="bar"),
            SimpleObjectWithDictComparison(foo="bar"),
        )
        assert_eq(
            SimpleObjectWithDictComparison(x=SimpleObjectWithDictComparison(y="z")),
            SimpleObjectWithDictComparison(x=SimpleObjectWithDictComparison(y="z")),
        )

        # not equal
        assert_ne(
            SimpleObjectWithDictComparison(x=42), SimpleObjectWithDictComparison(x=43)
        )
        assert_ne(
            SimpleObjectWithDictComparison(), SimpleObjectWithDictComparison(foo="bar")
        )

    def test_compare_to_non_object(self):
        empty_object = SimpleObjectWithDictComparison(oid=3)
        # make sure we call both methods
        assert empty_object != 1
        assert not (empty_object == 1)

        other_object = OidObject(3)
        assert empty_object != other_object
        assert not (empty_object == other_object)

        # make sure old-style classes (which lack __class__) also work
        assert empty_object != OldStyleClass
        assert not (empty_object == OldStyleClass)
        # instances do have __class__ but let's check them too
        assert empty_object != OldStyleClass()
        assert not (empty_object == OldStyleClass())

    def test_repr_and_str(self):
        self._check_repr_and_str(
            "SimpleObjectWithDictComparison()", SimpleObjectWithDictComparison()
        )
        self._check_repr_and_str(
            "SimpleObjectWithDictComparison(foo='bar')",
            SimpleObjectWithDictComparison(foo="bar"),
        )
        self._check_repr_and_str(
            "SimpleObjectWithDictComparison(bar='baz', foo='bar')",
            SimpleObjectWithDictComparison(foo="bar", bar="baz"),
        )
        self._check_repr_and_str("OidObject(oid=3)", OidObject(3))

    def test_hash(self):
        d = {}
        obj1 = SimpleObjectWithDictComparison(oid=1)
        d[obj1] = "val1"
        assert_eq("val1", d[obj1])
        # different but equal object also works
        assert_eq("val1", d[SimpleObjectWithDictComparison(oid=1)])

        obj2 = SimpleObjectWithDictComparison(oid=1)
        d[obj2] = "val2"
        assert_eq(1, len(d))
        assert_eq("val2", d[obj1])

        # non-equal object
        obj3 = SimpleObjectWithDictComparison(oid=3)
        d[obj3] = "val3"
        assert_eq(2, len(d))
        assert_eq("val2", d[obj1])
        assert_eq("val3", d[obj3])

    def test_excluded_attributes(self):
        obj1 = ObjectWithExcludedAttributes(1, 1)
        obj2 = ObjectWithExcludedAttributes(2, 1)
        obj3 = ObjectWithExcludedAttributes(1, 2)
        assert_eq(obj1, obj2)
        assert_ne(obj1, obj3)
        assert_ne(obj2, obj3)
        self._check_repr_and_str("ObjectWithExcludedAttributes(attr2=1)", obj1)
        self._check_repr_and_str("ObjectWithExcludedAttributes(attr2=1)", obj2)
        self._check_repr_and_str("ObjectWithExcludedAttributes(attr2=2)", obj3)

    def test_slots(self):
        obj1 = ObjectWithSlots(1)
        obj2 = ObjectWithSlots(2)
        obj3 = ObjectWithSlots(1)
        assert_eq(obj1, obj3)
        assert_eq(obj1, obj1)
        assert_ne(obj1, obj2)
        self._check_repr_and_str("ObjectWithSlots(oid=1)", obj1)
