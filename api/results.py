from http.server import BaseHTTPRequestHandler
import json
from database import LotteryDatabase
import logging
from datetime import datetime

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - ดึงผลลอตเตอรี่"""
        try:
            db = LotteryDatabase()
            
            # ดึงผลล่าสุด
            latest_result = db.get_latest_result()
            
            if latest_result:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "data": latest_result,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                logger.info("ดึงข้อมูลผลลอตเตอรี่สำเร็จ")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "error",
                    "message": "ไม่พบข้อมูลผลลอตเตอรี่",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                logger.warning("ไม่พบข้อมูลผลลอตเตอรี่")
                
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
