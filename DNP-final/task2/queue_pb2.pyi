from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class item(_message.Message):
    __slots__ = ("item",)
    ITEM_FIELD_NUMBER: _ClassVar[int]
    item: str
    def __init__(self, item: _Optional[str] = ...) -> None: ...

class size(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: int
    def __init__(self, size: _Optional[int] = ...) -> None: ...

class empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class isFull(_message.Message):
    __slots__ = ("full",)
    FULL_FIELD_NUMBER: _ClassVar[int]
    full: bool
    def __init__(self, full: bool = ...) -> None: ...
