# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service_rpc.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11service_rpc.proto\")\n\x14lookupRequestMessage\x12\x11\n\tstockname\x18\x01 \x02(\t\"!\n\rleaderMessage\x12\x10\n\x08leaderId\x18\x01 \x02(\x05\"R\n\x12leaderOrderMessage\x12\x10\n\x08leaderId\x18\x01 \x02(\x05\x12\x13\n\x0b\x66ollowerIds\x18\x02 \x03(\x05\x12\x15\n\rfollowerPorts\x18\x03 \x03(\x05\" \n\x0eleaderResponse\x12\x0e\n\x06result\x18\x01 \x02(\x08\"h\n\x15lookupResponseMessage\x12\x1b\n\x05\x65rror\x18\x01 \x02(\x0e\x32\x0c.ERROR_CODES\x12\x11\n\tstockname\x18\x02 \x01(\t\x12\r\n\x05price\x18\x03 \x01(\x02\x12\x10\n\x08quantity\x18\x04 \x01(\x05\"[\n\x13orderRequestMessage\x12\x11\n\tstockname\x18\x01 \x02(\t\x12\x10\n\x08quantity\x18\x02 \x02(\x05\x12\x0c\n\x04type\x18\x03 \x02(\t\x12\x11\n\tserviceId\x18\x04 \x02(\x05\"3\n\x14orderResponseMessage\x12\x1b\n\x05\x65rror\x18\x01 \x02(\x0e\x32\x0c.ERROR_CODES\"H\n\x13tradeRequestMessage\x12\x11\n\tstockname\x18\x01 \x02(\t\x12\x10\n\x08quantity\x18\x02 \x02(\x05\x12\x0c\n\x04type\x18\x03 \x02(\t\"O\n\x14tradeResponseMessage\x12\x1b\n\x05\x65rror\x18\x01 \x02(\x0e\x32\x0c.ERROR_CODES\x12\x1a\n\x12transaction_number\x18\x02 \x01(\x05\"\x1c\n\x0c\x63heckMessage\x12\x0c\n\x04ping\x18\x01 \x02(\t\"0\n\rcheckResponse\x12\x10\n\x08response\x18\x01 \x01(\t\x12\r\n\x05\x65rror\x18\x02 \x01(\t*v\n\x0b\x45RROR_CODES\x12\x0c\n\x08NO_ERROR\x10\x00\x12\x15\n\x11INVALID_STOCKNAME\x10\x01\x12\x12\n\x0eINTERNAL_ERROR\x10\x02\x12\x19\n\x15INSUFFICIENT_QUANTITY\x10\x03\x12\x13\n\x0fINVALID_REQUEST\x10\x04\x32\xb2\x01\n\x07\x43\x61talog\x12\x37\n\x06lookup\x12\x15.lookupRequestMessage\x1a\x16.lookupResponseMessage\x12@\n\x11\x62uy_or_sell_stock\x12\x14.orderRequestMessage\x1a\x15.orderResponseMessage\x12,\n\tsetLeader\x12\x0e.leaderMessage\x1a\x0f.leaderResponse2\x9e\x01\n\x05Order\x12\x34\n\x05trade\x12\x14.tradeRequestMessage\x1a\x15.tradeResponseMessage\x12,\n\x0bhealthCheck\x12\r.checkMessage\x1a\x0e.checkResponse\x12\x31\n\tsetLeader\x12\x13.leaderOrderMessage\x1a\x0f.leaderResponse')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_rpc_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ERROR_CODES._serialized_start=704
  _ERROR_CODES._serialized_end=822
  _LOOKUPREQUESTMESSAGE._serialized_start=21
  _LOOKUPREQUESTMESSAGE._serialized_end=62
  _LEADERMESSAGE._serialized_start=64
  _LEADERMESSAGE._serialized_end=97
  _LEADERORDERMESSAGE._serialized_start=99
  _LEADERORDERMESSAGE._serialized_end=181
  _LEADERRESPONSE._serialized_start=183
  _LEADERRESPONSE._serialized_end=215
  _LOOKUPRESPONSEMESSAGE._serialized_start=217
  _LOOKUPRESPONSEMESSAGE._serialized_end=321
  _ORDERREQUESTMESSAGE._serialized_start=323
  _ORDERREQUESTMESSAGE._serialized_end=414
  _ORDERRESPONSEMESSAGE._serialized_start=416
  _ORDERRESPONSEMESSAGE._serialized_end=467
  _TRADEREQUESTMESSAGE._serialized_start=469
  _TRADEREQUESTMESSAGE._serialized_end=541
  _TRADERESPONSEMESSAGE._serialized_start=543
  _TRADERESPONSEMESSAGE._serialized_end=622
  _CHECKMESSAGE._serialized_start=624
  _CHECKMESSAGE._serialized_end=652
  _CHECKRESPONSE._serialized_start=654
  _CHECKRESPONSE._serialized_end=702
  _CATALOG._serialized_start=825
  _CATALOG._serialized_end=1003
  _ORDER._serialized_start=1006
  _ORDER._serialized_end=1164
# @@protoc_insertion_point(module_scope)
