"""Global configuration for the Telegram bot."""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Telegram Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "your_channel")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/your_channel")

# Optional: channel ID-based membership check (useful for private channels)
_channel_id_raw = os.getenv("CHANNEL_ID", "").strip()
# When CHANNEL_ID is empty or "0", treat it as not configured
if _channel_id_raw and _channel_id_raw not in {"0", "-0"} and _channel_id_raw.lstrip("-").isdigit():
    CHANNEL_ID = int(_channel_id_raw)
else:
    CHANNEL_ID = None

# Optional: backup channel URL
SECONDARY_CHANNEL_URL = os.getenv("SECONDARY_CHANNEL_URL", "")

# Admin configuration
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "123456789"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "Wrymy")

# Credit/points configuration
VERIFY_COST = 1         # Credits consumed per verification
CHECKIN_REWARD = 1      # Credits given for daily check-in
# INVITE_REWARD is used internally in the invitation logic
# (currently the effective rule is: every 10 successful invites = +1 credit)
INVITE_REWARD = 2       # Invitation reward coefficient
REGISTER_REWARD = 1     # Credits given on first registration

# Paid package configuration (display only; actual payments handled manually)
CREDIT_BRONZE_PRICE = os.getenv("CREDIT_BRONZE_PRICE", "2$")
CREDIT_BRONZE_CREDITS = int(os.getenv("CREDIT_BRONZE_CREDITS", "1"))
CREDIT_SILVER_PRICE = os.getenv("CREDIT_SILVER_PRICE", "5$")
CREDIT_SILVER_CREDITS = int(os.getenv("CREDIT_SILVER_CREDITS", "3"))

# Help / documentation link
HELP_NOTION_URL = "https://rhetorical-era-3f3.notion.site/dd78531dbac745af9bbac156b51da9cc"
