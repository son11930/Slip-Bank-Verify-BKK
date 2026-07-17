import discord
from discord.ext import commands
from discord import app_commands
import os


class BankInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # คำที่ลูกค้าอาจจะพิมพ์เพื่อขอเลขบัญชี (เพิ่มคำค้นหาให้ครอบคลุมขึ้น)
        keywords = [
            "ขอบัญชี", "ขอเลขบัญชี", "ขอธนาคาร", "ขอช่องทาง",
            "โอนเงินทางไหน", "เลขบัญชีอะไร", "โอนเข้าไหน",
            "จ่ายเงินทางไหน", "ขอเลขหน่อย", "โอนเงินเข้า"
        ]

        # ตัดช่องว่างออกเพื่อให้ตรวจจับคำได้แม่นยำขึ้น
        content = message.content.replace(" ", "")

        if any(keyword in content for keyword in keywords):
            await message.channel.send(
                f"{message.author.mention} กรุณาพิมพ์คำสั่ง `/bank` เพื่อดูข้อมูลบัญชีธนาคารและช่องทางโอนเงินครับ 🏦",
                reference=message.to_reference(fail_if_not_exists=False)
            )

    @app_commands.command(name="bank",
                          description="ดูข้อมูลบัญชีธนาคารสำหรับโอนเงิน")
    async def bank_command(self, interaction: discord.Interaction):
        bank_details = (
            "**ข้อมูลบัญชีธนาคาร**\n"
            "```text\n"
            "2085257892\n"
            "ธนาคารเกียรตินาคินภัทร (KKP)\n"
            "เนติณัฏฐ์\n"
            "```"
        )

        image_path = "assets/bank_qr.jpg"
        if os.path.exists(image_path):
            file = discord.File(image_path, filename="bank_qr.jpg")
            await interaction.response.send_message(content=bank_details, file=file)
        else:
            await interaction.response.send_message(content=bank_details + "\n*(ไม่พบรูปภาพ QR Code)*")


async def setup(bot):
    await bot.add_cog(BankInfo(bot))
