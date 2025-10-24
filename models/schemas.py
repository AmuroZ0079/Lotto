from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class LotteryCheckRequest(BaseModel):
    number: str = Field(..., min_length=6, max_length=6, description="6-digit lottery number")
    draw_date: str = Field(..., description="Draw date in YYYY-MM-DD format (must be 1st or 16th)")

    @validator('number')
    def validate_number(cls, v):
        if not v.isdigit():
            raise ValueError('เลขหวยต้องเป็นตัวเลขเท่านั้น')
        return v

    @validator('draw_date')
    def validate_draw_date(cls, v):
        try:
            date_obj = datetime.strptime(v, '%Y-%m-%d')
            if date_obj.day not in [1, 16]:
                raise ValueError(f'หวยออกเฉพาะวันที่ 1 และ 16 ของทุกเดือน ไม่ใช่วันที่ {date_obj.day}')
            return v
        except ValueError as e:
            if 'หวยออกเฉพาะ' in str(e):
                raise e
            raise ValueError('รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD')


class LotteryResult(BaseModel):
    match_type: str
    matched_digits: str
    prize_type: str
    prize_name: str
    amount: int
    position: int


class LotteryCheckResponse(BaseModel):
    number: str
    draw_date: str
    draw_number: Optional[str] = None
    total_matches: Optional[int] = 0
    results: List[LotteryResult] = []
    message: str


class LotteryDrawData(BaseModel):
    draw_date: str
    draw_number: str
    first_prize: str
    second_prize_1: str
    second_prize_2: str
    third_prize_1: str
    third_prize_2: str
    fourth_prize_1: str


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str