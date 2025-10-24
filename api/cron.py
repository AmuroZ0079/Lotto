from http.server import BaseHTTPRequestHandler
import json
from main import LotteryScraper
import logging
from datetime import datetime

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for cron job"""
        try:
            logger.info("เริ่มรัน cron job")
            
            # รันการ scraping
            scraper = LotteryScraper()
            success = scraper.run_scraping()
            
            if success:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "การดึงข้อมูลผลลอตเตอรี่สำเร็จ",
                    "timestamp": str(datetime.now())
                }
                
                self.wfile.write(json.dumps(response).encode())
                logger.info("Cron job สำเร็จ")
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "status": "error",
                    "message": "การดึงข้อมูลผลลอตเตอรี่ล้มเหลว",
                    "timestamp": str(datetime.now())
                }
                
                self.wfile.write(json.dumps(response).encode())
                logger.error("Cron job ล้มเหลว")
                
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดใน cron job: {e}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "error",
                "message": f"เกิดข้อผิดพลาด: {str(e)}",
                "timestamp": str(datetime.now())
            }
            
            self.wfile.write(json.dumps(response).encode())
