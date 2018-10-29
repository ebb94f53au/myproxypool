import requests
from requests.exceptions import ConnectionError
'''
工具类
'''

def get_page(url):
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6756.400 QQBrowser/10.3.2473.400',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    try:
        print('Getting', url)
        response=requests.get(url,headers=headers)
        print('Getting result', url, response.status_code)
        if response.status_code==200:
            return response.text
        else:
            return None
    except ConnectionError:
        print('Crawling Failed', url)
        return None
