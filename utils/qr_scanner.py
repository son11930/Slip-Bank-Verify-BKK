import io
from PIL import Image
from pyzbar.pyzbar import decode


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
    except Exception as e:
        print(f"[QR Scanner] Error: {e}")
        return None
