#coding=utf-8
from proxypool.schedule import Schedule
from proxypool.api import app
# s=Schedule()
# s.run()
#web 服务器运行
if __name__ == '__main__':
    s=Schedule()
    s.run()
    app.run()