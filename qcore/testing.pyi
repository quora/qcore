from typing import Any, Callable, Type

TEST_PREFIX: str
Anything: Any

class GreaterEq:
    val: object
    def __init__(self, val: object) -> None: ...

def disabled(func_or_class: Any) -> Any: ...
def decorate_all_test_methods(
    decorator: Callable[[Callable[..., Any]], Any]
) -> Callable[[Type[object]], Type[object]]: ...
def decorate_func_or_method_or_class(
    decorator: Callable[[Callable[..., Any]], Any]
) -> Callable[[Any], Any]: ...
