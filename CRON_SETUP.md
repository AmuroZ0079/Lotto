# Lottery Auto-Scraping Cron Job Setup

## วิธีการทำงาน

**Smart Cron Logic:**
1. รันทุกวันเวลา 19:00 น.
2. เช็คว่าวันนี้ควร scrape หรือไม่:
   - **วันที่ 1, 16** → scrape เสมอ (วันหวยออก)
   - **วันอื่นๆ** → scrape ต่อถ้ายังไม่มีข้อมูลงวดปัจจุบัน
3. หยุดเมื่อได้ข้อมูลครบถ้วนแล้ว

## การติดตั้ง

### 1. เพิ่ม Cron Routes ใน FastAPI

ใน `fastapi_main.py`:
```python
from api.cron_service import router as cron_router
app.include_router(cron_router, prefix="/cron")
```

### 2. Linux/Mac Cron Setup

```bash
# เปิด crontab editor
crontab -e

# เพิ่มบรรทัดนี้ (รันทุกวันเวลา 19:00)
0 19 * * * /usr/bin/python3 /path/to/lottery/cron_script.py >> /var/log/lottery_cron.log 2>&1

# หรือระบุ environment variables
0 19 * * * cd /path/to/lottery && /usr/bin/python3 cron_script.py >> lottery_cron.log 2>&1
```

### 3. Windows Task Scheduler

1. เปิด Task Scheduler
2. Create Basic Task
3. **Trigger:** Daily at 7:00 PM
4. **Action:** Start a program
   - **Program:** `C:\Python39\python.exe`
   - **Arguments:** `C:\path\to\lottery\cron_script.py`
   - **Start in:** `C:\path\to\lottery`

### 4. หรือใช้ External Cron Services

**Vercel Cron Functions (แนะนำ):**
```javascript
// api/cron/scrape.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // เรียก scrape API
  const response = await fetch('https://lotto-six-roan.vercel.app/cron/scrape-current', {
    method: 'POST'
  });

  const result = await response.json();
  return res.status(200).json(result);
}
```

**GitHub Actions (ฟรี):**
```yaml
# .github/workflows/lottery-cron.yml
name: Lottery Auto Scrape
on:
  schedule:
    - cron: '0 12 * * *'  # 19:00 Thailand = 12:00 UTC
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run scrape
        run: |
          curl -X POST https://lotto-six-roan.vercel.app/cron/scrape-current
```

## API Endpoints สำหรับ Cron

### เช็คสถานะ
```bash
GET https://lotto-six-roan.vercel.app/cron/status
```

### Scrape งวดปัจจุบัน
```bash
POST https://lotto-six-roan.vercel.app/cron/scrape-current
```

### Scrape งวดเฉพาะ
```bash
POST https://lotto-six-roan.vercel.app/cron/scrape-date/2025-07-16
```

### เช็คงวดที่ขาดหาย
```bash
GET https://lotto-six-roan.vercel.app/cron/check-missing
```

## การทดสอบ

### 1. ทดสอบ Manual
```bash
# เรียก cron script
python3 cron_script.py

# เช็ค log
tail -f lottery_cron.log
```

### 2. ทดสอบ API
```bash
# เช็คสถานะ
curl https://lotto-six-roan.vercel.app/cron/status

# ทดสอบ scrape
curl -X POST https://lotto-six-roan.vercel.app/cron/scrape-current
```

## การ Monitor

### Log Files
```bash
# ดู log ล่าสุด
tail -f lottery_cron.log

# ดู error เฉพาะ
grep "ERROR\|❌" lottery_cron.log

# ดู success เฉพาะ
grep "SUCCESS\|✅" lottery_cron.log
```

### ตัวอย่าง Log Output
```
2025-10-25 19:00:01 - INFO - 🚀 เริ่มต้น Lottery Cron Job - 2025-10-25 19:00:01
2025-10-25 19:00:02 - INFO - 🎯 ต้อง scrape วันนี้ - lottery_day
2025-10-25 19:00:03 - INFO - 🔄 เริ่มต้น scrape ข้อมูลหวยงวดปัจจุบัน...
2025-10-25 19:00:45 - INFO - 🎉 Scrape สำเร็จ! งวด 2025-10-16 ได้ข้อมูล 171 รางวัล
2025-10-25 19:00:45 - INFO - ✅ Lottery Cron: Scrape สำเร็จ! งวด 2025-10-16 ได้ข้อมูล 171 รางวัล (Reason: lottery_day)
```

## การแจ้งเตือน (อนาคต)

สามารถเพิ่ม:
- **LINE Notify** - แจ้งเตือนผ่าน LINE
- **Email** - ส่งอีเมลแจ้งสถานะ
- **Discord/Slack** - แจ้งใน team chat
- **Dashboard** - หน้าเว็บแสดงสถานะ

## Troubleshooting

### Cron ไม่ทำงาน
1. เช็ค cron service: `sudo systemctl status cron`
2. เช็ค crontab: `crontab -l`
3. เช็ค log: `grep CRON /var/log/syslog`

### Script Error
1. เช็ค Python path: `which python3`
2. เช็ค permissions: `chmod +x cron_script.py`
3. ทดสอบ manual: `python3 cron_script.py`

### API Error
1. เช็ค internet connection
2. เช็ค API endpoint ใน browser
3. เช็ค Vercel deployment status