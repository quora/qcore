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
from qcore.asserts import assert_eq, assert_ne, assert_unordered_list_eq, AssertRaises


class NonCython:
    pass


class InheritFromCython(qcore.caching.LazyConstant):
    pass


def test_is_cython_class():
    if qcore.caching.__file__.endswith(".so"):
        assert qcore.inspection.is_cython_class(qcore.caching.LazyConstant)
    assert not qcore.inspection.is_cython_class(NonCython)
    assert not qcore.inspection.is_cython_class(InheritFromCython)


class A:
    pass


class B(A):
    pass


class C(B):
    pass


class MetaA(type):
    pass


class MetaB(MetaA):
    pass


def test_get_subclass_tree():
    assert_unordered_list_eq([C, B], qcore.inspection.get_subclass_tree(A))
    assert_eq([C], qcore.inspection.get_subclass_tree(B))
    assert_eq([], qcore.inspection.get_subclass_tree(C))

    assert_eq([MetaB], qcore.inspection.get_subclass_tree(MetaA))
    assert_eq([], qcore.inspection.get_subclass_tree(MetaB))


def fun_with_args(a, b, c, d="e", **f):
    pass


def test_getargspec():
    empty = qcore.inspection.ArgSpec(
        args=[], varargs=None, keywords=None, defaults=None
    )
    assert_eq(empty, qcore.inspection.getargspec(test_get_subclass_tree))
    assert_eq(empty, qcore.inspection.getargspec(qcore.inspection.lazy_stack))

    emptymethod = qcore.inspection.ArgSpec(
        args=["self"], varargs=None, keywords=None, defaults=None
    )
    assert_eq(emptymethod, qcore.inspection.getargspec(X.myinstancemethod))
    assert_eq(emptymethod, qcore.inspection.getargspec(X().myinstancemethod))

    emptyclsmethod = qcore.inspection.ArgSpec(
        args=["cls"], varargs=None, keywords=None, defaults=None
    )
    assert_eq(emptyclsmethod, qcore.inspection.getargspec(X.myclassmethod))

    spec = qcore.inspection.ArgSpec(
        args=["a", "b", "c", "d"], varargs=None, keywords="f", defaults=("e",)
    )
    assert_eq(spec, qcore.inspection.getargspec(fun_with_args))


def fun_with_annotations(a: int, b: str, *args) -> None:
    pass


def fun_with_kwonly_args(a=1, *, b, c=3):
    pass


def test_getargspec_py3_only():
    spec = qcore.inspection.ArgSpec(
        args=["a", "b"], varargs="args", keywords=None, defaults=None
    )
    assert_eq(spec, qcore.inspection.getargspec(fun_with_annotations))
    with AssertRaises(ValueError):
        qcore.inspection.getargspec(fun_with_kwonly_args)


class X:
    @classmethod
    def myclassmethod(cls):
        pass

    def myinstancemethod(self):
        pass


class OldStyle:
    @classmethod
    def myclassmethod(cls):
        pass

    def myinstancemethod(self):
        pass


class BoolConversionFails:
    def method(self):
        pass

    def __nonzero__(self):
        raise TypeError("Cannot convert %s to bool" % self)

    __bool__ = __nonzero__


def test_is_classmethod():
    assert not qcore.inspection.is_classmethod(X)
    assert not qcore.inspection.is_classmethod(X())
    assert not qcore.inspection.is_classmethod(OldStyle)
    assert not qcore.inspection.is_classmethod(OldStyle())
    assert not qcore.inspection.is_classmethod("x")
    assert not qcore.inspection.is_classmethod(qcore)
    assert not qcore.inspection.is_classmethod(qcore.inspection.is_classmethod)
    assert qcore.inspection.is_classmethod(X.myclassmethod)
    assert qcore.inspection.is_classmethod(X().myclassmethod)
    assert qcore.inspection.is_classmethod(OldStyle.myclassmethod)
    assert qcore.inspection.is_classmethod(OldStyle().myclassmethod)
    assert not qcore.inspection.is_classmethod(X.myinstancemethod)
    assert not qcore.inspection.is_classmethod(X().myinstancemethod)
    assert not qcore.inspection.is_classmethod(OldStyle.myinstancemethod)
    assert not qcore.inspection.is_classmethod(OldStyle().myinstancemethod)
    # this throws an error if you do "not im_self"
    assert not qcore.inspection.is_classmethod(BoolConversionFails().method)


def test_get_function_call_str():
    class TestObject:
        """A test object containing no __str__ implementation."""

        def __str__(self):
            raise NotImplementedError()

        def __repr__(self):
            return "test"

    def test_function():
        pass

    function_str_kv = qcore.inspection.get_function_call_str(
        test_function, (1, 2, 3), {"k": "v"}
    )
    function_str_dummy = qcore.inspection.get_function_call_str(
        test_function, (TestObject(),), {}
    )

    assert_eq("test_inspection.test_function(1,2,3,k=v)", function_str_kv)
    assert_eq("test_inspection.test_function(test)", function_str_dummy)


def test_get_function_call_repr():
    def dummy_function():
        pass

    function_repr_kv = qcore.inspection.get_function_call_repr(
        dummy_function, ("x",), {"k": "v"}
    )
    function_repr_kr = qcore.inspection.get_function_call_repr(
        dummy_function, ("x",), {"k": "r"}
    )

    assert_eq("test_inspection.dummy_function('x',k='v')", function_repr_kv)
    assert_ne(function_repr_kv, function_repr_kr)
