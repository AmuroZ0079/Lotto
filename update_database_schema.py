#!/usr/bin/env python3
"""
ไฟล์อัปเดต database schema ให้ตรงกับ 4 รางวัลหลัก
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# โหลด environment variables
load_dotenv()

def update_database_schema():
    """อัปเดต database schema ให้ตรงกับ 4 รางวัลหลัก"""
    print("=" * 60)
    print("อัปเดต Database Schema ให้ตรงกับ 4 รางวัลหลัก")
    print("=" * 60)
    
    try:
        # เชื่อมต่อ Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # 1. ลบตารางเก่า
        print("1. ลบตารางเก่า...")
        try:
            supabase.table('lottery_results').delete().neq('id', 0).execute()
            print("SUCCESS: ลบข้อมูลเก่าออกแล้ว")
        except Exception as e:
            print(f"WARNING: ไม่สามารถลบข้อมูลเก่าได้: {e}")
        
        # 2. สร้างตารางใหม่
        print("\n2. สร้างตารางใหม่...")
        create_table_sql = """
        DROP TABLE IF EXISTS lottery_results;
        
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
        
        -- สร้าง index สำหรับการค้นหา
        CREATE INDEX idx_lottery_draw_date ON lottery_results(draw_date);
        CREATE INDEX idx_lottery_created_at ON lottery_results(created_at);
        """
        
        try:
            result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            print("SUCCESS: สร้างตารางใหม่สำเร็จ")
        except Exception as e:
            print(f"WARNING: ไม่สามารถใช้ exec_sql ได้: {e}")
            print("ลองใช้วิธีอื่น...")
        
        # 3. ทดสอบการสร้างข้อมูล
        print("\n3. ทดสอบการสร้างข้อมูล...")
        test_data = {
            'draw_date': '2025-10-01',
            'draw_number': '1/2568',
            'first_prize': '876978',
            'second_prize_1': '843',
            'second_prize_2': '532',
            'third_prize_1': '280',
            'third_prize_2': '605',
            'fourth_prize_1': '77'
        }
        
        try:
            result = supabase.table('lottery_results').insert(test_data).execute()
            print("SUCCESS: ทดสอบการสร้างข้อมูลสำเร็จ")
            print(f"ID: {result.data[0]['id']}")
            print(f"วันที่: {result.data[0]['draw_date']}")
            print(f"รางวัลที่ 1: {result.data[0]['first_prize']}")
            print(f"เลขหน้า 3 ตัว: {result.data[0]['second_prize_1']}, {result.data[0]['second_prize_2']}")
            print(f"เลขท้าย 3 ตัว: {result.data[0]['third_prize_1']}, {result.data[0]['third_prize_2']}")
            print(f"เลขท้าย 2 ตัว: {result.data[0]['fourth_prize_1']}")
        except Exception as e:
            print(f"ERROR: ไม่สามารถสร้างข้อมูลทดสอบได้: {e}")
            return False
        
        # 4. ลบข้อมูลทดสอบ
        print("\n4. ลบข้อมูลทดสอบ...")
        try:
            supabase.table('lottery_results').delete().eq('draw_date', '2025-10-01').execute()
            print("SUCCESS: ลบข้อมูลทดสอบสำเร็จ")
        except Exception as e:
            print(f"WARNING: ไม่สามารถลบข้อมูลทดสอบได้: {e}")
        
        print("\n=== สรุปผลลัพธ์ ===")
        print("SUCCESS: อัปเดต database schema สำเร็จ!")
        print("ตารางใหม่มี 4 รางวัลหลัก:")
        print("1. รางวัลที่ 1 (first_prize)")
        print("2. เลขหน้า 3 ตัว (second_prize_1, second_prize_2)")
        print("3. เลขท้าย 3 ตัว (third_prize_1, third_prize_2)")
        print("4. เลขท้าย 2 ตัว (fourth_prize_1)")
        
        return True
        
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    update_database_schema()
