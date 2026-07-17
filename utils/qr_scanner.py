import io
import logging
from PIL import Image
from pyzbar.pyzbar import decode

logger = logging.getLogger(__name__)

# Set explicit pixel limit (25 Megapixels) to prevent decompression bombs (DoS)
Image.MAX_IMAGE_PIXELS = 25_000_000


def scan_qr_from_bytes(image_bytes: bytes) -> str | None:
    """
    อ่านรูปภาพจาก memory (bytes) และสแกนหา QR Code
    คืนค่าเป็น string ของ QR Code หากพบ หากไม่พบหรือเกิดข้อผิดพลาดจะคืนค่า None
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        decoded_objects = decode(image)

        if decoded_objects:
            # คืนค่าข้อความจาก QR Code ตัวแรกที่พบ
            return decoded_objects[0].data.decode('utf-8')
        return None
    except Image.DecompressionBombError as e:
        logger.warning(f"[QR Scanner] Decompression bomb detected or image too large: {e}")
        return None
    except Exception as e:
        logger.error(f"[QR Scanner] Error decoding QR from bytes: {e}")
        return None
