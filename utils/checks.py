"""权限检查和验证工具"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import CHANNEL_USERNAME, CHANNEL_URL, CHANNEL_ID, SECONDARY_CHANNEL_URL

logger = logging.getLogger(__name__)


def is_group_chat(update: Update) -> bool:
    """判断是否为群聊"""
    chat = update.effective_chat
    return chat and chat.type in ("group", "supergroup")


async def reject_group_command(update: Update) -> bool:
    """群聊限制：仅允许 /verify /verify2 /verify3 /verify4 /verify5 /qd"""
    if is_group_chat(update):
        await update.message.reply_text("群聊仅支持 /verify /verify2 /verify3 /verify4 /verify5 /qd，请私聊使用其他命令。")
        return True
    return False


async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """检查用户是否加入了频道；若未配置频道则默认放行"""
    # 未配置频道用户名且未配置频道 ID 时，不强制检查
    if (not CHANNEL_USERNAME or CHANNEL_USERNAME in {"your_channel", "pk_oa"}) and CHANNEL_ID is None:
        return True

    try:
        target_chat = CHANNEL_ID if CHANNEL_ID is not None else f"@{CHANNEL_USERNAME}"
        member = await context.bot.get_chat_member(target_chat, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramError as e:
        logger.error("检查频道成员失败: %s", e)
        # 配置错误时，为防止滥用，这里返回 False
        return False


async def ensure_channel_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """确保用户已加入频道，未加入时发送引导消息"""
    user = update.effective_user
    if not user:
        return False

    is_member = await check_channel_membership(user.id, context)
    if is_member:
        return True

    # 构造提示消息
    lines = ["⚠️ 使用机器人前请先加入频道：", ""]
    if CHANNEL_URL:
        lines.append(f"🌀 主频道：{CHANNEL_URL}")
    if SECONDARY_CHANNEL_URL:
        lines.append(f"♠ 备用频道：{SECONDARY_CHANNEL_URL}")
    lines.append("")
    lines.append("加入后请重新发送命令。")

    buttons = []
    if CHANNEL_URL:
        buttons.append([InlineKeyboardButton("🌀 加入主频道", url=CHANNEL_URL)])
    if SECONDARY_CHANNEL_URL:
        buttons.append([InlineKeyboardButton("♠ 加入备用频道", url=SECONDARY_CHANNEL_URL)])

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    if getattr(update, "message", None):
        await update.message.reply_text("\n".join(lines), reply_markup=reply_markup)
    elif getattr(update, "callback_query", None) and update.callback_query.message:
        await update.callback_query.message.reply_text("\n".join(lines), reply_markup=reply_markup)

    return False
