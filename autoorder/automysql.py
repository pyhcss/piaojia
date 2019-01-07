# coding=utf-8

import pymysql


class AutoMySql():
    """自动执行mysql"""
    def autoExecute(self,sql,*args):
        """自动执行sql语句"""
        try:
            self.dbCli = pymysql.Connection(host="127.0.0.1", user="root",
                                            password="", database="piaojia",
                                            port=3306, charset='utf8')
            self.cursor = self.dbCli.cursor()                  # mysql游标
            self.cursor.execute(sql,*args)                     # 执行sql
            self.dbCli.commit()                                # 提交事务
        except Exception as e:
            print e
        finally:
            self.cursor.close()
            self.dbCli.close()
