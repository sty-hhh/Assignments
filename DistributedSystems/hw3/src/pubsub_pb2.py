# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pubsub.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cpubsub.proto\x12\x0brpc_package\"\x1a\n\nmes2server\x12\x0c\n\x04mes1\x18\x01 \x01(\t\"\x1a\n\nmes2client\x12\x0c\n\x04mes2\x18\x01 \x01(\t2K\n\x06pubsub\x12\x41\n\x0bpubsubServe\x12\x17.rpc_package.mes2server\x1a\x17.rpc_package.mes2client\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'pubsub_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MES2SERVER._serialized_start=29
  _MES2SERVER._serialized_end=55
  _MES2CLIENT._serialized_start=57
  _MES2CLIENT._serialized_end=83
  _PUBSUB._serialized_start=85
  _PUBSUB._serialized_end=160
# @@protoc_insertion_point(module_scope)