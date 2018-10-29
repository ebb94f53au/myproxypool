#coding=utf-8
from proxypool.utils import get_page
from pyquery import PyQuery as pq
import re
'''

获取代理ip
'''

class ProxyMetaclass(type):
    """
        元类，在FreeProxyGetter类中加入
        __CrawlFunc__和__CrawlFuncCount__
        两个参数，分别表示爬虫函数，和爬虫函数的数量。
    """
    def __new__(cls,name,bases,attrs):
        count=0
        attrs['__CrawlFunc__']=[]
        for k,v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count+=1
        attrs['__CrawlFuncCount__']=count
        # print(count)
        # print(attrs['__CrawlFunc__'])
        return type.__new__(cls,name,bases,attrs)


import json
class FreeProxyGetter(object, metaclass=ProxyMetaclass):
    def get_raw_proxies(self, callback):
        #根据返回的名字调用函数,
        proxies=[]
        print('Callback', callback)
        for proxy in eval('self.{}()'.format(callback)):
            print('getting',proxy,'from',callback)
            proxies.append(proxy)
        return proxies

    def crawl_ip181(self):
        start_url = 'http://www.ip181.com/'
        text=get_page(start_url)
        try:
            a=json.loads(text)['RESULT']
            for item in a:
                result=item['ip']+':'+item['port']
                yield result.replace(' ','')
        except:
            return None

    def crawl_kuaidaili(self):
        for page in range(1, 2):
            # 国内高匿代理
            start_url = 'https://www.kuaidaili.com/free/inha/{}/'.format(page)
            text=get_page(start_url)
            doc=pq(text)
            for item in doc('#list > table > tbody > tr').items():
                ip=item('td:nth-child(1)').text()
                port=item('td:nth-child(2)').text()
                if not ip or not port or '.'not in ip:
                    #如果不存在ip或者port 跳过
                    continue
                result=ip+':'+port
                yield result.replace(' ','')

    def crawl_xicidaili(self):
        for page in range(1, 4):
            start_url = 'http://www.xicidaili.com/wt/{}'.format(page)
            text=get_page(start_url)
            doc = pq(text)
            for item in doc('#ip_list  > tr').items():
                ip =item('td:nth-child(2)').text()
                port =item('td:nth-child(3)').text()
                if not ip or not port or '.'not in ip:
                    #如果不存在ip或者port 跳过
                    continue
                result = ip + ':' + port
                yield result.replace(' ', '')

    def crawl_daili66(self):
        for page in range(1,4):
            start_url ='http://www.66ip.cn/{}.html'.format(page)
            text = get_page(start_url)
            doc = pq(text)
            for item in doc('table >  tr').items():
                ip = item('td:nth-child(1)').text()
                port = item('td:nth-child(2)').text()
                if not ip or not port or '.'not in ip:
                    # 如果不存在ip或者port 跳过,或者ip没有'.'作为判断
                    continue
                result = ip + ':' + port
                yield result.replace(' ', '')

    def crawl_data5u(self):
        for i in ['gngn', 'gnpt']:
            start_url = 'http://www.data5u.com/free/{}/index.shtml'.format(i)
            text = get_page(start_url)
            doc = pq(text)
            for item in doc('.l2').items():
                ip = item('span:nth-child(1) > li').text()
                port = item('span:nth-child(2) > li').text()
                if not ip or not port or '.' not in ip:
                    # 如果不存在ip或者port 跳过,或者ip没有'.'作为判断
                    continue
                result = ip + ':' + port
                yield result.replace(' ', '')

    def crawl_89ip(self):
        start_url='http://www.89ip.cn/tqdl.html?api=1&num=100&port=&address=&isp='
        text = get_page(start_url)

        # a=re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]{1,5}',text)
        for i in re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]{1,5}',text):
            yield i

if __name__ == '__main__':
    f=FreeProxyGetter()
    print([i for i in f.crawl_89ip()])
