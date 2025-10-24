from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.schemas import (
    LotteryCheckRequest,
    LotteryCheckResponse,
    LotteryDrawData,
    HealthResponse
)
from services.lottery_service import LotteryService

# Create router
router = APIRouter()

# Initialize lottery service (ใช้ logic เดิมที่ copy มาแล้ว)
lottery_service = LotteryService()


@router.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Thai Lottery API with FastAPI",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "check_lottery": "POST /lottery/check",
            "get_lottery": "GET /lottery/{draw_date}",
            "health": "GET /health"
        }
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="lottery-api"
    )


@router.get("/lottery/{draw_date}", tags=["Lottery"])
async def get_lottery_data(draw_date: str):
    """Get lottery data for specific date"""
    try:
        # Validate date format
        try:
            date_obj = datetime.strptime(draw_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD"
            )

        # Validate lottery date (must be 1st or 16th)
        if date_obj.day not in [1, 16]:
            raise HTTPException(
                status_code=400,
                detail=f"หวยออกเฉพาะวันที่ 1 และ 16 ของทุกเดือน ไม่ใช่วันที่ {date_obj.day}"
            )

        # Try to get from database first
        existing_data = lottery_service.get_from_database(draw_date)
        if existing_data:
            return existing_data

        # If not in database, scrape from website
        lottery_data = lottery_service.get_lottery_by_date(draw_date)
        if lottery_data:
            # Save to database
            lottery_service.save_to_database(lottery_data)
            return lottery_data
        else:
            raise HTTPException(
                status_code=404,
                detail="ไม่พบข้อมูลหวยสำหรับวันที่ที่ระบุ"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )


@router.post("/lottery/check", response_model=LotteryCheckResponse, tags=["Lottery"])
async def check_lottery_number(request: LotteryCheckRequest):
    """Check if a 6-digit number won any prizes"""
    try:
        # Check the number using the lottery service
        result = lottery_service.check_number_complete(request.number, request.draw_date)

        # Check for errors in the result
        if "เกิดข้อผิดพลาด" in result.get("message", ""):
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )

        return LotteryCheckResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"เกิดข้อผิดพลาดในการตรวจสอบเลข: {str(e)}"
        )