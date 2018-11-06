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

# 车站代码表
create table train_station(
id int auto_increment primary key not null comment "车站id",
ts_start_code varchar(10) not null comment "首字母编码",
ts_name varchar(10) not null comment "名称",
ts_name_code varchar(5) not null comment "正式编码三个大写字母",
ts_pinyin varchar(32) not null comment "拼音",
ts_start varchar(10) not null comment "首字母",
ts_card_id int not null comment "网站中编号",
ts_ctime datetime not null default current_timestamp comment "创建时间",
ts_utime datetime not null default current_timestamp on update current_timestamp comment "更新时间",
ts_isDelete boolean not null default false comment "是否删除",
index(ts_name),
index(ts_name_code)
) comment "车站代码表";

# 常用联系人表
create table person_info(
id int auto_increment primary key not null comment "联系人id",
pi_user int not null comment "所属用户",
pi_name varchar(32) not null comment "姓名",
pi_sex tinyint null comment "性别 0女1男",
pi_born_date datetime null comment "生日",
pi_idcard varchar(20) not null comment "身份证号",
pi_type tinyint not null default "1" comment "旅客类型1成人2儿童3学生",
pi_mobile varchar(11) null comment "手机号",
pi_email varchar(32) null comment "邮箱",
pi_address varchar(128) null comment "地址",
pi_ctime datetime not null default current_timestamp comment "创建时间",
pi_utime datetime not null default current_timestamp on update current_timestamp comment "更新时间",
pi_isDelete boolean not null default false comment "是否删除",
foreign key (pi_user) references user_info(id),
index (pi_idcard),
index (pi_name)
)comment "常用联系人表";

# 订单表
create table order_info(
id int auto_increment primary key not null comment "订单id",
oi_user int not null comment "所属用户",
oi_from varchar(32) not null comment "出发地",
oi_from_code varchar(5) not null comment "出发地代号",
oi_to varchar(32) not null comment "目的地",
oi_to_code varchar(5) not null comment "目的地代号",
oi_date datetime not null comment "出发时间",
oi_trains varchar(1024) not null comment "所选车次",
oi_seats varchar(512) not null comment "座位类型",
oi_persons varchar(512) not null comment "乘车人",
oi_email varchar(32) not null comment "邮箱",
oi_status tinyint not null default "0" comment "0待处理 1抢票中 2已抢到　3已完成 4已取消",
oi_comment text null comment "评价",
oi_ctime datetime not null default current_timestamp comment "创建时间",
oi_utime datetime not null default current_timestamp on update current_timestamp comment "更新时间",
oi_isDelete boolean not null default false comment "是否删除",
foreign key (oi_user) references user_info(id)
) comment "订单信息表";
