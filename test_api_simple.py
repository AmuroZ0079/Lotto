#!/usr/bin/env python3
"""
ไฟล์ทดสอบ API แบบง่าย
"""

def test_lottery_api():
    """ทดสอบ Lottery API"""
    print("=" * 60)
    print("ทดสอบ Lottery API")
    print("=" * 60)
    
    try:
        from api.lottery import LotteryAPI
        
        # สร้าง API instance
        api = LotteryAPI()
        
        # ทดสอบวันที่ 16 ต.ค. 2568
        print("กำลังทดสอบวันที่: 2025-10-16")
        result = api.get_lottery_by_date("2025-10-16")
        
        if result:
            print("SUCCESS: ได้ข้อมูลลอตเตอรี่")
            print(f"วันที่: {result['draw_date']}")
            print(f"งวด: {result['draw_number']}")
            print(f"รางวัลที่ 1: {result['first_prize']}")
            print(f"รางวัลที่ 2: {result['second_prize_1']}, {result['second_prize_2']}")
            print(f"รางวัลที่ 3: {result['third_prize_1']}, {result['third_prize_2']}")
            print(f"เลขท้าย 2 ตัว: {result['fourth_prize_1']}")
            
            # บันทึกลงฐานข้อมูล
            if api.save_to_database(result):
                print("SUCCESS: บันทึกลงฐานข้อมูลสำเร็จ")
            else:
                print("ERROR: ไม่สามารถบันทึกลงฐานข้อมูลได้")
        else:
            print("ERROR: ไม่สามารถดึงข้อมูลได้")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_lottery_api()
