# LINE Bot Setup Guide

## 1. LINE Developers Console Setup

1. ไปที่ [LINE Developers Console](https://developers.line.biz/)
2. Login ด้วย LINE account
3. สร้าง New Provider (ถ้ายังไม่มี)
4. สร้าง New Channel → Messaging API

## 2. Get LINE Credentials

จาก LINE Developers Console ดึงข้อมูลนี้:

- **Channel Secret** - จาก Basic Settings tab
- **Channel Access Token** - จาก Messaging API tab (Generate ใหม่ถ้าจำเป็น)

## 3. Set Environment Variables

### ใน Vercel Dashboard:
Settings → Environment Variables → Add:

```
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
LINE_CHANNEL_SECRET=your_channel_secret_here
```

### ใน Local Development (.env):
```
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
LINE_CHANNEL_SECRET=your_channel_secret_here
```

## 4. Set Webhook URL

ใน LINE Developers Console → Messaging API tab:

**Webhook URL:**
```
https://lotto-six-roan.vercel.app/line/webhook
```

**Webhook Settings:**
- Use webhook: **ON**
- Auto-reply messages: **OFF** (เพื่อไม่ให้ขัดแย้งกับ bot)

## 5. LINE Bot Features

### รูปแบบข้อความที่รองรับ:

1. **เลข 6 ตัวเท่านั้น:**
   ```
   123456
   ```

2. **เลข 6 ตัว + วันที่:**
   ```
   123456 2025-07-16
   123456 16/7/68
   123456 16/07/2568
   ```

3. **ใช้คำว่า "ตรวจ":**
   ```
   ตรวจ 123456
   ตรวจ 123456 16/7/68
   ```

### ตัวอย่าง Response:

**กรณีไม่ถูกรางวัล:**
```
🎫 เลข 123456
📅 งวด 16/2568 (2025-07-16)

💔 ไม่ถูกรางวัล

ลองใหม่งวดหน้านะคะ! 🍀
```

**กรณีถูกรางวัล:**
```
🎊 เลข 245324
📅 งวด 16/2568 (2025-07-16)

🏆 ถูกรางวัล 1 รางวัล!

🎁 รางวัลที่ 1
   เลขที่ถูก: 245324
   รางวัล: 6,000,000 บาท

💰 รวมทั้งหมด: 6,000,000 บาท

🎉 ยินดีด้วยค่ะ!
```

## 6. Testing

1. Add LINE Bot เป็น friend ด้วย QR Code จาก Messaging API tab
2. ส่งข้อความทดสอบ เช่น "245324 2025-07-16"
3. Bot ควรตอบกลับด้วยผลการตรวจหวย

## 7. API Endpoints

**Webhook Endpoint:**
```
POST https://lotto-six-roan.vercel.app/line/webhook
```

**หมายเหตุ:** Endpoint นี้ถูกเรียกโดย LINE Platform เท่านั้น ไม่ต้องเรียกเอง

## 8. Troubleshooting

### Bot ไม่ตอบ:
1. เช็ค Environment Variables ใน Vercel
2. เช็ค Webhook URL ใน LINE Console
3. ดู Runtime Logs ใน Vercel

### Error Messages:
- "LINE Bot not configured" = ไม่มี Environment Variables
- "Invalid signature" = Channel Secret ผิด
- "เกิดข้อผิดพลาด" = ปัญหาการเชื่อมต่อ Lottery API

## 9. Security Notes

- ไม่แชร์ Channel Secret และ Access Token
- ใช้ HTTPS เท่านั้น
- LINE จะ verify signature ทุกครั้ง