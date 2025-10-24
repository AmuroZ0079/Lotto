#!/usr/bin/env python3
"""
ไฟล์ตรวจสอบข้อมูลในฐานข้อมูล
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# โหลด environment variables
load_dotenv()

def check_database():
    """ตรวจสอบข้อมูลในฐานข้อมูล"""
    print("=" * 60)
    print("ตรวจสอบข้อมูลในฐานข้อมูล")
    print("=" * 60)
    
    try:
        # เชื่อมต่อ Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ดึงข้อมูลทั้งหมด
        all_data = supabase.table('lottery_results').select('*').order('draw_date', desc=True).execute()
        
        print(f"พบข้อมูลทั้งหมด: {len(all_data.data)} รายการ")
        print("\nข้อมูลล่าสุด:")
        print("-" * 50)
        
        for i, item in enumerate(all_data.data):
            print(f"รายการที่ {i+1}:")
            print(f"  ID: {item['id']}")
            print(f"  วันที่: {item['draw_date']}")
            print(f"  งวด: {item['draw_number']}")
            print(f"  รางวัลที่ 1: {item['first_prize']}")
            print(f"  รางวัลที่ 2: {item['second_prize_1']}, {item['second_prize_2']}")
            print(f"  รางวัลที่ 3: {item['third_prize_1']}, {item['third_prize_2']}, {item['third_prize_3']}")
            print(f"  สร้างเมื่อ: {item['created_at']}")
            print("-" * 50)
        
        # สถิติ
        print(f"\nสถิติ:")
        print(f"  จำนวนรายการทั้งหมด: {len(all_data.data)}")
        if all_data.data:
            latest = all_data.data[0]
            print(f"  ข้อมูลล่าสุด: {latest['draw_date']}")
            print(f"  รางวัลที่ 1 ล่าสุด: {latest['first_prize']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    check_database()
