import requests
from bs4 import BeautifulSoup
from database import LotteryDatabase
from config import LOTTERY_URLS, USER_AGENT
import logging
from datetime import datetime, date
import re
import json

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LotteryScraper:
    def __init__(self):
        """เริ่มต้น Lottery Scraper"""
        self.db = LotteryDatabase()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
    def scrape_lottery_result(self, use_sample_data=False):
        """ดึงผลลอตเตอรี่จากเว็บไซต์"""
        try:
            # ใช้ข้อมูลตัวอย่างสำหรับทดสอบ
            if use_sample_data:
                logger.info("ใช้ข้อมูลตัวอย่างสำหรับทดสอบ")
                from sample_data import get_sample_lottery_data
                return get_sample_lottery_data()
            
            # ลองใช้ API ก่อน (ถ้ามี)
            result = self._try_api_endpoint()
            if result:
                return result
            
            # ลองดึงจาก URL หลัก
            result = self._scrape_from_url(LOTTERY_URLS['primary'])
            if result:
                return result
            
            # หากไม่สำเร็จ ลอง URL สำรอง
            logger.warning("ไม่สามารถดึงข้อมูลจาก URL หลักได้ ลอง URL สำรอง")
            return self._scrape_from_url(LOTTERY_URLS['backup'])
            
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
            return None

    def _try_api_endpoint(self):
        """ลองใช้ API endpoint ก่อน"""
        try:
            api_url = LOTTERY_URLS['api']
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data and 'results' in data:
                return self._parse_api_data(data)
            return None
            
        except Exception as e:
            logger.warning(f"ไม่สามารถใช้ API ได้: {e}")
            return None

    def _parse_api_data(self, data):
        """แยกข้อมูลจาก API response"""
        try:
            results = data.get('results', [])
            if not results:
                return None
                
            latest_result = results[0]  # เอาผลล่าสุด
            
            return {
                'draw_date': latest_result.get('draw_date', date.today().strftime('%Y-%m-%d')),
                'draw_number': latest_result.get('draw_number', ''),
                'first_prize': latest_result.get('first_prize', ''),
                'second_prize_1': latest_result.get('second_prize_1', ''),
                'second_prize_2': latest_result.get('second_prize_2', ''),
                'third_prize_1': latest_result.get('third_prize_1', ''),
                'third_prize_2': latest_result.get('third_prize_2', ''),
                'third_prize_3': latest_result.get('third_prize_3', ''),
                'fourth_prize_1': latest_result.get('fourth_prize_1', ''),
                'fourth_prize_2': latest_result.get('fourth_prize_2', ''),
                'fourth_prize_3': latest_result.get('fourth_prize_3', ''),
                'fourth_prize_4': latest_result.get('fourth_prize_4', ''),
                'fifth_prize_1': latest_result.get('fifth_prize_1', ''),
                'fifth_prize_2': latest_result.get('fifth_prize_2', ''),
                'fifth_prize_3': latest_result.get('fifth_prize_3', '')
            }
            
        except Exception as e:
            logger.error(f"ไม่สามารถแยกข้อมูลจาก API ได้: {e}")
            return None

    def _scrape_from_url(self, url):
        """ดึงข้อมูลจาก URL ที่กำหนด"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # หาข้อมูลผลลอตเตอรี่ (ต้องปรับตามโครงสร้างของเว็บไซต์จริง)
            lottery_data = self._parse_lottery_data(soup)
            
            if lottery_data:
                logger.info(f"ดึงข้อมูลสำเร็จจาก {url}")
                return lottery_data
            else:
                logger.warning(f"ไม่พบข้อมูลจาก {url}")
                return None
                
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลจาก {url}: {e}")
            return None

    def _parse_lottery_data(self, soup):
        """แยกข้อมูลผลลอตเตอรี่จาก HTML"""
        try:
            # หาข้อมูลวันที่
            draw_date = self._extract_date(soup)
            
            # หาข้อมูลรางวัลต่างๆ
            prizes = self._extract_prizes(soup)
            
            lottery_data = {
                'draw_date': draw_date,
                'draw_number': self._get_draw_number(soup),
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
            
            # ตรวจสอบว่ามีข้อมูลรางวัลที่ 1 หรือไม่
            if not lottery_data['first_prize']:
                logger.warning("ไม่พบข้อมูลรางวัลที่ 1")
                return None
                
            return lottery_data
            
        except Exception as e:
            logger.error(f"ไม่สามารถแยกข้อมูลได้: {e}")
            return None

    def _extract_date(self, soup):
        """ดึงวันที่ออกสลาก"""
        try:
            # หา element ที่มีวันที่
            date_elements = soup.find_all(['span', 'div', 'p'], string=re.compile(r'\d{1,2}/\d{1,2}/\d{4}'))
            for element in date_elements:
                date_text = element.get_text().strip()
                if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_text):
                    # แปลงรูปแบบวันที่
                    from datetime import datetime
                    try:
                        date_obj = datetime.strptime(date_text, '%d/%m/%Y')
                        return date_obj.strftime('%Y-%m-%d')
                    except:
                        continue
            
            # หากไม่พบ ใช้วันที่ปัจจุบัน
            return date.today().strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.warning(f"ไม่สามารถดึงวันที่ได้: {e}")
            return date.today().strftime('%Y-%m-%d')

    def _extract_prizes(self, soup):
        """ดึงข้อมูลรางวัลทั้งหมด"""
        prizes = {}
        
        try:
            # หาข้อมูลจาก Sanook Lotto
            # ดูจากโครงสร้าง HTML ที่มีในเว็บไซต์
            
            # หา link ไปยังผลลอตเตอรี่งวดล่าสุด
            latest_links = soup.find_all('a', href=re.compile(r'ตรวจหวย.*งวด.*ล่าสุด'))
            
            if latest_links:
                # ไปที่หน้าผลลอตเตอรี่งวดล่าสุด
                latest_url = latest_links[0].get('href')
                if latest_url.startswith('/'):
                    latest_url = 'https://news.sanook.com' + latest_url
                
                logger.info(f"ไปที่หน้า: {latest_url}")
                response = self.session.get(latest_url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
            
            # หาข้อมูลรางวัลจากโครงสร้างของ Sanook
            # ใช้ pattern ที่เหมาะกับ Sanook
            prize_sections = soup.find_all(['div', 'section'], class_=re.compile(r'lottery|result|prize'))
            
            for section in prize_sections:
                section_text = section.get_text().lower()
                
                # หารางวัลที่ 1
                if 'รางวัลที่ 1' in section_text or 'first prize' in section_text:
                    numbers = re.findall(r'\d{6}', section.get_text())
                    if numbers:
                        prizes['first_prize'] = numbers[0]
                
                # หารางวัลที่ 2
                elif 'รางวัลที่ 2' in section_text or 'second prize' in section_text:
                    numbers = re.findall(r'\d{6}', section.get_text())
                    if len(numbers) >= 1:
                        prizes['second_prize_1'] = numbers[0]
                    if len(numbers) >= 2:
                        prizes['second_prize_2'] = numbers[1]
                
                # หารางวัลที่ 3
                elif 'รางวัลที่ 3' in section_text or 'third prize' in section_text:
                    numbers = re.findall(r'\d{6}', section.get_text())
                    if len(numbers) >= 1:
                        prizes['third_prize_1'] = numbers[0]
                    if len(numbers) >= 2:
                        prizes['third_prize_2'] = numbers[1]
                    if len(numbers) >= 3:
                        prizes['third_prize_3'] = numbers[2]
                
                # หารางวัลที่ 4
                elif 'รางวัลที่ 4' in section_text or 'fourth prize' in section_text:
                    numbers = re.findall(r'\d{6}', section.get_text())
                    for i, num in enumerate(numbers[:4]):
                        prizes[f'fourth_prize_{i+1}'] = num
                
                # หารางวัลที่ 5
                elif 'รางวัลที่ 5' in section_text or 'fifth prize' in section_text:
                    numbers = re.findall(r'\d{6}', section.get_text())
                    for i, num in enumerate(numbers[:3]):
                        prizes[f'fifth_prize_{i+1}'] = num
            
            # หากไม่พบข้อมูลจาก section ให้ลองหาจาก pattern ทั่วไป
            if not prizes:
                all_numbers = re.findall(r'\d{6}', soup.get_text())
                if all_numbers:
                    # ใช้ตัวเลขแรกเป็นรางวัลที่ 1
                    prizes['first_prize'] = all_numbers[0]
                    
                    # จัดกลุ่มตัวเลขที่เหลือ
                    remaining = all_numbers[1:]
                    if len(remaining) >= 2:
                        prizes['second_prize_1'] = remaining[0]
                        prizes['second_prize_2'] = remaining[1]
                    if len(remaining) >= 5:
                        prizes['third_prize_1'] = remaining[2]
                        prizes['third_prize_2'] = remaining[3]
                        prizes['third_prize_3'] = remaining[4]
            
            return prizes
            
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลรางวัลได้: {e}")
            return {}

    def _get_draw_number(self, soup):
        """ดึงหมายเลขงวด"""
        try:
            # หาข้อมูลงวดจาก Sanook
            # ดูจาก pattern "งวด 1 พ.ย. 68" หรือ "งวด 16 ต.ค. 68"
            draw_patterns = [
                r'งวด\s*(\d+)\s*[ก-๙]+\.\s*\d+',  # งวด 1 พ.ย. 68
                r'งวด\s*(\d+)\s*[ก-๙]+\s*\d+',     # งวด 1 พ.ย. 68
                r'งวด\s*(\d+)',                     # งวด 1
            ]
            
            for pattern in draw_patterns:
                matches = re.findall(pattern, soup.get_text())
                if matches:
                    return f"งวด {matches[0]}"
            
            # หาจาก title หรือ heading
            title_elements = soup.find_all(['title', 'h1', 'h2', 'h3'])
            for element in title_elements:
                text = element.get_text()
                if 'งวด' in text:
                    match = re.search(r'งวด\s*(\d+)', text)
                    if match:
                        return f"งวด {match.group(1)}"
            
            return None
            
        except Exception as e:
            logger.warning(f"ไม่สามารถดึงหมายเลขงวดได้: {e}")
            return None

    def _get_first_prize(self, soup):
        """ดึงรางวัลที่ 1"""
        # หา element ที่มีรางวัลที่ 1
        first_prize_elements = soup.find_all(['span', 'div'], class_=re.compile(r'first|prize|1st'))
        for element in first_prize_elements:
            text = element.get_text().strip()
            if re.match(r'\d{6}', text):
                return text
        return None

    def _get_second_prize_1(self, soup):
        """ดึงรางวัลที่ 2 หมายเลขที่ 1"""
        return self._get_prize_by_pattern(soup, r'second|2nd|2')

    def _get_second_prize_2(self, soup):
        """ดึงรางวัลที่ 2 หมายเลขที่ 2"""
        return self._get_prize_by_pattern(soup, r'second|2nd|2')

    def _get_third_prize_1(self, soup):
        """ดึงรางวัลที่ 3 หมายเลขที่ 1"""
        return self._get_prize_by_pattern(soup, r'third|3rd|3')

    def _get_third_prize_2(self, soup):
        """ดึงรางวัลที่ 3 หมายเลขที่ 2"""
        return self._get_prize_by_pattern(soup, r'third|3rd|3')

    def _get_third_prize_3(self, soup):
        """ดึงรางวัลที่ 3 หมายเลขที่ 3"""
        return self._get_prize_by_pattern(soup, r'third|3rd|3')

    def _get_fourth_prize_1(self, soup):
        """ดึงรางวัลที่ 4 หมายเลขที่ 1"""
        return self._get_prize_by_pattern(soup, r'fourth|4th|4')

    def _get_fourth_prize_2(self, soup):
        """ดึงรางวัลที่ 4 หมายเลขที่ 2"""
        return self._get_prize_by_pattern(soup, r'fourth|4th|4')

    def _get_fourth_prize_3(self, soup):
        """ดึงรางวัลที่ 4 หมายเลขที่ 3"""
        return self._get_prize_by_pattern(soup, r'fourth|4th|4')

    def _get_fourth_prize_4(self, soup):
        """ดึงรางวัลที่ 4 หมายเลขที่ 4"""
        return self._get_prize_by_pattern(soup, r'fourth|4th|4')

    def _get_fifth_prize_1(self, soup):
        """ดึงรางวัลที่ 5 หมายเลขที่ 1"""
        return self._get_prize_by_pattern(soup, r'fifth|5th|5')

    def _get_fifth_prize_2(self, soup):
        """ดึงรางวัลที่ 5 หมายเลขที่ 2"""
        return self._get_prize_by_pattern(soup, r'fifth|5th|5')

    def _get_fifth_prize_3(self, soup):
        """ดึงรางวัลที่ 5 หมายเลขที่ 3"""
        return self._get_prize_by_pattern(soup, r'fifth|5th|5')

    def _get_prize_by_pattern(self, soup, pattern):
        """หาข้อมูลรางวัลตาม pattern"""
        elements = soup.find_all(['span', 'div'], class_=re.compile(pattern, re.I))
        for element in elements:
            text = element.get_text().strip()
            if re.match(r'\d{6}', text):
                return text
        return None

    def run_scraping(self):
        """รันการ scraping และบันทึกข้อมูล"""
        try:
            logger.info("เริ่มต้นการดึงข้อมูลผลลอตเตอรี่")
            
            # ดึงข้อมูล
            lottery_data = self.scrape_lottery_result()
            
            if lottery_data:
                # บันทึกลงฐานข้อมูล
                if self.db.save_lottery_result(lottery_data):
                    logger.info("บันทึกข้อมูลสำเร็จ")
                    return True
                else:
                    logger.error("ไม่สามารถบันทึกข้อมูลได้")
                    return False
            else:
                logger.error("ไม่สามารถดึงข้อมูลได้")
                return False
                
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการรัน scraping: {e}")
            return False

def main():
    """ฟังก์ชันหลัก"""
    scraper = LotteryScraper()
    success = scraper.run_scraping()
    
    if success:
        print("การดึงข้อมูลผลลอตเตอรี่สำเร็จ")
    else:
        print("การดึงข้อมูลผลลอตเตอรี่ล้มเหลว")

if __name__ == "__main__":
    main()
