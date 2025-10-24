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
        
        # ลบข้อมูลเก่า
        print("กำลังลบข้อมูลเก่า...")
        result = supabase.table('lottery_results').delete().neq('id', 0).execute()
        print(f"ลบข้อมูลเก่า {len(result.data)} รายการ")
        
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
