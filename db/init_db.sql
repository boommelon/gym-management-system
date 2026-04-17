-- ========================================
-- 健身房会员及课程管理系统 - 数据库初始化脚本
-- ========================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS gym_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gym_db;

-- ========================================
-- 1. 创建卡类型表
-- ========================================
DROP TABLE IF EXISTS card_type;
CREATE TABLE card_type (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '卡类型名称',
    card_category ENUM('次卡', '月卡', '季卡', '年卡') NOT NULL COMMENT '卡类别',
    times_limit INT DEFAULT NULL COMMENT '限制次数（次卡用）',
    valid_days INT DEFAULT NULL COMMENT '有效期天数（月卡/季卡/年卡用）',
    price DECIMAL(10,2) NOT NULL COMMENT '价格',
    description VARCHAR(200) DEFAULT NULL COMMENT '描述'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='卡类型表';

-- 插入默认卡类型
INSERT INTO card_type (name, card_category, times_limit, valid_days, price, description) VALUES
('10次卡', '次卡', 10, NULL, 500.00, '可健身10次'),
('20次卡', '次卡', 20, NULL, 900.00, '可健身20次'),
('月卡', '月卡', NULL, 30, 300.00, '可健身一个月'),
('季卡', '季卡', NULL, 90, 800.00, '可健身一个季度'),
('年卡', '年卡', NULL, 365, 2800.00, '可健身一年');

-- ========================================
-- 2. 创建会员表
-- ========================================
DROP TABLE IF EXISTS member;
CREATE TABLE member (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号',
    gender ENUM('男', '女') DEFAULT '男' COMMENT '性别',
    id_card VARCHAR(18) DEFAULT NULL COMMENT '身份证号',
    join_date DATE NOT NULL DEFAULT (CURRENT_DATE) COMMENT '入会日期',
    status ENUM('正常', '冻结', '已过期') DEFAULT '正常' COMMENT '状态',
    remark VARCHAR(200) DEFAULT NULL COMMENT '备注'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员表';

-- ========================================
-- 3. 创建会员卡表
-- ========================================
DROP TABLE IF EXISTS member_card;
CREATE TABLE member_card (
    id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL COMMENT '会员ID',
    card_type_id INT NOT NULL COMMENT '卡类型ID',
    buy_date DATE NOT NULL DEFAULT (CURRENT_DATE) COMMENT '购买日期',
    expire_date DATE DEFAULT NULL COMMENT '有效期截止日期（时限卡）',
    remain_times INT DEFAULT NULL COMMENT '剩余次数（次卡）',
    status ENUM('未激活', '正常', '已用完', '已过期') DEFAULT '未激活' COMMENT '卡状态',
    price DECIMAL(10,2) NOT NULL COMMENT '购买价格',
    FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE,
    FOREIGN KEY (card_type_id) REFERENCES card_type(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员卡表';

-- ========================================
-- 4. 创建教练表
-- ========================================
DROP TABLE IF EXISTS coach;
CREATE TABLE coach (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号',
    gender ENUM('男', '女') DEFAULT '男' COMMENT '性别',
    specialty VARCHAR(100) DEFAULT NULL COMMENT '专长',
    salary DECIMAL(10,2) DEFAULT 5000.00 COMMENT '月薪',
    hire_date DATE NOT NULL DEFAULT (CURRENT_DATE) COMMENT '入职日期',
    status ENUM('在职', '离职') DEFAULT '在职' COMMENT '状态'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教练表';

-- ========================================
-- 5. 创建课程类别表
-- ========================================
DROP TABLE IF EXISTS course;
CREATE TABLE course (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '课程名称',
    category VARCHAR(50) DEFAULT NULL COMMENT '类别（如瑜伽、动感单车等）',
    duration INT DEFAULT 60 COMMENT '课程时长（分钟）',
    max_capacity INT DEFAULT 20 COMMENT '最大容纳人数',
    description VARCHAR(200) DEFAULT NULL COMMENT '课程描述'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程类别表';

-- 插入默认课程
INSERT INTO course (name, category, duration, max_capacity, description) VALUES
('瑜伽基础课', '瑜伽', 60, 15, '适合初学者的瑜伽课程'),
('高温瑜伽', '瑜伽', 90, 12, '在高温环境下进行的瑜伽课程'),
('动感单车', '单车', 45, 25, '燃脂效果极佳的室内单车课'),
('普拉提', '普拉提', 60, 12, '核心力量训练课程'),
('有氧操', '操课', 60, 30, '全身有氧运动课程');

-- ========================================
-- 6. 创建课程安排表
-- ========================================
DROP TABLE IF EXISTS course_schedule;
CREATE TABLE course_schedule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL COMMENT '课程ID',
    coach_id INT NOT NULL COMMENT '教练ID',
    schedule_time DATETIME NOT NULL COMMENT '课程时间',
    room VARCHAR(50) DEFAULT NULL COMMENT '上课教室',
    max_capacity INT DEFAULT 20 COMMENT '最大人数',
    current_count INT DEFAULT 0 COMMENT '当前预约人数',
    status ENUM('未开始', '进行中', '已结束', '已取消') DEFAULT '未开始' COMMENT '状态',
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (coach_id) REFERENCES coach(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程安排表';

-- ========================================
-- 7. 创建预约/签到/评价表
-- ========================================
DROP TABLE IF EXISTS booking;
CREATE TABLE booking (
    id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL COMMENT '会员ID',
    schedule_id INT NOT NULL COMMENT '课程安排ID',
    book_time DATETIME NOT NULL DEFAULT (CURRENT_TIME) COMMENT '预约时间',
    checkin_time DATETIME DEFAULT NULL COMMENT '签到时间',
    rating TINYINT DEFAULT NULL COMMENT '评分（1-5）',
    remark VARCHAR(200) DEFAULT NULL COMMENT '评价备注',
    status ENUM('已预约', '已签到', '已取消', '已过期') DEFAULT '已预约' COMMENT '状态',
    FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES course_schedule(id),
    UNIQUE KEY uk_member_schedule (member_id, schedule_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预约签到表';

-- ========================================
-- 8. 创建器材表
-- ========================================
DROP TABLE IF EXISTS equipment;
CREATE TABLE equipment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '器材名称',
    equipment_type VARCHAR(50) DEFAULT NULL COMMENT '器材类别',
    status ENUM('在库', '借出', '维修中', '已报废') DEFAULT '在库' COMMENT '状态',
    buy_date DATE DEFAULT NULL COMMENT '购买日期',
    remark VARCHAR(200) DEFAULT NULL COMMENT '备注'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='器材表';

-- 插入默认器材
INSERT INTO equipment (name, equipment_type, status, remark) VALUES
('哑铃套装', '自由重量', '在库', '5-30kg套装'),
('跑步机01', '有氧设备', '在库', '商用跑步机'),
('椭圆机01', '有氧设备', '在库', '商用椭圆机'),
('动感单车01', '有氧设备', '在库', '室内单车'),
('瑜伽垫', '辅助器材', '在库', '标准瑜伽垫'),
('瑜伽球', '辅助器材', '在库', '75cm瑜伽球');

-- ========================================
-- 9. 创建器材借用记录表
-- ========================================
DROP TABLE IF EXISTS equipment_borrow;
CREATE TABLE equipment_borrow (
    id INT PRIMARY KEY AUTO_INCREMENT,
    equipment_id INT NOT NULL COMMENT '器材ID',
    member_id INT NOT NULL COMMENT '借用会员ID',
    borrow_time DATETIME NOT NULL DEFAULT (CURRENT_TIME) COMMENT '借用时间',
    return_time DATETIME DEFAULT NULL COMMENT '归还时间',
    status ENUM('借用中', '已归还') DEFAULT '借用中' COMMENT '状态',
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (member_id) REFERENCES member(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='器材借用记录表';

-- ========================================
-- 10. 创建管理员表（用于登录）
-- ========================================
DROP TABLE IF EXISTS admin;
CREATE TABLE admin (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    name VARCHAR(50) DEFAULT NULL COMMENT '姓名',
    created_at DATETIME DEFAULT (CURRENT_TIME) COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员表';

-- 插入默认管理员（密码: admin）
INSERT INTO admin (username, password, name) VALUES
('admin', 'admin', '系统管理员');

-- ========================================
-- 11. 创建示例数据
-- ========================================

-- 插入会员
INSERT INTO member (name, phone, gender, id_card, remark) VALUES
('张三', '13800138001', '男', '110101199001011234', '普通会员'),
('李四', '13800138002', '女', '110101199002022345', 'VIP会员'),
('王五', '13800138003', '男', '110101199003033456', '普通会员'),
('赵六', '13800138004', '女', '110101199004044567', '普通会员'),
('钱七', '13800138005', '男', '110101199005055678', '普通会员');

-- 插入教练
INSERT INTO coach (name, phone, gender, specialty, salary, hire_date) VALUES
('刘教练', '13900139001', '男', '瑜伽、普拉提', 8000.00, '2023-01-15'),
('陈教练', '13900139002', '女', '动感单车、有氧操', 7500.00, '2023-03-20'),
('周教练', '13900139003', '男', '力量训练', 7000.00, '2023-06-01'),
('吴教练', '13900139004', '女', '瑜伽', 7800.00, '2023-09-10');

-- 插入会员卡（关联会员和卡类型）
INSERT INTO member_card (member_id, card_type_id, buy_date, expire_date, remain_times, status, price) VALUES
(1, 3, '2026-01-01', '2026-04-17', NULL, '正常', 300.00),
(2, 5, '2026-01-15', '2027-01-15', NULL, '正常', 2800.00),
(3, 1, '2026-03-01', NULL, 8, '正常', 500.00),
(4, 4, '2026-02-01', '2026-04-17', NULL, '正常', 800.00),
(5, 2, '2026-04-01', NULL, 15, '正常', 900.00);

-- 插入课程安排
INSERT INTO course_schedule (course_id, coach_id, schedule_time, room, max_capacity, current_count, status) VALUES
(1, 1, '2026-04-17 09:00:00', '瑜伽教室A', 15, 3, '未开始'),
(2, 1, '2026-04-17 14:00:00', '高温瑜伽室', 12, 2, '未开始'),
(3, 2, '2026-04-17 19:00:00', '动感单车室', 25, 5, '未开始'),
(4, 3, '2026-04-18 10:00:00', '综合训练区', 12, 1, '未开始'),
(5, 4, '2026-04-18 15:00:00', '操课室', 30, 4, '未开始'),
(1, 4, '2026-04-19 09:00:00', '瑜伽教室A', 15, 2, '未开始'),
(3, 2, '2026-04-19 19:00:00', '动感单车室', 25, 3, '未开始'),
(2, 1, '2026-04-20 14:00:00', '高温瑜伽室', 12, 1, '未开始');

-- 插入预约记录
INSERT INTO booking (member_id, schedule_id, book_time, status) VALUES
(1, 1, '2026-04-16 10:00:00', '已预约'),
(1, 3, '2026-04-16 10:30:00', '已预约'),
(2, 1, '2026-04-15 14:00:00', '已预约'),
(2, 2, '2026-04-16 09:00:00', '已预约'),
(3, 3, '2026-04-16 11:00:00', '已预约'),
(4, 4, '2026-04-16 15:00:00', '已预约'),
(5, 5, '2026-04-16 16:00:00', '已预约'),
(1, 6, '2026-04-16 17:00:00', '已预约'),
(2, 7, '2026-04-16 18:00:00', '已预约'),
(3, 7, '2026-04-16 18:30:00', '已预约'),
(5, 7, '2026-04-16 19:00:00', '已预约');

-- 更新课程安排的当前预约人数
UPDATE course_schedule SET current_count = (
    SELECT COUNT(*) FROM booking WHERE booking.schedule_id = course_schedule.id AND booking.status = '已预约'
);

-- ========================================
-- 触发器：会员签到时自动扣减次数/更新有效期
-- ========================================
DROP TRIGGER IF EXISTS trg_after_checkin;

DELIMITER //

CREATE TRIGGER trg_after_checkin
AFTER UPDATE ON booking
FOR EACH ROW
BEGIN
    -- 仅当签到时间被设置且原签到时间为空时才处理
    IF NEW.checkin_time IS NOT NULL AND OLD.checkin_time IS NULL THEN

        -- 获取该会员的有效会员卡
        SET @m_card_id = (
            SELECT mc.id FROM member_card mc
            WHERE mc.member_id = NEW.member_id
              AND mc.status = '正常'
              AND (mc.expire_date IS NULL OR mc.expire_date >= CURDATE())
              AND (mc.remain_times IS NULL OR mc.remain_times > 0)
            ORDER BY mc.buy_date DESC
            LIMIT 1
        );

        -- 获取该卡的类型信息
        SET @card_cat = (SELECT card_category FROM card_type ct
                         JOIN member_card mc ON mc.card_type_id = ct.id
                         WHERE mc.id = @m_card_id);

        IF @card_cat = '次卡' THEN
            -- 次卡：扣减次数
            UPDATE member_card SET remain_times = remain_times - 1
            WHERE id = @m_card_id;

            -- 如果次数用完，更新卡状态
            IF (SELECT remain_times FROM member_card WHERE id = @m_card_id) <= 0 THEN
                UPDATE member_card SET status = '已用完' WHERE id = @m_card_id;
            END IF;

        ELSE
            -- 时限卡：检查并更新有效期
            -- 如果是当天第一次签到，提前扣减一天有效期
            IF (SELECT COUNT(*) FROM booking b
                WHERE b.member_id = NEW.member_id
                  AND b.schedule_id = NEW.schedule_id
                  AND DATE(b.checkin_time) = CURDATE()) = 1 THEN

                UPDATE member_card
                SET expire_date = DATE_SUB(expire_date, INTERVAL 1 DAY)
                WHERE id = @m_card_id;

                -- 检查是否已过期
                IF (SELECT expire_date FROM member_card WHERE id = @m_card_id) < CURDATE() THEN
                    UPDATE member_card SET status = '已过期' WHERE id = @m_card_id;
                END IF;
            END IF;
        END IF;

    END IF;
END //

DELIMITER ;

-- ========================================
-- 视图：查询各课程近一周的预约人数、签到人数及签到率
-- ========================================
DROP VIEW IF EXISTS v_course_weekly_stats;

CREATE VIEW v_course_weekly_stats AS
SELECT
    c.id AS course_id,
    c.name AS course_name,
    c.category AS course_category,
    COUNT(DISTINCT cs.id) AS total_schedules,
    COUNT(DISTINCT CASE WHEN b.status IN ('已预约', '已签到') THEN b.id END) AS booking_count,
    COUNT(DISTINCT CASE WHEN b.status = '已签到' THEN b.id END) AS checkin_count,
    ROUND(
        COUNT(DISTINCT CASE WHEN b.status = '已签到' THEN b.id END) * 100.0 /
        NULLIF(COUNT(DISTINCT CASE WHEN b.status IN ('已预约', '已签到') THEN b.id END), 0),
        1
    ) AS checkin_rate
FROM course c
LEFT JOIN course_schedule cs ON c.id = cs.course_id
    AND cs.schedule_time BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE() + INTERVAL 7 DAY
LEFT JOIN booking b ON cs.id = b.schedule_id
GROUP BY c.id, c.name, c.category
ORDER BY booking_count DESC;

-- ========================================
-- 存储过程：查询指定会员的剩余次数/有效期、历史预约记录及消费明细
-- ========================================
DROP PROCEDURE IF EXISTS sp_member_detail;

DELIMITER //

CREATE PROCEDURE sp_member_detail(IN p_member_id INT)
BEGIN
    -- 临时表存放结果
    DROP TEMPORARY TABLE IF EXISTS tmp_member_detail;

    CREATE TEMPORARY TABLE tmp_member_detail (
        info_type VARCHAR(50),
        info_detail VARCHAR(200),
        info_value VARCHAR(100)
    );

    -- 1. 会员基本信息
    INSERT INTO tmp_member_detail
    SELECT '基本信息', '姓名', name FROM member WHERE id = p_member_id;
    INSERT INTO tmp_member_detail
    SELECT '基本信息', '手机号', phone FROM member WHERE id = p_member_id;
    INSERT INTO tmp_member_detail
    SELECT '基本信息', '入会日期', DATE_FORMAT(join_date, '%Y-%m-%d') FROM member WHERE id = p_member_id;

    -- 2. 当前有效卡信息
    INSERT INTO tmp_member_detail
    SELECT '会员卡', '卡类型', ct.name
    FROM member_card mc
    JOIN card_type ct ON mc.card_type_id = ct.id
    WHERE mc.member_id = p_member_id AND mc.status = '正常'
      AND (mc.expire_date IS NULL OR mc.expire_date >= CURDATE())
      AND (mc.remain_times IS NULL OR mc.remain_times > 0)
    LIMIT 1;

    INSERT INTO tmp_member_detail
    SELECT '会员卡', '剩余次数', CONCAT(COALESCE(remain_times, '无限制'), '次')
    FROM member_card mc
    WHERE mc.member_id = p_member_id AND mc.status = '正常'
      AND (mc.expire_date IS NULL OR mc.expire_date >= CURDATE())
    LIMIT 1;

    INSERT INTO tmp_member_detail
    SELECT '会员卡', '有效期至', COALESCE(DATE_FORMAT(expire_date, '%Y-%m-%d'), '无限制')
    FROM member_card mc
    WHERE mc.member_id = p_member_id AND mc.status = '正常'
    LIMIT 1;

    -- 3. 历史预约记录
    INSERT INTO tmp_member_detail
    SELECT '预约记录', CONCAT(c.name, ' ', DATE_FORMAT(cs.schedule_time, '%m-%d %H:%i')), b.status
    FROM booking b
    JOIN course_schedule cs ON b.schedule_id = cs.id
    JOIN course c ON cs.course_id = c.id
    WHERE b.member_id = p_member_id
    ORDER BY b.book_time DESC
    LIMIT 20;

    -- 4. 消费明细汇总
    INSERT INTO tmp_member_detail
    SELECT '消费明细', '办卡费用', CONCAT('¥', FORMAT(price, 2))
    FROM member_card WHERE member_id = p_member_id;

    INSERT INTO tmp_member_detail
    SELECT '消费明细', '累计消费', CONCAT('¥', FORMAT(
        (SELECT COALESCE(SUM(price), 0) FROM member_card WHERE member_id = p_member_id), 2
    ));

    -- 输出结果
    SELECT * FROM tmp_member_detail;

    -- 清理
    DROP TEMPORARY TABLE IF EXISTS tmp_member_detail;
END //

DELIMITER ;

-- ========================================
-- 存储过程：自动更新过期的课程安排状态
-- ========================================
DROP PROCEDURE IF EXISTS sp_update_schedule_status;

DELIMITER //

CREATE PROCEDURE sp_update_schedule_status()
BEGIN
    -- 将已过期的课程安排标记为已结束
    UPDATE course_schedule
    SET status = '已结束'
    WHERE status = '未开始'
      AND schedule_time < NOW() - INTERVAL 2 HOUR;

    -- 将已过期的预约标记为已过期
    UPDATE booking b
    JOIN course_schedule cs ON b.schedule_id = cs.id
    SET b.status = '已过期'
    WHERE b.status = '已预约'
      AND cs.schedule_time < NOW();
END //

DELIMITER ;

-- ========================================
-- 给外键约束命名（提高可维护性）
-- ========================================
-- 给 member_card 表添加外键约束名称
ALTER TABLE member_card
ADD CONSTRAINT fk_member_card_member FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_member_card_cardtype FOREIGN KEY (card_type_id) REFERENCES card_type(id);

ALTER TABLE course_schedule
ADD CONSTRAINT fk_schedule_course FOREIGN KEY (course_id) REFERENCES course(id),
ADD CONSTRAINT fk_schedule_coach FOREIGN KEY (coach_id) REFERENCES coach(id);

ALTER TABLE booking
ADD CONSTRAINT fk_booking_member FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_booking_schedule FOREIGN KEY (schedule_id) REFERENCES course_schedule(id);

ALTER TABLE equipment_borrow
ADD CONSTRAINT fk_borrow_equipment FOREIGN KEY (equipment_id) REFERENCES equipment(id),
ADD CONSTRAINT fk_borrow_member FOREIGN KEY (member_id) REFERENCES member(id);

-- ========================================
-- 完成
-- ========================================
SELECT '数据库初始化完成！' AS message;
