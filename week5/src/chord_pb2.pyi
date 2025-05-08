from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SaveDataMessage(_message.Message):
    __slots__ = ("key", "text")
    KEY_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    key: str
    text: str
    def __init__(self, key: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class RemoveDataMessage(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class FindDataMessage(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class GetFingerTableMessage(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SaveDataResponse(_message.Message):
    __slots__ = ("node_id", "status")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    node_id: int
    status: bool
    def __init__(self, node_id: _Optional[int] = ..., status: bool = ...) -> None: ...

class RemoveDataResponse(_message.Message):
    __slots__ = ("node_id", "status")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    node_id: int
    status: bool
    def __init__(self, node_id: _Optional[int] = ..., status: bool = ...) -> None: ...

class FindDataResponse(_message.Message):
    __slots__ = ("node_id", "data")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    node_id: int
    data: str
    def __init__(self, node_id: _Optional[int] = ..., data: _Optional[str] = ...) -> None: ...

class GetFingerTableResponse(_message.Message):
    __slots__ = ("finger_table",)
    FINGER_TABLE_FIELD_NUMBER: _ClassVar[int]
    finger_table: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, finger_table: _Optional[_Iterable[int]] = ...) -> None: ...
