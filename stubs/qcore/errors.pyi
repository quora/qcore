from mypy_extensions import NoReturn
from types import TracebackType
from typing import Optional, Tuple, Type, TypeVar

class ArgumentError(RuntimeError): ...
class OperationError(RuntimeError): ...
class NotSupportedError(OperationError): ...
class SecurityError(OperationError): ...
class PermissionError(SecurityError): ...
class TimeoutError(RuntimeError): ...

_ExceptionT = TypeVar('_ExceptionT', bound=BaseException)

def prepare_for_reraise(error: _ExceptionT, exc_info: Optional[Tuple[Type[BaseException], BaseException, TracebackType]] = ...) -> _ExceptionT: ...
def reraise(error: BaseException) -> NoReturn: ...
