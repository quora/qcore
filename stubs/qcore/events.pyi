from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Type, TypeVar
from types import TracebackType

_HandlerT = Callable[..., Any]

class EventHook(object):
    def __init__(self, handlers: Optional[List[_HandlerT]] = ...) -> None: ...
    def subscribe(self, handler: _HandlerT) -> None: ...
    def unsubscribe(self, handler: _HandlerT) -> None: ...
    def safe_trigger(self, *args: Any) -> None: ...
    def trigger(self, *args: Any) -> None: ...
    def __call__(self, *args: Any) -> None: ...
    def __contains__(self, item: _HandlerT) -> bool: ...
    def __iter__(self) -> Iterator[_HandlerT]: ...

class SinkingEventHook(EventHook): ...

sinking_event_hook: SinkingEventHook

class EventInterceptor(object):
    source: object
    events: Dict[str, _HandlerT]
    def __init__(self, source: object, **events: _HandlerT) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(self, typ: Optional[Type[BaseException]], value: Optional[BaseException], traceback: Optional[TracebackType]) -> None: ...

_HubT = TypeVar('_HubT', bound=EventHub)

class EventHub(object):
    def __init__(self, source: Optional[Dict[Any, Any]] = ...) -> None: ...
    def on(self: _HubT, event: object, handler: _HandlerT) -> _HubT: ...
    def off(self: _HubT, event: object, handler: _HandlerT) -> _HubT: ...
    def trigger(self: _HubT, event: object, *args: Any) -> _HubT: ...
    def safe_trigger(self: _HubT, event: object, *args: Any) -> _HubT: ...
    def get_or_create(self, event: object) -> EventHook: ...
    def __getattr__(self, key: str) -> EventHook: ...
    def __contains__(self, item: str) -> bool: ...
    def __len__(self) -> int: ...
    def __getitem__(self, item: str) -> EventHook: ...
    def __setitem__(self, key: str, value: EventHook) -> None: ...
    def __delitem__(self, key: str) -> None: ...
    def __iter__(self) -> Iterator[Tuple[str, EventHook]]: ...

class EnumBasedEventHubType(type): ...
class EnumBasedEventHub(EventHub, metaclass=EnumBasedEventHubType): ...

hub: EventHub
