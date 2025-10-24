#!/usr/bin/env python3
"""
ไฟล์ลบข้อมูลในฐานข้อมูล
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# โหลด environment variables
load_dotenv()

def clean_database():
    """ลบข้อมูลในฐานข้อมูล"""
    print("=" * 50)
    print("ลบข้อมูลในฐานข้อมูล")
    print("=" * 50)
    
    try:
        # เชื่อมต่อ Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ดูข้อมูลที่มีอยู่
        all_data = supabase.table('lottery_results').select('*').execute()
        print(f"พบข้อมูล: {len(all_data.data)} รายการ")
        
        if all_data.data:
            for item in all_data.data:
                print(f"  ID: {item['id']}, วันที่: {item['draw_date']}, รางวัลที่ 1: {item['first_prize']}")
        
        # ลบข้อมูลทั้งหมด
        print("\nกำลังลบข้อมูลทั้งหมด...")
        delete_result = supabase.table('lottery_results').delete().neq('id', 0).execute()
        
        if delete_result.data:
            print(f"SUCCESS: ลบข้อมูลสำเร็จ! ลบไป {len(delete_result.data)} รายการ")
        else:
            print("SUCCESS: ไม่มีข้อมูลให้ลบ")
        
        # ตรวจสอบอีกครั้ง
        all_data_after = supabase.table('lottery_results').select('*').execute()
        print(f"ข้อมูลที่เหลือ: {len(all_data_after.data)} รายการ")
        
        return True
        
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    clean_database()
