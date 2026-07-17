# 🧾 Slip Verify Bot ✨

บอท Discord สุดล้ำสำหรับ **ตรวจสอบสลิปโอนเงินอัตโนมัติ** รองรับทั้งสลิปธนาคาร (Bank Slip) และสลิป TrueMoney Wallet ทำงานรวดเร็วด้วย **SlipOK API v1.13** พร้อมระบบป้องกันสลิปซ้ำ (Duplicate Detection) และฟีเจอร์ตอบกลับข้อมูลบัญชีอัตโนมัติ

---

## 🌟 ฟีเจอร์หลัก (Features)

- 🔍 **อ่าน QR Code จากสลิปธนาคาร:** ดึงข้อมูล QR Payload เพื่อส่งไปตรวจสอบผ่าน SlipOK
- 🧡 **รองรับ TrueMoney Wallet และรูปภาพสลิป:** ตรวจสอบสลิปได้โดยตรงผ่านการอ่าน QR หรืออัปโหลดรูปภาพ
- 🛡️ **ป้องกันสลิปซ้ำ:** ตรวจสอบกับฐานข้อมูล SlipOK ว่าสลิปนี้เคยถูกใช้งานไปแล้วหรือไม่ (`code 1012`) เพื่อป้องกันการทุจริต
- 🏦 **แจ้งเลขบัญชีอัตโนมัติ (`/bank`):** มีระบบดักจับคำเช่น *"ขอเลขบัญชี"*, *"โอนเงินทางไหน"* เพื่อแจ้งเตือน และมี Slash Command `/bank` ส่งรูป QR Code ช่องทางโอนเงินให้ลูกค้าทันที
- 🤖 **ทำงานอัตโนมัติฉลาดล้ำ:** บอทจะเช็คเฉพาะรูปภาพที่มีแนวโน้มเป็นสลิป หากเป็นรูปภาพทั่วไป (เช่น รูปมีมหรือรูปถ่าย) จะข้ามไปอัตโนมัติไม่แจ้งเตือนกวนใจ

---

## ⚙️ สิ่งที่ต้องเตรียม (Prerequisites)

1. **Python 3.8+** (แนะนำ 3.10 ขึ้นไป)
2. **Discord Bot Token** (สร้างได้ที่ [Discord Developer Portal](https://discord.com/developers/applications))
3. **SlipOK API Key & Branch ID** (จำเป็นสำหรับการตรวจสอบสลิปของแท้จาก [SlipOK Dashboard](https://www.slipok.com))

---

## 🛠️ วิธีการติดตั้ง (Installation)

1. **โคลนโปรเจกต์ลงเครื่อง:**
   ```bash
   git clone <repository-url>
   cd slip-verify-bot
   ```

2. **สร้าง Virtual Environment (แนะนำ):**
   ```bash
   python -m venv venv
   # สำหรับ Windows
   venv\Scripts\activate
   # สำหรับ Mac/Linux
   source venv/bin/activate
   ```

3. **ติดตั้งไลบรารีที่จำเป็น:**
   ```bash
   pip install -r requirements.txt
   ```
   > ⚠️ **หมายเหตุสำหรับ Windows:** โมดูล `pyzbar` (ใช้อ่าน QR) อาจต้องการตัวอ่านในระบบ หากมีปัญหาติดตั้งให้อ่านวิธีแก้ที่ [pyzbar PyPI](https://pypi.org/project/pyzbar/)

4. **ตั้งค่า Environment Variables (`.env`):**
   - คัดลอกไฟล์ `.env.example` เป็น `.env` (หรือสร้างไฟล์ `.env` ใหม่)
   - ใส่ข้อมูล Token และ API Key ของคุณ:
     ```env
     DISCORD_TOKEN=ใส่_Token_ของบอทที่นี่
     SLIPOK_API_KEY=ใส่_API_Key_ที่นี่
     SLIPOK_BRANCH_ID=71503
     ```

---

## 🚀 วิธีการรันบอท (Running the Bot)

เมื่อติดตั้งและตั้งค่า `.env` เสร็จแล้ว สั่งรันบอทด้วยคำสั่ง:

```bash
python main.py
```

หากบอททำงานสำเร็จ คุณจะเห็นข้อความใน Terminal:
> `Bot is ready and Cogs are loaded.`

---

## 🧪 การทดสอบระบบ (Running Tests)

โปรเจกต์นี้มี Unit Tests (TDD) ครอบคลุมการทำงานหลัก สามารถรันตรวจสอบความถูกต้องได้ด้วยคำสั่ง:

```bash
pytest
```
*หรือหากต้องการดู Test Coverage:*
```bash
pytest --cov=.
```

---

## 📂 โครงสร้างโปรเจกต์ (Project Structure)

```text
slip-verify-bot/
├── main.py                # ไฟล์หลัก รันบอทและโหลด Cogs
├── cogs/
│   ├── slip_verifier.py   # ระบบตรวจสอบสลิปและแจ้งเตือนสลิปซ้ำ
│   └── bank_info.py       # ระบบตอบกลับข้อมูลธนาคารและ /bank
├── utils/
│   ├── slipok.py          # ตัวเชื่อมต่อ API กับ SlipOK
│   └── qr_scanner.py      # ตัวอ่าน QR Code จากรูปภาพ
├── assets/
│   └── bank_qr.jpg        # รูปภาพ QR Code บัญชีธนาคาร (Local Storage)
├── tests/                 # โฟลเดอร์เก็บไฟล์ Unit Tests
├── .env                   # ไฟล์เก็บ Token/API Keys (ต้องสร้างเอง)
├── requirements.txt       # รายชื่อไลบรารีที่ใช้งาน
└── README.md              # คู่มือที่คุณกำลังอ่านอยู่!
```

---

*พัฒนาและดูแลโดย [son11930]*
