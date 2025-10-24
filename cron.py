import schedule
import time
from main import LotteryScraper
import logging
from datetime import datetime

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_lottery_scraping():
    """ฟังก์ชันสำหรับรันการ scraping"""
    try:
        logger.info(f"เริ่มรันการ scraping ณ เวลา {datetime.now()}")
        scraper = LotteryScraper()
        success = scraper.run_scraping()
        
        if success:
            logger.info("การ scraping สำเร็จ")
        else:
            logger.error("การ scraping ล้มเหลว")
            
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาดในการรัน scraping: {e}")

def setup_cron_jobs():
    """ตั้งค่า cron jobs"""
    # ตั้งเวลาให้รันทุกวันที่ 1 และ 16 ของเดือน เวลา 20:00
    schedule.every().month.do(run_lottery_scraping).tag("lottery_scraping")
    
    # หรือใช้ schedule แบบอื่น
    # schedule.every().day.at("20:00").do(run_lottery_scraping)
    
    logger.info("ตั้งค่า cron jobs สำเร็จ")
    logger.info("ระบบจะรันทุกวันที่ 1 และ 16 ของเดือน เวลา 20:00")

def main():
    """ฟังก์ชันหลักสำหรับ cron job"""
    setup_cron_jobs()
    
    logger.info("เริ่มรอการรัน cron jobs...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # ตรวจสอบทุกนาที

if __name__ == "__main__":
    main()
