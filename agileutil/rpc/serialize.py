#coding=utf-8

import pickle
import json
from abc import ABCMeta, abstractmethod


class RpcSerialize(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass
    
    @abstractmethod
    def serialize(cls, obj) -> bytes:
        pass

    @abstractmethod
    def unserialize(cls, bytearr):
        pass


class BinarySerialize(RpcSerialize):

    def __init__(self):
        pass

    @classmethod
    def serialize(cls, obj) -> bytes:
        return pickle.dumps(obj)

    @classmethod
    def unserialize(cls, bytearr):
        return pickle.loads(bytearr)


class JsonSerialize(RpcSerialize):

    def __init__(self):
        pass

    @classmethod
    def serialize(cls, obj) -> bytes:
        return json.dumps(obj)

    @classmethod
    def unserialize(cls, bytearr):
        return json.loads(bytearr)