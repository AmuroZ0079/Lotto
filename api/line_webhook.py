from fastapi import APIRouter, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import re
import requests
import json
from datetime import datetime

# LINE Bot credentials (จะตั้งใน environment variables)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN) if LINE_CHANNEL_ACCESS_TOKEN else None
handler = WebhookHandler(LINE_CHANNEL_SECRET) if LINE_CHANNEL_SECRET else None

router = APIRouter()

@router.post("/webhook", tags=["LINE Bot"])
async def line_webhook(request: Request):
    """LINE Bot webhook endpoint"""
    if not line_bot_api or not handler:
        raise HTTPException(status_code=500, detail="LINE Bot not configured")

    signature = request.headers.get('X-Line-Signature', '')
    body = await request.body()

    try:
        handler.handle(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return {"status": "OK"}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """Handle incoming LINE messages"""
    user_message = event.message.text.strip()
    user_id = event.source.user_id

    # Parse lottery number and date from message
    result = parse_lottery_message(user_message)

    if result["error"]:
        reply_message = result["error"]
    else:
        # Call lottery API
        api_result = check_lottery_number(result["number"], result["date"])
        reply_message = format_lottery_response(api_result)

    # Reply to user
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

def parse_lottery_message(message):
    """Parse lottery number and date from user message"""
    try:
        # รูปแบบที่รองรับ:
        # "123456" - ใช้งวดล่าสุด
        # "123456 2025-07-16" - ระบุวันที่
        # "ตรวจ 123456" - ใช้งวดล่าสุด
        # "ตรวจ 123456 16/7/68" - รูปแบบไทย

        # ลบคำที่ไม่จำเป็น
        clean_message = re.sub(r'(ตรวจ|หวย|เลข)', '', message).strip()

        # หาเลข 6 ตัว
        number_match = re.search(r'\b(\d{6})\b', clean_message)
        if not number_match:
            return {"error": "กรุณาส่งเลข 6 ตัว เช่น: 123456"}

        number = number_match.group(1)

        # หาวันที่
        date = extract_date_from_message(clean_message)

        return {
            "number": number,
            "date": date,
            "error": None
        }

    except Exception as e:
        return {"error": f"รูปแบบข้อความไม่ถูกต้อง: {str(e)}"}

def extract_date_from_message(message):
    """Extract date from message or use latest draw date"""
    # รูปแบบวันที่ที่รองรับ:
    # 2025-07-16, 16/7/68, 16/07/2568

    # ISO format
    iso_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', message)
    if iso_match:
        date_str = iso_match.group(1)
        # Validate that it's 1st or 16th
        day = int(date_str.split('-')[2])
        if day in [1, 16]:
            return date_str

    # Thai format (16/7/68 or 16/07/2568)
    thai_match = re.search(r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b', message)
    if thai_match:
        day, month, year = thai_match.groups()
        day = int(day)
        month = int(month)
        year = int(year)

        # Convert Buddhist year to Christian year
        if year < 100:  # 68 -> 2568 -> 2025
            year = 2500 + year
        if year > 2500:  # 2568 -> 2025
            year = year - 543

        if day in [1, 16]:
            return f"{year:04d}-{month:02d}-{day:02d}"

    # Default to latest draw date
    today = datetime.now()
    if today.day >= 16:
        return f"{today.year}-{today.month:02d}-16"
    else:
        return f"{today.year}-{today.month:02d}-01"

def check_lottery_number(number, date):
    """Call lottery API to check number"""
    try:
        api_url = "https://lotto-six-roan.vercel.app/lottery/check"
        payload = {
            "number": number,
            "draw_date": date
        }

        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()

        return response.json()

    except Exception as e:
        return {
            "number": number,
            "draw_date": date,
            "total_matches": 0,
            "results": [],
            "message": f"เกิดข้อผิดพลาด: {str(e)}"
        }

def format_lottery_response(api_result):
    """Format API response for LINE message"""
    number = api_result.get("number", "")
    date = api_result.get("draw_date", "")
    draw_number = api_result.get("draw_number", "")
    total_matches = api_result.get("total_matches", 0)
    results = api_result.get("results", [])
    message = api_result.get("message", "")

    if "เกิดข้อผิดพลาด" in message:
        return f"❌ {message}"

    if total_matches == 0:
        return f"🎫 เลข {number}\n📅 งวด {draw_number} ({date})\n\n💔 ไม่ถูกรางวัล\n\nลองใหม่งวดหน้านะคะ! 🍀"

    # Format winning results
    response = f"🎊 เลข {number}\n📅 งวด {draw_number} ({date})\n\n🏆 ถูกรางวัล {total_matches} รางวัล!\n\n"

    total_amount = 0
    for result in results:
        prize_name = result.get("prize_name", "")
        amount = result.get("amount", 0)
        matched_digits = result.get("matched_digits", "")

        total_amount += amount
        response += f"🎁 {prize_name}\n"
        response += f"   เลขที่ถูก: {matched_digits}\n"
        response += f"   รางวัล: {amount:,} บาท\n\n"

    response += f"💰 รวมทั้งหมด: {total_amount:,} บาท\n\n🎉 ยินดีด้วยค่ะ!"

    return response