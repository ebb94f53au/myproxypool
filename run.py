from proxypool.schedule import Schedule
from proxypool.api import app

if __name__ == '__main__':
    s=Schedule()
    s.run()
    app.run()