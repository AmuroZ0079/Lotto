#!/usr/bin/env python3
"""
ไฟล์ทดสอบการ scrap Sanook ที่ปรับปรุงแล้ว
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def test_improved_scraping():
    """ทดสอบการ scrap ที่ปรับปรุงแล้ว"""
    print("=" * 60)
    print("ทดสอบการ scrap Sanook ที่ปรับปรุงแล้ว")
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
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. หารางวัลที่ 1 จาก class 'first'
        print("\n=== รางวัลที่ 1 ===")
        first_prize_elements = soup.find_all(class_='first')
        for element in first_prize_elements:
            text = element.get_text().strip()
            if re.match(r'\d{6}', text):
                print(f"รางวัลที่ 1: {text}")
                break
        
        # 2. หาเลขหน้า 3 ตัว
        print("\n=== เลขหน้า 3 ตัว ===")
        front3_elements = soup.find_all(string=re.compile(r'เลขหน้า.*3.*ตัว'))
        for element in front3_elements:
            parent = element.parent
            if parent:
                # หาตัวเลข 3 หลักในบริเวณใกล้เคียง
                siblings = parent.find_next_siblings()
                for sibling in siblings:
                    numbers = re.findall(r'\d{3}', sibling.get_text())
                    if numbers:
                        print(f"เลขหน้า 3 ตัว: {numbers[:2]}")  # เอาสองตัวแรก
                        break
        
        # 3. หาเลขท้าย 3 ตัว
        print("\n=== เลขท้าย 3 ตัว ===")
        last3_elements = soup.find_all(string=re.compile(r'เลขท้าย.*3.*ตัว'))
        for element in last3_elements:
            parent = element.parent
            if parent:
                # หาตัวเลข 3 หลักในบริเวณใกล้เคียง
                siblings = parent.find_next_siblings()
                for sibling in siblings:
                    numbers = re.findall(r'\d{3}', sibling.get_text())
                    if numbers:
                        print(f"เลขท้าย 3 ตัว: {numbers[:2]}")  # เอาสองตัวแรก
                        break
        
        # 4. หาเลขท้าย 2 ตัว
        print("\n=== เลขท้าย 2 ตัว ===")
        last2_elements = soup.find_all(string=re.compile(r'เลขท้าย.*2.*ตัว'))
        for element in last2_elements:
            parent = element.parent
            if parent:
                # หาตัวเลข 2 หลักในบริเวณใกล้เคียง
                siblings = parent.find_next_siblings()
                for sibling in siblings:
                    numbers = re.findall(r'\d{2}', sibling.get_text())
                    if numbers:
                        print(f"เลขท้าย 2 ตัว: {numbers[0]}")  # เอาตัวแรก
                        break
        
        # 5. หาข้อมูลจากโครงสร้าง HTML ที่เฉพาะเจาะจง
        print("\n=== ข้อมูลจากโครงสร้าง HTML ===")
        
        # หา elements ที่มี class 'number'
        number_elements = soup.find_all(class_='number')
        print(f"พบ elements ที่มี class 'number': {len(number_elements)}")
        
        # หา elements ที่มี class 'first'
        first_elements = soup.find_all(class_='first')
        print(f"พบ elements ที่มี class 'first': {len(first_elements)}")
        
        # 6. หาข้อมูลจาก JSON-LD
        print("\n=== ข้อมูลจาก JSON-LD ===")
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and 'headline' in data:
                    print(f"Headline: {data['headline']}")
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_improved_scraping()
