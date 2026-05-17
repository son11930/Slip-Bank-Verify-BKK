# Slip Verify Bot - Project Plan & Requirements

## Overview
A Discord bot designed to verify bank transfer slips submitted by users.

## Core Verification Flow
- **Initial Idea:** Use an AI API to analyze and verify slips (scrapped due to API costs).
- **Current Approach:** 
  1. **QR Code Scanning:** The bot will scan and read the QR code embedded in the slip image.
  2. **Automated Verification (EasySlip API):** 
     - Use the QR Payload to verify bank slips via EasySlip.
     - Fallback to uploading the image to EasySlip for TrueMoney Wallet slips.
  3. **Duplicate Detection:** The bot prevents reuse of the same slip.
  4. **Manual Approval:** After automated verification displays the amount and sender/receiver, a human admin reviews and finalizes the approval.

## Image Handling Constraints
- The bot attempts to process images by checking for QR codes or passing them to the TrueMoney verification endpoint.
- **Rule:** If an image fails both Bank QR payload verification and TrueMoney image verification, it is ignored as a standard non-slip image.

## Deployment Strategy
- **Platform:** Google Cloud Run
- **Goal:** Ensure the bot is highly available and can run 24/7 without interruption.
