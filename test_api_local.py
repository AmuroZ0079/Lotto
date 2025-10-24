#!/usr/bin/env python3
"""
ไฟล์ทดสอบ API ในเครื่อง
"""

import requests
import json
from datetime import datetime

def test_api_local():
    """ทดสอบ API ในเครื่อง"""
    print("=" * 60)
    print("ทดสอบ API ในเครื่อง")
    print("=" * 60)
    
    # URL สำหรับทดสอบ
    base_url = "http://localhost:8000"
    
    # ข้อมูลทดสอบ
    test_dates = [
        "2025-10-16",  # งวด 16 ต.ค. 2568
        "2024-11-01",  # งวด 1 พ.ย. 2567
        "2024-10-16"   # งวด 16 ต.ค. 2567
    ]
    
    for draw_date in test_dates:
        print(f"\n--- ทดสอบวันที่: {draw_date} ---")
        
        try:
            # สร้าง URL
            url = f"{base_url}/api/lottery?draw_date={draw_date}"
            print(f"URL: {url}")
            
            # ส่ง request
            response = requests.get(url, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("SUCCESS: ได้ข้อมูลลอตเตอรี่")
                print(f"วันที่: {data['data']['draw_date']}")
                print(f"งวด: {data['data']['draw_number']}")
                print(f"รางวัลที่ 1: {data['data']['first_prize']}")
                print(f"รางวัลที่ 2: {data['data']['second_prize_1']}, {data['data']['second_prize_2']}")
                print(f"รางวัลที่ 3: {data['data']['third_prize_1']}, {data['data']['third_prize_2']}")
            else:
                print(f"ERROR: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"ERROR: {e}")

def test_api_without_server():
    """ทดสอบ API โดยไม่ต้องมี server"""
    print("\n" + "=" * 60)
    print("ทดสอบ API โดยตรง")
    print("=" * 60)
    
    try:
        from api.lottery import LotteryAPI
        
        api = LotteryAPI()
        
        # ทดสอบวันที่ 16 ต.ค. 2568
        result = api.get_lottery_by_date("2025-10-16")
        
        if result:
            print("SUCCESS: ได้ข้อมูลลอตเตอรี่")
            print(f"วันที่: {result['draw_date']}")
            print(f"งวด: {result['draw_number']}")
            print(f"รางวัลที่ 1: {result['first_prize']}")
            print(f"รางวัลที่ 2: {result['result']['second_prize_1']}, {result['second_prize_2']}")
            print(f"รางวัลที่ 3: {result['third_prize_1']}, {result['third_prize_2']}")
        else:
            print("ERROR: ไม่สามารถดึงข้อมูลได้")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("เลือกการทดสอบ:")
    print("1. ทดสอบ API ในเครื่อง (ต้องมี server)")
    print("2. ทดสอบ API โดยตรง")
    
    choice = input("\nเลือก (1 หรือ 2): ").strip()
    
    if choice == "1":
        test_api_local()
    elif choice == "2":
        test_api_without_server()
    else:
        print("ตัวเลือกไม่ถูกต้อง")
