import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class DatabaseService:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self._connect()

    def _connect(self):
        """เชื่อมต่อกับ Supabase"""
        try:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")

            if not url or not key:
                print("⚠️ Supabase credentials not found in environment variables")
                return

            self.supabase = create_client(url, key)
            print("✅ เชื่อมต่อ Supabase สำเร็จ")

        except Exception as e:
            print(f"❌ ไม่สามารถเชื่อมต่อ Supabase ได้: {e}")

    def get_lottery_draw(self, draw_date: str) -> Optional[Dict[str, Any]]:
        """ดึงข้อมูลงวดหวยจากฐานข้อมูล"""
        if not self.supabase:
            return None

        try:
            result = (self.supabase.table('lottery_draws')
                     .select("id, draw_number")
                     .eq("draw_date", draw_date)
                     .execute())

            return result.data[0] if result.data else None

        except Exception as e:
            print(f"ไม่สามารถดึงข้อมูลงวดจากฐานข้อมูลได้: {e}")
            return None

    def save_lottery_draw(self, draw_date: str, draw_number: str) -> Optional[int]:
        """บันทึกข้อมูลงวดหวยลงฐานข้อมูล"""
        if not self.supabase:
            return None

        try:
            # ตรวจสอบว่ามีงวดนี้แล้วหรือยัง
            existing = self.get_lottery_draw(draw_date)
            if existing:
                return existing['id']

            # บันทึกงวดใหม่
            result = (self.supabase.table('lottery_draws')
                     .insert({
                         "draw_date": draw_date,
                         "draw_number": draw_number,
                         "status": "active"
                     })
                     .execute())

            return result.data[0]['id'] if result.data else None

        except Exception as e:
            print(f"ไม่สามารถบันทึกข้อมูลงวดได้: {e}")
            return None

    def save_lottery_prizes(self, draw_id: int, prizes: List[Dict[str, Any]]) -> bool:
        """บันทึกข้อมูลรางวัลลงฐานข้อมูล"""
        if not self.supabase:
            return False

        try:
            # ลบข้อมูลเก่าของงวดนี้ก่อน (ถ้ามี)
            self.supabase.table('lottery_prizes').delete().eq('draw_id', draw_id).execute()

            # บันทึกข้อมูลใหม่
            if prizes:
                self.supabase.table('lottery_prizes').insert(prizes).execute()

            print(f"✅ บันทึกรางวัล {len(prizes)} รายการสำเร็จ")
            return True

        except Exception as e:
            print(f"ไม่สามารถบันทึกรางวัลได้: {e}")
            return False

    def search_lottery_prizes(self, number: str, draw_date: str) -> List[Dict[str, Any]]:
        """ค้นหารางวัลที่ถูกใจเลขที่กำหนด"""
        if not self.supabase:
            return []

        try:
            result = (self.supabase.table('lottery_prizes')
                     .select('prize_type, amount, position, lottery_draws!inner(draw_date, draw_number)')
                     .eq('prize_number', number)
                     .eq('lottery_draws.draw_date', draw_date)
                     .execute())

            return result.data if result.data else []

        except Exception as e:
            print(f"ไม่สามารถค้นหารางวัลได้: {e}")
            return []

    def get_lottery_data_from_db(self, draw_date: str) -> Optional[Dict[str, Any]]:
        """ดึงข้อมูลหวยแบบเก่าจากฐานข้อมูล (backward compatibility)"""
        if not self.supabase:
            return None

        try:
            result = (self.supabase.table('lottery_results')
                     .select("*")
                     .eq("draw_date", draw_date)
                     .execute())

            return result.data[0] if result.data else None

        except Exception as e:
            print(f"ไม่สามารถดึงข้อมูลจากฐานข้อมูลได้: {e}")
            return None