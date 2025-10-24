#!/usr/bin/env python3
"""
API สำหรับดึงข้อมูลลอตเตอรี่ตามวันที่งวด
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import date, datetime
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

# โหลด environment variables
load_dotenv()

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LotteryAPI:
    def __init__(self):
        """เริ่มต้น Lottery API"""
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

    def get_lottery_by_date(self, draw_date):
        """ดึงข้อมูลลอตเตอรี่ตามวันที่งวด"""
        try:
            # แปลงวันที่เป็นรูปแบบที่ใช้ใน URL
            # ตัวอย่าง: 2025-10-16 -> 16102568
            date_obj = datetime.strptime(draw_date, '%Y-%m-%d')
            day = date_obj.day
            month = date_obj.month
            year = date_obj.year + 543  # แปลงเป็น พ.ศ.
            
            # สร้าง URL
            url = f"https://news.sanook.com/lotto/check/{day:02d}{month:02d}{year}/"
            logger.info(f"กำลังดึงข้อมูลจาก: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # แยกข้อมูล
            lottery_data = self._parse_lottery_data(soup, draw_date)
            return lottery_data
            
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลได้: {e}")
            return None

    def _parse_lottery_data(self, soup, draw_date):
        """แยกข้อมูลลอตเตอรี่จาก HTML"""
        try:
            # ข้อมูลงวด
            lottery_data = {
                'draw_date': draw_date,
                'draw_number': f"{datetime.strptime(draw_date, '%Y-%m-%d').day}/{datetime.strptime(draw_date, '%Y-%m-%d').year + 543}",
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
            
            # หาข้อมูลจาก HTML
            # หารางวัลที่ 1
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

    def get_from_database(self, draw_date):
        """ดึงข้อมูลจากฐานข้อมูล"""
        if not self.supabase:
            return None
        
        try:
            result = self.supabase.table('lottery_results').select("*").eq("draw_date", draw_date).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลจากฐานข้อมูลได้: {e}")
            return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            # แยก path และ query parameters
            path = self.path
            if '?' in path:
                path, query_string = path.split('?', 1)
                params = urllib.parse.parse_qs(query_string)
            else:
                params = {}
            
            # ตรวจสอบ path
            if path == '/api/lottery':
                # ต้องมี parameter draw_date
                if 'draw_date' not in params:
                    self.send_error_response(400, "Missing required parameter: draw_date")
                    return
                
                draw_date = params['draw_date'][0]
                
                # ตรวจสอบรูปแบบวันที่
                try:
                    datetime.strptime(draw_date, '%Y-%m-%d')
                except ValueError:
                    self.send_error_response(400, "Invalid date format. Use YYYY-MM-DD")
                    return
                
                # สร้าง API instance
                api = LotteryAPI()
                
                # ลองดึงจากฐานข้อมูลก่อน
                existing_data = api.get_from_database(draw_date)
                if existing_data:
                    self.send_success_response(existing_data)
                    return
                
                # หากไม่มีในฐานข้อมูล ให้ scrap จากเว็บไซต์
                lottery_data = api.get_lottery_by_date(draw_date)
                
                if lottery_data:
                    # บันทึกลงฐานข้อมูล
                    api.save_to_database(lottery_data)
                    self.send_success_response(lottery_data)
                else:
                    self.send_error_response(404, "ไม่พบข้อมูลลอตเตอรี่สำหรับวันที่ที่ระบุ")
            else:
                self.send_error_response(404, "Not Found")
                
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดใน API: {e}")
            self.send_error_response(500, f"Internal Server Error: {str(e)}")

    def send_success_response(self, data):
        """ส่ง response สำเร็จ"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def send_error_response(self, status_code, message):
        """ส่ง response ข้อผิดพลาด"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "error",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests"""
        self.do_GET()

if __name__ == "__main__":
    # สำหรับทดสอบ
    api = LotteryAPI()
    result = api.get_lottery_by_date("2025-10-16")
    if result:
        print("SUCCESS: ได้ข้อมูลลอตเตอรี่")
        print(f"วันที่: {result['draw_date']}")
        print(f"งวด: {result['draw_number']}")
        print(f"รางวัลที่ 1: {result['first_prize']}")
    else:
        print("ERROR: ไม่สามารถดึงข้อมูลได้")
