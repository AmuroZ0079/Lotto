#!/usr/bin/env python3
"""
ไฟล์ทดสอบการ scrap แบบอัตโนมัติ
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import date
import logging

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sanook_scraping():
    """ทดสอบการ scrap จาก Sanook"""
    print("=" * 60)
    print("ทดสอบการ scrap จาก Sanook Lotto")
    print("=" * 60)
    
    try:
        url = "https://news.sanook.com/lotto/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"กำลังเข้าถึง: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("SUCCESS: เข้าถึงเว็บไซต์สำเร็จ")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # หา link ไปยังผลลอตเตอรี่งวดล่าสุด
            latest_links = soup.find_all('a', href=lambda x: x and 'ตรวจหวย' in x and 'งวด' in x)
            
            print(f"พบ link ผลลอตเตอรี่: {len(latest_links)} ลิงก์")
            
            if latest_links:
                # ไปที่หน้าผลลอตเตอรี่งวดล่าสุด
                latest_url = latest_links[0].get('href')
                if latest_url.startswith('/'):
                    latest_url = 'https://news.sanook.com' + latest_url
                
                print(f"กำลังไปที่: {latest_url}")
                response2 = requests.get(latest_url, headers=headers, timeout=15)
                
                if response2.status_code == 200:
                    soup2 = BeautifulSoup(response2.content, 'html.parser')
                    
                    # หาตัวเลข 6 หลัก
                    numbers = re.findall(r'\d{6}', soup2.get_text())
                    print(f"พบตัวเลข 6 หลัก: {len(numbers)} ตัว")
                    
                    if numbers:
                        print("\nตัวเลขที่พบ:")
                        for i, num in enumerate(numbers[:15]):  # แสดง 15 ตัวแรก
                            print(f"  {i+1:2d}. {num}")
                        
                        # พยายามจัดกลุ่มรางวัล
                        if len(numbers) >= 1:
                            print(f"\nรางวัลที่ 1: {numbers[0]}")
                        if len(numbers) >= 3:
                            print(f"รางวัลที่ 2: {numbers[1]}, {numbers[2]}")
                        if len(numbers) >= 6:
                            print(f"รางวัลที่ 3: {numbers[3]}, {numbers[4]}, {numbers[5]}")
                        if len(numbers) >= 10:
                            print(f"รางวัลที่ 4: {numbers[6]}, {numbers[7]}, {numbers[8]}, {numbers[9]}")
                        if len(numbers) >= 13:
                            print(f"รางวัลที่ 5: {numbers[10]}, {numbers[11]}, {numbers[12]}")
                        
                        return numbers
                    else:
                        print("ERROR: ไม่พบตัวเลข 6 หลัก")
                        print("\nเนื้อหาหน้าเว็บ (ส่วนแรก):")
                        print(soup2.get_text()[:500])
                else:
                    print(f"ERROR: ไม่สามารถเข้าถึงหน้าได้: {response2.status_code}")
            else:
                print("ERROR: ไม่พบ link ผลลอตเตอรี่")
                print("\nเนื้อหาหน้าเว็บ (ส่วนแรก):")
                print(soup.get_text()[:500])
                
        else:
            print(f"ERROR: ไม่สามารถเข้าถึงเว็บไซต์ได้: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        logger.error(f"Error in test_sanook_scraping: {e}")
        return None

def test_with_sample_data():
    """ทดสอบด้วยข้อมูลตัวอย่าง"""
    print("\n" + "=" * 60)
    print("ทดสอบด้วยข้อมูลตัวอย่าง")
    print("=" * 60)
    
    # ข้อมูลตัวอย่าง
    sample_data = {
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
    
    print("SUCCESS: ข้อมูลตัวอย่าง:")
    print("-" * 40)
    for key, value in sample_data.items():
        if value:
            print(f"{key}: {value}")
    print("-" * 40)
    
    return sample_data

if __name__ == "__main__":
    print("ระบบทดสอบการ scrap แบบอัตโนมัติ")
    print("1. ทดสอบการ scrap จาก Sanook")
    print("2. ทดสอบด้วยข้อมูลตัวอย่าง")
    
    # ทดสอบการ scrap จาก Sanook
    print("\n=== ทดสอบการ scrap จาก Sanook ===")
    result1 = test_sanook_scraping()
    
    # ทดสอบด้วยข้อมูลตัวอย่าง
    print("\n=== ทดสอบด้วยข้อมูลตัวอย่าง ===")
    result2 = test_with_sample_data()
    
    print("\n=== สรุปผลลัพธ์ ===")
    if result1:
        print("SUCCESS: การ scrap จาก Sanook สำเร็จ")
    else:
        print("ERROR: การ scrap จาก Sanook ล้มเหลว")
    
    if result2:
        print("SUCCESS: ข้อมูลตัวอย่างใช้งานได้")
    else:
        print("ERROR: ข้อมูลตัวอย่างมีปัญหา")
