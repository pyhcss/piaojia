# coding=utf-8

import smtplib
from email.mime.text import MIMEText


def sendemail(address,from_to):
    smtp_address = "smtp.163.com"
    from_mail = "newzn_admin@163.com"
    from_pwd = "yunlong3637"
    to_mail = address

    message = MIMEText("您好,欢迎使用票家,恭喜您抢到了"+from_to+"的火车票,请于30分钟内登录12306官网进行支付,谢谢使用","plain","utf-8")
    message["From"] = from_mail
    message["To"] = to_mail
    message["Subject"] = u"票家"
    try:
        smtp_server = smtplib.SMTP(smtp_address,port=25)
        smtp_server.login(from_mail,from_pwd)
        smtp_server.sendmail(from_mail,to_mail,message.as_string())
        return "发送成功"
    except Exception as e:
        print e
        return "发送失败"


if __name__ == "__main__":
    res = sendemail("909576924@qq.com","北京－侯马")
    print res