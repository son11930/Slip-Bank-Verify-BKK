import discord
from discord.ext import commands
from utils.qr_scanner import scan_qr_from_bytes
from utils.easyslip import EasySlipAPI


class AdminReviewView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Approve",
                       style=discord.ButtonStyle.success,
                       custom_id="approve_slip")
    async def approve_button(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button):
        await interaction.response.send_message(f"⚠️ สลิปนี้ถูกยืนยันโดย {interaction.user.mention} ให้ Admin ตรวจสอบอีกที", ephemeral=False)
        self.stop()

    @discord.ui.button(label="Reject",
                       style=discord.ButtonStyle.danger,
                       custom_id="reject_slip")
    async def reject_button(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button):
        await interaction.response.send_message(f"❌ สลิปนี้ถูกปฏิเสธโดย {interaction.user.mention}", ephemeral=False)
        self.stop()


class SlipVerifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.easyslip = EasySlipAPI()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not message.attachments:
            return

        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith(
                    'image/'):
                # ตรวจสอบขนาดไฟล์ไม่เกิน 5MB (5 * 1024 * 1024 bytes) ป้องกัน
                # DoS
                if attachment.size > 5 * 1024 * 1024:
                    await message.channel.send("❌ ไฟล์รูปภาพมีขนาดใหญ่เกินไป (จำกัด 5MB) โปรดลดขนาดรูปภาพ", reference=message)
                    continue

                try:
                    image_bytes = await attachment.read()

                    qr_data = scan_qr_from_bytes(image_bytes)

                    slip_data = None
                    is_truemoney = False
                    is_fake = False
                    fake_reason = ""

                    if qr_data:
                        try:
                            slip_data = await self.easyslip.verify_bank_payload(qr_data)
                        except Exception as e:
                            # มี QR แต่ตรวจสอบไม่ผ่าน อาจเป็นสลิปปลอม หรือ QR
                            # ทั่วไป
                            is_fake = True
                            fake_reason = str(e)

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

                    if slip_data and slip_data.get('isDuplicate'):
                        is_fake = True
                        fake_reason = "สลิปนี้ถูกใช้งานไปแล้ว (Duplicate)"

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

                    if not slip_data:
                        continue

                    if is_truemoney:
                        amount = slip_data.get('amountInSlip')
                        sender = slip_data.get(
                            'rawSlip',
                            {}).get(
                            'sender',
                            {}).get(
                            'name',
                            'Unknown')
                        receiver = slip_data.get(
                            'rawSlip',
                            {}).get(
                            'receiver',
                            {}).get(
                            'name',
                            'Unknown')
                    else:
                        amount = slip_data.get(
                            'rawSlip', {}).get(
                            'amount', {}).get('amount')
                        sender = slip_data.get(
                            'rawSlip',
                            {}).get(
                            'sender',
                            {}).get(
                            'account',
                            {}).get(
                            'name',
                            {}).get(
                            'th',
                            'Unknown')
                        receiver = slip_data.get(
                            'rawSlip',
                            {}).get(
                            'receiver',
                            {}).get(
                            'account',
                            {}).get(
                            'name',
                            {}).get(
                            'th',
                            'Unknown')

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
