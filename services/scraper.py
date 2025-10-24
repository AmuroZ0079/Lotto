import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from typing import Dict, Optional, Any


class LotteryScraper:
    def __init__(self):
        self.base_url = "https://news.sanook.com"

    def scrape_lottery_data(self, draw_date: str) -> Optional[Dict[str, Any]]:
        """ดึงข้อมูลหวยจากเว็บไซต์"""
        try:
            url = f"{self.base_url}/lotto/{draw_date}"
            print(f"กำลังดึงข้อมูลจาก: {url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # ลองดึงข้อมูลจาก JSON-LD ก่อน
            lottery_data = self._parse_json_ld_data(soup, draw_date)

            if lottery_data:
                # ดึงรางวัลเพิ่มเติม (รางวัลที่ 2-5)
                self._extract_additional_prizes(soup, lottery_data)

            return lottery_data

        except Exception as e:
            print(f"ไม่สามารถดึงข้อมูลได้: {e}")
            return None

    def _parse_json_ld_data(self, soup: BeautifulSoup, draw_date: str) -> Optional[Dict[str, Any]]:
        """แยกข้อมูลจาก JSON-LD"""
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            print(f"พบ JSON-LD script: {len(scripts)}")

            for script in scripts:
                try:
                    data = json.loads(script.string)
                    print(f"JSON-LD type: {data.get('@type')}")

                    if data.get('@type') == 'NewsArticle':
                        article_body = data.get('articleBody', '')

                        if 'รางวัลที่ 1' in article_body:
                            return self._parse_lottery_data(soup, draw_date)

                except json.JSONDecodeError:
                    continue

            return None

        except Exception as e:
            print(f"ไม่สามารถแยก JSON-LD ได้: {e}")
            return None

    def _parse_lottery_data(self, soup: BeautifulSoup, draw_date: str) -> Dict[str, Any]:
        """แยกข้อมูลหวยจาก HTML"""
        try:
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

            # รางวัลที่ 1
            first_prize_elements = soup.find_all(class_='lotto_number--first')
            for element in first_prize_elements:
                text = element.get_text().strip()
                if re.match(r'\d{6}', text):
                    lottery_data['first_prize'] = text
                    print(f"พบรางวัลที่ 1: {text}")
                    break

            # เลขหน้า 3 ตัว และเลขท้าย 3 ตัว
            lottocheck_columns = soup.find_all(class_='lottocheck_column')

            if len(lottocheck_columns) >= 2:
                # Column 2: เลขหน้า 3 ตัว
                column2 = lottocheck_columns[1]
                front3_numbers = column2.find_all(class_='lotto_number')
                if len(front3_numbers) >= 2:
                    lottery_data['second_prize_1'] = front3_numbers[0].get_text().strip()
                    lottery_data['second_prize_2'] = front3_numbers[1].get_text().strip()

            if len(lottocheck_columns) >= 3:
                # Column 3: เลขท้าย 3 ตัว
                column3 = lottocheck_columns[2]
                back3_numbers = column3.find_all(class_='lotto_number')
                if len(back3_numbers) >= 2:
                    lottery_data['third_prize_1'] = back3_numbers[0].get_text().strip()
                    lottery_data['third_prize_2'] = back3_numbers[1].get_text().strip()

            # เลขท้าย 2 ตัว
            if len(lottocheck_columns) >= 4:
                column4 = lottocheck_columns[3]
                back2_number = column4.find(class_='lotto_number')
                if back2_number:
                    lottery_data['fourth_prize_1'] = back2_number.get_text().strip()

            return lottery_data

        except Exception as e:
            print(f"ไม่สามารถแยกข้อมูลหวยได้: {e}")
            return {}

    def _extract_additional_prizes(self, soup: BeautifulSoup, lottery_data: Dict[str, Any]):
        """ดึงข้อมูลรางวัลที่ 2-5 และข้างเคียง"""
        try:
            # หา articleBody จาก JSON-LD
            scripts = soup.find_all('script', type='application/ld+json')
            article_body = ""

            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if data.get('@type') == 'NewsArticle':
                        article_body = data.get('articleBody', '')
                        break
                except json.JSONDecodeError:
                    continue

            if not article_body:
                return

            # รางวัลข้างเคียงรางวัลที่ 1
            first_prize = lottery_data.get('first_prize', '')
            if first_prize:
                first_number = int(first_prize)
                nearby_numbers = [str(first_number - 1).zfill(6), str(first_number + 1).zfill(6)]
                lottery_data['nearby_prizes'] = nearby_numbers

            # รางวัลที่ 2 (5 รางวัล)
            second_section = re.search(r'รางวัลที่ 2 มี 5 รางวัล.*?(\d{6}&nbsp;.*?)(?=ผลสลากกินแบ่งรัฐบาล รางวัลที่ 3|$)', article_body, re.DOTALL)
            if second_section:
                second_numbers = re.findall(r'(\d{6})&nbsp;', second_section.group(1))
                lottery_data['second_prizes'] = second_numbers[:5]

            # รางวัลที่ 3 (10 รางวัล)
            third_section = re.search(r'รางวัลที่ 3 มี 10 รางวัล.*?(\d{6}&nbsp;.*?)(?=ผลสลากกินแบ่งรัฐบาล รางวัลที่ 4|$)', article_body, re.DOTALL)
            if third_section:
                third_numbers = re.findall(r'(\d{6})&nbsp;', third_section.group(1))
                lottery_data['third_prizes'] = third_numbers[:10]

            # รางวัลที่ 4 (50 รางวัล)
            fourth_section = re.search(r'รางวัลที่ 4 มี 50 รางวัล.*?(\d{6}.*?)(?=ผลสลากกินแบ่งรัฐบาล รางวัลที่ 5|$)', article_body, re.DOTALL)
            if fourth_section:
                fourth_numbers = re.findall(r'(\d{6})(?:&nbsp;|(?=\s)|(?=\n)|$)', fourth_section.group(1))
                lottery_data['fourth_prizes'] = fourth_numbers[:50]

            # รางวัลที่ 5 (100 รางวัล)
            fifth_section = re.search(r'รางวัลที่ 5 มี 100 รางวัล.*?(\d{6}.*?)(?=$)', article_body, re.DOTALL)
            if fifth_section:
                fifth_numbers = re.findall(r'(\d{6})(?:&nbsp;|(?=\s)|(?=\n)|$)', fifth_section.group(1))
                lottery_data['fifth_prizes'] = fifth_numbers[:100]

        except Exception as e:
            print(f"ไม่สามารถดึงรางวัลเพิ่มเติมได้: {e}")