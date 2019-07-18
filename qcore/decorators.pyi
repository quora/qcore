from abc import abstractmethod
from typing import (
    Any,
    Callable,
    ContextManager,
    Generic,
    Tuple,
    Type,
    TypeVar,
    Optional,
    Union,
)

_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])
_T = TypeVar("_T")

class DecoratorBinder(Generic[_T]):
    decorator: DecoratorBase[_T]
    instance: Optional[object]
    def __init__(
        self, decorator: DecoratorBase[_T], instance: Optional[object] = ...
    ) -> None: ...
    def name(self) -> str: ...
    def is_decorator(self) -> bool: ...
    def __call__(self, *args: Any, **kwargs: Any) -> _T: ...

class DecoratorBase(Generic[_T]):
    binder_cls: Type[DecoratorBinder[_T]]
    def __init__(self, fn: Callable[..., _T]) -> None: ...
    @abstractmethod
    def name(self) -> str: ...
    def is_decorator(self) -> bool: ...
    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> _T: ...
    def __get__(self, owner: object, cls: Type[object]) -> DecoratorBinder[_T]: ...

def decorate(
    decorator_cls: Type[DecoratorBase[_T]], *args: Any, **kwargs: Any
) -> Callable[[Callable[..., _T]], Callable[..., _T]]: ...
def deprecated(replacement_description: str) -> Callable[[_CallableT], _CallableT]: ...

_InputT = TypeVar("_InputT")
_OutputT = TypeVar("_OutputT")

def convert_result(
    converter: Callable[[_InputT], _OutputT]
) -> Callable[[Callable[..., _InputT]], Callable[..., _OutputT]]: ...
def retry(
    exception_cls: Union[Type[BaseException], Tuple[Type[BaseException], ...]],
    max_tries: int = ...,
    sleep: float = ...,
) -> Callable[[_CallableT], _CallableT]: ...
def decorator_of_context_manager(
    ctxt: Callable[..., ContextManager[Any]]
) -> Callable[..., Callable[[_CallableT], _CallableT]]: ...
