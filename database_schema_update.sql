-- อัปเดต database schema ให้ตรงกับ 4 รางวัลหลัก
-- รันคำสั่งเหล่านี้ใน Supabase Dashboard > SQL Editor

-- 1. ลบตารางเก่า
DROP TABLE IF EXISTS lottery_results;

-- 2. สร้างตารางใหม่
CREATE TABLE lottery_results (
    id SERIAL PRIMARY KEY,
    draw_date DATE NOT NULL UNIQUE,
    draw_number VARCHAR(20),
    first_prize VARCHAR(6),
    second_prize_1 VARCHAR(3),
    second_prize_2 VARCHAR(3),
    third_prize_1 VARCHAR(3),
    third_prize_2 VARCHAR(3),
    fourth_prize_1 VARCHAR(2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. สร้าง index
CREATE INDEX idx_lottery_results_draw_date ON lottery_results(draw_date);
CREATE INDEX idx_lottery_results_first_prize ON lottery_results(first_prize);

-- 4. ตรวจสอบตาราง
SELECT * FROM lottery_results LIMIT 1;
