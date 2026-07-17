import os
import logging
from typing import Any, Dict, Optional
import aiohttp

logger = logging.getLogger(__name__)


class SlipOKError(Exception):
    """Base exception for SlipOK API errors."""
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.code = code


class SlipDuplicateError(SlipOKError):
    """Exception raised when a slip has already been used (Duplicate - Code 1012)."""
    def __init__(self, message: str, code: int = 1012):
        super().__init__(message, code)


class SlipOKAPI:
    """Client for SlipOK API v1.13 to verify bank transfer slips and check duplicates."""
    def __init__(self, api_key: Optional[str] = None, branch_id: Optional[str] = None, session: Optional[aiohttp.ClientSession] = None):
        self.api_key = api_key or os.getenv('SLIPOK_API_KEY')
        self.branch_id = branch_id or os.getenv('SLIPOK_BRANCH_ID', '71503')
        self._external_session = session is not None
        self._session = session
        
        self.api_url = os.getenv('SLIPOK_API_URL')
        if not self.api_url:
            self.api_url = f"https://api.slipok.com/api/line/apikey/{self.branch_id}"

    def _validate_config(self) -> None:
        if not self.api_key:
            raise ValueError("SLIPOK_API_KEY is not set in environment variables.")
        if not self.branch_id and not os.getenv('SLIPOK_API_URL'):
            raise ValueError("SLIPOK_BRANCH_ID is not set in environment variables.")

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=15)
            self._session = aiohttp.ClientSession(timeout=timeout)
            self._external_session = False
        return self._session

    async def close(self) -> None:
        """Close the underlying HTTP session if owned by this client."""
        if self._session is not None and not self._session.closed and not self._external_session:
            await self._session.close()

    def _handle_response_error(self, result: Dict[str, Any]) -> None:
        """Parses response error codes and raises appropriate exceptions."""
        code_raw = result.get("code")
        if code_raw is None and isinstance(result.get("error"), dict):
            code_raw = result["error"].get("code")
        if code_raw is None and isinstance(result.get("data"), dict):
            code_raw = result["data"].get("code")

        message = result.get("message")
        if not message and isinstance(result.get("error"), dict):
            message = result["error"].get("message")
        if not message and isinstance(result.get("data"), dict):
            message = result["data"].get("message")
        if not message:
            message = "Unknown error occurred during verification."

        code: Optional[int] = None
        if code_raw is not None:
            try:
                code = int(code_raw)
            except (ValueError, TypeError):
                code = None

        if code == 1012 or (isinstance(message, str) and "สลิปซ้ำ" in message):
            raise SlipDuplicateError(message, code=code or 1012)
        
        raise SlipOKError(message, code=code)

    async def verify_payload(self, payload: str, log: bool = True) -> Dict[str, Any]:
        """Verify bank slip using QR Code payload string."""
        self._validate_config()

        headers = {
            "x-authorization": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "data": payload,
            "log": log
        }

        session = await self._get_session()
        async with session.post(self.api_url, headers=headers, json=data) as response:
            if response.status >= 500:
                text = await response.text()
                logger.error(f"[SlipOK] Upstream server error ({response.status}): {text[:200]}")
                raise SlipOKError(f"SlipOK server returned HTTP {response.status}", code=response.status)

            try:
                result = await response.json()
            except Exception as e:
                text = await response.text()
                logger.error(f"[SlipOK] Invalid JSON from API ({response.status}): {text[:200]}")
                raise SlipOKError("Invalid JSON response from SlipOK", code=response.status) from e

            if not result.get("success"):
                self._handle_response_error(result)

            data_section = result.get("data", {})
            if isinstance(data_section, dict) and not data_section.get("success", True):
                self._handle_response_error(data_section)

            return data_section

    async def verify_image(
        self,
        image_bytes: bytes,
        log: bool = True,
        filename: str = 'slip.jpg',
        content_type: str = 'image/jpeg'
    ) -> Dict[str, Any]:
        """Verify bank slip using direct image upload (JPG, JPEG, PNG, WEBP)."""
        self._validate_config()

        headers = {
            "x-authorization": self.api_key
        }

        data = aiohttp.FormData()
        data.add_field('files',
                       image_bytes,
                       filename=filename,
                       content_type=content_type)
        data.add_field('log', 'true' if log else 'false')

        session = await self._get_session()
        async with session.post(self.api_url, headers=headers, data=data) as response:
            if response.status >= 500:
                text = await response.text()
                logger.error(f"[SlipOK] Upstream server error ({response.status}): {text[:200]}")
                raise SlipOKError(f"SlipOK server returned HTTP {response.status}", code=response.status)

            try:
                result = await response.json()
            except Exception as e:
                text = await response.text()
                logger.error(f"[SlipOK] Invalid JSON from API ({response.status}): {text[:200]}")
                raise SlipOKError("Invalid JSON response from SlipOK", code=response.status) from e

            if not result.get("success"):
                self._handle_response_error(result)

            data_section = result.get("data", {})
            if isinstance(data_section, dict) and not data_section.get("success", True):
                self._handle_response_error(data_section)

            return data_section
