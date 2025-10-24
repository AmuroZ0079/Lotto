from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, TABLE_NAME
import logging

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LotteryDatabase:
    def __init__(self):
        """เริ่มต้นการเชื่อมต่อ Supabase"""
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("เชื่อมต่อ Supabase สำเร็จ")
        except Exception as e:
            logger.error(f"ไม่สามารถเชื่อมต่อ Supabase ได้: {e}")
            raise

    def create_table_if_not_exists(self):
        """สร้างตารางหากยังไม่มี"""
        try:
            # สร้างตาราง lottery_results
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                draw_date DATE NOT NULL UNIQUE,
                draw_number VARCHAR(20),
                first_prize VARCHAR(6),
                second_prize_1 VARCHAR(6),
                second_prize_2 VARCHAR(6),
                third_prize_1 VARCHAR(6),
                third_prize_2 VARCHAR(6),
                third_prize_3 VARCHAR(6),
                fourth_prize_1 VARCHAR(6),
                fourth_prize_2 VARCHAR(6),
                fourth_prize_3 VARCHAR(6),
                fourth_prize_4 VARCHAR(6),
                fifth_prize_1 VARCHAR(6),
                fifth_prize_2 VARCHAR(6),
                fifth_prize_3 VARCHAR(6),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            
            -- สร้าง index สำหรับการค้นหา
            CREATE INDEX IF NOT EXISTS idx_lottery_draw_date ON {TABLE_NAME}(draw_date);
            CREATE INDEX IF NOT EXISTS idx_lottery_created_at ON {TABLE_NAME}(created_at);
            """
            
            result = self.supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            logger.info("สร้างตารางและ index สำเร็จ")
            return True
        except Exception as e:
            logger.error(f"ไม่สามารถสร้างตารางได้: {e}")
            return False

    def save_lottery_result(self, lottery_data):
        """บันทึกผลลอตเตอรี่ลงฐานข้อมูล"""
        try:
            # ตรวจสอบว่ามีข้อมูลในวันที่นี้แล้วหรือไม่
            existing = self.supabase.table(TABLE_NAME).select("*").eq("draw_date", lottery_data['draw_date']).execute()
            
            if existing.data:
                # อัปเดตข้อมูลที่มีอยู่
                result = self.supabase.table(TABLE_NAME).update(lottery_data).eq("draw_date", lottery_data['draw_date']).execute()
                logger.info(f"อัปเดตผลลอตเตอรี่วันที่ {lottery_data['draw_date']} สำเร็จ")
            else:
                # เพิ่มข้อมูลใหม่
                result = self.supabase.table(TABLE_NAME).insert(lottery_data).execute()
                logger.info(f"บันทึกผลลอตเตอรี่วันที่ {lottery_data['draw_date']} สำเร็จ")
            
            return True
        except Exception as e:
            logger.error(f"ไม่สามารถบันทึกข้อมูลได้: {e}")
            return False

    def get_latest_result(self):
        """ดึงผลลอตเตอรี่ล่าสุด"""
        try:
            result = self.supabase.table(TABLE_NAME).select("*").order("draw_date", desc=True).limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลได้: {e}")
            return None

    def get_result_by_date(self, date):
        """ดึงผลลอตเตอรี่ตามวันที่"""
        try:
            result = self.supabase.table(TABLE_NAME).select("*").eq("draw_date", date).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลได้: {e}")
            return None

    def get_all_results(self, limit=10):
        """ดึงผลลอตเตอรี่ทั้งหมด (จำกัดจำนวน)"""
        try:
            result = self.supabase.table(TABLE_NAME).select("*").order("draw_date", desc=True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลได้: {e}")
            return []

    def delete_old_results(self, days=365):
        """ลบข้อมูลเก่า (มากกว่า days วัน)"""
        try:
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            result = self.supabase.table(TABLE_NAME).delete().lt("draw_date", cutoff_date).execute()
            logger.info(f"ลบข้อมูลเก่ากว่า {days} วันสำเร็จ")
            return True
        except Exception as e:
            logger.error(f"ไม่สามารถลบข้อมูลเก่าได้: {e}")
            return False

    def get_statistics(self):
        """ดึงสถิติข้อมูล"""
        try:
            # นับจำนวนข้อมูลทั้งหมด
            total_count = self.supabase.table(TABLE_NAME).select("id", count="exact").execute()
            
            # ข้อมูลล่าสุด
            latest = self.get_latest_result()
            
            return {
                'total_records': total_count.count if total_count.count else 0,
                'latest_draw_date': latest['draw_date'] if latest else None,
                'latest_draw_number': latest['draw_number'] if latest else None
            }
        except Exception as e:
            logger.error(f"ไม่สามารถดึงสถิติได้: {e}")
            return None
