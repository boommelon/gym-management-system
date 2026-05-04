-- ========================================
-- 健身房会员及课程管理系统
-- 已有数据库升级脚本（适合你当前已经初始化过的库）
-- 说明：尽量不删除业务数据，只修复结构、对象和默认值
-- ========================================

USE gym_db;

SET NAMES utf8mb4;

ALTER TABLE member
    MODIFY gender ENUM('男', '女') NOT NULL DEFAULT '男',
    MODIFY status ENUM('正常', '冻结', '已过期') NOT NULL DEFAULT '正常';

ALTER TABLE card_type
    MODIFY card_category ENUM('次卡', '月卡', '季卡', '年卡') NOT NULL;

ALTER TABLE member_card
    MODIFY status ENUM('未激活', '正常', '已用完', '已过期') NOT NULL DEFAULT '正常';

ALTER TABLE coach
    MODIFY gender ENUM('男', '女') NOT NULL DEFAULT '男',
    MODIFY status ENUM('在职', '离职') NOT NULL DEFAULT '在职';

ALTER TABLE course_schedule
    MODIFY status ENUM('未开始', '进行中', '已结束', '已取消') NOT NULL DEFAULT '未开始';

ALTER TABLE booking
    MODIFY status ENUM('已预约', '已签到', '已取消', '已过期') NOT NULL DEFAULT '已预约',
    MODIFY rating TINYINT DEFAULT NULL;

ALTER TABLE equipment
    MODIFY status ENUM('在库', '借出', '维修中', '已报废') NOT NULL DEFAULT '在库';

ALTER TABLE equipment_borrow
    MODIFY status ENUM('借用中', '已归还') NOT NULL DEFAULT '借用中';

UPDATE equipment SET status = '在库' WHERE status = '在库';
UPDATE equipment SET status = '借出' WHERE status = '借出';
UPDATE equipment SET status = '维修中' WHERE status = '维修中';
UPDATE equipment SET status = '已报废' WHERE status = '已报废';

DROP TRIGGER IF EXISTS trg_after_checkin;
DROP VIEW IF EXISTS v_course_weekly_stats;
DROP PROCEDURE IF EXISTS sp_member_detail;
DROP PROCEDURE IF EXISTS sp_update_schedule_status;

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

UPDATE course_schedule cs
SET current_count = (
    SELECT COUNT(*)
    FROM booking b
    WHERE b.schedule_id = cs.id
      AND b.status = '已预约'
);

SELECT 'gym_db 结构升级完成，原有业务数据已保留' AS message;
