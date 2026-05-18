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
- Enhanced keyword detection to prompt users to use the `/bank` command with support for variations like "ขอบัญชี", "ขอเลข", "ขอธนาคาร" for better UX.
- Implemented and passed automated unit tests for the `/bank` feature to maintain high test coverage.
