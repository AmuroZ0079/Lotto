# คู่มือการทดสอบระบบ Web Scraping ลอตเตอรี่

## ขั้นตอนการทดสอบ

### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 2. ทดสอบการ Scrap

#### วิธีที่ 1: ทดสอบด้วยข้อมูลตัวอย่าง (แนะนำ)

```bash
python test_scraping.py
# เลือกตัวเลือก 3
```

#### วิธีที่ 2: ทดสอบการ Scrap จริง

```bash
python test_scraping.py
# เลือกตัวเลือก 2
```

#### วิธีที่ 3: ทดสอบแบบเต็ม (รวมฐานข้อมูล)

```bash
# ตั้งค่า environment variables ก่อน
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"

python test_scraping.py
# เลือกตัวเลือก 1
```

### 3. ทดสอบ API Endpoints

#### ทดสอบในเครื่อง

```bash
# รัน API server
python -m http.server 8000

# ทดสอบ endpoint
curl http://localhost:8000/api/
curl http://localhost:8000/api/results
```

#### ทดสอบบน Vercel

```bash
# Deploy ไปยัง Vercel
vercel

# ทดสอบ endpoint
curl https://your-app.vercel.app/api/
curl https://your-app.vercel.app/api/results
```

## การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

1. **ไม่สามารถ scrap ได้**
   - ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
   - ตรวจสอบว่าเว็บไซต์เป้าหมายยังใช้งานได้
   - ลองใช้ข้อมูลตัวอย่างก่อน

2. **ไม่สามารถเชื่อมต่อฐานข้อมูลได้**
   - ตรวจสอบ SUPABASE_URL และ SUPABASE_KEY
   - ตรวจสอบการตั้งค่าใน Supabase Dashboard

3. **ข้อมูลไม่ถูกต้อง**
   - ตรวจสอบ CSS selectors ใน main.py
   - ปรับแต่งการ parse ข้อมูลตามเว็บไซต์จริง

### การ Debug

```bash
# เปิด debug mode
export LOG_LEVEL=DEBUG
python test_scraping.py
```

### การตรวจสอบ Logs

```bash
# ดู logs รายละเอียด
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from main import LotteryScraper
scraper = LotteryScraper()
result = scraper.scrape_lottery_result(use_sample_data=True)
print(result)
"
```

## การปรับแต่ง

### เปลี่ยนเว็บไซต์เป้าหมาย

แก้ไขใน `config.py`:

```python
LOTTERY_URLS = {
    'primary': 'https://your-lottery-website.com',
    'backup': 'https://backup-website.com'
}
```

### เปลี่ยน CSS Selectors

แก้ไขใน `main.py` ฟังก์ชัน `_extract_prizes()`:

```python
# เปลี่ยน class names ตามเว็บไซต์จริง
prize_elements = soup.find_all(['div', 'span'], class_='your-class-name')
```

### เปลี่ยนรูปแบบข้อมูล

แก้ไขใน `main.py` ฟังก์ชัน `_parse_lottery_data()`:

```python
lottery_data = {
    'draw_date': draw_date,
    'first_prize': prizes.get('first_prize', ''),
    # เพิ่มฟิลด์อื่นๆ ตามต้องการ
}
```

## การทดสอบ Cron Job

### ทดสอบในเครื่อง

```bash
# รัน cron job
python cron.py
```

### ทดสอบบน Vercel

1. ตั้งค่า cron job ใน Vercel Dashboard
2. หรือใช้ external service เช่น:
   - GitHub Actions
   - Cron-job.org
   - Uptime Robot

## การตรวจสอบผลลัพธ์

### ตรวจสอบฐานข้อมูล

```python
from database import LotteryDatabase

db = LotteryDatabase()
# ดูข้อมูลล่าสุด
latest = db.get_latest_result()
print(latest)

# ดูสถิติ
stats = db.get_statistics()
print(stats)
```

### ตรวจสอบ API

```bash
# ทดสอบ API
curl -X GET "https://your-app.vercel.app/api/results" \
  -H "Content-Type: application/json"
```

## หมายเหตุ

- ควรทดสอบด้วยข้อมูลตัวอย่างก่อน
- ตรวจสอบ robots.txt ของเว็บไซต์เป้าหมาย
- ใช้ rate limiting เพื่อไม่ให้ส่งผลกระทบต่อเว็บไซต์
- บันทึก logs เพื่อการ debug
