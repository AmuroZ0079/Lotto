#!/usr/bin/env python3
"""
ไฟล์ดึงข้อมูลงวดวันที่ 16 ต.ค. 2568
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import date
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# โหลด environment variables
load_dotenv()

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class October16Scraper:
    def __init__(self):
        """เริ่มต้น October 16 Scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # เชื่อมต่อ Supabase
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            self.supabase: Client = create_client(supabase_url, supabase_key)
            logger.info("เชื่อมต่อ Supabase สำเร็จ")
        except Exception as e:
            logger.error(f"ไม่สามารถเชื่อมต่อ Supabase ได้: {e}")
            self.supabase = None

    def get_october_16_lottery(self):
        """ดึงข้อมูลงวดวันที่ 16 ต.ค. 2568"""
        try:
            # URL สำหรับงวด 16 ต.ค. 2568
            url = "https://news.sanook.com/lotto/check/16102568/"
            logger.info(f"กำลังดึงข้อมูลจาก: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # หาข้อมูลงวด
            lottery_data = self._parse_october_16_data(soup)
            return lottery_data
            
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลได้: {e}")
            return None

    def _parse_october_16_data(self, soup):
        """แยกข้อมูลงวด 16 ต.ค. 2568"""
        try:
            # ข้อมูลงวด
            lottery_data = {
                'draw_date': '2025-10-16',
                'draw_number': '16/2568',
                'first_prize': '',
                'second_prize_1': '',
                'second_prize_2': '',
                'third_prize_1': '',
                'third_prize_2': '',
                'third_prize_3': '',
                'fourth_prize_1': '',
                'fourth_prize_2': '',
                'fourth_prize_3': '',
                'fourth_prize_4': '',
                'fifth_prize_1': '',
                'fifth_prize_2': '',
                'fifth_prize_3': ''
            }
            
            # หาข้อมูลรางวัลจากโครงสร้าง HTML
            # หารางวัลที่ 1
            first_prize_elements = soup.find_all(['span', 'div', 'td'], class_=re.compile(r'first|prize|number'))
            for element in first_prize_elements:
                text = element.get_text().strip()
                if re.match(r'\d{6}', text):
                    lottery_data['first_prize'] = text
                    break
            
            # หาเลขหน้า 3 ตัว
            front3_elements = soup.find_all(['span', 'div', 'td'], class_=re.compile(r'front|หน้า'))
            front3_numbers = []
            for element in front3_elements:
                text = element.get_text().strip()
                if re.match(r'\d{3}', text):
                    front3_numbers.append(text)
            if len(front3_numbers) >= 2:
                lottery_data['second_prize_1'] = front3_numbers[0]
                lottery_data['second_prize_2'] = front3_numbers[1]
            
            # หาเลขท้าย 3 ตัว
            last3_elements = soup.find_all(['span', 'div', 'td'], class_=re.compile(r'last|ท้าย'))
            last3_numbers = []
            for element in last3_elements:
                text = element.get_text().strip()
                if re.match(r'\d{3}', text):
                    last3_numbers.append(text)
            if len(last3_numbers) >= 2:
                lottery_data['third_prize_1'] = last3_numbers[0]
                lottery_data['third_prize_2'] = last3_numbers[1]
            
            # หาเลขท้าย 2 ตัว
            last2_elements = soup.find_all(['span', 'div', 'td'], class_=re.compile(r'last|ท้าย'))
            for element in last2_elements:
                text = element.get_text().strip()
                if re.match(r'\d{2}', text):
                    lottery_data['fourth_prize_1'] = text
                    break
            
            # หาข้อมูลจาก HTML จริง
            # หารางวัลที่ 1 จากโครงสร้าง HTML
            prize_elements = soup.find_all(['span', 'div', 'td', 'strong'], string=re.compile(r'\d{6}'))
            for element in prize_elements:
                text = element.get_text().strip()
                if re.match(r'\d{6}', text):
                    lottery_data['first_prize'] = text
                    break
            
            # หาเลขหน้า 3 ตัว
            front3_elements = soup.find_all(['span', 'div', 'td'], string=re.compile(r'\d{3}'))
            front3_numbers = []
            for element in front3_elements:
                text = element.get_text().strip()
                if re.match(r'\d{3}', text):
                    front3_numbers.append(text)
            if len(front3_numbers) >= 2:
                lottery_data['second_prize_1'] = front3_numbers[0]
                lottery_data['second_prize_2'] = front3_numbers[1]
            
            # หาเลขท้าย 3 ตัว
            last3_elements = soup.find_all(['span', 'div', 'td'], string=re.compile(r'\d{3}'))
            last3_numbers = []
            for element in last3_elements:
                text = element.get_text().strip()
                if re.match(r'\d{3}', text):
                    last3_numbers.append(text)
            if len(last3_numbers) >= 2:
                lottery_data['third_prize_1'] = last3_numbers[0]
                lottery_data['third_prize_2'] = last3_numbers[1]
            
            # หาเลขท้าย 2 ตัว
            last2_elements = soup.find_all(['span', 'div', 'td'], string=re.compile(r'\d{2}'))
            for element in last2_elements:
                text = element.get_text().strip()
                if re.match(r'\d{2}', text):
                    lottery_data['fourth_prize_1'] = text
                    break
            
            return lottery_data
            
        except Exception as e:
            logger.error(f"ไม่สามารถแยกข้อมูลได้: {e}")
            return None

    def save_to_database(self, lottery_data):
        """บันทึกข้อมูลลงฐานข้อมูล"""
        if not self.supabase:
            logger.error("ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
            return False
        
        try:
            # ตรวจสอบว่ามีข้อมูลในวันที่นี้แล้วหรือไม่
            existing = self.supabase.table('lottery_results').select("*").eq("draw_date", lottery_data['draw_date']).execute()
            
            if existing.data:
                # อัปเดตข้อมูลที่มีอยู่
                result = self.supabase.table('lottery_results').update(lottery_data).eq("draw_date", lottery_data['draw_date']).execute()
                logger.info(f"อัปเดตผลลอตเตอรี่วันที่ {lottery_data['draw_date']} สำเร็จ")
            else:
                # เพิ่มข้อมูลใหม่
                result = self.supabase.table('lottery_results').insert(lottery_data).execute()
                logger.info(f"บันทึกผลลอตเตอรี่วันที่ {lottery_data['draw_date']} สำเร็จ")
            
            return True
            
        except Exception as e:
            logger.error(f"ไม่สามารถบันทึกข้อมูลได้: {e}")
            return False

    def run_october_16_process(self):
        """รันกระบวนการดึงข้อมูลงวด 16 ต.ค. 2568"""
        try:
            logger.info("เริ่มต้นการดึงข้อมูลงวด 16 ต.ค. 2568")
            
            # ดึงข้อมูล
            lottery_data = self.get_october_16_lottery()
            
            if lottery_data:
                logger.info("ได้ข้อมูลงวด 16 ต.ค. 2568 แล้ว")
                print(f"วันที่: {lottery_data['draw_date']}")
                print(f"งวด: {lottery_data['draw_number']}")
                print(f"รางวัลที่ 1: {lottery_data['first_prize']}")
                print(f"รางวัลที่ 2: {lottery_data['second_prize_1']}, {lottery_data['second_prize_2']}")
                print(f"รางวัลที่ 3: {lottery_data['third_prize_1']}, {lottery_data['third_prize_2']}, {lottery_data['third_prize_3']}")
                
                # บันทึกลงฐานข้อมูล
                if self.save_to_database(lottery_data):
                    logger.info("บันทึกข้อมูลสำเร็จ")
                    return True
                else:
                    logger.error("ไม่สามารถบันทึกข้อมูลได้")
                    return False
            else:
                logger.error("ไม่สามารถดึงข้อมูลได้")
                return False
                
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในกระบวนการ: {e}")
            return False

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 60)
    print("ระบบดึงข้อมูลงวดวันที่ 16 ต.ค. 2568")
    print("=" * 60)
    
    scraper = October16Scraper()
    success = scraper.run_october_16_process()
    
    if success:
        print("\nSUCCESS: สำเร็จ! ดึงข้อมูลงวด 16 ต.ค. 2568 และบันทึกลงฐานข้อมูลแล้ว")
    else:
        print("\nERROR: ล้มเหลว! ไม่สามารถดึงข้อมูลหรือบันทึกได้")

if __name__ == "__main__":
    main()
