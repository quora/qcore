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

from qcore.caching import (
    LRUCache,
    miss,
    cached_per_instance,
    memoize,
    memoize_with_ttl,
    LazyConstant,
    ThreadLocalLazyConstant,
    lazy_constant,
    not_computed,
    lru_cache,
)
from qcore.asserts import (
    assert_eq,
    assert_ne,
    assert_is,
    assert_in,
    assert_not_in,
    AssertRaises,
)
import qcore
import threading

from unittest import mock
from unittest.mock import MagicMock, call
import pickle


class TestLazyConstant:
    def test_decorator(self):
        self.is_computed = False

        @lazy_constant
        def test_function():
            assert_is(
                False, self.is_computed, "test_function has been called more than once"
            )
            self.is_computed = True
            return 42

        assert_eq(42, test_function())
        assert_eq(42, test_function())
        assert self.is_computed, "test_function has not been called"

    def test_not_compute(self):
        lazy_constant = LazyConstant(lambda: not_computed)
        assert_is(None, lazy_constant.compute())
        assert_is(None, lazy_constant.get_value())

    def test_clear(self):
        lazy_constant = LazyConstant(qcore.utime)
        lazy_time = lazy_constant.get_value()
        with qcore.TimeOffset(qcore.HOUR):
            assert_eq(lazy_time, lazy_constant.get_value(), tolerance=qcore.MINUTE)
            lazy_constant.clear()
            assert_ne(lazy_time, lazy_constant.get_value(), tolerance=qcore.MINUTE)

    def test_compute_clear(self):
        def test_function():
            self.is_called = True
            return 42

        lazy_constant = LazyConstant(test_function)
        assert_eq(42, lazy_constant.compute())
        assert self.is_called, "test_function has not been called"
        self.is_called = False
        assert_eq(42, lazy_constant.compute())
        assert self.is_called, "test_function has not been called"


class TestThreadLocalLazyConstant:
    def test_thread_locality(self):
        lazy_constant = ThreadLocalLazyConstant(threading.current_thread)
        results = []
        lock = threading.RLock()

        def execute():
            with lock:
                results.append(lazy_constant.get_value())

        threads = [threading.Thread(target=execute) for i in range(5)]
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

        assert_eq(5, len(results))
        assert_eq(5, len(set(results)))

    def test_not_compute(self):
        lazy_constant = ThreadLocalLazyConstant(lambda: not_computed)
        assert_is(None, lazy_constant.compute())
        assert_is(None, lazy_constant.get_value())

    def test_clear(self):
        lazy_constant = ThreadLocalLazyConstant(qcore.utime)
        lazy_time = lazy_constant.get_value()
        with qcore.TimeOffset(qcore.HOUR):
            assert_eq(lazy_time, lazy_constant.get_value(), tolerance=qcore.MINUTE)
            lazy_constant.clear()
            assert_ne(lazy_time, lazy_constant.get_value(), tolerance=qcore.MINUTE)

    def test_compute_clear(self):
        def test_function():
            self.is_called = True
            return 42

        lazy_constant = ThreadLocalLazyConstant(test_function)

        assert_eq(42, lazy_constant.compute())
        assert self.is_called, "test_function has not been called"
        self.is_called = False

        assert_eq(42, lazy_constant.compute())
        assert self.is_called, "test_function has not been called"


class TestLRUCache:
    def test_deletion(self):
        # Zero capacity cache is not allowed
        with AssertRaises(ValueError):
            c = LRUCache(0)

        # Capacity = 1
        c = LRUCache(1)
        c[0] = "0"
        c[1] = "1"
        assert_eq(1, len(c))
        assert_eq("1", c[1])
        assert_is(miss, c.get(2))
        del c[1]
        assert_eq(0, len(c))

        # Capacity = 2
        c = LRUCache(2)
        c[0] = "0"
        c[1] = "1"
        c[2] = "2"
        del c[1]
        assert_eq(1, len(c))
        assert_is(miss, c.get(1))
        assert_eq("2", c[2])

        c = LRUCache(2)
        c[0] = "0"
        c[1] = "1"
        c[2] = "2"
        del c[2]
        assert_eq(1, len(c))
        assert_eq("1", c[1])
        assert_is(miss, c.get(2))

        # Capacity = 3
        c = LRUCache(3)
        c[0] = "0"
        c[1] = "1"
        c[2] = "2"
        c[3] = "3"
        del c[2]
        assert_eq(2, len(c))
        assert_is(miss, c.get(2))
        assert_eq("1", c[1])
        assert_eq("3", c[3])

        # Deletion of invalid item
        with AssertRaises(KeyError):
            del c[15]

    def test_eviction(self):
        on_eviction = MagicMock()

        c = LRUCache(1, on_eviction)
        c[0] = "0"
        c[1] = "1"
        assert_eq(1, on_eviction.call_count)
        on_eviction.assert_called_once_with(0, "0")

        on_eviction.reset_mock()
        del c[1]
        assert_eq(1, on_eviction.call_count)
        on_eviction.assert_called_once_with(1, "1")

    def _check_order(self, expected, cache):
        items = expected
        keys = [item[0] for item in items]
        values = [item[1] for item in items]

        assert_eq(keys, list(cache))

        assert_eq(keys, list(cache.keys()))

        assert_eq(values, list(cache.values()))

        assert_eq(items, list(cache.items()))

    def test_iteration(self):
        c = LRUCache(3)
        c[0] = "a"
        c[1] = "b"
        c[2] = "c"

        self._check_order([(0, "a"), (1, "b"), (2, "c")], c)

    def test_getitem(self):
        c = LRUCache(3)
        c[0] = "a"
        c[1] = "b"
        c[2] = "c"

        assert_eq(3, c.get_capacity())
        self._check_order([(0, "a"), (1, "b"), (2, "c")], c)

        # Getting a value should make it MRU
        assert_eq("b", c[1])
        self._check_order([(0, "a"), (2, "c"), (1, "b")], c)

        # Missing value should fail
        with AssertRaises(KeyError):
            c[100]

    def test_get(self):
        c = LRUCache(3)
        c[0] = "a"
        c[1] = "b"
        c[2] = "c"

        # Getting a value should make it MRU
        assert_in(1, c)
        assert_eq("b", c.get(1))
        self._check_order([(0, "a"), (2, "c"), (1, "b")], c)

        # Missing value should have no effect
        assert_not_in(100, c)
        assert_eq(miss, c.get(100))
        self._check_order([(0, "a"), (2, "c"), (1, "b")], c)

    def test_sets(self):
        c = LRUCache(3)
        c[0] = "a"
        c[1] = "b"
        c[2] = "c"

        # Updating a value should make it MRU
        c[0] = "d"
        assert_in(0, c)
        self._check_order([(1, "b"), (2, "c"), (0, "d")], c)

        # Update order and evict the LRU item
        c[3] = "e"
        assert_in(3, c)
        self._check_order([(2, "c"), (0, "d"), (3, "e")], c)

    def test_clear(self):
        on_evict = MagicMock()

        c = LRUCache(3, on_evict)
        c[0] = "a"
        c[1] = "b"
        c[2] = "c"

        c.clear()
        self._check_order([], c)
        assert_eq(3, on_evict.call_count)
        assert_eq([call(0, "a"), call(1, "b"), call(2, "c")], on_evict.call_args_list)


def test_lru_cache():
    calls = []

    @lru_cache(maxsize=3)
    def cube(n):
        calls.append(n)
        return n * n * n

    assert_eq(1, cube(1))
    assert_eq([1], calls)
    assert_eq(1, cube(1))
    assert_eq([1], calls)

    assert_eq(8, cube(2))
    assert_eq([1, 2], calls)

    assert_eq(27, cube(3))
    assert_eq([1, 2, 3], calls)
    assert_eq(1, cube(1))
    assert_eq([1, 2, 3], calls)

    assert_eq(64, cube(4))
    assert_eq([1, 2, 3, 4], calls)

    assert_eq(1, cube(1))
    assert_eq([1, 2, 3, 4], calls)

    # 2 should have been evicted
    assert_eq(8, cube(2))
    assert_eq([1, 2, 3, 4, 2], calls)

    # manually clear the cache
    cube.clear()
    assert_eq(1, cube(1))
    assert_eq([1, 2, 3, 4, 2, 1], calls)
    assert_eq(8, cube(2))
    assert_eq([1, 2, 3, 4, 2, 1, 2], calls)
    assert_eq(27, cube(3))
    assert_eq([1, 2, 3, 4, 2, 1, 2, 3], calls)
    assert_eq(64, cube(4))
    assert_eq([1, 2, 3, 4, 2, 1, 2, 3, 4], calls)


def test_lru_cache_key_fn():
    calls = []

    @lru_cache(maxsize=3, key_fn=lambda args, kwargs: args[0] % 2 == 0)
    def cube(n):
        calls.append(n)
        return n * n * n

    assert_eq(1, cube(1))
    assert_eq([1], calls)
    assert_eq(1, cube(3))
    assert_eq([1], calls)

    assert_eq(8, cube(2))
    assert_eq([1, 2], calls)
    assert_eq(8, cube(4))
    assert_eq([1, 2], calls)

    cube.clear()
    assert_eq(27, cube(3))
    assert_eq([1, 2, 3], calls)
    assert_eq(27, cube(1))
    assert_eq([1, 2, 3], calls)


class CachingClass:
    # not hashable
    __hash__ = None  # type: ignore

    def __init__(self, val):
        self.val = val
        self.x = 0

    @cached_per_instance()
    def get_x(self):
        self.x += self.val
        return self.x

    @cached_per_instance()
    def with_kwargs(self, x=1, y=2, z=3):
        self.x += x + y + z
        return self.x

    @cached_per_instance()
    def with_variable_kwargs(self, **kwargs):
        self.x += sum(kwargs.values())
        return self.x


def test_cached_per_instance():
    get_x_cache = CachingClass.get_x.__cached_per_instance_cache__
    with_kwargs_cache = CachingClass.with_kwargs.__cached_per_instance_cache__
    assert_eq(0, len(get_x_cache), extra=repr(get_x_cache))
    assert_eq(0, len(with_kwargs_cache), extra=repr(with_kwargs_cache))

    object1 = CachingClass(1)
    object2 = CachingClass(2)

    assert_eq(object1.x, 0)
    assert_eq(object2.x, 0)

    assert_eq(object1.get_x(), 1)
    assert_eq(1, len(get_x_cache), extra=repr(get_x_cache))
    assert_eq(0, len(with_kwargs_cache), extra=repr(with_kwargs_cache))

    assert_eq(object1.x, 1)
    assert_eq(object2.x, 0)

    assert_eq(object1.get_x(), 1)
    assert_eq(1, len(get_x_cache), extra=repr(get_x_cache))
    assert_eq(0, len(with_kwargs_cache), extra=repr(with_kwargs_cache))

    assert_eq(object1.x, 1)
    assert_eq(object2.x, 0)

    assert_eq(object2.get_x(), 2)
    assert_eq(2, len(get_x_cache), extra=repr(get_x_cache))
    assert_eq(0, len(with_kwargs_cache), extra=repr(with_kwargs_cache))

    assert_eq(object1.x, 1)
    assert_eq(object2.x, 2)

    assert_eq(7, object1.with_kwargs())
    assert_eq(7, object1.with_kwargs(x=1))
    assert_eq(7, object1.with_kwargs())
    assert_eq(16, object1.with_kwargs(x=3, y=3, z=3))

    assert_eq(2, len(get_x_cache), extra=repr(get_x_cache))
    assert_eq(1, len(with_kwargs_cache), extra=repr(with_kwargs_cache))

    del object1
    assert_eq(1, len(get_x_cache), extra=repr(get_x_cache))
    assert_eq(0, len(with_kwargs_cache), extra=repr(with_kwargs_cache))

    del object2
    assert_eq(0, len(get_x_cache), extra=repr(get_x_cache))
    assert_eq(0, len(with_kwargs_cache), extra=repr(with_kwargs_cache))

    object3 = CachingClass(0)
    assert_eq(0, object3.x)
    object3.with_variable_kwargs(k1=2)
    assert_eq(2, object3.x)
    object3.with_variable_kwargs(k1=2)
    assert_eq(2, object3.x)
    object3.with_variable_kwargs(k2=2)
    assert_eq(4, object3.x)
    object3.with_variable_kwargs(k1=2, k2=2)
    assert_eq(8, object3.x)


class PickleCachingClass:
    @cached_per_instance()
    def f(self, x):
        return x


def test_cached_per_instance_pickling():
    # make sure cached stuff doesn't appear in the pickled representation

    obj = PickleCachingClass()
    obj.attr = "spam"
    assert_eq(set(), set(PickleCachingClass.f.__cached_per_instance_cache__.keys()))
    obj.f("my hovercraft is full of eels")
    assert_eq({id(obj)}, set(PickleCachingClass.f.__cached_per_instance_cache__.keys()))

    serialized = pickle.dumps(obj)
    assert_not_in(b"my hovercraft is full of eels", serialized)
    assert_in(b"spam", serialized)

    restored = pickle.loads(serialized)
    assert_eq({id(obj)}, set(PickleCachingClass.f.__cached_per_instance_cache__.keys()))
    restored.f("my hovercraft is full of eels")
    assert_eq(
        {id(obj), id(restored)},
        set(PickleCachingClass.f.__cached_per_instance_cache__.keys()),
    )
    assert_eq("spam", obj.attr)

    # make sure we can use this with a custom __getstate__

    class X:
        @cached_per_instance()
        def f(self, x):
            return x

        def __getstate__(self):
            return {}

    X().f(1)


x = 0


@memoize
def cached_fn(y, z=4):
    global x
    x += 1
    return y * z


@memoize
def cached_fn_with_annotations(y: int, z: int = 4) -> int:
    global x
    x += 1
    return y * z


@memoize
def cached_fn_with_kwonly_args(y, *, z):
    global x
    x += 1
    return y * z


memoize_fns = [cached_fn, cached_fn_with_annotations]


def test_memoize_with_kwonly_args():
    global x
    x = 0
    with AssertRaises(TypeError):
        cached_fn_with_kwonly_args(1)
    with AssertRaises(TypeError):
        cached_fn_with_kwonly_args(1, 2)

    assert_eq(0, x)

    assert_eq(4, cached_fn_with_kwonly_args(2, z=2))
    assert_eq(1, x)
    assert_eq(4, cached_fn_with_kwonly_args(z=2, y=2))
    assert_eq(1, x)

    assert_eq(8, cached_fn_with_kwonly_args(2, z=4))
    assert_eq(2, x)
    assert_eq(8, cached_fn_with_kwonly_args(y=2, z=4))
    assert_eq(2, x)

    cached_fn_with_kwonly_args.clear_cache()
    assert_eq(4, cached_fn_with_kwonly_args(2, z=2))
    assert_eq(3, x)


@memoize_with_ttl(ttl_secs=500)
def cached_fn_with_ttl(y, z=4):
    global x
    x += 1
    return y * z


@memoize_with_ttl(ttl_secs=500)
def cached_fn_with_ttl_unhashable(y, z={"a": 1, "b": 2, "c": 3}):
    global x
    x += 1
    return y * (z["a"] + z["b"] + z["c"])


def test_memoize():
    """Test Caching with no Time-To-Live (TTL)."""
    global x
    for fn in memoize_fns:
        x = 0
        assert_eq(4, fn(1))
        assert_eq(1, x)

        assert_eq(8, fn(2, 4))
        assert_eq(2, x)
        # should not result in another call
        assert_eq(8, fn(2, z=4))
        assert_eq(2, x)
        assert_eq(8, fn(y=2, z=4))
        assert_eq(2, x)

        fn.clear_cache()
        assert_eq(4, fn(1))
        assert_eq(3, x)


def test_memoize_with_ttl():
    """Test Caching with Time-To-Live (TTL)."""
    global x
    x = 0
    then = 10000
    just_after = 10005
    now = 10700

    with mock.patch("time.time") as mock_time:
        mock_time.return_value = then
        assert_eq(4, cached_fn_with_ttl(1))
        assert_eq(1, x)

    with mock.patch("time.time") as mock_time:
        mock_time.return_value = just_after
        assert_eq(8, cached_fn_with_ttl(2, 4))
        assert_eq(2, x)

        # should not result in another call
        assert_eq(8, cached_fn_with_ttl(2, z=4))
        assert_eq(2, x)
        assert_eq(8, cached_fn_with_ttl(y=2, z=4))
        assert_eq(2, x)

    # after the ttl expires, should result in another call
    with mock.patch("time.time") as mock_time:
        mock_time.return_value = now
        assert_eq(8, cached_fn_with_ttl(2, z=4))
        assert_eq(3, x)
        assert_eq(8, cached_fn_with_ttl(y=2, z=4))
        assert_eq(3, x)

        cached_fn_with_ttl.clear_cache()
        assert_eq(4, cached_fn_with_ttl(1))
        assert_eq(4, x)
        assert_eq(8, cached_fn_with_ttl(2, z=4))
        assert_eq(5, x)

        # test dirtying a key.
        # first, the key should be cached
        assert_eq(8, cached_fn_with_ttl(2, z=4))
        assert_eq(5, x)
        cached_fn_with_ttl.dirty(2, z=4)

        # now, we should recompute the function
        assert_eq(8, cached_fn_with_ttl(2, z=4))
        assert_eq(6, x)


def test_memoize_with_ttl_unhashable():
    """Test Caching with TTL using dictionary arguments."""
    global x
    x = 0
    assert_eq(12, cached_fn_with_ttl_unhashable(2))
    assert_eq(1, x)

    assert_eq(10, cached_fn_with_ttl_unhashable(1, z={"a": 2, "b": 3, "c": 5}))
    assert_eq(2, x)
    # should not result in another call
    assert_eq(10, cached_fn_with_ttl_unhashable(1, z={"a": 2, "b": 3, "c": 5}))
    assert_eq(2, x)
    assert_eq(12, cached_fn_with_ttl_unhashable(2, z={"a": 1, "b": 2, "c": 3}))
    assert_eq(2, x)

    cached_fn_with_ttl_unhashable.clear_cache()
    assert_eq(12, cached_fn_with_ttl_unhashable(2))
    assert_eq(3, x)
