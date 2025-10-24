#!/usr/bin/env python3
"""
ไฟล์ทดสอบการ scrap จาก Sanook Lotto จริง
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import date
import logging

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sanook_real_scraping():
    """ทดสอบการ scrap จาก Sanook จริง"""
    print("=" * 60)
    print("ทดสอบการ scrap จาก Sanook Lotto จริง")
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
            
            # หาข้อมูลงวดล่าสุด
            print("\n=== ข้อมูลงวดล่าสุด ===")
            
            # หาข้อความ "ตรวจหวย 1 พฤศจิกายน 2568"
            date_elements = soup.find_all(text=re.compile(r'ตรวจหวย.*\d+.*\w+.*\d+'))
            for element in date_elements:
                if element.strip():
                    print(f"พบงวด: {element.strip()}")
            
            # หาข้อความ "รอผลสลากกินแบ่งรัฐบาล"
            waiting_elements = soup.find_all(text=re.compile(r'รอผลสลาก'))
            for element in waiting_elements:
                if element.strip():
                    print(f"สถานะ: {element.strip()}")
            
            # หาข้อมูลรางวัล
            print("\n=== ข้อมูลรางวัล ===")
            
            # หาข้อความ "รางวัลที่ 1"
            first_prize_elements = soup.find_all(text=re.compile(r'รางวัลที่ 1'))
            for element in first_prize_elements:
                parent = element.parent
                if parent:
                    text = parent.get_text().strip()
                    if 'รางวัลที่ 1' in text:
                        print(f"รางวัลที่ 1: {text}")
            
            # หาข้อความ "รางวัลละ 6,000,000 บาท"
            prize_amount_elements = soup.find_all(text=re.compile(r'รางวัลละ.*บาท'))
            for element in prize_amount_elements:
                if element.strip():
                    print(f"จำนวนเงินรางวัล: {element.strip()}")
            
            # หาตัวเลข 6 หลัก
            print("\n=== ตัวเลขที่พบ ===")
            numbers = re.findall(r'\d{6}', soup.get_text())
            if numbers:
                print(f"พบตัวเลข 6 หลัก: {len(numbers)} ตัว")
                for i, num in enumerate(numbers[:10]):  # แสดง 10 ตัวแรก
                    print(f"  {i+1:2d}. {num}")
            else:
                print("ไม่พบตัวเลข 6 หลัก")
            
            # หาข้อมูลจาก dropdown
            print("\n=== ข้อมูลจาก Dropdown ===")
            select_elements = soup.find_all('select')
            for select in select_elements:
                options = select.find_all('option')
                for option in options:
                    if option.get('value') and '2568' in option.get_text():
                        print(f"Dropdown: {option.get_text().strip()}")
            
            # หาข้อมูลจากฟอร์ม
            print("\n=== ข้อมูลจากฟอร์ม ===")
            form_elements = soup.find_all('form')
            for form in form_elements:
                inputs = form.find_all('input')
                for input_elem in inputs:
                    if input_elem.get('name') and 'เลขสลาก' in input_elem.get('name', ''):
                        print(f"ฟอร์ม: {input_elem.get('name')}")
            
            return True
            
        else:
            print(f"ERROR: ไม่สามารถเข้าถึงเว็บไซต์ได้: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        logger.error(f"Error in test_sanook_real_scraping: {e}")
        return False

def test_sanook_api():
    """ทดสอบการเข้าถึง API ของ Sanook"""
    print("\n" + "=" * 60)
    print("ทดสอบการเข้าถึง API ของ Sanook")
    print("=" * 60)
    
    try:
        # ลองหา API endpoint
        api_urls = [
            "https://news.sanook.com/api/lottery/result",
            "https://news.sanook.com/lotto/api/result",
            "https://api.sanook.com/lottery/result"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for api_url in api_urls:
            try:
                print(f"ลอง: {api_url}")
                response = requests.get(api_url, headers=headers, timeout=10)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  SUCCESS: พบ API ที่ใช้งานได้!")
                    print(f"  Content: {response.text[:200]}...")
                    return True
                    
            except Exception as e:
                print(f"  ERROR: {e}")
        
        print("ERROR: ไม่พบ API ที่ใช้งานได้")
        return False
        
    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    print("ระบบทดสอบการ scrap จาก Sanook Lotto จริง")
    
    # ทดสอบการ scrap
    result1 = test_sanook_real_scraping()
    
    # ทดสอบ API
    result2 = test_sanook_api()
    
    print("\n=== สรุปผลลัพธ์ ===")
    if result1:
        print("SUCCESS: การ scrap จาก Sanook สำเร็จ")
    else:
        print("ERROR: การ scrap จาก Sanook ล้มเหลว")
    
    if result2:
        print("SUCCESS: พบ API ที่ใช้งานได้")
    else:
        print("ERROR: ไม่พบ API ที่ใช้งานได้")
