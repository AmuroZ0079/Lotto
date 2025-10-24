import os
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

# การตั้งค่า Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# การตั้งค่า Web Scraping
LOTTERY_URLS = {
    'primary': 'https://news.sanook.com/lotto/',  # เว็บไซต์หลัก - Sanook
    'backup': 'https://www.lottery.co.th/result',  # URL สำรอง
    'api': 'https://news.sanook.com/api/lottery/result'  # API endpoint ที่ใช้งานได้
}

# การตั้งค่า Cron Job
CRON_SCHEDULE = {
    'day_1': '0 20 1 * *',  # วันที่ 1 เวลา 20:00
    'day_16': '0 20 16 * *'  # วันที่ 16 เวลา 20:00
}

# การตั้งค่า Database
TABLE_NAME = 'lottery_results'

# User Agent สำหรับการ request
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
