#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
อัปเดต database schema ให้ตรงกับ 4 รางวัลหลัก
- รางวัลที่ 1
- เลขหน้า 3 ตัว (2 ตัว)
- เลขท้าย 3 ตัว (2 ตัว)
- เลขท้าย 2 ตัว (1 ตัว)
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# โหลด environment variables
load_dotenv()

# การตั้งค่า Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def update_database_schema():
    """อัปเดต database schema ให้ตรงกับ 4 รางวัลหลัก"""
    try:
        # เชื่อมต่อ Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("เชื่อมต่อ Supabase สำเร็จ")
        
        # ลบตารางเก่า
        print("กำลังลบตารางเก่า...")
        drop_table_sql = "DROP TABLE IF EXISTS lottery_results;"
        supabase.rpc('exec_sql', {'sql': drop_table_sql}).execute()
        print("ลบตารางเก่าสำเร็จ")
        
        # สร้างตารางใหม่
        print("กำลังสร้างตารางใหม่...")
        create_table_sql = """
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
        
        -- สร้าง index
        CREATE INDEX idx_lottery_results_draw_date ON lottery_results(draw_date);
        CREATE INDEX idx_lottery_results_first_prize ON lottery_results(first_prize);
        """
        
        supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("สร้างตารางใหม่สำเร็จ")
        
        print("อัปเดต database schema สำเร็จ!")
        print("Schema ใหม่:")
        print("   - draw_date: วันที่งวด")
        print("   - draw_number: เลขงวด")
        print("   - first_prize: รางวัลที่ 1 (6 หลัก)")
        print("   - second_prize_1: เลขหน้า 3 ตัว ตัวที่ 1")
        print("   - second_prize_2: เลขหน้า 3 ตัว ตัวที่ 2")
        print("   - third_prize_1: เลขท้าย 3 ตัว ตัวที่ 1")
        print("   - third_prize_2: เลขท้าย 3 ตัว ตัวที่ 2")
        print("   - fourth_prize_1: เลขท้าย 2 ตัว")
        
    except Exception as e:
        print(f"ไม่สามารถอัปเดต database schema ได้: {e}")

if __name__ == "__main__":
    update_database_schema()
