"""Inline button and menu callback handlers."""
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
    """Handle all callback buttons coming from menus/help."""
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = (query.data or "").strip()

    # Usage guides for /verify commands
    if data in _HELP_VERIFY_MAPPING:
        command, service_name = _HELP_VERIFY_MAPPING[data]
        text = get_verify_usage_message(command, service_name)
        await query.message.reply_text(text)
        return

    # Buy credits
    if data == "help_buy":
        text = get_buy_message()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Contact admin to buy (@{})".format(OWNER_USERNAME),
                        url=f"https://t.me/{OWNER_USERNAME}",
                    )
                ]
            ]
        )
        await query.message.reply_text(text, reply_markup=keyboard)
        return

    # Admin help buttons
    if data.startswith("admin_help_"):
        user_id = query.from_user.id
        if user_id != ADMIN_USER_ID:
            await query.message.reply_text("You don't have permission to view this admin help.")
            return

        if data == "admin_help_addbalance":
            await query.message.reply_text(
                "➕ Add credits:\n"
                "Command: /addbalance <user_id> <amount>\n"
                "Example: /addbalance 123456789 10"
            )
        elif data == "admin_help_block":
            await query.message.reply_text(
                "🚫 Block user:\n"
                "Command: /block <user_id>\n"
                "Example: /block 123456789"
            )
        elif data == "admin_help_white":
            await query.message.reply_text(
                "✅ Unblock user:\n"
                "Command: /white <user_id>\n"
                "Example: /white 123456789"
            )
        elif data == "admin_help_broadcast":
            await query.message.reply_text(
                "📢 Broadcast message:\n"
                "Command: /broadcast <text>\n"
                "Or: reply to a message and then send /broadcast"
            )
        else:
            logger.warning("Received unknown admin_help callback data: %s", data)

        return

    logger.warning("Received unknown menu callback data: %s", data)