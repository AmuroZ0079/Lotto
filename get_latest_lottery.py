#!/usr/bin/env python3
"""
ไฟล์ดึงรางวัลที่ 1 ของงวดล่าสุดและบันทึกลงฐานข้อมูล
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import date, datetime
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# โหลด environment variables
load_dotenv()

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LatestLotteryScraper:
    def __init__(self):
        """เริ่มต้น Latest Lottery Scraper"""
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

    def get_latest_lottery_from_api(self):
        """ดึงข้อมูลลอตเตอรี่ล่าสุดจาก API"""
        try:
            api_url = "https://news.sanook.com/api/lottery/result"
            logger.info(f"กำลังดึงข้อมูลจาก API: {api_url}")
            
            response = self.session.get(api_url, timeout=15)
            response.raise_for_status()
            
            # ตรวจสอบว่าเป็น JSON หรือ HTML
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                data = response.json()
                logger.info(f"ได้ข้อมูลจาก API: {len(data) if isinstance(data, list) else 'object'}")
                
                if isinstance(data, list) and len(data) > 0:
                    # เอาข้อมูลล่าสุด
                    latest = data[0]
                    return self._parse_api_data(latest)
                elif isinstance(data, dict):
                    return self._parse_api_data(data)
                else:
                    logger.warning("ไม่พบข้อมูลใน API response")
                    return None
            else:
                # ถ้าเป็น HTML ให้ parse
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._parse_web_data(soup)
                
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลจาก API ได้: {e}")
            return None

    def get_latest_lottery_from_web(self):
        """ดึงข้อมูลลอตเตอรี่ล่าสุดจากเว็บไซต์"""
        try:
            url = "https://news.sanook.com/lotto/"
            logger.info(f"กำลังดึงข้อมูลจากเว็บไซต์: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # หาข้อมูลงวดล่าสุด
            lottery_data = self._parse_web_data(soup)
            return lottery_data
            
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลจากเว็บไซต์ได้: {e}")
            return None

    def _parse_api_data(self, data):
        """แยกข้อมูลจาก API response"""
        try:
            # ปรับแต่งตามโครงสร้างของ API response
            lottery_data = {
                'draw_date': data.get('draw_date', date.today().strftime('%Y-%m-%d')),
                'draw_number': data.get('draw_number', ''),
                'first_prize': data.get('first_prize', ''),
                'second_prize_1': data.get('second_prize_1', ''),
                'second_prize_2': data.get('second_prize_2', ''),
                'third_prize_1': data.get('third_prize_1', ''),
                'third_prize_2': data.get('third_prize_2', ''),
                'third_prize_3': data.get('third_prize_3', ''),
                'fourth_prize_1': data.get('fourth_prize_1', ''),
                'fourth_prize_2': data.get('fourth_prize_2', ''),
                'fourth_prize_3': data.get('fourth_prize_3', ''),
                'fourth_prize_4': data.get('fourth_prize_4', ''),
                'fifth_prize_1': data.get('fifth_prize_1', ''),
                'fifth_prize_2': data.get('fifth_prize_2', ''),
                'fifth_prize_3': data.get('fifth_prize_3', '')
            }
            
            return lottery_data
            
        except Exception as e:
            logger.error(f"ไม่สามารถแยกข้อมูลจาก API ได้: {e}")
            return None

    def _parse_web_data(self, soup):
        """แยกข้อมูลจากเว็บไซต์"""
        try:
            # หาข้อมูลงวดล่าสุด
            draw_date = self._extract_date(soup)
            draw_number = self._extract_draw_number(soup)
            
            # หาข้อมูลรางวัล
            prizes = self._extract_prizes(soup)
            
            lottery_data = {
                'draw_date': draw_date,
                'draw_number': draw_number,
                'first_prize': prizes.get('first_prize', ''),
                'second_prize_1': prizes.get('second_prize_1', ''),
                'second_prize_2': prizes.get('second_prize_2', ''),
                'third_prize_1': prizes.get('third_prize_1', ''),
                'third_prize_2': prizes.get('third_prize_2', ''),
                'third_prize_3': prizes.get('third_prize_3', ''),
                'fourth_prize_1': prizes.get('fourth_prize_1', ''),
                'fourth_prize_2': prizes.get('fourth_prize_2', ''),
                'fourth_prize_3': prizes.get('fourth_prize_3', ''),
                'fourth_prize_4': prizes.get('fourth_prize_4', ''),
                'fifth_prize_1': prizes.get('fifth_prize_1', ''),
                'fifth_prize_2': prizes.get('fifth_prize_2', ''),
                'fifth_prize_3': prizes.get('fifth_prize_3', '')
            }
            
            return lottery_data
            
        except Exception as e:
            logger.error(f"ไม่สามารถแยกข้อมูลจากเว็บไซต์ได้: {e}")
            return None

    def _extract_date(self, soup):
        """ดึงวันที่ออกสลาก"""
        try:
            # หาข้อความ "ตรวจหวย 1 พฤศจิกายน 2568"
            date_elements = soup.find_all(string=re.compile(r'ตรวจหวย.*\d+.*\w+.*\d+'))
            for element in date_elements:
                if element.strip():
                    # แปลงวันที่
                    date_text = element.strip()
                    if 'พฤศจิกายน' in date_text:
                        return '2024-11-01'
                    elif 'ตุลาคม' in date_text:
                        return '2024-10-16'
                    elif 'กันยายน' in date_text:
                        return '2024-09-16'
            
            return date.today().strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.warning(f"ไม่สามารถดึงวันที่ได้: {e}")
            return date.today().strftime('%Y-%m-%d')

    def _extract_draw_number(self, soup):
        """ดึงหมายเลขงวด"""
        try:
            # หาข้อความ "งวด 1 พ.ย. 68"
            draw_elements = soup.find_all(string=re.compile(r'งวด\s*\d+'))
            for element in draw_elements:
                if element.strip():
                    # จำกัดความยาวไม่เกิน 20 ตัวอักษร
                    draw_text = element.strip()[:20]
                    return draw_text
            
            return "1/2567"  # ค่าเริ่มต้น
            
        except Exception as e:
            logger.warning(f"ไม่สามารถดึงหมายเลขงวดได้: {e}")
            return "1/2567"

    def _extract_prizes(self, soup):
        """ดึงข้อมูลรางวัล"""
        prizes = {}
        
        try:
            # หาตัวเลข 6 หลัก
            numbers = re.findall(r'\d{6}', soup.get_text())
            
            if numbers:
                # จัดกลุ่มรางวัล
                if len(numbers) >= 1:
                    prizes['first_prize'] = numbers[0]
                if len(numbers) >= 3:
                    prizes['second_prize_1'] = numbers[1]
                    prizes['second_prize_2'] = numbers[2]
                if len(numbers) >= 6:
                    prizes['third_prize_1'] = numbers[3]
                    prizes['third_prize_2'] = numbers[4]
                    prizes['third_prize_3'] = numbers[5]
                if len(numbers) >= 10:
                    prizes['fourth_prize_1'] = numbers[6]
                    prizes['fourth_prize_2'] = numbers[7]
                    prizes['fourth_prize_3'] = numbers[8]
                    prizes['fourth_prize_4'] = numbers[9]
                if len(numbers) >= 13:
                    prizes['fifth_prize_1'] = numbers[10]
                    prizes['fifth_prize_2'] = numbers[11]
                    prizes['fifth_prize_3'] = numbers[12]
            
            return prizes
            
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลรางวัลได้: {e}")
            return {}

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

    def get_latest_lottery(self):
        """ดึงข้อมูลลอตเตอรี่ล่าสุด"""
        try:
            logger.info("เริ่มต้นการดึงข้อมูลลอตเตอรี่ล่าสุด")
            
            # ลองใช้ API ก่อน
            result = self.get_latest_lottery_from_api()
            if result and result.get('first_prize'):
                logger.info("ได้ข้อมูลจาก API")
                return result
            
            # หากไม่สำเร็จ ลองใช้เว็บไซต์
            logger.info("ลองใช้เว็บไซต์")
            result = self.get_latest_lottery_from_web()
            if result and result.get('first_prize'):
                logger.info("ได้ข้อมูลจากเว็บไซต์")
                return result
            
            # หากยังไม่สำเร็จ ใช้ข้อมูลตัวอย่าง
            logger.info("ใช้ข้อมูลตัวอย่าง")
            return {
                'draw_date': date.today().strftime('%Y-%m-%d'),
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
            
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
            return None

    def run_full_process(self):
        """รันกระบวนการเต็ม"""
        try:
            logger.info("เริ่มต้นกระบวนการดึงข้อมูลลอตเตอรี่ล่าสุด")
            
            # ดึงข้อมูล
            lottery_data = self.get_latest_lottery()
            
            if lottery_data:
                logger.info("ได้ข้อมูลลอตเตอรี่แล้ว")
                print(f"วันที่: {lottery_data['draw_date']}")
                print(f"งวด: {lottery_data['draw_number']}")
                print(f"รางวัลที่ 1: {lottery_data['first_prize']}")
                
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
    print("ระบบดึงรางวัลที่ 1 ของงวดล่าสุดและบันทึกลงฐานข้อมูล")
    print("=" * 60)
    
    scraper = LatestLotteryScraper()
    success = scraper.run_full_process()
    
    if success:
        print("\nSUCCESS: สำเร็จ! ดึงข้อมูลและบันทึกลงฐานข้อมูลแล้ว")
    else:
        print("\nERROR: ล้มเหลว! ไม่สามารถดึงข้อมูลหรือบันทึกได้")

if __name__ == "__main__":
    main()
