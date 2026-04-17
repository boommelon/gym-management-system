# 健身房会员及课程管理系统

基于 Python + Tkinter + MySQL 实现的健身房管理系统。

## 功能模块

- 会员管理：增删改查会员信息
- 会员卡管理：卡类型设置、办卡
- 教练管理：教练信息维护
- 课程管理：课程类别、课程安排
- 预约签到：会员预约课程、签到、评价
- 器材管理：器材借用与归还
- 数据报表：课程预约统计（视图）
- 消费查询：会员消费明细（存储过程）

## 数据库特性

- 触发器：会员签到时自动扣减次数/更新有效期
- 视图：课程近一周预约统计
- 存储过程：查询会员消费明细

## 环境要求

- Python 3.8+
- MySQL 8.0+

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `db/config.ini`，修改数据库连接信息：

```ini
[database]
host = localhost
port = 3306
user = root
password = your_password
database = gym_db
charset = utf8mb4
```

### 3. 初始化数据库

在MySQL中执行初始化脚本：

```bash
mysql -u root -p < db/init_db.sql
```

或者登录MySQL后：

```sql
source d:/Desktop/shujuku1/gym_system/db/init_db.sql
```

### 4. 运行程序

```bash
python views/main_window.py
```

## 登录信息

- 用户名：admin
- 密码：admin
