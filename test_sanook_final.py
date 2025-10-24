#!/usr/bin/env python3
"""
ไฟล์ทดสอบการ scrap Sanook เวอร์ชันสุดท้าย
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def test_final_scraping():
    """ทดสอบการ scrap เวอร์ชันสุดท้าย"""
    print("=" * 60)
    print("ทดสอบการ scrap Sanook เวอร์ชันสุดท้าย")
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
        
        # 1. หาข้อมูลจาก HTML structure ที่เฉพาะเจาะจง
        print("\n=== ข้อมูลจาก HTML Structure ===")
        
        # หา elements ที่มีข้อมูลรางวัล
        prize_sections = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'lottery|result|prize|check'))
        print(f"พบ sections ที่เกี่ยวข้อง: {len(prize_sections)}")
        
        for i, section in enumerate(prize_sections[:5]):  # ดู 5 sections แรก
            text = section.get_text().strip()
            if len(text) > 50:  # เอาที่มีเนื้อหา
                print(f"Section {i+1}: {text[:100]}...")
        
        # 2. หาตัวเลข 6 หลักที่อาจเป็นรางวัลที่ 1
        print("\n=== ตัวเลข 6 หลักที่เป็นไปได้ ===")
        all_numbers_6 = re.findall(r'\d{6}', soup.get_text())
        print(f"พบตัวเลข 6 หลักทั้งหมด: {len(all_numbers_6)}")
        
        # เอาตัวเลขที่ปรากฏบ่อย (อาจเป็นรางวัล)
        from collections import Counter
        number_counts = Counter(all_numbers_6)
        most_common = number_counts.most_common(10)
        
        print("ตัวเลขที่ปรากฏบ่อย:")
        for number, count in most_common:
            print(f"  {number}: {count} ครั้ง")
        
        # 3. หาข้อมูลจาก meta tags
        print("\n=== ข้อมูลจาก Meta Tags ===")
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('name') and 'lottery' in meta.get('name', '').lower():
                print(f"Meta {meta.get('name')}: {meta.get('content')}")
        
        # 4. หาข้อมูลจาก script tags
        print("\n=== ข้อมูลจาก Script Tags ===")
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'lottery' in script.string.lower():
                print(f"Script content: {script.string[:200]}...")
                break
        
        # 5. หาข้อมูลจาก title และ headings
        print("\n=== ข้อมูลจาก Title และ Headings ===")
        titles = soup.find_all(['title', 'h1', 'h2', 'h3', 'h4'])
        for title in titles:
            text = title.get_text().strip()
            if 'งวด' in text or 'รางวัล' in text or 'ลอตเตอรี่' in text:
                print(f"Title: {text}")
        
        # 6. หาข้อมูลจาก links
        print("\n=== ข้อมูลจาก Links ===")
        links = soup.find_all('a', href=re.compile(r'lottery|lotto|check'))
        for link in links[:5]:  # ดู 5 links แรก
            print(f"Link: {link.get('href')} - {link.get_text().strip()}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_final_scraping()
