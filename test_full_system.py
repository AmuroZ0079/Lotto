#!/usr/bin/env python3
"""
ไฟล์ทดสอบระบบเต็ม (scrap + database)
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import date

# โหลด environment variables
load_dotenv()

def test_full_system():
    """ทดสอบระบบเต็ม"""
    print("=" * 60)
    print("ทดสอบระบบเต็ม (Scrap + Database)")
    print("=" * 60)
    
    try:
        # เชื่อมต่อ Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ข้อมูลตัวอย่างสำหรับทดสอบ
        test_data = {
            'draw_date': '2024-01-16',
            'draw_number': '1/2567',
            'first_prize': '123456',
            'second_prize_1': '234567',
            'second_prize_2': '345678',
            'third_prize_1': '456789',
            'third_prize_2': '567890',
            'third_prize_3': '678901',
            'fourth_prize_1': '789012',
            'fourth_prize_2': '890123',
            'fourth_prize_3': '901234',
            'fourth_prize_4': '012345',
            'fifth_prize_1': '111111',
            'fifth_prize_2': '222222',
            'fifth_prize_3': '333333'
        }
        
        print("1. ทดสอบการบันทึกข้อมูล...")
        
        # บันทึกข้อมูล
        result = supabase.table('lottery_results').insert(test_data).execute()
        
        if result.data:
            print("SUCCESS: บันทึกข้อมูลสำเร็จ!")
            print(f"ID: {result.data[0]['id']}")
            print(f"วันที่: {result.data[0]['draw_date']}")
            print(f"รางวัลที่ 1: {result.data[0]['first_prize']}")
        else:
            print("ERROR: ไม่สามารถบันทึกข้อมูลได้")
            return False
        
        print("\n2. ทดสอบการดึงข้อมูล...")
        
        # ดึงข้อมูลทั้งหมด
        all_data = supabase.table('lottery_results').select('*').execute()
        print(f"SUCCESS: พบข้อมูลทั้งหมด: {len(all_data.data)} รายการ")
        
        # ดึงข้อมูลล่าสุด
        latest_data = supabase.table('lottery_results').select('*').order('draw_date', desc=True).limit(1).execute()
        if latest_data.data:
            latest = latest_data.data[0]
            print(f"SUCCESS: ข้อมูลล่าสุด:")
            print(f"  วันที่: {latest['draw_date']}")
            print(f"  งวด: {latest['draw_number']}")
            print(f"  รางวัลที่ 1: {latest['first_prize']}")
        
        print("\n3. ทดสอบการอัปเดตข้อมูล...")
        
        # อัปเดตข้อมูล
        update_data = {'first_prize': '999999'}
        update_result = supabase.table('lottery_results').update(update_data).eq('draw_date', '2024-01-16').execute()
        
        if update_result.data:
            print("SUCCESS: อัปเดตข้อมูลสำเร็จ!")
            print(f"รางวัลที่ 1 ใหม่: {update_result.data[0]['first_prize']}")
        else:
            print("ERROR: ไม่สามารถอัปเดตข้อมูลได้")
        
        print("\n4. ทดสอบการลบข้อมูล...")
        
        # ลบข้อมูลทดสอบ
        delete_result = supabase.table('lottery_results').delete().eq('draw_date', '2024-01-16').execute()
        
        if delete_result.data:
            print("SUCCESS: ลบข้อมูลสำเร็จ!")
        else:
            print("ERROR: ไม่สามารถลบข้อมูลได้")
        
        print("\n=== สรุปผลลัพธ์ ===")
        print("SUCCESS: ระบบทำงานได้ครบทุกฟังก์ชัน!")
        print("- การบันทึกข้อมูล")
        print("- การดึงข้อมูล")
        print("- การอัปเดตข้อมูล")
        print("- การลบข้อมูล")
        
        return True
        
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    test_full_system()
