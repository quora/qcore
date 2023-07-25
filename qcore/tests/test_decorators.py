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

from qcore import (
    convert_result,
    decorate,
    decorator_of_context_manager,
    DecoratorBase,
    deprecated,
    retry,
    get_original_fn,
    DecoratorBinder,
)
from qcore.asserts import assert_eq, assert_is, assert_in, assert_ne, AssertRaises
import inspect
import pickle
from unittest import mock


@deprecated("Deprecated.")
def deprecated_fn():
    pass


@deprecated("Deprecated.")
class DeprecatedClass:
    pass


def test_deprecated():
    fn = deprecated_fn
    fn.__doc__.startswith("Deprecated")

    # should not fail
    deprecated("Deprecated.")(3)


def test_convert_result():
    @convert_result(list)
    def test1(*args):
        for a in args:
            yield a

    result = test1(1, 2)
    assert_is(list, result.__class__)
    assert_eq([1, 2], result)


class AnyException(Exception):
    pass


class AnyOtherException(Exception):
    pass


@retry(Exception)
def retry_it():
    pass


class TestRetry:
    def create_generator_function(self, exception_type, max_tries):
        fn_body = mock.Mock()
        fn_body.return_value = range(3)

        @retry(exception_type, max_tries=max_tries)
        def any_function(*args, **kwargs):
            for it in fn_body(*args, **kwargs):
                yield it

        return any_function, fn_body

    def create_any_function(self, exception_type, max_tries):
        fn_body = mock.Mock()
        fn_body.return_value = []

        @retry(exception_type, max_tries=max_tries)
        def any_function(*args, **kwargs):
            return fn_body(*args, **kwargs)

        return any_function, fn_body

    def test_pickling(self):
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(retry_it, protocol=protocol)
            assert_is(retry_it, pickle.loads(pickled))

    def test_retry_passes_all_arguments(self):
        any_expected_exception_type = AnyException

        for method in (self.create_any_function, self.create_generator_function):
            any_function, fn_body = method(any_expected_exception_type, max_tries=2)
            list(any_function(1, 2, foo=3))
            fn_body.assert_called_once_with(1, 2, foo=3)

    def test_retry_does_not_retry_on_no_exception(self):
        any_expected_exception_type = AnyException

        for method in (self.create_any_function, self.create_generator_function):
            any_function, fn_body = method(any_expected_exception_type, max_tries=3)
            list(any_function())
            fn_body.assert_called_once_with()

    def test_retry_does_not_retry_on_unspecified_exception(self):
        any_expected_exception_type = AnyException
        any_unexpected_exception_type = AnyOtherException

        for method in (self.create_any_function, self.create_generator_function):
            any_function, fn_body = method(any_expected_exception_type, max_tries=3)
            fn_body.side_effect = any_unexpected_exception_type

            with AssertRaises(any_unexpected_exception_type):
                list(any_function())

            fn_body.assert_called_once_with()

    def test_retry_retries_on_provided_exception(self):
        max_tries = 4
        any_expected_exception_type = AnyException

        for method in (self.create_any_function, self.create_generator_function):
            any_function, fn_body = method(any_expected_exception_type, max_tries)
            fn_body.side_effect = any_expected_exception_type

            with AssertRaises(any_expected_exception_type):
                list(any_function())

            assert_eq(max_tries, fn_body.call_count)

    def test_retry_requires_max_try_at_least_one(self):
        any_expected_exception_type = AnyException
        for method in (self.create_any_function, self.create_generator_function):
            with AssertRaises(Exception):
                method(any_expected_exception_type, max_tries=0)
            method(any_expected_exception_type, max_tries=1)

    def test_retry_can_take_multiple_exceptions(self):
        max_tries = 4
        any_expected_exception_type = AnyException
        any_other_expected_exception_type = AnyOtherException

        expected_exceptions = (
            any_expected_exception_type,
            any_other_expected_exception_type,
        )

        for method in (self.create_any_function, self.create_generator_function):
            any_function, fn_body = method(expected_exceptions, max_tries)
            fn_body.side_effect = any_expected_exception_type

            with AssertRaises(any_expected_exception_type):
                list(any_function())

            assert_eq(max_tries, fn_body.call_count)
            fn_body.reset_mock()

            fn_body.side_effect = any_other_expected_exception_type

            with AssertRaises(any_other_expected_exception_type):
                list(any_function())

            assert_eq(max_tries, fn_body.call_count)

    def test_retry_preserves_argspec(self):
        def fn(foo, bar, baz=None, **kwargs):
            pass

        decorated = retry(Exception)(fn)

        assert_eq(inspect.signature(fn), inspect.signature(get_original_fn(decorated)))


def test_decorator_of_context_manager():
    data = []

    class Context:
        "Dummy context"

        def __init__(self, key):
            self.key = key

        def __enter__(self):
            data.append("enter %s" % self.key)

        def __exit__(self, *args):
            data.append("exit %s" % self.key)

    decorator = decorator_of_context_manager(Context)

    @decorator("maras")
    def decorated():
        data.append("inside maras")

    assert_eq("Dummy context", decorator.__doc__)

    decorated()

    assert_eq(["enter maras", "inside maras", "exit maras"], data)

    class NoDocString:
        def __enter__(self):
            pass

        def __exit__(self, *args):
            pass

    assert_eq(
        "Decorator that runs the inner function in the context of {}".format(
            NoDocString
        ),
        decorator_of_context_manager(NoDocString).__doc__,
    )


class UselessDecorator(DecoratorBase):
    def name(self):
        return "UselessDecorator"


def useless_decorator(fn):
    return decorate(UselessDecorator)(fn)


@useless_decorator
def decorated_fn():
    pass


def test_decorated_fn_name():
    # test that the decorator preserves the __module__
    assert_in("test_decorators", decorated_fn.__module__)


class CacheDecoratorBinder(DecoratorBinder):
    def dirty(self, *args):
        if self.instance is None:
            return self.decorator.dirty(*args)
        else:
            return self.decorator.dirty(self.instance, *args)


class CacheDecorator(DecoratorBase):
    binder_cls = CacheDecoratorBinder

    def __init__(self, *args):
        super().__init__(*args)
        self._cache = {}

    def name(self):
        return "@cached"

    def dirty(self, *args):
        try:
            del self._cache[args]
        except KeyError:
            pass

    def __call__(self, *args):
        try:
            return self._cache[args]
        except KeyError:
            value = self.fn(*args)
            self._cache[args] = value
            return value


cached = decorate(CacheDecorator)

i = 0


@cached
def f(a, b):
    global i
    i += 1
    return a + b + i


class CachedMethods:
    @cached
    def f(self, a, b):
        global i
        i += 1
        return a + b + i

    @cached
    @classmethod
    def cached_classmethod(cls, a, b):
        global i
        i += 1
        return a + b + i

    @cached
    @staticmethod
    def cached_staticmethod(a, b):
        global i
        i += 1
        return a + b + i

    @cached
    @cached
    @classmethod
    def double_cached(cls, a, b):
        global i
        i += 1
        return a + b + i

    def __str__(self):
        return "CachedMethods()"

    def __repr__(self):
        return str(self)


class TestDecorators:
    def setup_method(self):
        global i
        i = 0

    def test_cached(self):
        global i
        instance = CachedMethods()
        methods = [
            f,
            instance.f,
            CachedMethods.cached_classmethod,
            CachedMethods.cached_staticmethod,
        ]

        for method in methods:
            i = 0
            assert method.is_decorator()
            assert_eq("@cached", method.name())
            assert_eq(3, method(1, 1))
            assert_eq(3, method(1, 1))
            method.dirty(2, 1)
            assert_eq(3, method(1, 1))
            method.dirty(1, 1)
            assert_eq(4, method(1, 1))

    def test_unbound_method(self):
        instance = CachedMethods()
        assert_eq(3, CachedMethods.f(instance, 1, 1))
        assert_eq(3, CachedMethods.f(instance, 1, 1))
        CachedMethods.f.dirty(instance, 1, 2)
        assert_eq(3, CachedMethods.f(instance, 1, 1))
        CachedMethods.f.dirty(instance, 1, 1)
        assert_eq(4, CachedMethods.f(instance, 1, 1))

    def test_decorator_str_and_repr(self):
        cases = [
            (f, "@cached test_decorators.f"),
            (CachedMethods().f, "<@cached test_decorators.f bound to CachedMethods()>"),
            (CachedMethods.f, "<@cached test_decorators.f unbound>"),
            (
                CachedMethods.cached_classmethod,
                (
                    "<@cached test_decorators.cached_classmethod bound to <class "
                    "'test_decorators.CachedMethods'>>"
                ),
            ),
            (
                CachedMethods.cached_staticmethod,
                "@cached test_decorators.cached_staticmethod",
            ),
        ]
        for method, expected in cases:
            assert_eq(expected, str(method))
            assert_eq(expected, repr(method))

    def test_binder_equality(self):
        assert_eq(CachedMethods.f, CachedMethods.f)
        instance = CachedMethods()
        assert_eq(instance.f, instance.f)
        assert_ne(instance.f, CachedMethods.f)
        assert_eq(1, len({instance.f, instance.f}))

    def test_double_caching(self):
        assert_eq(3, CachedMethods.double_cached(1, 1))
        assert_eq(3, CachedMethods.double_cached(1, 1))
        CachedMethods.double_cached.dirty(1, 1)
        assert_eq(3, CachedMethods.double_cached(1, 1))
        CachedMethods.double_cached.decorator.fn.dirty(CachedMethods, 1, 1)
        assert_eq(3, CachedMethods.double_cached(1, 1))
        CachedMethods.double_cached.dirty(1, 1)
        CachedMethods.double_cached.decorator.fn.dirty(CachedMethods, 1, 1)
        assert_eq(4, CachedMethods.double_cached(1, 1))

    def test_pickling(self):
        f.dirty(1, 1)
        pickled = pickle.dumps(f)
        unpickled = pickle.loads(pickled)
        assert_eq(3, unpickled(1, 1))
