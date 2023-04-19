from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
INSUFFICIENT_QUANTITY: ERROR_CODES
INTERNAL_ERROR: ERROR_CODES
INVALID_ORDERNUMBER: ERROR_CODES
INVALID_REQUEST: ERROR_CODES
INVALID_STOCKNAME: ERROR_CODES
NO_ERROR: ERROR_CODES

class lookupOrderRequestMessage(_message.Message):
    __slots__ = ["order_number"]
    ORDER_NUMBER_FIELD_NUMBER: _ClassVar[int]
    order_number: int
    def __init__(self, order_number: _Optional[int] = ...) -> None: ...

class lookupOrderResponseMessage(_message.Message):
    __slots__ = ["error", "name", "number", "quantity", "type"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    error: ERROR_CODES
    name: str
    number: int
    quantity: int
    type: str
    def __init__(self, error: _Optional[_Union[ERROR_CODES, str]] = ..., number: _Optional[int] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...

class lookupRequestMessage(_message.Message):
    __slots__ = ["stockname"]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    stockname: str
    def __init__(self, stockname: _Optional[str] = ...) -> None: ...

class lookupResponseMessage(_message.Message):
    __slots__ = ["error", "price", "quantity", "stockname"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    error: ERROR_CODES
    price: float
    quantity: int
    stockname: str
    def __init__(self, error: _Optional[_Union[ERROR_CODES, str]] = ..., stockname: _Optional[str] = ..., price: _Optional[float] = ..., quantity: _Optional[int] = ...) -> None: ...

class orderRequestMessage(_message.Message):
    __slots__ = ["quantity", "stockname", "type"]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    stockname: str
    type: str
    def __init__(self, stockname: _Optional[str] = ..., quantity: _Optional[int] = ..., type: _Optional[str] = ...) -> None: ...

class orderResponseMessage(_message.Message):
    __slots__ = ["error"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: ERROR_CODES
    def __init__(self, error: _Optional[_Union[ERROR_CODES, str]] = ...) -> None: ...

class tradeRequestMessage(_message.Message):
    __slots__ = ["quantity", "stockname", "type"]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    stockname: str
    type: str
    def __init__(self, stockname: _Optional[str] = ..., quantity: _Optional[int] = ..., type: _Optional[str] = ...) -> None: ...

class tradeResponseMessage(_message.Message):
    __slots__ = ["error", "transaction_number"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    error: ERROR_CODES
    transaction_number: int
    def __init__(self, error: _Optional[_Union[ERROR_CODES, str]] = ..., transaction_number: _Optional[int] = ...) -> None: ...

class ERROR_CODES(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
