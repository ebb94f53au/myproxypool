#coding=utf-8
from proxypool.db import RedisClient
import aiohttp
import asyncio
from proxypool.setting import TEST_API,PROXY_TIMEOUT,POOL_LOWER_THRESHOLD,POOL_UPPER_THRESHOLD,VALID_CHECK_TIME,POOL_LEN_CHECK_TIME
try:
    from aiohttp.errors import ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
from asyncio import TimeoutError
from proxypool.getter import FreeProxyGetter
import time
from multiprocessing import Process
'''
调度器主要分为2个工作，
一个是爬取目标站点的代理ip、并检查是否可用、再存储下来，
另一个是检查原有的代理ip现在能不能使用
'''
class ValidityTester(object):
    #检查代理是否可用,并保存。
    def __init__(self):
        self._raw_proxies=None
    def set_raw_proxies(self,proxies):
        self._raw_proxies=proxies
        self._redis=RedisClient()
    async def check_single_proxy(self,proxy):
        #检查单个代理
        if isinstance(proxy,bytes):
            proxy=proxy.decode('utf-8')
        real_proxy='http://'+proxy
        try:
            async with aiohttp.ClientSession() as session:

                try:
                    async with session.get(TEST_API,proxy=real_proxy,timeout=PROXY_TIMEOUT) as response:
                        print('Check proxy',proxy)
                        if response.status==200:
                            self._redis.add(proxy)
                            print('Add to redis',proxy)
                except (ProxyConnectionError,TimeoutError):
                    print('Dont add to proxy',proxy)
                    await session.close()

        except(ServerDisconnectedError, ClientResponseError,ClientConnectorError,Exception) as s:
            print(s)
            await session.close()

    def check_some_proxies(self):
        '''
        建立循环消息圈：循环检查_raw_proxies中的代理ip
        _raw_proxies 为空或者None 抛出异常
        '''
        if not self._raw_proxies:
            return
        try:
            print('Check_some_proxies Ing')
            loop=asyncio.get_event_loop()
            tasks=[self.check_single_proxy(task) for task in self._raw_proxies]
            loop.run_until_complete(asyncio.wait(tasks))
        except:
            print('Check_some_proxies Error')


class GetNewProxy(object):
    #得到新的代理ip
    def __init__(self,max):
        self._max_count=max
        self._redis=RedisClient()
        self._tester=ValidityTester()
        self._getter=FreeProxyGetter()
    def is_over(self):
        #是否超过总数
        print(self._redis.len())
        if self._redis.len()>=self._max_count:
            return True
        else:
            return False

    def add_new_proxy(self):
        #增加新的代理ip到代理池中
        print('Add and get new proxy')
        while not self.is_over():
            for callback in range(self._getter.__CrawlFuncCount__):
                # print(self._getter.__CrawlFunc__[callback])
                self._tester.set_raw_proxies(self._getter.get_raw_proxies(self._getter.__CrawlFunc__[callback]))
                self._tester.check_some_proxies()
                if self.is_over():
                    print('IP is enough, waiting to be used')
                    break






class Schedule(object):
    '''

    '''


    @staticmethod
    def checkproxypool(wait_time=VALID_CHECK_TIME):
        #检查原有的代理池
        print('Checking pool')
        tester = ValidityTester()
        redis=RedisClient()
        while True:
            halfcount = int(redis.len() / 2)
            if halfcount==0:
                time.sleep(wait_time)
                continue
            halfproxies = redis.cget(halfcount)
            tester.set_raw_proxies(halfproxies)
            tester.check_some_proxies()
            time.sleep(wait_time)

    @staticmethod
    def addnewproxy(wait_time=POOL_LEN_CHECK_TIME,min_count=POOL_LOWER_THRESHOLD):
        #增加新的代理ip
        g = GetNewProxy(POOL_UPPER_THRESHOLD)
        redis=RedisClient()

        while True:
            if redis.len()<min_count:
                print('Add new Proxies')
                g.add_new_proxy()
            time.sleep(wait_time)


    def run(self):
        print('Process is running')
        check_pro=Process(target=self.checkproxypool)
        add_pro=Process(target=self.addnewproxy)
        add_pro.start()
        check_pro.start()



if __name__ == '__main__':

    a=Schedule()
    a.run()
