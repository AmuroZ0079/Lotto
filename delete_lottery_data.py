#!/usr/bin/env python3
"""
ไฟล์ลบข้อมูลลอตเตอรี่ในฐานข้อมูล
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# โหลด environment variables
load_dotenv()

def delete_lottery_data(draw_date):
    """ลบข้อมูลลอตเตอรี่ตามวันที่"""
    print("=" * 60)
    print(f"ลบข้อมูลลอตเตอรี่วันที่: {draw_date}")
    print("=" * 60)
    
    try:
        # เชื่อมต่อ Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ดูข้อมูลที่มีอยู่ก่อน
        existing_data = supabase.table('lottery_results').select("*").eq("draw_date", draw_date).execute()
        print(f"พบข้อมูล: {len(existing_data.data)} รายการ")
        
        if existing_data.data:
            for item in existing_data.data:
                print(f"  ID: {item['id']}, วันที่: {item['draw_date']}, รางวัลที่ 1: {item['first_prize']}")
        
        # ลบข้อมูล
        if existing_data.data:
            print(f"\nกำลังลบข้อมูลวันที่ {draw_date}...")
            delete_result = supabase.table('lottery_results').delete().eq("draw_date", draw_date).execute()
            
            if delete_result.data:
                print(f"SUCCESS: ลบข้อมูลสำเร็จ! ลบไป {len(delete_result.data)} รายการ")
            else:
                print("SUCCESS: ไม่มีข้อมูลให้ลบ")
        else:
            print("ไม่มีข้อมูลให้ลบ")
        
        # ตรวจสอบอีกครั้ง
        remaining_data = supabase.table('lottery_results').select("*").eq("draw_date", draw_date).execute()
        print(f"ข้อมูลที่เหลือ: {len(remaining_data.data)} รายการ")
        
        return True
        
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        return False

def delete_all_lottery_data():
    """ลบข้อมูลลอตเตอรี่ทั้งหมด"""
    print("=" * 60)
    print("ลบข้อมูลลอตเตอรี่ทั้งหมด")
    print("=" * 60)
    
    try:
        # เชื่อมต่อ Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ดูข้อมูลทั้งหมด
        all_data = supabase.table('lottery_results').select("*").execute()
        print(f"พบข้อมูลทั้งหมด: {len(all_data.data)} รายการ")
        
        if all_data.data:
            for item in all_data.data:
                print(f"  ID: {item['id']}, วันที่: {item['draw_date']}, รางวัลที่ 1: {item['first_prize']}")
        
        # ลบข้อมูลทั้งหมด
        if all_data.data:
            print(f"\nกำลังลบข้อมูลทั้งหมด...")
            delete_result = supabase.table('lottery_results').delete().neq('id', 0).execute()
            
            if delete_result.data:
                print(f"SUCCESS: ลบข้อมูลสำเร็จ! ลบไป {len(delete_result.data)} รายการ")
            else:
                print("SUCCESS: ไม่มีข้อมูลให้ลบ")
        else:
            print("ไม่มีข้อมูลให้ลบ")
        
        # ตรวจสอบอีกครั้ง
        remaining_data = supabase.table('lottery_results').select("*").execute()
        print(f"ข้อมูลที่เหลือ: {len(remaining_data.data)} รายการ")
        
        return True
        
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("เลือกการลบข้อมูล:")
    print("1. ลบข้อมูลวันที่เฉพาะ")
    print("2. ลบข้อมูลทั้งหมด")
    
    choice = input("\nเลือก (1 หรือ 2): ").strip()
    
    if choice == "1":
        draw_date = input("กรอกวันที่ (YYYY-MM-DD): ").strip()
        if draw_date:
            delete_lottery_data(draw_date)
        else:
            print("ERROR: กรุณากรอกวันที่")
    elif choice == "2":
        confirm = input("ยืนยันการลบข้อมูลทั้งหมด? (y/N): ").strip().lower()
        if confirm == 'y':
            delete_all_lottery_data()
        else:
            print("ยกเลิกการลบข้อมูล")
    else:
        print("ตัวเลือกไม่ถูกต้อง")

if __name__ == "__main__":
    main()
