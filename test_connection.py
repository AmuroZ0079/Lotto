#!/usr/bin/env python3
"""
ไฟล์ทดสอบการเชื่อมต่อ Supabase
"""

import os
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

def test_supabase_connection():
    """ทดสอบการเชื่อมต่อ Supabase"""
    print("=" * 50)
    print("ทดสอบการเชื่อมต่อ Supabase")
    print("=" * 50)
    
    try:
        # ตรวจสอบ environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ ไม่พบ SUPABASE_URL หรือ SUPABASE_KEY")
            print("กรุณาตั้งค่าในไฟล์ .env")
            return False
        
        print(f"✅ SUPABASE_URL: {supabase_url[:20]}...")
        print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...")
        
        # ทดสอบการเชื่อมต่อ
        from supabase import create_client, Client
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ทดสอบการดึงข้อมูล
        result = supabase.table('lottery_results').select('*').limit(1).execute()
        
        print("✅ เชื่อมต่อ Supabase สำเร็จ!")
        print(f"✅ พบข้อมูล: {len(result.data)} รายการ")
        
        return True
        
    except ImportError:
        print("❌ ไม่พบโมดูล supabase")
        print("กรุณาติดตั้งด้วย: pip install supabase")
        return False
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
