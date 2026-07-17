# Slip Verify Bot - Project Plan & Requirements

## Overview
A Discord bot designed to verify bank transfer slips submitted by users.

## Core Verification Flow
- **Initial Idea:** Use an AI API to analyze and verify slips (scrapped due to API costs).
- **Previous Approach:** Used EasySlip API (`utils/easyslip.py`).
- **Current Approach (SlipOK API Migration):** 
  1. **QR Code Scanning & Image Verification:** 
     - Scan QR payload from the slip image using `pyzbar`.
     - Send POST request to SlipOK API (`https://api.slipok.com/api/line/apikey/{SLIPOK_BRANCH_ID}`) with header `x-authorization: {SLIPOK_API_KEY}`.
     - Support passing `data` (QR Payload string) or `files` (Image bytes) with `log: true`.
  2. **Duplicate Detection:** 
     - When `log: true` is sent, SlipOK validates and checks against previously used slips. If duplicate, API returns error code `1012` (`สลิปซ้ำ สลิปนี้เคยส่งเข้ามาในระบบเมื่อ {timestamp}`).
  3. **Data Extraction & Formatting:**
     - Extract `amount`, `sender` (`displayName` or `name`), `receiver` (`displayName` or `name`), `sendingBank`, and `receivingBank` from the structured SlipOK response.
  4. **Manual Approval / Exception Handling:** 
     - If the slip is duplicate (`code: 1012`) or suspected fake, the bot displays an admin review prompt with Approve/Reject buttons.

## Image Handling Constraints
- The bot attempts to verify images via QR code payload string first; if not found or invalid, falls back to direct image verification (`files`).
- **Rule:** If an image returns non-slip error codes from SlipOK (`1005` file not image, `1006` invalid image, `1007` no QR code in image when uploaded, `1008` not payment QR), it is ignored or reported based on error type.

## Deployment Strategy
- **Platform:** Google Cloud Run / Remote Linux Server via `screen` session (`bot_manager.bat`).
- **Goal:** Ensure the bot is highly available and can run 24/7 without interruption.
