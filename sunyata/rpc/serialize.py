import pickle
import ujson
from abc import ABCMeta, abstractmethod


class RpcSerialize(object):

    __metaclass__ = ABCMeta
    
    @abstractmethod
    def serialize(cls, obj) -> bytes:
        pass

    @abstractmethod
    def unserialize(cls, bytearr):
        pass


class BinarySerialize(RpcSerialize):

    @classmethod
    def serialize(cls, obj) -> bytes:
        return pickle.dumps(obj)

    @classmethod
    def unserialize(cls, bytearr):
        return pickle.loads(bytearr)


class JsonSerialize(RpcSerialize):

    @classmethod
    def serialize(cls, obj) -> bytes:
        return ujson.dumps(obj)

    @classmethod
    def unserialize(cls, bytearr):
        return ujson.loads(bytearr)