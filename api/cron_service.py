from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import requests
import json
import os
from typing import Dict, Any

router = APIRouter()

class LotteryCronService:
    def __init__(self):
        self.base_url = "https://lotto-six-roan.vercel.app"
        # หรือใช้ localhost สำหรับ development
        # self.base_url = "http://127.0.0.1:8000"

    def get_next_lottery_date(self) -> str:
        """คำนวณวันที่หวยออกถัดไป (1 หรือ 16)"""
        today = datetime.now()

        if today.day < 1:
            return f"{today.year}-{today.month:02d}-01"
        elif today.day < 16:
            return f"{today.year}-{today.month:02d}-16"
        else:
            # ไปเดือนถัดไป วันที่ 1
            next_month = today + timedelta(days=32)
            next_month = next_month.replace(day=1)
            return f"{next_month.year}-{next_month.month:02d}-01"

    def get_current_lottery_date(self) -> str:
        """วันที่หวยงวดปัจจุบัน"""
        today = datetime.now()

        if today.day >= 16:
            return f"{today.year}-{today.month:02d}-16"
        else:
            return f"{today.year}-{today.month:02d}-01"

    def check_lottery_data_exists(self, date: str) -> Dict[str, Any]:
        """เช็คว่ามีข้อมูลหวยงวดนั้นแล้วหรือไม่"""
        try:
            response = requests.get(f"{self.base_url}/lottery/{date}", timeout=30)

            if response.status_code == 200:
                data = response.json()
                # เช็คว่ามีข้อมูลครบถ้วน (มีรางวัลมากกว่า 100 รายการ)
                total_prizes = (
                    len(data.get('second_prizes', [])) +
                    len(data.get('third_prizes', [])) +
                    len(data.get('fourth_prizes', [])) +
                    len(data.get('fifth_prizes', [])) +
                    (1 if data.get('first_prize') else 0) +
                    (1 if data.get('fourth_prize_1') else 0) +
                    len(data.get('nearby_prizes', []))
                )

                return {
                    "exists": total_prizes > 100,  # ถือว่าครบถ้วนถ้ามีมากกว่า 100 รางวัล
                    "total_prizes": total_prizes,
                    "data": data
                }
            else:
                return {"exists": False, "total_prizes": 0}

        except Exception as e:
            print(f"Error checking lottery data: {e}")
            return {"exists": False, "total_prizes": 0, "error": str(e)}

    def scrape_lottery_data(self, date: str) -> Dict[str, Any]:
        """เรียก API เพื่อ scrape ข้อมูลหวย"""
        try:
            # ใช้ check API เพื่อ trigger การ scrape
            response = requests.post(
                f"{self.base_url}/lottery/check",
                json={"number": "000000", "draw_date": date},
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": "draw_number" in result and result["draw_number"] is not None,
                    "message": result.get("message", ""),
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error scraping: {str(e)}"
            }

cron_service = LotteryCronService()

@router.get("/cron/status", tags=["Cron"])
async def cron_status():
    """เช็คสถานะ cron job"""
    current_date = cron_service.get_current_lottery_date()
    next_date = cron_service.get_next_lottery_date()

    current_exists = cron_service.check_lottery_data_exists(current_date)

    return {
        "current_lottery_date": current_date,
        "next_lottery_date": next_date,
        "current_data_exists": current_exists["exists"],
        "current_total_prizes": current_exists.get("total_prizes", 0),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/cron/scrape-current", tags=["Cron"])
async def scrape_current_lottery():
    """ใช้สำหรับ cron job - scrape งวดปัจจุบัน"""
    current_date = cron_service.get_current_lottery_date()

    # เช็คว่ามีข้อมูลแล้วหรือไม่
    exists_check = cron_service.check_lottery_data_exists(current_date)

    if exists_check["exists"]:
        return {
            "status": "already_exists",
            "date": current_date,
            "total_prizes": exists_check["total_prizes"],
            "message": f"ข้อมูลงวด {current_date} มีอยู่แล้ว ({exists_check['total_prizes']} รางวัล)"
        }

    # ยังไม่มีข้อมูล ให้ scrape
    print(f"🔄 เริ่ม scrape ข้อมูลงวด {current_date}")
    scrape_result = cron_service.scrape_lottery_data(current_date)

    if scrape_result["success"]:
        # เช็คอีกครั้งว่า scrape สำเร็จจริงหรือไม่
        verification = cron_service.check_lottery_data_exists(current_date)

        return {
            "status": "success" if verification["exists"] else "partial_success",
            "date": current_date,
            "total_prizes": verification.get("total_prizes", 0),
            "message": f"Scrape สำเร็จ! ได้ข้อมูล {verification.get('total_prizes', 0)} รางวัล",
            "scrape_details": scrape_result
        }
    else:
        return {
            "status": "failed",
            "date": current_date,
            "message": f"Scrape ไม่สำเร็จ: {scrape_result['message']}",
            "scrape_details": scrape_result
        }

@router.post("/cron/scrape-date/{date}", tags=["Cron"])
async def scrape_specific_date(date: str):
    """Scrape ข้อมูลงวดวันที่ระบุ"""
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD")

    # เช็คว่ามีข้อมูลแล้วหรือไม่
    exists_check = cron_service.check_lottery_data_exists(date)

    if exists_check["exists"]:
        return {
            "status": "already_exists",
            "date": date,
            "total_prizes": exists_check["total_prizes"],
            "message": f"ข้อมูลงวด {date} มีอยู่แล้ว"
        }

    # Scrape ข้อมูล
    print(f"🔄 เริ่ม scrape ข้อมูลงวด {date}")
    scrape_result = cron_service.scrape_lottery_data(date)

    if scrape_result["success"]:
        verification = cron_service.check_lottery_data_exists(date)
        return {
            "status": "success" if verification["exists"] else "partial_success",
            "date": date,
            "total_prizes": verification.get("total_prizes", 0),
            "message": f"Scrape สำเร็จ! ได้ข้อมูล {verification.get('total_prizes', 0)} รางวัล"
        }
    else:
        return {
            "status": "failed",
            "date": date,
            "message": f"Scrape ไม่สำเร็จ: {scrape_result['message']}"
        }

@router.get("/cron/check-missing", tags=["Cron"])
async def check_missing_dates():
    """เช็คว่ามีงวดไหนยังไม่มีข้อมูลบ้าง (3 เดือนย้อนหลัง)"""
    missing_dates = []

    # เช็ค 3 เดือนย้อนหลัง
    current = datetime.now()

    for month_offset in range(3):
        check_date = current - timedelta(days=month_offset * 30)

        # วันที่ 1 และ 16 ของเดือนนั้น
        for day in [1, 16]:
            lottery_date = f"{check_date.year}-{check_date.month:02d}-{day:02d}"

            # เช็คไม่เกินวันปัจจุบัน
            if datetime.strptime(lottery_date, '%Y-%m-%d').date() <= current.date():
                exists_check = cron_service.check_lottery_data_exists(lottery_date)

                if not exists_check["exists"]:
                    missing_dates.append({
                        "date": lottery_date,
                        "total_prizes": exists_check.get("total_prizes", 0)
                    })

    return {
        "missing_dates": missing_dates,
        "total_missing": len(missing_dates),
        "checked_period": "3 เดือนย้อนหลัง"
    }