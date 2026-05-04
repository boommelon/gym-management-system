# 健身房会员及课程管理系统

基于 `Python + Tkinter + MySQL` 的数据库原理课程设计项目，覆盖会员、会员卡、教练、课程、预约签到、器材借还、视图统计、存储过程查询与触发器自动处理等基础要求。

## 功能概览

- 会员管理：会员信息增删改查、状态维护
- 会员卡管理：卡类型管理、办卡记录管理
- 教练管理：教练资料维护
- 课程管理：课程类别与课程安排管理
- 预约签到：会员预约、取消预约、签到、课程评价
- 器材管理：器材信息、借用与归还
- 数据报表：近一周课程预约人数、签到人数、签到率
- 消费查询：调用存储过程查询会员卡、历史预约、消费明细
- 登录功能：管理员账号密码登录后进入主界面

## 项目结构

```text
gym_system/
|-- main.py
|-- requirements.txt
|-- README.md
|-- db/
|   |-- config.ini
|   |-- init_db.sql
|   `-- upgrade_existing_db.sql
|-- services/
|   |-- auth_service.py
|   |-- member_service.py
|   |-- course_service.py
|   `-- equipment_service.py
|-- utils/
|   `-- db_utils.py
`-- views/
    |-- common.py
    |-- login_window.py
    |-- main_window.py
    |-- member_views.py
    |-- course_views.py
    `-- equipment_views.py
```

## 数据库设计要点

核心实体包括：

- `member`：会员
- `card_type`：会员卡类型
- `member_card`：会员办卡记录
- `coach`：教练
- `course`：课程类别
- `course_schedule`：课程安排
- `booking`：预约签到记录
- `equipment`：器材
- `equipment_borrow`：器材借还记录
- `admin`：管理员

数据库对象满足课设要求：

- 触发器 `trg_after_checkin`
  - 会员签到后自动扣减次卡次数
  - 时限卡按签到情况更新有效期
- 视图 `v_course_weekly_stats`
  - 查询课程近一周预约人数、签到人数、签到率
- 存储过程 `sp_member_detail`
  - 查询指定会员的剩余次数或有效期、历史预约记录、消费明细
- 存储过程 `sp_update_schedule_status`
  - 自动更新过期课程和预约状态

## 环境要求

- Python 3.8+
- MySQL 8.0+

## 安装依赖

```bash
pip install -r requirements.txt
```

## 数据库配置

编辑 `db/config.ini`：

```ini
[database]
host = 127.0.0.1
port = 3306
user = root
password = zk406521
database = gym_db
charset = utf8mb4
```

## 数据库初始化

### 1. 全新建库

```bash
mysql -u root -p < db/init_db.sql
```

### 2. 已有数据库升级

```bash
mysql -u root -p gym_db < db/upgrade_existing_db.sql
```

升级脚本会尽量保留原有业务数据，同时修复结构、视图、触发器、存储过程和默认管理员密码。

## 运行项目

```bash
python main.py
```

## 默认管理员账号

- 用户名：`admin`
- 密码：`123456`

## 当前版本说明

- 程序启动后会先进入登录窗口。
- 登录成功后进入主功能界面。
- 表单中尽量只保留关键业务字段，自动生成字段由系统和数据库自动处理。

## 课程设计报告可对应的内容

- 需求分析：会员、教练、课程、器材四类核心业务
- E-R 设计：会员与会员卡、课程与排课、排课与预约、器材与借用
- 关系模式转换：实体表和联系表设计
- 完整性设计：主键、外键、唯一约束、状态枚举、评分范围
- 数据库对象设计：触发器、视图、存储过程
- 系统实现：Tkinter 前端 + Service 业务层 + MySQL
- 维护方案：初始化脚本与升级脚本分离
