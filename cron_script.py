#!/usr/bin/env python3
"""
Smart Lottery Cron Script

ลอจิก:
1. รันทุกวันเวลา 19:00
2. เช็คว่าเป็นวันที่ 1 หรือ 16 หรือไม่
3. ถ้าใช่ → พยายาม scrape งวดปัจจุบัน
4. ถ้าไม่เจอข้อมูล → รันต่อทุกวันจนกว่าจะเจอ
5. เจอแล้ว → หยุด รอถึงวันที่ 1 หรือ 16 ถัดไป

การใช้งาน:
- Linux/Mac: python3 cron_script.py
- Windows: python cron_script.py

Cron job setting (Linux):
0 19 * * * /usr/bin/python3 /path/to/cron_script.py >> /var/log/lottery_cron.log 2>&1
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import logging

# กำหนด URL ของ API
API_BASE_URL = "https://lotto-six-roan.vercel.app"

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lottery_cron.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def should_scrape_today():
    """ตรวจสอบว่าวันนี้ควร scrape หรือไม่"""
    today = datetime.now()

    # วันที่ 1 และ 16 ต้อง scrape เสมอ
    if today.day in [1, 16]:
        return True, "lottery_day"

    # วันอื่นๆ → เช็คว่ามีข้อมูลงวดปัจจุบันแล้วหรือไม่
    try:
        response = requests.get(f"{API_BASE_URL}/cron/status", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if not data.get("current_data_exists", True):
                return True, "missing_data"

        return False, "data_exists"

    except Exception as e:
        logging.error(f"Error checking status: {e}")
        return False, "error"

def scrape_current_lottery():
    """เรียก API เพื่อ scrape งวดปัจจุบัน"""
    try:
        logging.info("🔄 เริ่มต้น scrape ข้อมูลหวยงวดปัจจุบัน...")

        response = requests.post(
            f"{API_BASE_URL}/cron/scrape-current",
            timeout=120  # เพิ่ม timeout เพราะ scraping ใช้เวลานาน
        )

        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "unknown")
            date = result.get("date", "")
            total_prizes = result.get("total_prizes", 0)
            message = result.get("message", "")

            if status == "already_exists":
                logging.info(f"✅ ข้อมูลงวด {date} มีอยู่แล้ว ({total_prizes} รางวัล)")
                return True, message

            elif status == "success":
                logging.info(f"🎉 Scrape สำเร็จ! งวด {date} ได้ข้อมูล {total_prizes} รางวัล")
                return True, message

            elif status == "partial_success":
                logging.warning(f"⚠️ Scrape บางส่วน งวด {date} ได้ {total_prizes} รางวัล")
                return False, message

            elif status == "failed":
                logging.error(f"❌ Scrape ไม่สำเร็จ งวด {date}: {message}")
                return False, message

            else:
                logging.error(f"❓ สถานะไม่ทราบ: {status}")
                return False, message

        else:
            error_msg = f"HTTP Error {response.status_code}: {response.text}"
            logging.error(f"❌ API Error: {error_msg}")
            return False, error_msg

    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        logging.error(f"❌ เกิดข้อผิดพลาด: {error_msg}")
        return False, error_msg

def send_notification(success, message, reason=""):
    """ส่งการแจ้งเตือน (อนาคตอาจเพิ่ม LINE Notify หรือ Email)"""
    status_emoji = "✅" if success else "❌"
    log_message = f"{status_emoji} Lottery Cron: {message}"

    if reason:
        log_message += f" (Reason: {reason})"

    logging.info(log_message)

    # TODO: เพิ่มการส่ง LINE Notify หรือ Email ในอนาคต
    # send_line_notify(log_message)
    # send_email_notification(log_message)

def main():
    """Main cron function"""
    try:
        now = datetime.now()
        logging.info(f"🚀 เริ่มต้น Lottery Cron Job - {now.strftime('%Y-%m-%d %H:%M:%S')}")

        # ตรวจสอบว่าควร scrape หรือไม่
        should_scrape, reason = should_scrape_today()

        if not should_scrape:
            logging.info(f"⏭️ ไม่ต้อง scrape วันนี้ - {reason}")
            send_notification(True, f"ไม่ต้อง scrape วันนี้", reason)
            return

        logging.info(f"🎯 ต้อง scrape วันนี้ - {reason}")

        # เริ่ม scrape
        success, message = scrape_current_lottery()

        # ส่งการแจ้งเตือน
        send_notification(success, message, reason)

        if success:
            logging.info("🎉 Cron job เสร็จสิ้น - สำเร็จ")
        else:
            logging.error("💔 Cron job เสร็จสิ้น - ไม่สำเร็จ")

    except Exception as e:
        error_msg = f"Cron job failed: {str(e)}"
        logging.error(f"💥 {error_msg}")
        send_notification(False, error_msg, "exception")

if __name__ == "__main__":
    main()