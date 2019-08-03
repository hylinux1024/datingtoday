# coding=utf-8

import redis
import pickle
import json
import datetime

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)


class Redis:
    @staticmethod
    def connect(db=0):
        r = redis.Redis(connection_pool=pool, db=db)
        return r

    # 将内存数据二进制通过序列号转为文本流，再存入redis
    @staticmethod
    def set(r, key: str, data, ex=None):
        r.set(key, json.dumps(data, cls=CJsonEncoder), ex=ex)

    # 将文本流从redis中读取并反序列化，返回
    @staticmethod
    def get(r, key: str):
        data = r.get(key)
        if data is None:
            return None

        return json.loads(data)


# def serialize_instance(obj):
#     d = {'__classname__': type(obj).__name__}
#     d.update(vars(obj))
#     return d
#
#
# def unserialize_object(d):
#     clsname = d.pop('__classname__', None)
#     if clsname:
#         cls = classes[clsname]
#         obj = cls.__new__(cls)  # Make instance without calling __init__
#         for key, value in d.items():
#             setattr(obj, key, value)
#         return obj
#     else:
#         return d


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
