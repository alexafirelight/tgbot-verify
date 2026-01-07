"""内联按钮与菜单回调处理"""
import logging
from typing import Dict, Tuple

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from config import OWNER_USERNAME, ADMIN_USER_ID
from database_mysql import Database
from utils.messages import get_verify_usage_message, get_buy_message

logger = logging.getLogger(__name__)

_HELP_VERIFY_MAPPING: Dict[str, Tuple[str, str]] = {
    "help_verify1": ("/verify", "Gemini One Pro"),
    "help_verify2": ("/verify2", "ChatGPT Teacher K12"),
    "help_verify3": ("/verify3", "Spotify Student"),
    "help_verify4": ("/verify4", "Bolt.new Teacher"),
    "help_verify5": ("/verify5", "YouTube Student Premium"),
}


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理所有来自菜单/帮助的回调按钮"""
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = (query.data or "").strip()

    # 各 verify 使用说明
    if data in _HELP_VERIFY_MAPPING:
        command, service_name = _HELP_VERIFY_MAPPING[data]
        text = get_verify_usage_message(command, service_name)
        await query.message.reply_text(text)
        return

    # 购买积分说明
    if data == "help_buy":
        text = get_buy_message()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "联系管理员购买 / Contact @{}".format(OWNER_USERNAME),
                        url=f"https://t.me/{OWNER_USERNAME}",
                    )
                ]
            ]
        )
        await query.message.reply_text(text, reply_markup=keyboard)
        return

    # 管理员帮助按钮
    if data.startswith("admin_help_"):
        user_id = query.from_user.id
        if user_id != ADMIN_USER_ID:
            await query.message.reply_text("您没有权限查看此管理操作说明。")
            return

        if data == "admin_help_addbalance":
            await query.message.reply_text(
                "➕ 充值积分说明：\n"
                "命令格式：/addbalance <用户ID> <积分数量>\n"
                "示例：/addbalance 123456789 10"
            )
        elif data == "admin_help_block":
            await query.message.reply_text(
                "🚫 拉黑用户说明：\n"
                "命令格式：/block <用户ID>\n"
                "示例：/block 123456789"
            )
        elif data == "admin_help_white":
            await query.message.reply_text(
                "✅ 取消拉黑说明：\n"
                "命令格式：/white <用户ID>\n"
                "示例：/white 123456789"
            )
        elif data == "admin_help_broadcast":
            await query.message.reply_text(
                "📢 群发通知说明：\n"
                "命令格式：/broadcast <文本>\n"
                "或：回复一条要转发的消息后发送 /broadcast"
            )
        else:
            logger.warning("收到未知的 admin_help 回调数据：%s", data)

        return

    logger.warning("收到未知的菜单回调数据：%s", data)