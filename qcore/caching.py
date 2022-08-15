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

"""

Low-level caching abstractions.

"""

__all__ = [
    "miss",
    "not_computed",
    "LazyConstant",
    "lazy_constant",
    "ThreadLocalLazyConstant",
    "LRUCache",
    "cached_per_instance",
    "memoize",
    "memoize_with_ttl",
]

from collections import OrderedDict
import threading
import functools
import inspect
import time
import weakref

from .asserts import assert_is_instance, assert_gt
from . import helpers


miss = helpers.miss
not_computed = helpers.MarkerObject("not_computed @ qcore.caching")
globals()["miss"] = miss
globals()["not_computed"] = not_computed


class LazyConstant:
    """
    Describes lazy or rarely changing value.

    Normally used to cache lazy / rarely changing values that are re-computed
    only on demand (e.g. in case a particular event is raised).

    """

    def __init__(self, value_provider):
        self.value_provider = value_provider
        self.value = not_computed

    def get_value(self):
        """Returns the value of the constant."""
        if self.value is not_computed:
            self.value = self.value_provider()
            if self.value is not_computed:
                return None
        return self.value

    def compute(self):
        """Computes the value. Does not look at the cache."""
        self.value = self.value_provider()
        if self.value is not_computed:
            return None
        else:
            return self.value

    def clear(self):
        self.value = not_computed


def lazy_constant(fn):
    """Decorator to make a function that takes no arguments use the LazyConstant class."""

    class NewLazyConstant(LazyConstant):
        @functools.wraps(fn)
        def __call__(self):
            return self.get_value()

    return NewLazyConstant(fn)


class ThreadLocalLazyConstant(threading.local):
    """
    Describes lazy or rarely changing thread-local value.

    Normally used to cache lazy / rarely changing values that are re-computed
    only on demand (e.g. in case a particular event is raised).

    """

    def __init__(self, value_provider):
        self.value_provider = value_provider
        self.value = not_computed

    def get_value(self):
        if self.value is not_computed:
            self.value = self.value_provider()
            if self.value is not_computed:
                return None
        return self.value

    def compute(self):
        self.value = self.value_provider()
        if self.value is not_computed:
            return None
        else:
            return self.value

    def clear(self):
        self.value = not_computed


class LRUCache:
    """A dictionary-like object that stores only a certain number of items, and
    discards its least recently used item when full.

    >>> cache = LRUCache(3)
    >>> cache['A'] = 0
    >>> cache['B'] = 1
    >>> cache['C'] = 2
    >>> len(cache)
    3

    >>> cache['A']
    0

    Adding new items to the cache does not increase its size. Instead, the least
    recently used item is dropped:

    >>> cache['D'] = 3
    >>> len(cache)
    3
    >>> 'B' in cache
    False

    Iterating over the cache returns (key, item) pairs, starting with the least
    recently used:

    >>> for key, item in cache:
    ...     print key
    C
    A
    D

    This code is based on the LRUCache class from Genshi which is based on
    `Myghty <http://www.myghty.org>`_'s LRUCache from ``myghtyutils.util``,
    written by Mike Bayer and released under the MIT license (Genshi uses the
    BSD License).
    """

    def __init__(self, capacity, item_evicted=None):
        if not isinstance(capacity, int):
            raise TypeError("capacity must be integer, not {}".format(type(capacity)))
        if capacity <= 0:
            raise ValueError("capacity must be positive, not {}".format(capacity))
        self._capacity = capacity
        self._item_evicted = item_evicted
        self._dict = OrderedDict()

    def get_capacity(self):
        return self._capacity

    def __len__(self):
        return len(self._dict)

    def __contains__(self, key):
        return key in self._dict

    def __getitem__(self, key):
        value = self._dict[key]
        self._update_item(key, value)
        return value

    def get(self, key, default=miss):
        """Return the value for given key if it exists."""
        if key not in self._dict:
            return default

        # invokes __getitem__, which updates the item
        return self[key]

    def __setitem__(self, key, value):
        if key in self._dict:
            self._update_item(key, value)
        else:
            if len(self._dict) == self._capacity:
                item = self._dict.popitem(last=False)
                self._evict_item(item[0], item[1])
            self._dict[key] = value

    def __delitem__(self, key):
        value = self._dict[key]
        del self._dict[key]
        self._evict_item(key, value)

    def clear(self, omit_item_evicted=False):
        """Empty the cache and optionally invoke item_evicted callback."""
        if not omit_item_evicted:
            items = self._dict.items()
            for key, value in items:
                self._evict_item(key, value)
        self._dict.clear()

    def __iter__(self):
        return iter(self._dict)

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def _evict_item(self, key, value):
        if self._item_evicted:
            self._item_evicted(key, value)

    def _update_item(self, key, value):
        del self._dict[key]
        self._dict[key] = value


def lru_cache(maxsize=128, key_fn=None):
    """Decorator that adds an LRU cache of size maxsize to the decorated function.

    maxsize is the number of different keys cache can accomodate.
    key_fn is the function that builds key from args. The default key function
    creates a tuple out of args and kwargs. If you use the default, there is no reason
    not to use functools.lru_cache directly.

    Possible use cases:
    - Your cache key is very large, so you don't want to keep the whole key in memory.
    - The function takes some arguments that don't affect the result.

    """

    def decorator(fn):
        cache = LRUCache(maxsize)
        argspec = inspect.getfullargspec(fn)
        arg_names = argspec.args[1:] + argspec.kwonlyargs  # remove self
        kwargs_defaults = get_kwargs_defaults(argspec)

        cache_key = key_fn
        if cache_key is None:

            def cache_key(args, kwargs):
                return get_args_tuple(args, kwargs, arg_names, kwargs_defaults)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = cache_key(args, kwargs)
            try:
                return cache[key]
            except KeyError:
                value = fn(*args, **kwargs)
                cache[key] = value
                return value

        wrapper.clear = cache.clear
        wrapper.fn = fn

        return wrapper

    return decorator


def cached_per_instance():
    """Decorator that adds caching to an instance method.

    The cached value is stored so that it gets garbage collected together with the instance.

    The cached values are not stored when the object is pickled.

    """

    def cache_fun(fun):
        argspec = inspect.getfullargspec(fun)
        arg_names = argspec.args[1:] + argspec.kwonlyargs  # remove self
        kwargs_defaults = get_kwargs_defaults(argspec)
        cache = {}

        def cache_key(args, kwargs):
            return get_args_tuple(args, kwargs, arg_names, kwargs_defaults)

        def clear_cache(instance_key, ref):
            del cache[instance_key]

        @functools.wraps(fun)
        def new_fun(self, *args, **kwargs):
            instance_key = id(self)
            if instance_key not in cache:
                ref = weakref.ref(self, functools.partial(clear_cache, instance_key))
                cache[instance_key] = (ref, {})
            instance_cache = cache[instance_key][1]

            k = cache_key(args, kwargs)
            if k not in instance_cache:
                instance_cache[k] = fun(self, *args, **kwargs)
            return instance_cache[k]

        # just so unit tests can check that this is cleaned up correctly
        new_fun.__cached_per_instance_cache__ = cache
        new_fun.fn = fun
        return new_fun

    return cache_fun


def get_args_tuple(args, kwargs, arg_names, kwargs_defaults):
    """Generates a cache key from the passed in arguments."""
    args_list = list(args)
    args_len = len(args)
    all_args_len = len(arg_names)
    try:
        while args_len < all_args_len:
            arg_name = arg_names[args_len]
            if arg_name in kwargs_defaults:
                args_list.append(kwargs.get(arg_name, kwargs_defaults[arg_name]))
            else:
                args_list.append(kwargs[arg_name])
            args_len += 1
        remaining_keys = sorted([k for k in kwargs if k not in arg_names])
        for k in remaining_keys:
            args_list.append((k, kwargs[k]))
    except KeyError as e:
        raise TypeError("Missing argument %r" % (e.args[0],))
    return tuple(args_list)


def get_kwargs_defaults(argspec):
    """Computes a kwargs_defaults dictionary for use by get_args_tuple given an argspec."""
    arg_names = tuple(argspec.args)
    defaults = argspec.defaults or ()
    num_args = len(argspec.args) - len(defaults)
    kwargs_defaults = {}
    for i, default_value in enumerate(defaults):
        kwargs_defaults[arg_names[num_args + i]] = default_value
    if getattr(argspec, "kwonlydefaults", None):
        kwargs_defaults.update(argspec.kwonlydefaults)
    return kwargs_defaults


def memoize(fun):
    """Memoizes return values of the decorated function.

    Similar to l0cache, but the cache persists for the duration of the process, unless clear_cache()
    is called on the function.

    """
    argspec = inspect.getfullargspec(fun)
    arg_names = argspec.args + argspec.kwonlyargs
    kwargs_defaults = get_kwargs_defaults(argspec)

    def cache_key(args, kwargs):
        return get_args_tuple(args, kwargs, arg_names, kwargs_defaults)

    @functools.wraps(fun)
    def new_fun(*args, **kwargs):
        k = cache_key(args, kwargs)
        if k not in new_fun.__cache:
            new_fun.__cache[k] = fun(*args, **kwargs)
        return new_fun.__cache[k]

    def clear_cache():
        """Removes all cached values for this function."""
        new_fun.__cache.clear()

    new_fun.__cache = {}
    new_fun.clear_cache = clear_cache
    new_fun.fn = fun
    return new_fun


def memoize_with_ttl(ttl_secs=60 * 60 * 24):
    """Memoizes return values of the decorated function for a given time-to-live.

    Similar to l0cache, but the cache persists for the duration of the process, unless clear_cache()
    is called on the function or the time-to-live expires. By default, the time-to-live is set to
    24 hours.

    """

    error_msg = (
        "Incorrect usage of qcore.caching.memoize_with_ttl: "
        "ttl_secs must be a positive integer."
    )
    assert_is_instance(ttl_secs, int, error_msg)
    assert_gt(ttl_secs, 0, error_msg)

    def cache_fun(fun):
        argspec = inspect.getfullargspec(fun)
        arg_names = argspec.args + argspec.kwonlyargs
        kwargs_defaults = get_kwargs_defaults(argspec)

        def cache_key(args, kwargs):
            return repr(get_args_tuple(args, kwargs, arg_names, kwargs_defaults))

        @functools.wraps(fun)
        def new_fun(*args, **kwargs):
            k = cache_key(args, kwargs)
            current_time = int(time.time())

            # k is not in the cache; perform the function and cache the result.
            if k not in new_fun.__cache or k not in new_fun.__cache_times:
                new_fun.__cache[k] = fun(*args, **kwargs)
                new_fun.__cache_times[k] = current_time
                return new_fun.__cache[k]

            # k is in the cache at this point. Check if the ttl has expired;
            # if so, recompute the value and cache it.
            cache_time = new_fun.__cache_times[k]
            if current_time - cache_time > ttl_secs:
                new_fun.__cache[k] = fun(*args, **kwargs)
                new_fun.__cache_times[k] = current_time

            # finally, return the cached result.
            return new_fun.__cache[k]

        def clear_cache():
            """Removes all cached values for this function."""
            new_fun.__cache.clear()
            new_fun.__cache_times.clear()

        def dirty(*args, **kwargs):
            """Dirties the function for a given set of arguments."""
            k = cache_key(args, kwargs)
            new_fun.__cache.pop(k, None)
            new_fun.__cache_times.pop(k, None)

        new_fun.__cache = {}
        new_fun.__cache_times = {}
        new_fun.clear_cache = clear_cache
        new_fun.dirty = dirty
        new_fun.fn = fun
        return new_fun

    return cache_fun
