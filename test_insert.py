#!/usr/bin/env python3
"""
ไฟล์ทดสอบการบันทึกข้อมูลลง Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# โหลด environment variables
load_dotenv()

def test_insert_data():
    """ทดสอบการบันทึกข้อมูล"""
    print("=" * 50)
    print("ทดสอบการบันทึกข้อมูลลง Supabase")
    print("=" * 50)
    
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
        
        print("กำลังบันทึกข้อมูลทดสอบ...")
        
        # บันทึกข้อมูล
        result = supabase.table('lottery_results').insert(test_data).execute()
        
        if result.data:
            print("SUCCESS: บันทึกข้อมูลสำเร็จ!")
            print(f"ID: {result.data[0]['id']}")
            print(f"วันที่: {result.data[0]['draw_date']}")
            print(f"รางวัลที่ 1: {result.data[0]['first_prize']}")
            
            # ทดสอบการดึงข้อมูล
            print("\nกำลังดึงข้อมูล...")
            all_data = supabase.table('lottery_results').select('*').execute()
            print(f"SUCCESS: พบข้อมูลทั้งหมด: {len(all_data.data)} รายการ")
            
            return True
        else:
            print("ERROR: ไม่สามารถบันทึกข้อมูลได้")
            return False
            
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    test_insert_data()
