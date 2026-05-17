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
