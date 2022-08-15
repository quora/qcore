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
from qcore.asserts import (
    assert_eq,
    assert_is,
    assert_ne,
    assert_is_not,
    assert_is_substring,
    AssertRaises,
)

# this import is just for test_object_from_string
from qcore import asserts as asserts_

v = qcore.ScopedValue("a")


def test_true_fn():
    assert_is(True, qcore.true_fn())


def test_false_fn():
    assert_is(False, qcore.false_fn())


def test():
    def nested():
        assert_eq(v.get(), "b")
        with v.override("c"):
            assert_eq(v.get(), "c")

    assert_eq(v.get(), "a")
    with v.override("b"):
        assert_eq(v.get(), "b")
        nested()


def test_exception():
    assert_eq(v(), "a")
    try:
        with v.override("b"):
            assert_eq(v(), "b")
            raise NotImplementedError()
    except NotImplementedError:
        pass
    assert_eq(v(), "a")


def test_override():
    class TestObject:
        def __init__(self):
            self.v = None

    o = TestObject()
    o.v = "a"

    with qcore.override(o, "v", "b"):
        assert_eq(o.v, "b")
        try:
            with qcore.override(o, "v", "c"):
                assert_eq(o.v, "c")
                raise NotImplementedError()
        except NotImplementedError:
            pass
        assert_eq(o.v, "b")
    assert_eq(o.v, "a")


def test_dict_to_object():
    d = {"a": 1, "b": 2}

    o = qcore.dict_to_object(d)
    assert_eq(o.__dict__, d)

    o = qcore.dict_to_object(d)
    assert_eq(o.a, 1)
    assert_eq(o.b, 2)


def test_copy_public_attrs():
    def f():
        pass

    f.hi = 1
    f.hello = 2
    f._hi = 3
    f._hello = 4

    def g():
        pass

    g.hello = 5
    g._hi = 6
    g._hello = 7

    with AssertRaises(AttributeError):
        assert g.hi
    assert_eq(5, g.hello)
    assert_eq(6, g._hi)
    assert_eq(7, g._hello)

    qcore.copy_public_attrs(f, g)

    assert_eq(1, g.hi)
    assert_eq(2, g.hello)
    assert_eq(6, g._hi)
    assert_eq(7, g._hello)
    assert_ne(g.__code__, f.__code__)
    assert_ne(g.__name__, f.__name__)

    class A:
        pass

    a1 = A()
    a1._hey = 0
    a1.hi = 1
    a1.hello = 2
    a1._hi = 3
    a1._hello = 4

    a2 = A()
    a2.hello = 5
    a2._hi = 6
    a2._hello = 7

    assert_eq(0, a1._hey)
    assert_eq(1, a1.hi)
    assert_eq(2, a1.hello)
    assert_eq(3, a1._hi)
    assert_eq(4, a1._hello)
    with AssertRaises(AttributeError):
        assert a2.hi
    assert_eq(5, a2.hello)
    assert_eq(6, a2._hi)
    assert_eq(7, a2._hello)

    qcore.copy_public_attrs(a1, a2)

    assert_eq(0, a1._hey)
    assert_eq(1, a1.hi)
    assert_eq(2, a1.hello)
    assert_eq(3, a1._hi)
    assert_eq(4, a1._hello)
    with AssertRaises(AttributeError):
        assert a2._hey
    assert_eq(1, a2.hi)
    assert_eq(2, a2.hello)
    assert_eq(6, a2._hi)
    assert_eq(7, a2._hello)


def test_cached_hash_wrapper():
    class TestClass:
        pass

    w1a = qcore.CachedHashWrapper(TestClass())
    w1b = qcore.CachedHashWrapper(w1a())
    w2a = qcore.CachedHashWrapper(TestClass())

    print("w1a", w1a)
    print("w1b", w1b)
    print("w2a", w2a)

    assert_is(w1a.value(), w1a())
    assert_is(w1a(), w1b())
    assert_is_not(w1a(), w2a())

    assert_eq(w1a, w1b)
    assert_ne(w1a, w2a)
    assert_ne(w1b, w2a)

    assert_eq(w1a, w1b())
    assert_ne(w1a, w2a())
    assert_ne(w1b, w2a())

    assert_eq(hash(w1a), hash(w1b))
    assert_ne(hash(w1a), hash(w2a))
    assert_ne(hash(w1b), hash(w2a))


def _stub_serializable_func():
    pass


def test_object_from_string():
    def check(name, expected):
        actual = qcore.object_from_string(name)
        assert_eq(expected, actual)
        name = name.encode("ascii")
        with AssertRaises(TypeError):
            qcore.object_from_string(name)

    with AssertRaises(ValueError):
        # Not a fully qualified name
        qcore.object_from_string("FooBar")

    check("test_helpers._stub_serializable_func", _stub_serializable_func)
    import socket

    check("socket.gethostname", socket.gethostname)

    with AssertRaises(TypeError):
        # invalid type
        qcore.object_from_string({"name": "socket.gethostname"})

    # test the case when the from import fails
    check("test_helpers.asserts_.assert_eq", assert_eq)


def test_catchable_exceptions():
    assert_is(True, qcore.catchable_exceptions(Exception))
    assert_is(True, qcore.catchable_exceptions(BaseException))
    assert_is(False, qcore.catchable_exceptions(tuple()))
    assert_is(True, qcore.catchable_exceptions((Exception,)))
    assert_is(False, qcore.catchable_exceptions((Exception, int)))
    assert_is(False, qcore.catchable_exceptions([Exception]))


def test_ellipsis():
    assert_eq("abcdef", qcore.ellipsis("abcdef", 0))
    assert_eq("abcdef", qcore.ellipsis("abcdef", 10))
    assert_eq("ab...", qcore.ellipsis("abcdef", 5))


def test_safe_representation():
    class TestObject:
        """A test object that has neither __str__ nor __repr__."""

        def __str__(self):
            return NotImplementedError()

        def __repr__(self):
            return NotImplementedError()

    assert_eq("2", qcore.safe_str(2))
    assert_eq("2....", qcore.safe_str("2.192842", max_length=5))
    assert_is_substring("<n/a: str(...) raised", qcore.safe_str(TestObject()))

    assert_eq("'a'", qcore.safe_repr("a"))
    assert_eq("'...", qcore.safe_repr("2.192842", max_length=4))
    assert_eq("<n/a: repr...", qcore.safe_repr(TestObject(), max_length=13))


def test_marker_object():
    assert_eq("text", str(qcore.MarkerObject("text")))

    with AssertRaises(TypeError):
        qcore.MarkerObject(b"bytes")

    # MarkerObjects should be unique
    assert_ne(qcore.MarkerObject("name"), qcore.MarkerObject("name"))
