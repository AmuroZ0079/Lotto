#!/usr/bin/env python3
"""
ไฟล์ทดสอบโครงสร้าง HTML ของ Sanook Lotto
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def test_sanook_structure():
    """ทดสอบโครงสร้าง HTML ของ Sanook Lotto"""
    print("=" * 60)
    print("ทดสอบโครงสร้าง HTML ของ Sanook Lotto")
    print("=" * 60)
    
    try:
        # URL สำหรับงวด 1 ต.ค. 2568
        url = "https://news.sanook.com/lotto/check/01102568/"
        print(f"กำลังเข้าถึง: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. หาข้อมูลงวด
        print("\n=== ข้อมูลงวด ===")
        title_elements = soup.find_all(['title', 'h1', 'h2', 'h3'])
        for element in title_elements:
            text = element.get_text().strip()
            if 'งวด' in text or 'ต.ค.' in text or '2568' in text:
                print(f"Title: {text}")
        
        # 2. หาตัวเลข 6 หลัก
        print("\n=== ตัวเลข 6 หลัก ===")
        numbers_6 = re.findall(r'\d{6}', soup.get_text())
        print(f"พบตัวเลข 6 หลัก: {len(numbers_6)} ตัว")
        for i, num in enumerate(numbers_6[:10]):  # แสดง 10 ตัวแรก
            print(f"  {i+1:2d}. {num}")
        
        # 3. หาตัวเลข 3 หลัก
        print("\n=== ตัวเลข 3 หลัก ===")
        numbers_3 = re.findall(r'\d{3}', soup.get_text())
        print(f"พบตัวเลข 3 หลัก: {len(numbers_3)} ตัว")
        for i, num in enumerate(numbers_3[:10]):  # แสดง 10 ตัวแรก
            print(f"  {i+1:2d}. {num}")
        
        # 4. หาตัวเลข 2 หลัก
        print("\n=== ตัวเลข 2 หลัก ===")
        numbers_2 = re.findall(r'\d{2}', soup.get_text())
        print(f"พบตัวเลข 2 หลัก: {len(numbers_2)} ตัว")
        for i, num in enumerate(numbers_2[:10]):  # แสดง 10 ตัวแรก
            print(f"  {i+1:2d}. {num}")
        
        # 5. หาข้อความที่เกี่ยวข้องกับรางวัล
        print("\n=== ข้อความรางวัล ===")
        prize_keywords = ['รางวัลที่ 1', 'รางวัลที่1', 'first prize', 'เลขหน้า', 'เลขท้าย', 'front', 'last']
        for keyword in prize_keywords:
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.strip():
                    print(f"'{keyword}': {element.strip()[:100]}...")
        
        # 6. หา elements ที่มี class หรือ id เกี่ยวข้อง
        print("\n=== Elements ที่เกี่ยวข้อง ===")
        relevant_classes = ['prize', 'number', 'lottery', 'result', 'first', 'second', 'third']
        for class_name in relevant_classes:
            elements = soup.find_all(class_=re.compile(class_name, re.IGNORECASE))
            if elements:
                print(f"Class '{class_name}': {len(elements)} elements")
                for i, elem in enumerate(elements[:3]):  # แสดง 3 ตัวแรก
                    print(f"  {i+1}. {elem.get_text().strip()[:50]}...")
        
        # 7. หา table หรือ div ที่มีข้อมูลรางวัล
        print("\n=== Tables และ Divs ===")
        tables = soup.find_all('table')
        print(f"พบ tables: {len(tables)}")
        for i, table in enumerate(tables[:3]):
            print(f"Table {i+1}: {table.get_text().strip()[:100]}...")
        
        # 8. บันทึก HTML ลงไฟล์เพื่อดู
        with open('sanook_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"\nบันทึก HTML ลงไฟล์: sanook_page.html")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_sanook_structure()
