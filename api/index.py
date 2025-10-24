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
        """Handle GET requests"""
        try:
            logger.info("เริ่มรันการดึงข้อมูลผลลอตเตอรี่")
            
            # รันการ scraping
            scraper = LotteryScraper()
            success = scraper.run_scraping()
            
            if success:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "การดึงข้อมูลผลลอตเตอรี่สำเร็จ",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                logger.info("การดึงข้อมูลสำเร็จ")
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "error",
                    "message": "การดึงข้อมูลผลลอตเตอรี่ล้มเหลว",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                logger.error("การดึงข้อมูลล้มเหลว")
                
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาด: {e}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "error",
                "message": f"เกิดข้อผิดพลาด: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests"""
        self.do_GET()
