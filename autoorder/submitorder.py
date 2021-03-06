# coding=utf-8

import re
import time
import json
import urllib
import datetime
from baserequest import BaseRequest

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class SubmitOrder(BaseRequest):
    """提交订单类"""
    def check_uamtk(self,tk):
        """
        检测登录情况
        tk:cookie中的tk值
        return "0" or "uamtk login error"
        """
        url = "https://kyfw.12306.cn/otn/uamauthclient"     # 创建url
        data = "tk="+tk                                     # 参数
        request = self.request(url,data=data,headers=self.headers)
        count = 0
        while True:
            try:
                resp = self.opener.open(request).read()     # 发送请求获取响应
                data = json.loads(resp)                         # 解析json数据
            except Exception as e:
                count += 1
                if count <= 3:
                    continue
                else:
                    print "tk校验失败"
                    return "uamtk login error"
            if data["result_code"] == 0:
                return "0"                                  # 返回执行结果
            else:
                print data
                return "uamtk login error"

    def checklogin(self):
        """
        检查是否登录
        return: "0" or "check login error"
        """
        url = "https://kyfw.12306.cn/otn/login/checkUser"
        data = "_json_att="                                 # 构建请求对象
        request = self.request(url,headers=self.headers,data=data)
        count = 0
        while True:
            try:
                resp = self.opener.open(request).read()     # 发送请求 获取返回值
                data = json.loads(resp)                         # 解析数据
            except Exception as e:
                count += 1
                if count <= 3:
                    continue
                else:
                    print "预定验证登录失败"
                    return "check login error"
            if not data["data"]["flag"]:                    # 判断是否登陆成功
                count += 1
                if count <= 3:
                    continue
                else:
                    print "预定验证登录失败"
                    return "check login error"
            else:
                print "预定验证登录成功"
                return "0"

    def destine(self,sercret,date,from_name,to_name):
        """
        跳转到预定页面
        sercret:"fsdgfsadfsd" 车次列表中第一个超长字符串
        date:   "2018-10-10"  预定时间
        from_name:"北京"      搜索时的出发站名
        to_name:  "天津"      搜索时的目的站名
        return "0" or "destine error"
        """
        url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        # 拼接查询数据
        data = "secretStr="+sercret+"&train_date="+date+"&back_train_date="+datetime.datetime.now().strftime("%Y-%m-%d")+"&tour_flag=dc&purpose_codes=ADULT&query_from_station_name="+from_name+"&query_to_station_name="+to_name+"&undefined"
        request = self.request(url,data=data.encode("utf-8"),headers=self.headers)
        count = 0
        while True:
            try:
                resp = self.opener.open(request).read()     # 发送请求获取响应
                data = json.loads(resp)                         # 解析json数据
            except Exception as e:
                count += 1
                if count <= 3:
                    continue
                else:
                    print "获取预定页面失败"
                    return "destine error"
            if not data["status"]:                          # 检查是否获取成功
                count += 1
                if count <= 3:
                    continue
                else:
                    print "获取预定页面失败"
                    return "destine error"
            else:
                print "获取预定页面成功"
                return "0"

    def get_token(self):
        """
        获取全局token以及校验码
        return: {"token":"服务器值","key":"服务器值"}
        """
        url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        data = "_json_att="
        request = self.request(url,data=data,headers=self.headers)
        count = 0
        while True:
            data = {}
            try:                                            # 获取token及key
                resp = self.opener.open(request).read()         # 发送请求 获取响应
                data["key"] = re.search(r"'key_check_isChange':'(\w+)'",resp).group(1)
                data["token"] = re.search(r"globalRepeatSubmitToken = '(\w+)'",resp).group(1)
            except Exception as e:
                count += 1
                if count <= 3:
                    continue
                else:
                    print resp
                    print "key获取失败"
                    return ""
            print "已获取到全局token及key"
            return data

    def get_persons(self,persons,token):
        """
        获取常用联系人
        person: [乘车人姓名1,乘车人姓名2]
        return [{乘车人1},{乘车人2}]
        """
        url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
        data = "_json_att=&REPEAT_SUBMIT_TOKEN="+token
        request = self.request(url,data=data,headers=self.headers)
        count = 0
        while True:
            try:
                resp = self.opener.open(request).read()         # 发送请求 获取响应
                resp = json.loads(resp)                         # 解析json数据
            except Exception as e:
                count += 1
                if count <=3:
                    continue
                else:
                    print "常用联系人信息获取失败"
                    return False
            data = resp["data"]["normal_passengers"]        # 拿到常用联系人列表
            person_list = []
            if not data:
                count += 1
                if count <= 3:
                    continue
                else:
                    print "常用联系人信息获取失败"
                    return False
            for x in persons:                               # 查找乘车人信息
                for i in data:                              # 返回乘车人数据
                    if i["passenger_name"] == x:
                        person_list.append(i)
            print "已获取到常用联系人信息"
            return person_list                              # 返回值[{},]

    def order_person_submit(self,seattype,person_list,token_key):
        """
        乘车人信息预提交
        seat:-5       座位类型,车次信息列表下标
        person_list: [{乘车人信息1},{2}]
        token_key:   {"token":"","key":}   服务器值
        return:     {"new":"乘车人信息字符串","old":"乘车人信息字符串","chooseseats":"True"是否能选座}
        """
        url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
        if seattype == -6:                                 # 判断选择的坐席
            seat = "p"
        elif seattype == -7:
            seat = "M"
        elif seattype == -8:
            seat = "O"
        elif seattype == -15:
            seat = "4"
        elif seattype == -10:
            seat = "3"
        elif seattype == -9:
            seat = "1"
        else:
            seat = "O"
        person_info = {                                    # 按要求格式化字符串
            "new":"_".join([",".join([seat,"0",i["passenger_type"],i["passenger_name"],"1",i["passenger_id_no"],i["mobile_no"],"N"]) for i in person_list]),
            "old":"_".join([",".join([i["passenger_name"],"1",i["passenger_id_no"],i["passenger_type"]]) for i in person_list])
        }
        data = {
            "cancel_flag":2,                               # 固定值
            "bed_level_order_num":"000000000000000000000000000000",# 固定值
            "passengerTicketStr":person_info["new"],       # 乘车人信息
            "oldPassengerStr":person_info["old"],          # 多个之间用下划线隔开
            "tour_flag":"dc",                              # 旅客标示 固定值
            "randCode":"",                                 # 默认
            "whatsSelect":1,                               # 默认
            "_json_att":"",                                # 默认
            "REPEAT_SUBMIT_TOKEN":token_key["token"],      # 全局token
        }                                                  # 发送请求获取返回值
        request = self.request(url,data=urllib.urlencode(data),headers=self.headers)
        count = 0
        while True:
            try:
                resp = self.opener.open(request).read()
                data = json.loads(resp)["data"]                # 解析数据
            except Exception as e:
                count += 1
                if count<=3:
                    continue
                else:
                    print "乘车人信息获取失败"
                    return {"errcode":"4301","errmsg":"submit person error"}# 判断是否可以选座
            if not data["submitStatus"]:                   # 判断提交状态
                count += 1
                if count <= 3:
                    continue
                else:
                    print resp
                    return {"errcode":"4301","errmsg":"seat error"}# 判断是否可以选座
            person_info["chooseseats"] = True if data["canChooseSeats"] == "Y" else False
            print "乘车人信息已提交"                         # 返回组织好的乘车人信息
            return {"errcode":"0","errmsg":"乘车人信息已提交","data":person_info}

    def order_train_submit(self,date,train,person,token_key):
        """
        订票车次预提交
        date:       "2018-10-10"        车票时间
        train:      [车次信息列表]         车次信息
        person:     {"new":"","old":""} 组织好的乘车人信息字符串
        token_key:  {"token":"","key":""}服务器校验值
        return: "0" or "train error"
        """
        url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
        data = {                                           # 车票日期
            "train_date":time.strftime("%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)",time.strptime(date,"%Y-%m-%d")),
            "train_no":train[2],                           # 列车代号
            "stationTrainCode":train[3],                   # 简称代号
            "seatType":person["new"][:1],                  # 选择的座位类型
            "fromStationTelecode":train[6],                # 出发站代号
            "toStationTelecode":train[7],                  # 目的站代号
            "leftTicket":train[12],                        # 查询结果中第二个长代码 第13个值
            "purpose_codes":"00",                          # 目的编号
            "train_location":train[15],                    # 查询结果的第16个值
            "_json_att":"",                                # 默认
            "REPEAT_SUBMIT_TOKEN":token_key["token"]       # 全局token
        }                                                  # 发送请求拿到响应
        request = self.request(url,data=urllib.urlencode(data),headers=self.headers)
        count = 0
        while True:
            try:
                resp = self.opener.open(request).read()
                data = json.loads(resp)["data"]            # 解析数据
            except Exception as e:
                count += 1
                if count <= 3:
                    continue
                else:
                    print "订单车次提交失败"
                    return "train submit error"
            count = data["ticket"].split(",")              # 切割余票数量
            if count[0] == "0" or count[0] == "":          # 判断座位是否为空
                print "订单车次提交失败"
                print resp
                return "count error"
            elif not data["op_1"]:                         # 判断提交情况
                print "订单车次提交失败"
                print resp
                return "train error"
            # if len(count) == 2:
            #     if int(count[1]) > 0 and int(count[1]) <= 5: # 临时条件 避免分配到无座
            #         print resp
            #         return "count error"
            print "预定车次信息已提交"
            return "0"

    def order_submit(self,person,token_key,train):
        """
        最终提交预定信息
        person:     {"new":"","old":"","chooseseats":boolean} 组织好的乘车人信息字符串
        token_key:  {"token":"","key":""}服务器校验值
        train:      [车次信息列表]         车次信息
        """
        url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
        seats = ""
        if person["chooseseats"]:
            num = len(person["new"].split("_"))
            if num == 1:                                   # 根据人数设置座位类型
                seats = "1A"
            elif num == 2:
                seats = "1D1F"
            elif num == 3:
                seats = "1A1B1C"
            elif num == 4:
                seats = "1D1F2D2F"
            elif num == 5:
                seats = "1A1B1C2A2B"
        data = {
            "passengerTicketStr":person["new"],            # 购票信息
            "oldPassengerStr":person["old"],               # 购票信息
            "randCode":"",                                 # 默认
            "purpose_codes":"00",                          # 同上默认
            "key_check_isChange":token_key["key"],         # 检查钥匙是否改变
            "leftTicketStr":train[12],                     # 查询结果中第二个长代码 第13个值
            "train_location":train[15],                    # 查询结果中第16个值
            "choose_seats":seats,                          # 选择座位1A2B1C 只有两排
            "seatDetailType":"",                           # 座位描述类型
            "whatsSelect":"1",                             # 默认
            "roomType":"00",                               # 不清楚
            "dwAll":"N",                                   # 默认 不清楚
            "_json_att":"",                                # 默认
            "REPEAT_SUBMIT_TOKEN":token_key["token"]       # 全局token
        }
        request = self.request(url,data=urllib.urlencode(data),headers=self.headers)
        count = 0
        while True:
            try:
                resp = self.opener.open(request).read()
                data = json.loads(resp)["data"]            # 解析数据
            except Exception as e:
                count += 1
                if count <= 3:
                    continue
                else:
                    print "终极提交订单失败"
                    return "submit error"
            if not data["submitStatus"]:                   # 判断提交情况
                count += 1
                if count<=3:
                    continue
                else:
                    print resp
                    return "submit error"
            return "0"

    def query_submit(self,token_key):
        """
        查询订单预定情况
        token_key: {"token":服务器值,"key":服务器值}
        return: "0" 预定成功或者失败
        """
        count = 0
        while True:
            url = "https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?"
            url += "random="+str(int(time.time()*1000))+"&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN="+token_key["token"]
            request = self.request(url,headers=self.headers)
            try:
                resp = self.opener.open(request).read()   # 发送请求获取响应
                data = json.loads(resp)["data"]           # 解析数据
            except Exception as e:
                count += 1
                if count <= 3:
                    continue
                else:
                    return "orderid error"
            if data["waitTime"] > 0:                      # 如果等待时间大于0则还在队列
                time.sleep(5)
            elif data["orderId"] == None:                 # 获取不到订单号
                print data
                return "orderid error"
            else:
                print data
                return "0"
