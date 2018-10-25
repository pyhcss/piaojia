create database piaojia charset=utf8;

use piaojia;

# 用户表 id 账号 密码 姓名
create table user_info(
id int auto_increment primary key not null comment "用户id",
ui_name varchar(32) not null comment "用户名",
ui_account varchar(32) not null comment "账号",
ui_pwd varchar(32) not null comment "密码",
ui_login int not null default 0 comment "登录次数",
ui_ctime datetime not null default current_timestamp comment "创建时间",
ui_utime datetime not null default current_timestamp on update current_timestamp comment "更新时间",
ui_isDelete boolean not null default false comment "是否注销",
unique (ui_account)
) comment "用户信息表";