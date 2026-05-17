import discord
from discord.ext import commands
from utils.qr_scanner import scan_qr_from_bytes
from utils.easyslip import EasySlipAPI

class AdminReviewView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, custom_id="approve_slip")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # เพิ่ม Logic เมื่อแอดมินกดยืนยัน (เช่น อัปเดต Database หรือให้ Role)
        await interaction.response.send_message("✅ แอดมินตรวจสอบและอนุมัติสลิปเรียบร้อยแล้ว", ephemeral=False)
        self.stop()

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, custom_id="reject_slip")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # เพิ่ม Logic เมื่อแอดมินปฏิเสธ
        await interaction.response.send_message("❌ แอดมินปฏิเสธสลิปนี้", ephemeral=False)
        self.stop()

class SlipVerifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.easyslip = EasySlipAPI()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ไม่ประมวลผลข้อความจากตัวบอทเอง
        if message.author.bot:
            return

        # ถ้าไม่มีไฟล์แนบ ให้ข้ามไป
        if not message.attachments:
            return

        for attachment in message.attachments:
            # ตรวจสอบว่าเป็นไฟล์รูปภาพ
            if attachment.content_type and attachment.content_type.startswith('image/'):
                try:
                    # 1. ดาวน์โหลดรูปภาพลง Memory
                    image_bytes = await attachment.read()
                    
                    # 2. สแกนหา QR Code
                    qr_data = scan_qr_from_bytes(image_bytes)
                    
                    slip_data = None
                    is_truemoney = False
                    is_fake = False
                    fake_reason = ""
                    
                    if qr_data:
                        # ลองตรวจสอบว่าเป็นสลิปธนาคาร (ใช้ Payload)
                        try:
                            slip_data = await self.easyslip.verify_bank_payload(qr_data)
                        except Exception as e:
                            # มี QR แต่ตรวจสอบไม่ผ่าน อาจเป็นสลิปปลอม หรือ QR ทั่วไป
                            is_fake = True
                            fake_reason = str(e)
                    
                    # ถ้าสแกน QR ไม่เจอ ให้ลองสลิปทรูมันนี่
                    if not qr_data and not slip_data:
                        try:
                            slip_data = await self.easyslip.verify_truewallet_image(image_bytes)
                            is_truemoney = True
                        except Exception as e:
                            error_msg = str(e).lower()
                            # ถ้าเป็นรูปทั่วไป (ไม่เหมือนสลิปเลย) ให้ปล่อยผ่าน
                            if "not a valid" in error_msg or "invalid image" in error_msg or "size" in error_msg:
                                continue
                            # ถ้าเหมือนสลิปแต่หาไม่เจอ ถือว่าปลอม
                            is_fake = True
                            fake_reason = str(e)
                            
                    # ตรวจสอบว่าสลิปซ้ำหรือไม่
                    if slip_data and slip_data.get('isDuplicate'):
                        is_fake = True
                        fake_reason = "สลิปนี้ถูกใช้งานไปแล้ว (Duplicate)"
                        
                    # ถ้าพบว่าเป็นสลิปปลอมหรือมีปัญหา ให้ส่งให้ Admin ตรวจสอบ
                    if is_fake:
                        view = AdminReviewView()
                        await message.channel.send(
                            f"⚠️ **พบปัญหาการตรวจสอบสลิป (อาจเป็นสลิปปลอมหรือผิดพลาด)**\n"
                            f"📝 **สาเหตุ:** `{fake_reason}`\n"
                            f"\n👮‍♂️ รอแอดมินตรวจสอบ...", 
                            reference=message,
                            view=view
                        )
                        continue
                        
                    # ถ้าไม่ใช่สลิปปลอม แต่ก็ไม่มีข้อมูลสลิป (รูปทั่วไป)
                    if not slip_data:
                        continue
                        
                    # สกัดข้อมูลยอดเงินและบัญชีสำหรับสลิปที่ถูกต้อง
                    if is_truemoney:
                        amount = slip_data.get('amountInSlip')
                        sender = slip_data.get('rawSlip', {}).get('sender', {}).get('name', 'Unknown')
                        receiver = slip_data.get('rawSlip', {}).get('receiver', {}).get('name', 'Unknown')
                    else:
                        amount = slip_data.get('rawSlip', {}).get('amount', {}).get('amount')
                        sender = slip_data.get('rawSlip', {}).get('sender', {}).get('account', {}).get('name', {}).get('th', 'Unknown')
                        receiver = slip_data.get('rawSlip', {}).get('receiver', {}).get('account', {}).get('name', {}).get('th', 'Unknown')
                    
                    # แจ้งผลการตรวจสอบสำเร็จ (ไม่ต้องมีปุ่ม Admin แล้ว)
                    await message.channel.send(
                        f"✅ **ตรวจสอบสลิปสำเร็จ!**\n"
                        f"💰 **ยอดเงิน:** `{amount:,.2f} บาท`\n"
                        f"📤 **จาก:** `{sender}`\n"
                        f"📥 **ไปยัง:** `{receiver}`", 
                        reference=message
                    )
                except Exception as e:
                    print(f"[SlipVerifier] Error processing image: {e}")
                    await message.channel.send("❌ เกิดข้อผิดพลาดในระบบขณะประมวลผลรูปภาพ โปรดลองใหม่อีกครั้ง", reference=message)

async def setup(bot):
    await bot.add_cog(SlipVerifier(bot))
