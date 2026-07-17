# Project Setup Notes

## 2026-05-18
- Created `.env` file to store environment variables securely.
- Added `DISCORD_TOKEN` to `.env` based on user input.
- Removed unnecessary keys (`DISCORD_APP_ID` and `DISCORD_PUBLIC_KEY`) as only `DISCORD_TOKEN` is required by the bot.
- Documented project requirements and roadmap in `PROJECT_PLAN.md`.
- Updated `cogs/slip_verifier.py` to bypass API verification and immediately display the `AdminReviewView` (Approve/Reject buttons) when a QR code is detected, aligning with the low-cost rollout plan.
- Removed `intents.members = True` from `main.py` as it is not needed and causes privileged intents error on startup.
- Created `.gitignore` file to ensure `.env` and other sensitive/unnecessary files are not pushed to GitHub.
- Integrated EasySlip API for robust slip verification (both Bank Payload and TrueMoney Image).
- Updated `cogs/slip_verifier.py` to display exact transaction amount, sender, and receiver details.
- Added duplicate checking mechanism for slips.
- Refactored `cogs/slip_verifier.py` to automatically pass valid slips without Admin approval.
- Added condition to flag fake, duplicate, or invalid slips for Admin review with a warning message.
- Updated `.gitignore` to exclude `tests/` directory.
- Configured local Git credentials and pushed the initial commit to the remote GitHub repository (`Slip-Bank-Verify-BKK`).
- Documented step-by-step server deployment instructions for Google Cloud Compute Engine (e2-micro) including installing `libzbar0`, setting up a virtual environment, and running the bot as a background process using `tmux`.
- Conducted security review and improved `cogs/slip_verifier.py`: added 5MB file size limit to prevent DoS attacks.
- Modified admin verification logic in `cogs/slip_verifier.py` to log which user approved or rejected a slip.
- Added a 10-second timeout to `aiohttp` API requests in `utils/easyslip.py` to prevent resource exhaustion.
- Implemented unit tests for `utils/easyslip.py` using `pytest` and `aioresponses` with 100% pass rate.
- Added `/bank` slash command feature to automatically provide bank account details and QR code when requested.
- Implemented and passed automated unit tests for the `/bank` feature to maintain high test coverage.

## 2026-07-18
- Migrated core slip verification engine from EasySlip (`utils/easyslip.py`) to **SlipOK API v1.13** (`utils/slipok.py`).
- Updated `cogs/slip_verifier.py` to use `SlipOKAPI` and removed `AdminReviewView` (Approve/Reject buttons) per user specification (`manual top-up by staff`).
- Implemented immediate notification alerts when duplicate slips (`code 1012`) or invalid slips (`code 1005-1008`) are detected.
- Hardened `utils/slipok.py` with shared `aiohttp.ClientSession` for connection keep-alive/TLS reuse and explicit HTTP 5xx error handling.
- Offloaded CPU-bound `scan_qr_from_bytes` (`PIL.Image.open` and `pyzbar.decode`) to `asyncio.to_thread` to prevent blocking the Discord async event loop.
- Added decompression bomb protection (`Image.MAX_IMAGE_PIXELS = 25_000_000`), attachment limits per message (`[:3]`), and display name sanitization (`sanitize_discord_text`) against mention injection (`@everyone`).
- Created thorough unit tests (`tests/test_slipok.py`, `tests/test_slip_verifier.py`, `tests/test_qr_scanner.py`) achieving **93% total test coverage** across `cogs/` and `utils/`.
- Executed parallel subagent reviews (`code-reviewer` and `security-reviewer`) ensuring clean architecture and zero security vulnerabilities.
