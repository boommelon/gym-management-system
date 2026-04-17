# 健身房会员及课程管理系统

基于 Python + Tkinter + MySQL 开发的健身房综合管理平台，支持会员管理、课程预约、器材借用等核心功能。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 项目预览

| 模块 | 说明 |
|------|------|
| 会员管理 | 会员信息增删改查、会员卡办理与续费 |
| 教练管理 | 教练档案维护、排课管理 |
| 课程管理 | 团课/私教分类、课程时间表编排 |
| 预约签到 | 在线预约课程、扫码签到、课程评价 |
| 器材管理 | 器材借用登记、归还管理、损坏报备 |
| 数据报表 | 课程预约统计、消费记录查询 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端界面 | Python Tkinter |
| 业务逻辑 | Python 3.8+ |
| 数据库 | MySQL 8.0+ |
| 数据库连接 | PyMySQL |

---

## 项目结构

```
gym_system/
├── main.py                 # 程序入口
├── requirements.txt        # Python 依赖
├── README.md               # 项目文档
├── db/
│   ├── config.ini          # 数据库配置
│   └── init_db.sql         # 数据库初始化脚本
├── services/               # 业务逻辑层
│   ├── member_service.py   # 会员服务
│   ├── course_service.py   # 课程服务
│   └── equipment_service.py # 器材服务
├── utils/
│   └── db_utils.py         # 数据库工具类
└── views/
    └── main_window.py      # 主窗口界面
```

---

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- MySQL 8.0 或更高版本

### 1. 克隆项目

```bash
git clone https://github.com/boommelon/gym-management-system.git
cd gym-management-system
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

创建 `db/config.ini` 文件：

```ini
[database]
host = localhost
port = 3306
user = root
password = your_password
database = gym_db
charset = utf8mb4
```

### 4. 初始化数据库

```bash
mysql -u root -p < db/init_db.sql
```

### 5. 运行程序

```bash
python views/main_window.py
```

---

## 数据库特性

- **触发器**：会员签到时自动扣减课程次数、更新会员有效期
- **视图**：`view_course_weekly_stats` 统计课程近一周预约情况
- **存储过程**：`proc_member_consumption` 查询会员消费明细

---

## 默认登录账号

| 用户名 | 密码 |
|--------|------|
| admin | admin |

---

## License

MIT License
