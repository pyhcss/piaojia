# coding=utf-8

import time
import json
import redis
import pymysql
import threading
from Queue import Queue
from send_email import sendemail
from orderthread import OrderThread

THREAD_SWITCH_DICT = {}                    # 线程开关字典


class AutoOrder(object):
    """自动化下单主线程"""
    def __init__(self):
        """初始化函数"""
        global THREAD_SWITCH_DICT,THREAD_RETURN_DICT
        self.redis_cli = redis.StrictRedis()            # redis mysql数据库链接
        self.db_cli = pymysql.Connection(host="127.0.0.1", user="root",
                                         password="******",database="piaojia",
                                         port=3306,charset='utf8')
        self.cursor = self.db_cli.cursor()              # mysql游标
        self.thread_switch_dict = THREAD_SWITCH_DICT    # 开关字典
        self.switch_lock = threading.Lock()             # 开关字典锁
        self.return_queue = Queue()                     # 创建queue队列对象

    def start_thread(self):
        """读取需要开启的线程 传递参数开启线程"""
        global THREAD_SWITCH_DICT
        while True:
            start_count = self.redis_cli.llen("piaojia_new_order")
            if start_count != 0:
                json_data = self.redis_cli.lpop("piaojia_new_order")
                data = json.loads(json_data)
                self.switch_lock.acquire()
                self.thread_switch_dict[str(data["id"])] = True
                self.switch_lock.release()
                order_thread = OrderThread(self.thread_switch_dict,self.switch_lock,
                                           self.return_queue,data)
                order_thread.start()
                self.cursor.execute("update order_info set oi_status=1 where id=%s",data["id"])
                self.db_cli.commit()
            else:
                break

    def end_thread(self):
        """读取需要结束的线程、把开关设为False"""
        while True:
            end_count = self.redis_cli.llen("piaojia_end_order")
            if end_count != 0:
                order_id = self.redis_cli.lpop("piaojia_end_order")
                self.switch_lock.acquire()
                self.thread_switch_dict[str(order_id)] = False
                self.switch_lock.release()
            else:
                break

    def return_thread(self):
        """读取返回值队列,根据返回值处理相应操作,删除开关,删除返回值列表的值"""
        while True:
            if not self.return_queue.empty():
                data_dict = self.return_queue.get()
                if data_dict["data"]:
                    self.cursor.execute("update order_info set oi_status=2 where id=%s",data_dict["id"])
                    self.db_cli.commit()
                    resp = sendemail(data_dict["data"]["email"],data_dict["from"]+"-"+data_dict["to"])
                    print resp
                else:
                    self.cursor.execute("update order_info set oi_status=4 where id=%s",data_dict["id"])
                    self.db_cli.commit()
                self.switch_lock.acquire()
                del self.thread_switch_dict[str(data_dict["id"])]
                self.switch_lock.release()
            else:
                break

    def main(self):
        """控制函数"""
        try:
            global THREAD_SWITCH_DICT
            while True:
                self.start_thread()
                self.end_thread()
                self.return_thread()
                time.sleep(3)
        except Exception as e:
            print e
        finally:
            self.cursor.close()
            self.db_cli.close()




if __name__ == "__main__":
    auto_order = AutoOrder()
    auto_order.main()
    # auto_order.test()
