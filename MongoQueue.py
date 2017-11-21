# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
from pymongo import MongoClient

class MongoQueue:

    OUTSTANDING, PROCESSING, COMPLETE = range(3)

    def __init__(self, client=None, db_name='db_name', collect_name='collect_name', timeout=60):
        self.client = MongoClient('localhost', 27017) if client is None else client             # 创建数据库
        self.db = self.client[db_name]                                                          # 定义数据库名db_name
        self.collect = self.db[collect_name]                                                    # 定义集合名collect_name，或使用方法createCollection()
        self.timeout = timeout

    def __nonzero__(self):
        record = self.collect.find_one({'status': {'$ne': self.COMPLETE}})
        return True if record else False

    def push(self, url):
        self.collect.insert({'_id': url, 'status': self.OUTSTANDING, 'depth': 0})

    def pop(self):
        record = self.collect.find_and_modify(
            query={'status': self.OUTSTANDING},
            update={'$set': {'status': self.PROCESSING,
                             'timestamp': datetime.utcnow()}}
        )

        if record:
            return record['_id']
        else:
            self.repair()                                                   # 没有待处理的url时，则检查处理中的url是否超时，超时则重新设为待处理
            raise KeyError()

    def peek(self):
        record = self.collect.find_one({'status': self.OUTSTANDING})
        if record:
            return record['_id']

    def get_depth(self, url):
        record = self.collect.find_one({'_id': url})
        return record['depth']

    def update_depth(self, url):
        self.collect.update({'_id': url},
                                   {'$inc': {'depth': 1}})                  # '$inc'表示增减，1指定步长（正增负减）

    def complete(self, url):
        self.collect.update({'_id': url},
                                    {'$set': {'status': self.COMPLETE}})

    def repair(self):
                                                                            # find_and_modify：有返回值，modify可以是update，还可以是remove
        record = self.collect.find_and_modify(
            query={
                'timestamp': {'$lt': datetime.utcnow() -
                              timedelta(seconds=self.timeout)},
                'status': {'$ne': self.COMPLETE}
            },
            update={'$set': {'status': self.OUTSTANDING}}
        )                                                                   # '$lt'表示小于，'$ne'表示不相等

        if record:
            print 'Released:', record['_id']

    def clear(self):
        self.collect.drop()
