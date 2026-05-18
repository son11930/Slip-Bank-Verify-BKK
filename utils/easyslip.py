import os
import aiohttp


class EasySlipAPI:
    def __init__(self):
        self.api_key = os.getenv('EASYSLIP_API_KEY')
        self.base_url = "https://api.easyslip.com/v2"

    async def verify_bank_payload(
            self,
            payload: str,
            check_duplicate: bool = True) -> dict:
        """
        Verify Bank slip using QR Code Payload
        """
        if not self.api_key:
            raise ValueError(
                "EASYSLIP_API_KEY is not set in environment variables.")

        url = f"{self.base_url}/verify/bank"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "payload": payload,
            "checkDuplicate": check_duplicate
        }

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await response.json()
                if not result.get("success"):
                    error_message = result.get(
                        "error", {}).get(
                        "message", "Unknown error")
                    raise Exception(error_message)
                return result.get("data", {})

    async def verify_truewallet_image(
            self,
            image_bytes: bytes,
            check_duplicate: bool = True) -> dict:
        """
        Verify TrueMoney Wallet slip using Image file
        """
        if not self.api_key:
            raise ValueError(
                "EASYSLIP_API_KEY is not set in environment variables.")

        url = f"{self.base_url}/verify/truewallet"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        data = aiohttp.FormData()
        data.add_field('image',
                       image_bytes,
                       filename='slip.jpg',
                       content_type='image/jpeg')
        data.add_field(
            'checkDuplicate',
            'true' if check_duplicate else 'false')

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, data=data) as response:
                result = await response.json()
                if not result.get("success"):
                    error_message = result.get(
                        "error", {}).get(
                        "message", "Unknown error")
                    raise Exception(error_message)
                return result.get("data", {})
