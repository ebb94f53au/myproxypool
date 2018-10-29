import redis
from proxypool.setting import RedisHost,Redisdb,RedisPort,RedisPwd

import random
'''
数据库类，连接redis数据库，并增加 增删查等常用功能
'''
class RedisClient(object):
    def __init__(self):
        if RedisPwd:
            self._db = redis.Redis(host=RedisHost,port=RedisPort,db=Redisdb)
        else:
            self._db = redis.Redis(host=RedisHost, port=RedisPort, db=Redisdb,password=RedisPwd)

    def add(self,value):
        #增加代理
        self._db.rpush('proxy',value)

    def rget(self):
        #随机取代理
        temp=random.randint(0,self.len()-1)
        return self._db.lrange('proxy',temp,temp)[0]

    def cget(self,count=1):
        #检查代理列表，从头开始检查,取出多少删除多少
        proxies=self._db.lrange('proxy',0,count-1)
        self._db.ltrim('proxy',count,-1)
        return list(set(proxies))


    def len(self):
        #列表总长
        return self._db.llen('proxy')

    def flush(self):
        #删除所有代理
        self._db.delete('proxy')

if __name__ == '__main__':
    db=RedisClient()
    a=db._db.sadd('proxy1',1)
    a=db._db.sadd('proxy1',2)
    a=db._db.sadd('proxy1',1)
    print(a)


