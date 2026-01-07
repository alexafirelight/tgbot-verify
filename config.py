"""全局配置文件"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# Telegram Bot 配置
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "your_channel")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/your_channel")

# 支持通过频道 ID 做会员检查（适用于私有频道）
_channel_id_raw = os.getenv("CHANNEL_ID", "").strip()
# 当 CHANNEL_ID 为空或为 \"0\" 时，视为未配置
if _channel_id_raw and _channel_id_raw not in {"0", "-0"} and _channel_id_raw.lstrip("-").isdigit():
    CHANNEL_ID = int(_channel_id_raw)
else:
    CHANNEL_ID = None

SECONDARY_CHANNEL_URL = os.getenv("SECONDARY_CHANNEL_URL", "")

# 管理员配置
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "123456789"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "Wrymy")

# 积分配置
VERIFY_COST = 1  # 验证消耗的积分
CHECKIN_REWARD = 1  # 签到奖励积分
INVITE_REWARD = 2  # 邀请奖励积分（目前邀请奖励按「10 人=1 积分」逻辑发放）
REGISTER_REWARD = 1  # 注册奖励积分

# 付费套餐配置（仅用于展示文案）
CREDIT_BRONZE_PRICE = os.getenv("CREDIT_BRONZE_PRICE", "2$")
CREDIT_BRONZE_CREDITS = int(os.getenv("CREDIT_BRONZE_CREDITS", "1"))
CREDIT_SILVER_PRICE = os.getenv("CREDIT_SILVER_PRICE", "5$")
CREDIT_SILVER_CREDITS = int(os.getenv("CREDIT_SILVER_CREDITS", "3"))

# 帮助链接
HELP_NOTION_URL = "https://rhetorical-era-3f3.notion.site/dd78531dbac745af9bbac156b51da9cc"
