import asyncio
import logging
import os
from typing import Any, Dict, Optional
import discord
from discord.ext import commands
from utils.qr_scanner import scan_qr_from_bytes
from utils.slipok import SlipOKAPI, SlipDuplicateError, SlipOKError

logger = logging.getLogger(__name__)


def sanitize_discord_text(text: Any) -> str:
    """Sanitize text to prevent Discord markdown breakage or mention injection."""
    if text is None:
        return "Unknown"
    return str(text).replace('`', "'").replace('@', '`@`\u200b')


class SlipVerifier(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.slipok = SlipOKAPI()

    async def cog_unload(self) -> None:
        await self.slipok.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.attachments:
            return

        # Limit to 3 attachments per message to prevent DoS
        for attachment in message.attachments[:3]:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                await self._process_attachment(attachment, message)

    async def _process_attachment(self, attachment: discord.Attachment, message: discord.Message) -> None:
        if attachment.size > 5 * 1024 * 1024:
            await message.channel.send(
                "❌ ไฟล์รูปภาพมีขนาดใหญ่เกินไป (จำกัด 5MB) โปรดลดขนาดรูปภาพ",
                reference=message.to_reference(fail_if_not_exists=False)
            )
            return

        try:
            image_bytes = await attachment.read()
            # Run CPU-bound QR decoding in a background thread to prevent blocking event loop
            qr_data = await asyncio.to_thread(scan_qr_from_bytes, image_bytes)
            
            filename = attachment.filename or 'slip.jpg'
            content_type = attachment.content_type or 'image/jpeg'

            slip_data = await self._verify_slip_data(image_bytes, qr_data, filename, content_type, message)
            if slip_data:
                await self._handle_verification_success(slip_data, message)

        except Exception as e:
            logger.error(f"[SlipVerifier] Error processing attachment {attachment.filename}: {e}", exc_info=True)
            await message.channel.send(
                "❌ เกิดข้อผิดพลาดในระบบขณะประมวลผลรูปภาพ โปรดลองใหม่อีกครั้ง",
                reference=message.to_reference(fail_if_not_exists=False)
            )

    async def _verify_slip_data(
        self,
        image_bytes: bytes,
        qr_data: Optional[str],
        filename: str,
        content_type: str,
        message: discord.Message
    ) -> Optional[Dict[str, Any]]:
        if qr_data:
            try:
                return await self.slipok.verify_payload(qr_data, log=True)
            except SlipDuplicateError as dup_e:
                await self._send_duplicate_warning(dup_e.message, message)
                return None
            except SlipOKError as payload_err:
                # Fallback to image check if QR payload verification fails
                return await self._fallback_image_check(image_bytes, filename, content_type, message, payload_err)
        else:
            return await self._fallback_image_check(image_bytes, filename, content_type, message)

    async def _fallback_image_check(
        self,
        image_bytes: bytes,
        filename: str,
        content_type: str,
        message: discord.Message,
        previous_err: Optional[SlipOKError] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            return await self.slipok.verify_image(
                image_bytes, log=True, filename=filename, content_type=content_type
            )
        except SlipDuplicateError as dup_e:
            await self._send_duplicate_warning(dup_e.message, message)
            return None
        except SlipOKError as img_err:
            await self._handle_slipok_error(img_err, message, had_qr=previous_err is not None)
            return None

    async def _handle_slipok_error(self, err: SlipOKError, message: discord.Message, had_qr: bool) -> None:
        # Check if error code indicates non-slip image or non-payment QR
        if err.code in [1005, 1006, 1007, 1008]:
            if err.code == 1008 and had_qr:
                await message.channel.send(
                    "⚠️ **QR ดังกล่าวไม่ใช่ QR สำหรับการตรวจสอบการชำระเงิน**",
                    reference=message.to_reference(fail_if_not_exists=False)
                )
            return

        if not had_qr and any(
            kw in str(err.message).lower()
            for kw in ["no qr", "1007", "1005", "1006", "invalid image"]
        ):
            return

        # Protect against reflecting upstream/unknown errors (5xx/4xx HTML or WAF responses)
        if err.code is None or err.code not in range(1000, 1020):
            logger.error(f"[SlipVerifier] Upstream or unrecognized SlipOK error ({err.code}): {err.message}")
            await message.channel.send(
                "⚠️ **พบปัญหาในการติดต่อระบบตรวจสอบสลิป โปรดลองใหม่อีกครั้งภายหลัง**",
                reference=message.to_reference(fail_if_not_exists=False)
            )
            return

        if any(kw in str(err.message) for kw in ["ขัดข้อง", "ชั่วคราว", "ไม่เสียโควต้า", "โปรดตรวจใหม่อีกครั้ง"]):
            await message.channel.send(
                f"ℹ️ **ระบบธนาคาร/ทรูมันนี่ขัดข้องชั่วคราว**\n"
                f"📝 **สถานะ:** `{sanitize_discord_text(err.message)}`\n"
                f"💡 *คำแนะนำ: ระบบ Nethinat Verify Slip ไม่สามารถดึงข้อมูลจากธนาคาร/TrueMoney ได้ในขณะนี้ โปรดลองใหม่อีกครั้งในภายหลังครับ*",
                reference=message.to_reference(fail_if_not_exists=False)
            )
            return

        await message.channel.send(
            f"⚠️ **พบปัญหาการตรวจสอบสลิป (อาจเป็นสลิปปลอมหรือไม่ถูกต้อง)**\n📝 **สาเหตุ:** `{sanitize_discord_text(err.message)}`",
            reference=message.to_reference(fail_if_not_exists=False)
        )

    async def _send_duplicate_warning(self, reason: str, message: discord.Message) -> None:
        await message.channel.send(
            f"❌ **สลิปซ้ำ! ถูกใช้งานไปแล้ว**\n🕒 **รายละเอียด:** `{sanitize_discord_text(reason)}`",
            reference=message.to_reference(fail_if_not_exists=False)
        )

    async def _handle_verification_success(self, slip_data: Dict[str, Any], message: discord.Message) -> None:
        if slip_data.get('isDuplicate') or slip_data.get('code') == 1012:
            msg = slip_data.get('message', 'สลิปนี้ถูกใช้งานไปแล้ว')
            await self._send_duplicate_warning(msg, message)
            return

        amount = slip_data.get('amount', 0.0)
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            amount_float = 0.0

        sender_obj = slip_data.get('sender') or {}
        sender_raw = (
            sender_obj.get('displayName') or sender_obj.get('name') or 'Unknown'
            if isinstance(sender_obj, dict) else str(sender_obj)
        )
        sender = sanitize_discord_text(sender_raw)

        receiver_obj = slip_data.get('receiver') or {}
        receiver_raw = (
            receiver_obj.get('displayName') or receiver_obj.get('name') or 'Unknown'
            if isinstance(receiver_obj, dict) else str(receiver_obj)
        )
        receiver = sanitize_discord_text(receiver_raw)

        trans_ref = sanitize_discord_text(slip_data.get('transRef', '-'))

        # Check if receiver matches the store account keywords
        store_keywords_raw = os.getenv("STORE_RECEIVER_KEYWORDS", "เนติณัฏฐ์,netinat,7892,2085257892")
        store_keywords = [kw.strip().lower() for kw in store_keywords_raw.split(",") if kw.strip()]

        receiver_full_str = (
            str(receiver_obj).lower() if isinstance(receiver_obj, dict) else str(receiver_raw).lower()
        )
        is_store_account = any(kw in receiver_full_str for kw in store_keywords)

        if not is_store_account and store_keywords:
            await message.channel.send(
                f"⚠️ **สลิปถูกต้อง แต่ไม่ใช่บัญชีของทางร้าน!**\n"
                f"💰 **จำนวน:** `{amount_float:,.2f} บาท`\n"
                f"📥 **โอนไปยัง:** `{receiver}`\n"
                f"📤 **จาก:** `{sender}`\n"
                f"🔖 **อ้างอิง:** `{trans_ref}`",
                reference=message.to_reference(fail_if_not_exists=False)
            )
            return

        await message.channel.send(
            f"✅ **ตรวจสอบสลิปสำเร็จ!**\n"
            f"💰 **ยอดเงิน:** `{amount_float:,.2f} บาท`\n"
            f"📤 **จาก:** `{sender}`\n"
            f"📥 **ไปยัง:** `{receiver}`\n"
            f"🔖 **อ้างอิง:** `{trans_ref}`",
            reference=message.to_reference(fail_if_not_exists=False)
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SlipVerifier(bot))
