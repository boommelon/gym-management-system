-- ========================================
-- 健身房会员及课程管理系统
-- 全量初始化脚本（适合全新数据库）
-- ========================================

CREATE DATABASE IF NOT EXISTS gym_db
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE gym_db;

SET NAMES utf8mb4;

DROP TRIGGER IF EXISTS trg_after_checkin;
DROP VIEW IF EXISTS v_course_weekly_stats;
DROP PROCEDURE IF EXISTS sp_member_detail;
DROP PROCEDURE IF EXISTS sp_update_schedule_status;

DROP TABLE IF EXISTS equipment_borrow;
DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS course_schedule;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS coach;
DROP TABLE IF EXISTS member_card;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS card_type;
DROP TABLE IF EXISTS admin;

CREATE TABLE card_type (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '卡类型名称',
    card_category ENUM('次卡', '月卡', '季卡', '年卡') NOT NULL COMMENT '卡类别',
    times_limit INT DEFAULT NULL COMMENT '次卡可用次数',
    valid_days INT DEFAULT NULL COMMENT '时限卡有效天数',
    price DECIMAL(10, 2) NOT NULL COMMENT '卡价',
    description VARCHAR(200) DEFAULT NULL COMMENT '说明',
    CONSTRAINT chk_card_type_rule CHECK (
        (card_category = '次卡' AND times_limit IS NOT NULL AND valid_days IS NULL)
        OR (card_category IN ('月卡', '季卡', '年卡') AND times_limit IS NULL AND valid_days IS NOT NULL)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员卡类型表';

CREATE TABLE member (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '会员姓名',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号',
    gender ENUM('男', '女') NOT NULL DEFAULT '男' COMMENT '性别',
    id_card VARCHAR(18) DEFAULT NULL COMMENT '身份证号',
    join_date DATE NOT NULL DEFAULT (CURRENT_DATE) COMMENT '入会日期',
    status ENUM('正常', '冻结', '已过期') NOT NULL DEFAULT '正常' COMMENT '会员状态',
    remark VARCHAR(200) DEFAULT NULL COMMENT '备注'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员信息表';

CREATE TABLE member_card (
    id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL COMMENT '会员ID',
    card_type_id INT NOT NULL COMMENT '卡类型ID',
    buy_date DATE NOT NULL DEFAULT (CURRENT_DATE) COMMENT '购卡日期',
    expire_date DATE DEFAULT NULL COMMENT '有效期截止日',
    remain_times INT DEFAULT NULL COMMENT '剩余次数',
    status ENUM('未激活', '正常', '已用完', '已过期') NOT NULL DEFAULT '正常' COMMENT '会员卡状态',
    price DECIMAL(10, 2) NOT NULL COMMENT '购卡实收金额',
    CONSTRAINT fk_member_card_member FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE,
    CONSTRAINT fk_member_card_cardtype FOREIGN KEY (card_type_id) REFERENCES card_type(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员办卡记录表';

CREATE TABLE coach (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '教练姓名',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号',
    gender ENUM('男', '女') NOT NULL DEFAULT '男' COMMENT '性别',
    specialty VARCHAR(100) DEFAULT NULL COMMENT '擅长方向',
    salary DECIMAL(10, 2) NOT NULL DEFAULT 5000.00 COMMENT '月薪',
    hire_date DATE NOT NULL DEFAULT (CURRENT_DATE) COMMENT '入职日期',
    status ENUM('在职', '离职') NOT NULL DEFAULT '在职' COMMENT '任职状态'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教练信息表';

CREATE TABLE course (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '课程名称',
    category VARCHAR(50) NOT NULL COMMENT '课程类别',
    duration INT NOT NULL DEFAULT 60 COMMENT '课程时长（分钟）',
    max_capacity INT NOT NULL DEFAULT 20 COMMENT '默认容量',
    description VARCHAR(200) DEFAULT NULL COMMENT '课程说明'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程类别表';

CREATE TABLE course_schedule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL COMMENT '课程ID',
    coach_id INT NOT NULL COMMENT '教练ID',
    schedule_time DATETIME NOT NULL COMMENT '上课时间',
    room VARCHAR(50) DEFAULT NULL COMMENT '教室/区域',
    max_capacity INT NOT NULL DEFAULT 20 COMMENT '本次课程容量',
    current_count INT NOT NULL DEFAULT 0 COMMENT '当前预约人数',
    status ENUM('未开始', '进行中', '已结束', '已取消') NOT NULL DEFAULT '未开始' COMMENT '排课状态',
    CONSTRAINT fk_schedule_course FOREIGN KEY (course_id) REFERENCES course(id),
    CONSTRAINT fk_schedule_coach FOREIGN KEY (coach_id) REFERENCES coach(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程安排表';

CREATE TABLE booking (
    id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL COMMENT '会员ID',
    schedule_id INT NOT NULL COMMENT '课程安排ID',
    book_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '预约时间',
    checkin_time DATETIME DEFAULT NULL COMMENT '签到时间',
    rating TINYINT DEFAULT NULL COMMENT '课程评分',
    remark VARCHAR(200) DEFAULT NULL COMMENT '评价备注',
    status ENUM('已预约', '已签到', '已取消', '已过期') NOT NULL DEFAULT '已预约' COMMENT '预约状态',
    CONSTRAINT fk_booking_member FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE,
    CONSTRAINT fk_booking_schedule FOREIGN KEY (schedule_id) REFERENCES course_schedule(id),
    CONSTRAINT uk_member_schedule UNIQUE (member_id, schedule_id),
    CONSTRAINT chk_booking_rating CHECK (rating IS NULL OR rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程预约签到表';

CREATE TABLE equipment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '器材名称',
    equipment_type VARCHAR(50) DEFAULT NULL COMMENT '器材类别',
    status ENUM('在库', '借出', '维修中', '已报废') NOT NULL DEFAULT '在库' COMMENT '器材状态',
    buy_date DATE DEFAULT NULL COMMENT '购入日期',
    remark VARCHAR(200) DEFAULT NULL COMMENT '备注'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='器材信息表';

CREATE TABLE equipment_borrow (
    id INT PRIMARY KEY AUTO_INCREMENT,
    equipment_id INT NOT NULL COMMENT '器材ID',
    member_id INT NOT NULL COMMENT '会员ID',
    borrow_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '借用时间',
    return_time DATETIME DEFAULT NULL COMMENT '归还时间',
    status ENUM('借用中', '已归还') NOT NULL DEFAULT '借用中' COMMENT '借用状态',
    CONSTRAINT fk_borrow_equipment FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    CONSTRAINT fk_borrow_member FOREIGN KEY (member_id) REFERENCES member(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='器材借还记录表';

CREATE TABLE admin (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '账号',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    name VARCHAR(50) DEFAULT NULL COMMENT '姓名',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员表';

INSERT INTO card_type (name, card_category, times_limit, valid_days, price, description) VALUES
('10次卡', '次卡', 10, NULL, 500.00, '适合零散训练的基础次卡'),
('20次卡', '次卡', 20, NULL, 900.00, '适合中短期高频训练'),
('月卡', '月卡', NULL, 30, 300.00, '30天内不限次数'),
('季卡', '季卡', NULL, 90, 800.00, '90天内不限次数'),
('年卡', '年卡', NULL, 365, 2800.00, '365天内不限次数');

INSERT INTO member (name, phone, gender, id_card, join_date, status, remark) VALUES
('张三', '13800138001', '男', '110101199001011234', '2026-01-01', '正常', '普通会员'),
('李四', '13800138002', '女', '110101199202023456', '2026-01-15', '正常', '团课活跃会员'),
('王五', '13800138003', '男', '110101199303034567', '2026-02-10', '正常', '喜欢力量训练'),
('赵六', '13800138004', '女', '110101199404045678', '2026-02-18', '冻结', '暂时外出'),
('钱七', '13800138005', '男', '110101199505056789', '2026-03-01', '正常', '偏好有氧课程');

INSERT INTO coach (name, phone, gender, specialty, salary, hire_date, status) VALUES
('刘教练', '13900139001', '男', '瑜伽、普拉提', 8000.00, '2024-01-10', '在职'),
('陈教练', '13900139002', '女', '动感单车、有氧操', 7600.00, '2024-02-15', '在职'),
('周教练', '13900139003', '男', '力量训练', 7200.00, '2024-03-01', '在职'),
('吴教练', '13900139004', '女', '拉伸恢复', 7000.00, '2024-03-15', '在职');

INSERT INTO course (name, category, duration, max_capacity, description) VALUES
('瑜伽基础课', '瑜伽', 60, 15, '适合初学者的基础瑜伽课程'),
('高温瑜伽', '瑜伽', 90, 12, '在高温环境进行的柔韧训练'),
('动感单车', '动感单车', 45, 25, '节奏强、燃脂快的单车课'),
('力量循环训练', '力量训练', 60, 15, '器械与自重结合的循环训练'),
('有氧操', '有氧操', 60, 30, '适合大众的有氧课程');

INSERT INTO member_card (member_id, card_type_id, buy_date, expire_date, remain_times, status, price) VALUES
(1, 3, '2026-04-20', '2026-05-20', NULL, '正常', 300.00),
(2, 5, '2026-02-01', '2027-02-01', NULL, '正常', 2800.00),
(3, 1, '2026-04-10', NULL, 8, '正常', 500.00),
(4, 4, '2026-01-05', '2026-04-05', NULL, '已过期', 800.00),
(5, 2, '2026-04-15', NULL, 16, '正常', 900.00);

INSERT INTO course_schedule (course_id, coach_id, schedule_time, room, max_capacity, current_count, status) VALUES
(1, 1, CONCAT(DATE(DATE_ADD(NOW(), INTERVAL 1 DAY)), ' 09:00:00'), '瑜伽教室A', 15, 0, '未开始'),
(2, 1, CONCAT(DATE(DATE_ADD(NOW(), INTERVAL 2 DAY)), ' 14:00:00'), '高温教室', 12, 0, '未开始'),
(3, 2, CONCAT(DATE(DATE_ADD(NOW(), INTERVAL 1 DAY)), ' 17:00:00'), '单车房', 25, 0, '未开始'),
(4, 3, CONCAT(DATE(DATE_ADD(NOW(), INTERVAL 3 DAY)), ' 09:00:00'), '力量区', 15, 0, '未开始'),
(5, 4, CONCAT(DATE(DATE_ADD(NOW(), INTERVAL 4 DAY)), ' 14:00:00'), '操课室', 30, 0, '未开始'),
(1, 1, CONCAT(DATE(DATE_SUB(NOW(), INTERVAL 2 DAY)), ' 09:00:00'), '瑜伽教室A', 15, 0, '已结束'),
(3, 2, CONCAT(DATE(DATE_SUB(NOW(), INTERVAL 1 DAY)), ' 17:00:00'), '单车房', 25, 0, '已结束');

INSERT INTO booking (member_id, schedule_id, book_time, checkin_time, rating, remark, status) VALUES
(1, 1, DATE_SUB(NOW(), INTERVAL 12 HOUR), NULL, NULL, NULL, '已预约'),
(2, 1, DATE_SUB(NOW(), INTERVAL 10 HOUR), NULL, NULL, NULL, '已预约'),
(3, 3, DATE_SUB(NOW(), INTERVAL 9 HOUR), NULL, NULL, NULL, '已预约'),
(5, 4, DATE_SUB(NOW(), INTERVAL 8 HOUR), NULL, NULL, NULL, '已预约'),
(1, 6, DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY), 5, '课程节奏很好', '已签到'),
(2, 7, DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY), 4, '体验不错', '已签到');

UPDATE course_schedule cs
SET current_count = (
    SELECT COUNT(*)
    FROM booking b
    WHERE b.schedule_id = cs.id
      AND b.status = '已预约'
);

INSERT INTO equipment (name, equipment_type, status, buy_date, remark) VALUES
('哑铃套装', '自由重量', '在库', '2025-10-10', '5kg-30kg整套'),
('跑步机01', '有氧设备', '在库', '2025-08-01', '商用型跑步机'),
('椭圆机01', '有氧设备', '在库', '2025-08-15', '低冲击有氧器械'),
('动感单车01', '有氧设备', '借出', '2025-09-01', '课程备用车'),
('瑜伽垫01', '辅助器材', '在库', '2025-07-20', '防滑款'),
('泡沫轴01', '恢复器材', '在库', '2025-07-22', '深层放松');

INSERT INTO equipment_borrow (equipment_id, member_id, borrow_time, return_time, status) VALUES
(4, 2, DATE_SUB(NOW(), INTERVAL 3 HOUR), NULL, '借用中'),
(5, 1, DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY), '已归还');

INSERT INTO admin (username, password, name) VALUES
('admin', '123456', '系统管理员');

DELIMITER //

CREATE TRIGGER trg_after_checkin
AFTER UPDATE ON booking
FOR EACH ROW
BEGIN
    DECLARE v_member_card_id INT DEFAULT NULL;
    DECLARE v_card_category VARCHAR(20) DEFAULT NULL;

    IF NEW.checkin_time IS NOT NULL AND OLD.checkin_time IS NULL THEN
        SELECT mc.id, ct.card_category
        INTO v_member_card_id, v_card_category
        FROM member_card mc
        JOIN card_type ct ON mc.card_type_id = ct.id
        WHERE mc.member_id = NEW.member_id
          AND mc.status = '正常'
          AND (mc.expire_date IS NULL OR mc.expire_date >= CURDATE())
          AND (mc.remain_times IS NULL OR mc.remain_times > 0)
        ORDER BY mc.buy_date DESC, mc.id DESC
        LIMIT 1;

        IF v_member_card_id IS NOT NULL THEN
            IF v_card_category = '次卡' THEN
                UPDATE member_card
                SET remain_times = remain_times - 1
                WHERE id = v_member_card_id;

                UPDATE member_card
                SET status = '已用完'
                WHERE id = v_member_card_id
                  AND remain_times <= 0;
            ELSE
                IF (
                    SELECT COUNT(*)
                    FROM booking b
                    WHERE b.member_id = NEW.member_id
                      AND DATE(b.checkin_time) = DATE(NEW.checkin_time)
                ) = 1 THEN
                    UPDATE member_card
                    SET expire_date = DATE_SUB(expire_date, INTERVAL 1 DAY)
                    WHERE id = v_member_card_id
                      AND expire_date IS NOT NULL;

                    UPDATE member_card
                    SET status = '已过期'
                    WHERE id = v_member_card_id
                      AND expire_date < CURDATE();
                END IF;
            END IF;
        END IF;
    END IF;
END //

CREATE PROCEDURE sp_member_detail(IN p_member_id INT)
BEGIN
    DROP TEMPORARY TABLE IF EXISTS tmp_member_detail;

    CREATE TEMPORARY TABLE tmp_member_detail (
        info_type VARCHAR(50),
        info_detail VARCHAR(200),
        info_value VARCHAR(200)
    );

    INSERT INTO tmp_member_detail
    SELECT '基本信息', '姓名', name FROM member WHERE id = p_member_id;

    INSERT INTO tmp_member_detail
    SELECT '基本信息', '手机号', phone FROM member WHERE id = p_member_id;

    INSERT INTO tmp_member_detail
    SELECT '基本信息', '入会日期', DATE_FORMAT(join_date, '%Y-%m-%d')
    FROM member WHERE id = p_member_id;

    INSERT INTO tmp_member_detail
    SELECT '有效会员卡', '卡类型', ct.name
    FROM member_card mc
    JOIN card_type ct ON mc.card_type_id = ct.id
    WHERE mc.member_id = p_member_id
      AND mc.status = '正常'
      AND (mc.expire_date IS NULL OR mc.expire_date >= CURDATE())
      AND (mc.remain_times IS NULL OR mc.remain_times > 0)
    ORDER BY mc.buy_date DESC, mc.id DESC
    LIMIT 1;

    INSERT INTO tmp_member_detail
    SELECT '有效会员卡', '剩余次数', COALESCE(CAST(remain_times AS CHAR), '不限次数')
    FROM member_card
    WHERE member_id = p_member_id
      AND status = '正常'
      AND (expire_date IS NULL OR expire_date >= CURDATE())
    ORDER BY buy_date DESC, id DESC
    LIMIT 1;

    INSERT INTO tmp_member_detail
    SELECT '有效会员卡', '有效期至', COALESCE(DATE_FORMAT(expire_date, '%Y-%m-%d'), '不限日期')
    FROM member_card
    WHERE member_id = p_member_id
      AND status = '正常'
      AND (expire_date IS NULL OR expire_date >= CURDATE())
    ORDER BY buy_date DESC, id DESC
    LIMIT 1;

    INSERT INTO tmp_member_detail
    SELECT
        '历史预约',
        CONCAT(c.name, ' ', DATE_FORMAT(cs.schedule_time, '%Y-%m-%d %H:%i')),
        b.status
    FROM booking b
    JOIN course_schedule cs ON b.schedule_id = cs.id
    JOIN course c ON cs.course_id = c.id
    WHERE b.member_id = p_member_id
    ORDER BY b.book_time DESC
    LIMIT 20;

    INSERT INTO tmp_member_detail
    SELECT '消费明细', CONCAT('办卡-', ct.name), CONCAT('¥', FORMAT(mc.price, 2))
    FROM member_card mc
    JOIN card_type ct ON mc.card_type_id = ct.id
    WHERE mc.member_id = p_member_id
    ORDER BY mc.buy_date DESC;

    INSERT INTO tmp_member_detail
    SELECT
        '消费明细',
        '累计消费',
        CONCAT('¥', FORMAT(COALESCE(SUM(price), 0), 2))
    FROM member_card
    WHERE member_id = p_member_id;

    SELECT * FROM tmp_member_detail;

    DROP TEMPORARY TABLE IF EXISTS tmp_member_detail;
END //

CREATE PROCEDURE sp_update_schedule_status()
BEGIN
    UPDATE course_schedule
    SET status = '已结束'
    WHERE status = '未开始'
      AND schedule_time < NOW() - INTERVAL 2 HOUR;

    UPDATE booking b
    JOIN course_schedule cs ON b.schedule_id = cs.id
    SET b.status = '已过期'
    WHERE b.status = '已预约'
      AND cs.schedule_time < NOW();
END //

DELIMITER ;

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
LEFT JOIN course_schedule cs
    ON c.id = cs.course_id
   AND cs.schedule_time BETWEEN NOW() - INTERVAL 7 DAY AND NOW() + INTERVAL 7 DAY
LEFT JOIN booking b ON cs.id = b.schedule_id
GROUP BY c.id, c.name, c.category
ORDER BY booking_count DESC, c.id;

SELECT 'gym_db 初始化完成' AS message;
