# coding=utf-8

import redis
import pymysql
import urllib2
import cookielib
import threading


# 从redis读取需要执行的线程
# 从redis读取需要取消的线程
# 执行需要执行的线程 传递参数 储存线程开关 传递线程开关 传递返回值列表 传递返回值列表锁
# 关闭需要取消的线程
# 读取返回值列表 删除返回值线程的开关
# 执行返回值相应操作
# 返回值锁 设定成功或者失败id列表 [[id,True],[id:False]]
# order = {
# "id":order_id,
# "user_id":user_id,
# "from":from_station,
# "from_code":from_code,
# "to":to_station,
# "to_code":to_code,
# "data":date,
# "trains":trains,
# "seats":seats,
# "email":email,
# "cookies":cookies}
class AutoOrder(object):
    """自动化下单主线程"""
    def __init__(self):
        self.redis_cli = redis.StrictRedis()            # redis mysql数据库链接
        self.db_cli = pymysql.Connection(host="127.0.0.1", user="root",
                                         password="",database="piaojia",
                                         port=3306,charset='utf8')
        self.cursor = self.db_cli.cursor()              # mysql游标
        self.thread_switch_dict = {}                    # 线程开关字典
        self.thread_return_list = []                    # 线程返回值列表
        self.return_lock = threading.Lock()             # 返回值列表锁

    def start_thread(self):
        """读取需要开启的线程 传递参数开启线程"""
        while True:
            start_count = self.redis_cli.llen("piaojia_new_order")
            if start_count != 0:
                pass

    def main(self):
        """控制函数"""
        self.start_thread()





class OrderThread(threading.Thread):
    """订单线程"""
    def __init__(self,*args,**kwargs):
        super(OrderThread,self).__init__(*args,**kwargs)


    def run(self):
        pass

    def make_cookie(self,name,value):
        return cookielib.Cookie(
            version=None,
            name=name,
            value=value,
            port=None,
            port_specified=False,
            domain="",
            domain_specified=False,
            domain_initial_dot=False,
            path="/",
            path_specified=False,
            secure=False,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest=None,
        )


cookie = cookielib.CookieJar()  # 构建cookiejar对象 用来保存cookie对象
cookie.set_cookie(make_cookie("test_cookie","12345"))
cookie_handler = urllib2.HTTPCookieProcessor(cookie)  # 构建自定义cookie处理器对象 用来处理cookie
opener = urllib2.build_opener(cookie_handler)  # 构建opener
handlers = {
    "Cookie":"test_cookie=123456"
}
request = urllib2.Request("http://www.baidu.com",headers=handlers)
for i in cookie:
    print "----------------"
    print i.name
    print i.value
    print "----------------"
resp = opener.open(request)
print resp.read()
for i in cookie:
    print "----------------"
    print i.name
    print i.value
    print "----------------"