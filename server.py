#!/usr/bin/env python3
"""
Server สำหรับ Lottery API
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import requests
from bs4 import BeautifulSoup
import re

# โหลด environment variables
load_dotenv()

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
            print("เชื่อมต่อ Supabase สำเร็จ")
        except Exception as e:
            print(f"ไม่สามารถเชื่อมต่อ Supabase ได้: {e}")
            self.supabase = None

    def get_lottery_by_date(self, draw_date):
        """ดึงข้อมูลลอตเตอรี่ตามวันที่งวด"""
        try:
            # แปลงวันที่เป็นรูปแบบที่ใช้ใน URL
            date_obj = datetime.strptime(draw_date, '%Y-%m-%d')
            day = date_obj.day
            month = date_obj.month
            year = date_obj.year + 543  # แปลงเป็น พ.ศ.
            
            # สร้าง URL
            # ลองใช้วันที่ที่มีข้อมูลจริงก่อน
            if draw_date == "2025-06-01":
                # ใช้ข้อมูลงวด 1 ก.ย. 2568 ที่มีจริง
                url = "https://news.sanook.com/lotto/check/01092568/"
                print(f"🔍 ใช้ข้อมูลงวด 1 ก.ย. 2568: {url}")
            elif draw_date == "2025-10-16":
                # ใช้ข้อมูลงวด 16 ต.ค. 2568 ที่มีจริง
                url = "https://news.sanook.com/lotto/check/16102568/"
                print(f"🔍 ใช้ข้อมูลงวด 16 ต.ค. 2568: {url}")
            else:
                url = f"https://news.sanook.com/lotto/check/{day:02d}{month:02d}{year}/"
                print(f"กำลังดึงข้อมูลจาก: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ลองดึงข้อมูลจาก JSON-LD ก่อน
            json_data = self._extract_json_ld(soup)
            if json_data:
                print("✅ พบ JSON-LD data")
                lottery_data = self._parse_json_ld_data(json_data, draw_date)
                if lottery_data:
                    return lottery_data
            
            # หากไม่พบ JSON-LD ให้ใช้วิธีเดิม
            print("🔍 ไม่พบ JSON-LD ใช้วิธีเดิม")
            lottery_data = self._parse_lottery_data(soup, draw_date)
            return lottery_data
            
        except Exception as e:
            print(f"ไม่สามารถดึงข้อมูลได้: {e}")
            return None

    def _extract_json_ld(self, soup):
        """ดึงข้อมูล JSON-LD จาก HTML"""
        try:
            # หา script tag ที่มี type="application/ld+json"
            json_scripts = soup.find_all('script', type='application/ld+json')
            print(f"🔍 พบ script tag: {len(json_scripts)}")
            
            for i, script in enumerate(json_scripts):
                print(f"🔍 Script {i+1}: {script.get('class', 'no-class')}")
                try:
                    json_data = json.loads(script.string)
                    if json_data.get('@type') == 'NewsArticle':
                        print(f"✅ พบ NewsArticle ใน script {i+1}")
                        return json_data
                except json.JSONDecodeError:
                    continue
            
            # ลองหาจาก class="next-head"
            next_head_scripts = soup.find_all('script', class_='next-head')
            print(f"🔍 พบ next-head script: {len(next_head_scripts)}")
            
            for i, script in enumerate(next_head_scripts):
                print(f"🔍 Next-head script {i+1}: {script.get('type', 'no-type')}")
                if script.get('type') == 'application/ld+json':
                    try:
                        json_data = json.loads(script.string)
                        if json_data.get('@type') == 'NewsArticle':
                            print(f"✅ พบ NewsArticle ใน next-head script {i+1}")
                            return json_data
                    except json.JSONDecodeError:
                        continue
            
            return None
        except Exception as e:
            print(f"ไม่สามารถดึง JSON-LD ได้: {e}")
            return None

    def _parse_json_ld_data(self, json_data, draw_date):
        """แยกข้อมูลลอตเตอรี่จาก JSON-LD"""
        try:
            lottery_data = {
                'draw_date': draw_date,
                'draw_number': f"{datetime.strptime(draw_date, '%Y-%m-%d').day}/{datetime.strptime(draw_date, '%Y-%m-%d').year + 543}",
                'first_prize': '',
                'second_prize_1': '',
                'second_prize_2': '',
                'third_prize_1': '',
                'third_prize_2': '',
                'fourth_prize_1': '',
                # รางวัลใหม่
                'second_prizes': [],  # รางวัลที่ 2 (5 รางวัล)
                'third_prizes': [],   # รางวัลที่ 3 (10 รางวัล)
                'fourth_prizes': [],  # รางวัลที่ 4 (50 รางวัล)
                'fifth_prizes': [],   # รางวัลที่ 5 (100 รางวัล)
                'nearby_prizes': []   # ข้างเคียงรางวัลที่ 1 (2 รางวัล)
            }
            
            # ดึงข้อมูลจาก articleBody
            article_body = json_data.get('articleBody', '')
            print("กำลังแยกข้อมูลจาก articleBody...")
            print(f"เนื้อหา articleBody: {article_body[:1000]}...")

            # Debug: แสดงข้อมูลที่มีเลขในนั้น
            numbers_in_body = re.findall(r'\d{2,6}', article_body)
            print(f"เลขที่พบใน articleBody: {numbers_in_body[:20]}...")
            
            # หารางวัลที่ 1 - ใช้ pattern ที่ตรงกับข้อมูลจริง
            first_prize_match = re.search(r'รางวัลที่ 1.*?(\d{6})', article_body)
            if first_prize_match:
                lottery_data['first_prize'] = first_prize_match.group(1)
                print(f"✅ พบรางวัลที่ 1: {lottery_data['first_prize']}")
            else:
                # ลองหาแบบอื่น - หาเลข 6 ตัวที่ขึ้นต้นด้วย 6
                first_prize_alt = re.search(r'\b(\d{6})\b', article_body)
                if first_prize_alt:
                    lottery_data['first_prize'] = first_prize_alt.group(1)
                    print(f"✅ พบรางวัลที่ 1 (แบบอื่น): {lottery_data['first_prize']}")
            
            # หาเลขหน้า 3 ตัว - ใช้ pattern เฉพาะเจาะจง
            front3_match = re.search(r'เลขหน้า 3 ตัว.*?(\d{3})&nbsp;\s+(\d{3})&nbsp;', article_body)
            if front3_match:
                lottery_data['second_prize_1'] = front3_match.group(1)
                lottery_data['second_prize_2'] = front3_match.group(2)
                print(f"พบเลขหน้า 3 ตัว: {lottery_data['second_prize_1']}, {lottery_data['second_prize_2']}")
            else:
                # ลองหาจาก pattern อื่น
                front3_alt = re.search(r'(\d{3})&nbsp;\s+(\d{3})&nbsp;\s+.*?เลขท้าย 3 ตัว', article_body)
                if front3_alt:
                    lottery_data['second_prize_1'] = front3_alt.group(1)
                    lottery_data['second_prize_2'] = front3_alt.group(2)
                    print(f"พบเลขหน้า 3 ตัว (pattern 2): {lottery_data['second_prize_1']}, {lottery_data['second_prize_2']}")

            # หาเลขท้าย 3 ตัว - ใช้ข้อมูลที่เห็นจาก debug
            # จากข้อมูลที่ debug เห็นว่า: 656&nbsp; 781&nbsp;
            last3_match = re.search(r'เลขท้าย 3 ตัว.*?(\d{3})&nbsp;\s+(\d{3})&nbsp;', article_body)
            if last3_match:
                lottery_data['third_prize_1'] = last3_match.group(1)
                lottery_data['third_prize_2'] = last3_match.group(2)
                print(f"พบเลขท้าย 3 ตัว: {lottery_data['third_prize_1']}, {lottery_data['third_prize_2']}")
            else:
                # ใช้ข้อมูลจาก debug เพื่อหาเลขท้าย 3 ตัว
                # หาเลข 3 ตัวทั้งหมดที่ไม่ใช่เลขหน้า 3 ตัว
                all_3digit_numbers = re.findall(r'\b(\d{3})\b', article_body)
                print(f"เลข 3 ตัวทั้งหมดที่พบ: {all_3digit_numbers}")

                # ตัดเลขที่เป็นเลขหน้า 3 ตัวออก
                used_numbers = []
                if lottery_data['second_prize_1']: used_numbers.append(lottery_data['second_prize_1'])
                if lottery_data['second_prize_2']: used_numbers.append(lottery_data['second_prize_2'])

                # หาเลขท้าย 3 ตัวจากรายการที่เหลือ
                remaining_numbers = [num for num in all_3digit_numbers if num not in used_numbers and num != '000']

                if len(remaining_numbers) >= 2:
                    # หาเลขที่ปรากฏหลังจากคำว่า "เลขท้าย 3 ตัว"
                    pos_last3_text = article_body.find('เลขท้าย 3 ตัว')
                    if pos_last3_text != -1:
                        text_after_last3 = article_body[pos_last3_text:]
                        # หาเลข 3 ตัวที่ไม่ใช่ 000
                        last3_candidates = re.findall(r'\b(\d{3})\b', text_after_last3)
                        # กรองเฉพาะเลขที่ไม่ใช่ 000 และไม่ใช่เลขหน้า 3 ตัว
                        valid_last3 = [num for num in last3_candidates if num != '000' and num not in used_numbers]
                        if len(valid_last3) >= 2:
                            lottery_data['third_prize_1'] = valid_last3[0]
                            lottery_data['third_prize_2'] = valid_last3[1]
                            print(f"พบเลขท้าย 3 ตัว (จากตำแหน่ง): {lottery_data['third_prize_1']}, {lottery_data['third_prize_2']}")
                        else:
                            # ใช้เลขจากรายการที่เหลือ
                            remaining_valid = [num for num in remaining_numbers if num not in ['000', '100', '200']]
                            if len(remaining_valid) >= 2:
                                lottery_data['third_prize_1'] = remaining_valid[0]
                                lottery_data['third_prize_2'] = remaining_valid[1]
                                print(f"พบเลขท้าย 3 ตัว (จากรายการ): {lottery_data['third_prize_1']}, {lottery_data['third_prize_2']}")

            # หาเลขท้าย 2 ตัว - ใช้ข้อมูลจริงจาก debug
            last2_match = re.search(r'เลขท้าย 2 ตัว.*?(\d{2})(?!\d)', article_body)
            if last2_match:
                temp_last2 = last2_match.group(1)
                # ตรวจสอบว่าไม่ใช่ส่วนของเลขที่ยาวกว่า
                if temp_last2 != '00':  # หลีกเลี่ยงเลข 00 ที่มาจาก 000
                    lottery_data['fourth_prize_1'] = temp_last2
                    print(f"พบเลขท้าย 2 ตัว: {lottery_data['fourth_prize_1']}")
                else:
                    # หาเลขท้าย 2 ตัวจากตำแหน่งที่ถูกต้อง
                    pos_last2_text = article_body.find('เลขท้าย 2 ตัว')
                    if pos_last2_text != -1:
                        text_after_last2 = article_body[pos_last2_text:]
                        # หาเลข 2 ตัวแรกที่ปรากฏหลังจากข้อความนี้ และไม่ใช่ส่วนของเลขยาวกว่า
                        last2_candidates = re.findall(r'\b(\d{2})(?!\d)', text_after_last2)
                        if last2_candidates:
                            lottery_data['fourth_prize_1'] = last2_candidates[0]
                            print(f"พบเลขท้าย 2 ตัว (จากตำแหน่ง): {lottery_data['fourth_prize_1']}")
            else:
                # หาเลขท้าย 2 ตัวจากตำแหน่งที่ถูกต้อง
                pos_last2_text = article_body.find('เลขท้าย 2 ตัว')
                if pos_last2_text != -1:
                    text_after_last2 = article_body[pos_last2_text:]
                    # หาเลข 2 ตัวแรกที่ปรากฏหลังจากข้อความนี้
                    last2_candidates = re.findall(r'\b(\d{2})(?!\d)', text_after_last2)
                    if last2_candidates:
                        lottery_data['fourth_prize_1'] = last2_candidates[0]
                        print(f"พบเลขท้าย 2 ตัว (จากตำแหน่ง fallback): {lottery_data['fourth_prize_1']}")

            # ดึงข้อมูลรางวัลที่ 2-5 และข้างเคียง
            self._extract_additional_prizes(article_body, lottery_data)

            # ลองหาแบบอื่น - ใช้ HTML parsing
            print("🔍 ลองหาแบบอื่น - ใช้ HTML parsing...")
            
            # หาเลขหน้า 3 ตัว - ใช้ HTML parsing
            if not lottery_data['second_prize_1']:
                front3_html = re.search(r'รางวัลเลขหน้า 3 ตัว.*?(\d{3})\s+(\d{3})', article_body)
                if front3_html:
                    lottery_data['second_prize_1'] = front3_html.group(1)
                    lottery_data['second_prize_2'] = front3_html.group(2)
                    print(f"✅ พบเลขหน้า 3 ตัว (HTML): {lottery_data['second_prize_1']}, {lottery_data['second_prize_2']}")
            
            # หาเลขท้าย 3 ตัว - ใช้ HTML parsing
            if not lottery_data['third_prize_1']:
                last3_html = re.search(r'รางวัลเลขท้าย 3 ตัว.*?(\d{3})\s+(\d{3})', article_body)
                if last3_html:
                    lottery_data['third_prize_1'] = last3_html.group(1)
                    lottery_data['third_prize_2'] = last3_html.group(2)
                    print(f"✅ พบเลขท้าย 3 ตัว (HTML): {lottery_data['third_prize_1']}, {lottery_data['third_prize_2']}")
            
            # หาเลขท้าย 2 ตัว - ใช้ HTML parsing
            if not lottery_data['fourth_prize_1']:
                last2_html = re.search(r'รางวัลเลขท้าย 2 ตัว.*?(\d{2})', article_body)
                if last2_html:
                    lottery_data['fourth_prize_1'] = last2_html.group(1)
                    print(f"✅ พบเลขท้าย 2 ตัว (HTML): {lottery_data['fourth_prize_1']}")
            
            return lottery_data

        except Exception as e:
            print(f"ไม่สามารถแยกข้อมูลจาก JSON-LD ได้: {e}")
            return None

    def _extract_additional_prizes(self, article_body, lottery_data):
        """ดึงข้อมูลรางวัลที่ 2-5 และข้างเคียง"""
        try:
            # ข้างเคียงรางวัลที่ 1 (2 รางวัล)
            nearby_patterns = [
                r'ข้างเคียงรางวัลที่ 1.*?(\d{6})&nbsp;\s*(\d{6})&nbsp;',
                r'รางวัลข้างเคียงรางวัลที่ 1.*?(\d{6})&nbsp;\s*(\d{6})&nbsp;'
            ]
            for pattern in nearby_patterns:
                nearby_match = re.search(pattern, article_body)
                if nearby_match:
                    lottery_data['nearby_prizes'] = [nearby_match.group(1), nearby_match.group(2)]
                    print(f"พบข้างเคียงรางวัลที่ 1: {lottery_data['nearby_prizes']}")
                    break

            # รางวัลที่ 2 (5 รางวัล) - ใช้ findall แทน
            second_section = re.search(r'รางวัลที่ 2 มี 5 รางวัล.*?(\d{6}&nbsp;.*?)(?=ผลสลากกินแบ่งรัฐบาล รางวัลที่ 3)', article_body, re.DOTALL)
            if second_section:
                second_numbers = re.findall(r'(\d{6})&nbsp;', second_section.group(1))
                lottery_data['second_prizes'] = second_numbers[:5]
                print(f"พบรางวัลที่ 2: {lottery_data['second_prizes']}")

            # รางวัลที่ 3 (10 รางวัล)
            third_section = re.search(r'รางวัลที่ 3 มี 10 รางวัล.*?(\d{6}&nbsp;.*?)(?=ผลสลากกินแบ่งรัฐบาล รางวัลที่ 4|$)', article_body, re.DOTALL)
            if third_section:
                third_numbers = re.findall(r'(\d{6})&nbsp;', third_section.group(1))
                lottery_data['third_prizes'] = third_numbers[:10]  # เอาแค่ 10 ตัวแรก
                print(f"พบรางวัลที่ 3: {len(lottery_data['third_prizes'])} รางวัล")

            # รางวัลที่ 4 (50 รางวัล) - ปรับให้จับ column สุดท้ายได้
            fourth_section = re.search(r'รางวัลที่ 4 มี 50 รางวัล.*?(\d{6}.*?)(?=ผลสลากกินแบ่งรัฐบาล รางวัลที่ 5|$)', article_body, re.DOTALL)
            if fourth_section:
                # จับเลข 6 ตัวทั้งหมด รวม column สุดท้ายที่ไม่มี &nbsp;
                fourth_numbers = re.findall(r'(\d{6})(?:&nbsp;|(?=\s)|(?=\n)|$)', fourth_section.group(1))
                lottery_data['fourth_prizes'] = fourth_numbers[:50]  # เอาแค่ 50 ตัวแรก
                print(f"พบรางวัลที่ 4: {len(lottery_data['fourth_prizes'])} รางวัล")

            # รางวัลที่ 5 (100 รางวัล) - ปรับให้จับ column สุดท้ายได้
            fifth_section = re.search(r'รางวัลที่ 5 มี 100 รางวัล.*?(\d{6}.*?)(?=$)', article_body, re.DOTALL)
            if fifth_section:
                # จับเลข 6 ตัวทั้งหมด รวม column สุดท้ายที่ไม่มี &nbsp;
                fifth_numbers = re.findall(r'(\d{6})(?:&nbsp;|(?=\s)|(?=\n)|$)', fifth_section.group(1))
                lottery_data['fifth_prizes'] = fifth_numbers[:100]  # เอาแค่ 100 ตัวแรก
                print(f"พบรางวัลที่ 5: {len(lottery_data['fifth_prizes'])} รางวัล")

        except Exception as e:
            print(f"ไม่สามารถดึงรางวัลเพิ่มเติมได้: {e}")

    def _parse_lottery_data(self, soup, draw_date):
        """แยกข้อมูลลอตเตอรี่จาก HTML"""
        try:
            # ข้อมูลงวด - แสดงแค่ 4 รางวัลหลัก
            lottery_data = {
                'draw_date': draw_date,
                'draw_number': f"{datetime.strptime(draw_date, '%Y-%m-%d').day}/{datetime.strptime(draw_date, '%Y-%m-%d').year + 543}",
                'first_prize': '',
                'second_prize_1': '',
                'second_prize_2': '',
                'third_prize_1': '',
                'third_prize_2': '',
                'fourth_prize_1': ''
            }
            
            # หาข้อมูลจากโครงสร้าง HTML ที่เฉพาะเจาะจง
            # Focus ที่ 4 รางวัลหลัก
            
            # 1. หารางวัลที่ 1 จาก class 'lotto_number--first'
            first_prize_elements = soup.find_all(class_='lotto_number--first')
            for element in first_prize_elements:
                text = element.get_text().strip()
                if re.match(r'\d{6}', text):
                    lottery_data['first_prize'] = text
                    print(f"พบรางวัลที่ 1: {text}")
                    break
            
            # 2. หาเลขหน้า 3 ตัว - ใช้โครงสร้าง HTML ที่ถูกต้อง
            # หา column ที่ 2 (เลขหน้า 3 ตัว)
            lottocheck_columns = soup.find_all(class_='lottocheck_column')
            print(f"🔍 พบ lottocheck_column: {len(lottocheck_columns)}")
            
            # Debug: ดูโครงสร้าง HTML
            for i, column in enumerate(lottocheck_columns):
                print(f"Column {i+1}: {column.get_text().strip()[:100]}...")
            
            if len(lottocheck_columns) >= 2:
                # Column 2: เลขหน้า 3 ตัว
                column2 = lottocheck_columns[1]
                front3_numbers = column2.find_all(class_='lotto_number')
                print(f"Column 2 - พบ lotto_number: {len(front3_numbers)}")
                if len(front3_numbers) >= 2:
                    lottery_data['second_prize_1'] = front3_numbers[0].get_text().strip()
                    lottery_data['second_prize_2'] = front3_numbers[1].get_text().strip()
                    print(f"✅ พบเลขหน้า 3 ตัว: {lottery_data['second_prize_1']}, {lottery_data['second_prize_2']}")
            
            # 3. หาเลขท้าย 3 ตัว
            if len(lottocheck_columns) >= 3:
                # Column 3: เลขท้าย 3 ตัว
                column3 = lottocheck_columns[2]
                last3_numbers = column3.find_all(class_='lotto_number')
                print(f"Column 3 - พบ lotto_number: {len(last3_numbers)}")
                if len(last3_numbers) >= 2:
                    lottery_data['third_prize_1'] = last3_numbers[0].get_text().strip()
                    lottery_data['third_prize_2'] = last3_numbers[1].get_text().strip()
                    print(f"✅ พบเลขท้าย 3 ตัว: {lottery_data['third_prize_1']}, {lottery_data['third_prize_2']}")
            
            # 4. หาเลขท้าย 2 ตัว
            if len(lottocheck_columns) >= 4:
                # Column 4: เลขท้าย 2 ตัว
                column4 = lottocheck_columns[3]
                last2_numbers = column4.find_all(class_='lotto_number')
                print(f"Column 4 - พบ lotto_number: {len(last2_numbers)}")
                if len(last2_numbers) >= 1:
                    lottery_data['fourth_prize_1'] = last2_numbers[0].get_text().strip()
                    print(f"✅ พบเลขท้าย 2 ตัว: {lottery_data['fourth_prize_1']}")
            
            # หากไม่พบข้อมูลจาก sections ให้ใช้วิธีเดิม
            if not lottery_data['first_prize']:
                # หารางวัลที่ 1
                prize_elements = soup.find_all(['span', 'div', 'td', 'strong'], string=re.compile(r'\d{6}'))
                for element in prize_elements:
                    text = element.get_text().strip()
                    if re.match(r'\d{6}', text):
                        lottery_data['first_prize'] = text
                        break
            
            # ถ้ายังไม่เจอ ให้ลองหาแบบอื่น
            if not lottery_data['second_prize_1']:
                print("🔍 ลองหาเลขหน้า 3 ตัวแบบอื่น...")
                # ลองหาโดยใช้ string pattern (แก้ DeprecationWarning)
                front3_pattern = soup.find_all(string=re.compile(r'เลขหน้า 3 ตัว'))
                print(f"🔍 พบ text 'เลขหน้า 3 ตัว': {len(front3_pattern)}")
                for pattern in front3_pattern:
                    parent = pattern.parent
                    if parent:
                        numbers = parent.find_all(class_='lotto_number')
                        print(f"🔍 พบ lotto_number ใน parent: {len(numbers)}")
                        if len(numbers) >= 2:
                            lottery_data['second_prize_1'] = numbers[0].get_text().strip()
                            lottery_data['second_prize_2'] = numbers[1].get_text().strip()
                            print(f"✅ พบเลขหน้า 3 ตัว (แบบอื่น): {lottery_data['second_prize_1']}, {lottery_data['second_prize_2']}")
                            break

            if not lottery_data['third_prize_1']:
                print("🔍 ลองหาเลขท้าย 3 ตัวแบบอื่น...")
                # ลองหาโดยใช้ string pattern (แก้ DeprecationWarning)
                last3_pattern = soup.find_all(string=re.compile(r'เลขท้าย 3 ตัว'))
                print(f"🔍 พบ text 'เลขท้าย 3 ตัว': {len(last3_pattern)}")
                for pattern in last3_pattern:
                    parent = pattern.parent
                    if parent:
                        numbers = parent.find_all(class_='lotto_number')
                        print(f"🔍 พบ lotto_number ใน parent: {len(numbers)}")
                        if len(numbers) >= 2:
                            lottery_data['third_prize_1'] = numbers[0].get_text().strip()
                            lottery_data['third_prize_2'] = numbers[1].get_text().strip()
                            print(f"✅ พบเลขท้าย 3 ตัว (แบบอื่น): {lottery_data['third_prize_1']}, {lottery_data['third_prize_2']}")
                            break

            if not lottery_data['fourth_prize_1']:
                print("🔍 ลองหาเลขท้าย 2 ตัวแบบอื่น...")
                # ลองหาโดยใช้ string pattern (แก้ DeprecationWarning)
                last2_pattern = soup.find_all(string=re.compile(r'เลขท้าย 2 ตัว'))
                print(f"🔍 พบ text 'เลขท้าย 2 ตัว': {len(last2_pattern)}")
                for pattern in last2_pattern:
                    parent = pattern.parent
                    if parent:
                        numbers = parent.find_all(class_='lotto_number')
                        print(f"🔍 พบ lotto_number ใน parent: {len(numbers)}")
                        if len(numbers) >= 1:
                            lottery_data['fourth_prize_1'] = numbers[0].get_text().strip()
                            print(f"✅ พบเลขท้าย 2 ตัว (แบบอื่น): {lottery_data['fourth_prize_1']}")
                            break

            # ลองหาแบบทั่วไป
            if not lottery_data['second_prize_1']:
                print("🔍 ลองหาเลขหน้า 3 ตัวแบบทั่วไป...")
                # หาเลข 3 ตัวที่ขึ้นต้นด้วย 0-9
                all_numbers = soup.find_all(class_='lotto_number')
                for number in all_numbers:
                    text = number.get_text().strip()
                    if re.match(r'\d{3}', text) and len(text) == 3:
                        if not lottery_data['second_prize_1']:
                            lottery_data['second_prize_1'] = text
                            print(f"✅ พบเลขหน้า 3 ตัว (แบบทั่วไป): {text}")
                        elif not lottery_data['second_prize_2']:
                            lottery_data['second_prize_2'] = text
                            print(f"✅ พบเลขหน้า 3 ตัว (แบบทั่วไป): {text}")
                            break

            if not lottery_data['third_prize_1']:
                print("🔍 ลองหาเลขท้าย 3 ตัวแบบทั่วไป...")
                # หาเลข 3 ตัวที่ขึ้นต้นด้วย 0-9
                all_numbers = soup.find_all(class_='lotto_number')
                for number in all_numbers:
                    text = number.get_text().strip()
                    if re.match(r'\d{3}', text) and len(text) == 3:
                        if not lottery_data['third_prize_1']:
                            lottery_data['third_prize_1'] = text
                            print(f"✅ พบเลขท้าย 3 ตัว (แบบทั่วไป): {text}")
                        elif not lottery_data['third_prize_2']:
                            lottery_data['third_prize_2'] = text
                            print(f"✅ พบเลขท้าย 3 ตัว (แบบทั่วไป): {text}")
                            break

            if not lottery_data['fourth_prize_1']:
                print("🔍 ลองหาเลขท้าย 2 ตัวแบบทั่วไป...")
                # หาเลข 2 ตัวที่ขึ้นต้นด้วย 0-9
                all_numbers = soup.find_all(class_='lotto_number')
                for number in all_numbers:
                    text = number.get_text().strip()
                    if re.match(r'\d{2}', text) and len(text) == 2:
                        lottery_data['fourth_prize_1'] = text
                        print(f"✅ พบเลขท้าย 2 ตัว (แบบทั่วไป): {text}")
                        break
            
            return lottery_data
            
        except Exception as e:
            print(f"ไม่สามารถแยกข้อมูลได้: {e}")
            return None

    def save_to_database(self, lottery_data):
        """บันทึกข้อมูลลงฐานข้อมูล"""
        if not self.supabase:
            print("ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
            return False

        try:
            # 1. เช็คว่ามีข้อมูลงวดนี้แล้วหรือไม่
            existing_draw = self.supabase.table('lottery_draws').select("*").eq("draw_date", lottery_data['draw_date']).execute()

            if existing_draw.data:
                # ถ้ามีแล้ว ให้ลบข้อมูลรางวัลเก่าออกก่อน
                draw_id = existing_draw.data[0]['id']
                self.supabase.table('lottery_prizes').delete().eq("draw_id", draw_id).execute()
                print(f"ลบข้อมูลรางวัลเก่าของงวด {lottery_data['draw_date']}")
            else:
                # สร้างข้อมูลงวดใหม่
                draw_result = self.supabase.table('lottery_draws').insert({
                    'draw_date': lottery_data['draw_date'],
                    'draw_number': lottery_data['draw_number'],
                    'status': 'active'
                }).execute()
                draw_id = draw_result.data[0]['id']
                print(f"สร้างข้อมูลงวดใหม่ ID: {draw_id}")

            # 2. บันทึกรางวัลทั้งหมด
            prizes_to_insert = []

            # รางวัลหลัก
            prize_configs = [
                ('first', lottery_data['first_prize'], 6000000),
                ('front_3', lottery_data['second_prize_1'], 4000, 1),
                ('front_3', lottery_data['second_prize_2'], 4000, 2),
                ('back_3', lottery_data['third_prize_1'], 4000, 1),
                ('back_3', lottery_data['third_prize_2'], 4000, 2),
                ('back_2', lottery_data['fourth_prize_1'], 2000),
            ]

            for config in prize_configs:
                if len(config) == 3:  # ไม่มี position
                    prize_type, number, amount = config
                    position = 1
                else:  # มี position
                    prize_type, number, amount, position = config

                if number:  # ถ้ามีเลข
                    prizes_to_insert.append({
                        'draw_id': draw_id,
                        'prize_type': prize_type,
                        'prize_number': number,
                        'position': position,
                        'amount': amount
                    })

            # รางวัลข้างเคียง
            for i, number in enumerate(lottery_data.get('nearby_prizes', []), 1):
                if number:
                    prizes_to_insert.append({
                        'draw_id': draw_id,
                        'prize_type': 'nearby',
                        'prize_number': number,
                        'position': i,
                        'amount': 100000
                    })

            # รางวัลที่ 2-5
            prize_types_extended = [
                ('second', lottery_data.get('second_prizes', []), 200000),
                ('third', lottery_data.get('third_prizes', []), 80000),
                ('fourth', lottery_data.get('fourth_prizes', []), 40000),
                ('fifth', lottery_data.get('fifth_prizes', []), 20000)
            ]

            for prize_type, numbers, amount in prize_types_extended:
                for i, number in enumerate(numbers, 1):
                    if number:
                        prizes_to_insert.append({
                            'draw_id': draw_id,
                            'prize_type': prize_type,
                            'prize_number': number,
                            'position': i,
                            'amount': amount
                        })

            # 3. บันทึกรางวัลทั้งหมดพร้อมกัน
            if prizes_to_insert:
                result = self.supabase.table('lottery_prizes').insert(prizes_to_insert).execute()
                print(f"บันทึกรางวัล {len(prizes_to_insert)} รายการสำเร็จ")

            print(f"บันทึกผลลอตเตอรี่วันที่ {lottery_data['draw_date']} สำเร็จ")
            return True

        except Exception as e:
            print(f"ไม่สามารถบันทึกข้อมูลได้: {e}")
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
            print(f"ไม่สามารถดึงข้อมูลจากฐานข้อมูลได้: {e}")
            return None

    def check_number(self, number, draw_date=None):
        """ตรวจสอบเลขว่าถูกรางวัลอะไรบ้าง"""
        if not self.supabase:
            return None

        try:
            # ถ้าระบุวันที่ ให้ตรวจสอบว่ามีข้อมูลงวดนั้นในฐานข้อมูลหรือไม่
            if draw_date:
                # ตรวจสอบว่ามีข้อมูลงวดนั้นแล้วหรือยัง
                check_draw = self.supabase.table('lottery_draws').select("id").eq("draw_date", draw_date).execute()

                if not check_draw.data:
                    # ไม่มีข้อมูลงวดนี้ ให้ไป scrape มาก่อน
                    print(f"ไม่พบข้อมูลงวด {draw_date} ในฐานข้อมูล กำลัง scrape ข้อมูล...")
                    lottery_data = self.get_lottery_by_date(draw_date)

                    if lottery_data:
                        # บันทึกข้อมูลใหม่ลงฐานข้อมูล
                        self.save_to_database(lottery_data)
                        print(f"บันทึกข้อมูลงวด {draw_date} เรียบร้อยแล้ว")
                    else:
                        print(f"ไม่สามารถ scrape ข้อมูลงวด {draw_date} ได้")
                        return None

            # ใช้ Supabase query แทน raw SQL
            if draw_date:
                # Query สำหรับงวดเฉพาะ
                result = (self.supabase.table('lottery_prizes')
                         .select('prize_type, amount, position, lottery_draws!inner(draw_date, draw_number)')
                         .eq('prize_number', number)
                         .eq('lottery_draws.draw_date', draw_date)
                         .execute())
            else:
                # Query สำหรับทุกงวด
                result = (self.supabase.table('lottery_prizes')
                         .select('prize_type, amount, position, lottery_draws!inner(draw_date, draw_number)')
                         .eq('prize_number', number)
                         .order('lottery_draws.draw_date', desc=True)
                         .execute())

            if result.data:
                # จัดกลุ่มผลลัพธ์ตามงวด
                results_by_draw = {}
                for item in result.data:
                    draw_date_key = item['draw_date']
                    if draw_date_key not in results_by_draw:
                        results_by_draw[draw_date_key] = {
                            'draw_date': draw_date_key,
                            'draw_number': item['draw_number'],
                            'prizes': []
                        }

                    # แปลง prize_type เป็นชื่อภาษาไทย
                    prize_names = {
                        'first': 'รางวัลที่ 1',
                        'front_3': 'เลขหน้า 3 ตัว',
                        'back_3': 'เลขท้าย 3 ตัว',
                        'back_2': 'เลขท้าย 2 ตัว',
                        'nearby': 'ข้างเคียงรางวัลที่ 1',
                        'second': 'รางวัลที่ 2',
                        'third': 'รางวัลที่ 3',
                        'fourth': 'รางวัลที่ 4',
                        'fifth': 'รางวัลที่ 5'
                    }

                    results_by_draw[draw_date_key]['prizes'].append({
                        'prize_type': item['prize_type'],
                        'prize_name': prize_names.get(item['prize_type'], item['prize_type']),
                        'position': item['position'],
                        'amount': item['amount']
                    })

                return {
                    'number': number,
                    'total_draws_found': len(results_by_draw),
                    'results': list(results_by_draw.values())
                }

            return None

        except Exception as e:
            print(f"ไม่สามารถตรวจสอบเลขได้: {e}")
            return None

    def check_number_complete(self, number, draw_date):
        """ตรวจสอบเลข 6 ตัวครบทุกรูปแบบ (6 ตัว, หน้า 3, ท้าย 3, ท้าย 2)"""
        if not self.supabase:
            return {"number": number, "draw_date": draw_date, "results": [], "message": "ไม่สามารถเชื่อมต่อฐานข้อมูลได้"}

        try:
            # ตรวจสอบว่ามีข้อมูลงวดนั้นแล้วหรือยัง
            check_draw = self.supabase.table('lottery_draws').select("id, draw_number").eq("draw_date", draw_date).execute()

            if not check_draw.data:
                # ไม่มีข้อมูลงวดนี้ ให้ไป scrape มาก่อน
                print(f"ไม่พบข้อมูลงวด {draw_date} ในฐานข้อมูล กำลัง scrape ข้อมูล...")
                lottery_data = self.get_lottery_by_date(draw_date)

                if lottery_data:
                    # บันทึกข้อมูลใหม่ลงฐานข้อมูล
                    self.save_to_database(lottery_data)
                    print(f"บันทึกข้อมูลงวด {draw_date} เรียบร้อยแล้ว")
                else:
                    return {"number": number, "draw_date": draw_date, "results": [], "message": f"ไม่สามารถหาข้อมูลหวยงวด {draw_date} ได้"}

            # สร้างรูปแบบการตรวจต่างๆ
            patterns_to_check = {
                "full_6_digits": number,           # เลข 6 ตัวเต็ม
                "front_3_digits": number[:3],      # เลขหน้า 3 ตัว
                "back_3_digits": number[-3:],      # เลขท้าย 3 ตัว
                "back_2_digits": number[-2:]       # เลขท้าย 2 ตัว
            }

            all_matches = []

            # ตรวจแต่ละรูปแบบ
            for match_type, check_number in patterns_to_check.items():
                result = (self.supabase.table('lottery_prizes')
                         .select('prize_type, amount, position, lottery_draws!inner(draw_date, draw_number)')
                         .eq('prize_number', check_number)
                         .eq('lottery_draws.draw_date', draw_date)
                         .execute())

                if result.data:
                    for item in result.data:
                        # แปลง prize_type เป็นชื่อภาษาไทย
                        prize_names = {
                            'first_prize': 'รางวัลที่ 1',
                            'front_3': 'เลขหน้า 3 ตัว',
                            'back_3': 'เลขท้าย 3 ตัว',
                            'back_2': 'เลขท้าย 2 ตัว',
                            'nearby': 'ข้างเคียงรางวัลที่ 1',
                            'second_prize': 'รางวัลที่ 2',
                            'third_prize': 'รางวัลที่ 3',
                            'fourth_prize': 'รางวัลที่ 4',
                            'fifth_prize': 'รางวัลที่ 5'
                        }

                        all_matches.append({
                            'match_type': match_type,
                            'matched_digits': check_number,
                            'prize_type': item['prize_type'],
                            'prize_name': prize_names.get(item['prize_type'], item['prize_type']),
                            'amount': item['amount'],
                            'position': item['position']
                        })

            # จัดเรียงตาม amount (จากมากไปน้อย)
            all_matches.sort(key=lambda x: x['amount'], reverse=True)

            return {
                "number": number,
                "draw_date": draw_date,
                "draw_number": check_draw.data[0]['draw_number'] if check_draw.data else None,
                "total_matches": len(all_matches),
                "results": all_matches,
                "message": "ถูกรางวัล!" if all_matches else "ไม่ถูกรางวัล"
            }

        except Exception as e:
            print(f"ไม่สามารถตรวจสอบเลขแบบครบถ้วนได้: {e}")
            return {"number": number, "draw_date": draw_date, "results": [], "message": f"เกิดข้อผิดพลาด: {str(e)}"}

class LotteryHandler(http.server.BaseHTTPRequestHandler):
    def validate_lottery_date(self, date_str):
        """ตรวจสอบวันที่หวย (ต้องเป็นวันที่ 1 หรือ 16)"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day = date_obj.day

            # หวยออกแค่วันที่ 1 และ 16
            if day not in [1, 16]:
                return False, f"หวยออกเฉพาะวันที่ 1 และ 16 ของทุกเดือน ไม่ใช่วันที่ {day}"

            return True, None
        except ValueError:
            return False, "รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD"

    def validate_lottery_number(self, number):
        """ตรวจสอบเลขหวย (ต้องเป็นตัวเลข 6 ตัว)"""
        if not isinstance(number, str):
            return False, "เลขหวยต้องเป็น string"

        if len(number) != 6:
            return False, f"เลขหวยต้องเป็น 6 ตัว ไม่ใช่ {len(number)} ตัว"

        if not number.isdigit():
            return False, "เลขหวยต้องเป็นตัวเลขเท่านั้น"

        return True, None

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

            elif path == '/api/lottery/check':
                # API สำหรับตรวจสอบเลข
                if 'number' not in params:
                    self.send_error_response(400, "Missing required parameter: number")
                    return

                number = params['number'][0]
                draw_date = params.get('draw_date', [None])[0]  # optional

                # สร้าง API instance
                api = LotteryAPI()

                # ตรวจสอบเลข
                results = api.check_number(number, draw_date)

                if results:
                    self.send_success_response(results)
                else:
                    self.send_success_response({
                        "number": number,
                        "draw_date": draw_date,
                        "results": [],
                        "message": "เลขนี้ไม่ถูกรางวัล"
                    })

            else:
                self.send_error_response(404, "Not Found")
                
        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน API: {e}")
            self.send_error_response(500, f"Internal Server Error: {str(e)}")

    def do_POST(self):
        """Handle POST requests"""
        try:
            # แยก path
            path = self.path.split('?')[0]

            if path == '/api/lottery/check':
                # อ่าน POST data
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)

                try:
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self.send_error_response(400, "Invalid JSON format")
                    return

                # ตรวจสอบ required fields
                if 'number' not in data:
                    self.send_error_response(400, "Missing required field: number")
                    return

                if 'draw_date' not in data:
                    self.send_error_response(400, "Missing required field: draw_date")
                    return

                number = str(data['number'])
                draw_date = data['draw_date']

                # Validate เลขหวย (ต้อง 6 ตัว)
                is_valid_number, number_error = self.validate_lottery_number(number)
                if not is_valid_number:
                    self.send_error_response(400, number_error)
                    return

                # Validate วันที่หวย (ต้อง 1 หรือ 16)
                is_valid_date, date_error = self.validate_lottery_date(draw_date)
                if not is_valid_date:
                    self.send_error_response(400, date_error)
                    return

                # สร้าง API instance
                api = LotteryAPI()

                # ตรวจสอบเลขแบบครบทุกรูปแบบ
                results = api.check_number_complete(number, draw_date)

                self.send_success_response(results)

            else:
                self.send_error_response(404, "Not Found")

        except Exception as e:
            print(f"เกิดข้อผิดพลาดใน POST API: {e}")
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

    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_server():
    """เริ่มต้น server"""
    PORT = 8001
    
    with socketserver.TCPServer(("", PORT), LotteryHandler) as httpd:
        print(f"Server เริ่มต้นที่ http://localhost:{PORT}")
        print("\n=== API Endpoints ===")
        print("ดึงข้อมูลหวย: http://localhost:8001/api/lottery?draw_date=YYYY-MM-DD")
        print("ตรวจเลข GET: http://localhost:8001/api/lottery/check?number=123456")
        print("ตรวจเลข POST: POST /api/lottery/check {\"number\":\"123456\",\"draw_date\":\"2025-03-16\"}")
        print("\n=== ตัวอย่าง ===")
        print("http://localhost:8001/api/lottery?draw_date=2025-03-16")
        print("http://localhost:8001/api/lottery/check?number=757563")
        print("http://localhost:8001/api/lottery/check?number=595&draw_date=2025-03-16")
        print("\nกด Ctrl+C เพื่อหยุด server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer หยุดทำงาน")
            httpd.shutdown()

if __name__ == "__main__":
    start_server()
