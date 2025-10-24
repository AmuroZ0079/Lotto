#!/usr/bin/env python3
"""
ไฟล์ทดสอบการ scrap จาก Sanook Lotto
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

def test_sanook_scraping():
    """ทดสอบการ scrap จาก Sanook"""
    print("=" * 60)
    print("ทดสอบการ scrap จาก Sanook Lotto")
    print("=" * 60)
    
    try:
        # สร้าง scraper
        scraper = LotteryScraper()
        
        # ทดสอบการ scrap จาก Sanook
        print("กำลังดึงข้อมูลจาก Sanook...")
        result = scraper.scrape_lottery_result()
        
        if result:
            print("\n✅ การ scrap จาก Sanook สำเร็จ!")
            print("\nข้อมูลที่ได้:")
            print("-" * 40)
            for key, value in result.items():
                if value:
                    print(f"{key}: {value}")
            print("-" * 40)
            
            # ตรวจสอบข้อมูลสำคัญ
            if result.get('first_prize'):
                print(f"\n🎯 รางวัลที่ 1: {result['first_prize']}")
            else:
                print("\n⚠️ ไม่พบรางวัลที่ 1")
                
            if result.get('draw_number'):
                print(f"📅 งวด: {result['draw_number']}")
            else:
                print("⚠️ ไม่พบหมายเลขงวด")
                
        else:
            print("\n❌ การ scrap จาก Sanook ล้มเหลว!")
            print("\nสาเหตุที่เป็นไปได้:")
            print("- เว็บไซต์ไม่ตอบสนอง")
            print("- โครงสร้าง HTML เปลี่ยนแปลง")
            print("- ยังไม่มีผลลอตเตอรี่ออก")
            print("- ต้องปรับแต่ง CSS selectors")
            
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        logger.error(f"Error in test_sanook_scraping: {e}")

def test_sanook_direct():
    """ทดสอบการ scrap โดยตรงจาก Sanook"""
    print("\n" + "=" * 60)
    print("ทดสอบการ scrap โดยตรงจาก Sanook")
    print("=" * 60)
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = "https://news.sanook.com/lotto/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"กำลังเข้าถึง: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("✅ เข้าถึงเว็บไซต์สำเร็จ")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # หา link ไปยังผลลอตเตอรี่งวดล่าสุด
            latest_links = soup.find_all('a', href=lambda x: x and 'ตรวจหวย' in x and 'งวด' in x)
            
            print(f"\nพบ link ผลลอตเตอรี่: {len(latest_links)} ลิงก์")
            
            for i, link in enumerate(latest_links[:3]):  # แสดง 3 ลิงก์แรก
                href = link.get('href')
                text = link.get_text().strip()
                print(f"  {i+1}. {text} -> {href}")
            
            if latest_links:
                # ไปที่หน้าผลลอตเตอรี่งวดล่าสุด
                latest_url = latest_links[0].get('href')
                if latest_url.startswith('/'):
                    latest_url = 'https://news.sanook.com' + latest_url
                
                print(f"\nกำลังไปที่: {latest_url}")
                response2 = requests.get(latest_url, headers=headers, timeout=15)
                
                if response2.status_code == 200:
                    soup2 = BeautifulSoup(response2.content, 'html.parser')
                    
                    # หาตัวเลข 6 หลัก
                    import re
                    numbers = re.findall(r'\d{6}', soup2.get_text())
                    print(f"\nพบตัวเลข 6 หลัก: {len(numbers)} ตัว")
                    
                    if numbers:
                        print("ตัวเลขที่พบ:")
                        for i, num in enumerate(numbers[:10]):  # แสดง 10 ตัวแรก
                            print(f"  {i+1}. {num}")
                    else:
                        print("ไม่พบตัวเลข 6 หลัก")
                        print("\nเนื้อหาหน้าเว็บ (ส่วนแรก):")
                        print(soup2.get_text()[:500])
                else:
                    print(f"❌ ไม่สามารถเข้าถึงหน้าได้: {response2.status_code}")
            else:
                print("❌ ไม่พบ link ผลลอตเตอรี่")
                
        else:
            print(f"❌ ไม่สามารถเข้าถึงเว็บไซต์ได้: {response.status_code}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    print("ระบบทดสอบการ scrap จาก Sanook Lotto")
    print("เลือกการทดสอบ:")
    print("1. ทดสอบด้วย LotteryScraper")
    print("2. ทดสอบการเข้าถึงเว็บไซต์โดยตรง")
    
    choice = input("\nเลือก (1 หรือ 2): ").strip()
    
    if choice == "1":
        test_sanook_scraping()
    elif choice == "2":
        test_sanook_direct()
    else:
        print("ตัวเลือกไม่ถูกต้อง")
        sys.exit(1)
