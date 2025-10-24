#!/usr/bin/env python3
"""
ไฟล์ทดสอบการ scrap ผลลอตเตอรี่
รันไฟล์นี้เพื่อทดสอบว่าการ scrap ทำงานได้หรือไม่
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LotteryScraper
import logging

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_scraping():
    """ทดสอบการ scrap"""
    print("=" * 50)
    print("เริ่มทดสอบการ scrap ผลลอตเตอรี่")
    print("=" * 50)
    
    try:
        # สร้าง scraper
        scraper = LotteryScraper()
        
        # ทดสอบการ scrap
        print("กำลังดึงข้อมูลผลลอตเตอรี่...")
        result = scraper.scrape_lottery_result()
        
        if result:
            print("\n✅ การ scrap สำเร็จ!")
            print("\nข้อมูลที่ได้:")
            print("-" * 30)
            for key, value in result.items():
                if value:  # แสดงเฉพาะค่าที่ไม่ว่าง
                    print(f"{key}: {value}")
            print("-" * 30)
            
            # ทดสอบการบันทึกลงฐานข้อมูล (ถ้ามีการตั้งค่า)
            try:
                if scraper.db.save_lottery_result(result):
                    print("\n✅ บันทึกลงฐานข้อมูลสำเร็จ!")
                else:
                    print("\n⚠️ ไม่สามารถบันทึกลงฐานข้อมูลได้ (อาจยังไม่ได้ตั้งค่า Supabase)")
            except Exception as e:
                print(f"\n⚠️ ไม่สามารถบันทึกลงฐานข้อมูลได้: {e}")
                
        else:
            print("\n❌ การ scrap ล้มเหลว!")
            print("อาจเป็นเพราะ:")
            print("- เว็บไซต์ไม่ตอบสนอง")
            print("- โครงสร้าง HTML เปลี่ยนแปลง")
            print("- ยังไม่มีผลลอตเตอรี่ออก")
            
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        logger.error(f"Error in test_scraping: {e}")

def test_without_database():
    """ทดสอบการ scrap โดยไม่ใช้ฐานข้อมูล"""
    print("\n" + "=" * 50)
    print("ทดสอบการ scrap โดยไม่ใช้ฐานข้อมูล")
    print("=" * 50)
    
    try:
        # สร้าง scraper โดยไม่ใช้ฐานข้อมูล
        scraper = LotteryScraper()
        scraper.db = None  # ปิดการใช้งานฐานข้อมูล
        
        result = scraper.scrape_lottery_result()
        
        if result:
            print("✅ การ scrap สำเร็จ!")
            print("\nข้อมูลที่ได้:")
            for key, value in result.items():
                if value:
                    print(f"  {key}: {value}")
        else:
            print("❌ การ scrap ล้มเหลว!")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

def test_with_sample_data():
    """ทดสอบด้วยข้อมูลตัวอย่าง"""
    print("\n" + "=" * 50)
    print("ทดสอบด้วยข้อมูลตัวอย่าง")
    print("=" * 50)
    
    try:
        scraper = LotteryScraper()
        scraper.db = None  # ปิดการใช้งานฐานข้อมูล
        
        # ใช้ข้อมูลตัวอย่าง
        result = scraper.scrape_lottery_result(use_sample_data=True)
        
        if result:
            print("✅ การใช้ข้อมูลตัวอย่างสำเร็จ!")
            print("\nข้อมูลที่ได้:")
            for key, value in result.items():
                if value:
                    print(f"  {key}: {value}")
        else:
            print("❌ ไม่สามารถใช้ข้อมูลตัวอย่างได้!")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    print("ระบบทดสอบการ scrap ผลลอตเตอรี่")
    print("เลือกการทดสอบ:")
    print("1. ทดสอบแบบเต็ม (รวมฐานข้อมูล)")
    print("2. ทดสอบเฉพาะการ scrap")
    print("3. ทดสอบด้วยข้อมูลตัวอย่าง")
    
    choice = input("\nเลือก (1, 2 หรือ 3): ").strip()
    
    if choice == "1":
        test_scraping()
    elif choice == "2":
        test_without_database()
    elif choice == "3":
        test_with_sample_data()
    else:
        print("ตัวเลือกไม่ถูกต้อง")
        sys.exit(1)
