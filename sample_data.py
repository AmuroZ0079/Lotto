"""
ไฟล์ข้อมูลตัวอย่างสำหรับทดสอบ
ใช้เมื่อไม่สามารถ scrap จากเว็บไซต์จริงได้
"""

def get_sample_lottery_data():
    """ข้อมูลตัวอย่างผลลอตเตอรี่"""
    return {
        'draw_date': '2024-01-16',
        'draw_number': '1/2567',
        'first_prize': '123456',
        'second_prize_1': '234567',
        'second_prize_2': '345678',
        'third_prize_1': '456789',
        'third_prize_2': '567890',
        'third_prize_3': '678901',
        'fourth_prize_1': '789012',
        'fourth_prize_2': '890123',
        'fourth_prize_3': '901234',
        'fourth_prize_4': '012345',
        'fifth_prize_1': '111111',
        'fifth_prize_2': '222222',
        'fifth_prize_3': '333333'
    }

def get_sample_html():
    """HTML ตัวอย่างสำหรับทดสอบ"""
    return """
    <html>
    <body>
        <div class="lottery-result">
            <h2>ผลลอตเตอรี่ งวดที่ 1/2567</h2>
            <p>วันที่ออก: 16/01/2024</p>
            
            <div class="prize-section">
                <h3>รางวัลที่ 1</h3>
                <span class="prize-number">123456</span>
            </div>
            
            <div class="prize-section">
                <h3>รางวัลที่ 2</h3>
                <span class="prize-number">234567</span>
                <span class="prize-number">345678</span>
            </div>
            
            <div class="prize-section">
                <h3>รางวัลที่ 3</h3>
                <span class="prize-number">456789</span>
                <span class="prize-number">567890</span>
                <span class="prize-number">678901</span>
            </div>
            
            <div class="prize-section">
                <h3>รางวัลที่ 4</h3>
                <span class="prize-number">789012</span>
                <span class="prize-number">890123</span>
                <span class="prize-number">901234</span>
                <span class="prize-number">012345</span>
            </div>
            
            <div class="prize-section">
                <h3>รางวัลที่ 5</h3>
                <span class="prize-number">111111</span>
                <span class="prize-number">222222</span>
                <span class="prize-number">333333</span>
            </div>
        </div>
    </body>
    </html>
    """
