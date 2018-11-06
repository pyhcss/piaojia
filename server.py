# coding=utf-8

import redis
import torndb
import tornado.web
import tornado.ioloop
import tornado.httpserver

from urls import urls
from conf import settings,db_conf,redis_conf
from tornado.options import options,define

# 定义端口 启动时可以命令行键入port=int值
define("port",default=8000,type=int,help="please input port")


class Application(tornado.web.Application):
    """重写application增加数据库链接"""
    def __init__(self,*args,**kwargs):
        super(Application,self).__init__(*args,**kwargs)    # 调用父类init
        self.db = torndb.Connection(**db_conf)              # mysql链接
        self.redis = redis.StrictRedis(**redis_conf)        # redis链接


def main():
    options.parse_command_line()
    app = Application(urls,**settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port) # address="127.0.0.1"
    tornado.ioloop.IOLoop.current().start()
    
    
if __name__ == "__main__":
    main()