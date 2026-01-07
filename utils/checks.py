"""Permission and channel membership helper utilities."""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import CHANNEL_USERNAME, CHANNEL_URL, CHANNEL_ID, SECONDARY_CHANNEL_URL

logger = logging.getLogger(__name__)


def is_group_chat(update: Update) -> bool:
    """Return True if the update comes from a group or supergroup."""
    chat = update.effective_chat
    return chat and chat.type in ("group", "supergroup")


async def reject_group_command(update: Update) -> bool:
    """Restrict which commands are allowed in group chats."""
    if is_group_chat(update):
        await update.message.reply_text(
            "In group chats only /verify /verify2 /verify3 /verify4 /verify5 /qd "
            "are allowed. Please DM the bot for other commands."
        )
        return True
    return False


async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check whether a user has joined the configured channel.
    If no channel username/ID is configured, allow by default.
    """
    # If neither channel username nor channel ID is configured, do not enforce checks
    if (not CHANNEL_USERNAME or CHANNEL_USERNAME in {"your_channel", "pk_oa"}) and CHANNEL_ID is None:
        return True

    try:
        target_chat = CHANNEL_ID if CHANNEL_ID is not None else f"@{CHANNEL_USERNAME}"
        member = await context.bot.get_chat_member(target_chat, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramError as e:
        logger.error("Failed to check channel membership: %s", e)
        # If configuration/API is broken, be conservative and deny access
        return False


async def ensure_channel_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Ensure the user has joined the required channel.
    If not, send a message with join buttons and return False.
    """
    user = update.effective_user
    if not user:
        return False

    is_member = await check_channel_membership(user.id, context)
    if is_member:
        return True

    # Build hint message
    lines = ["⚠️ Please join the channel before using this bot:", ""]
    if CHANNEL_URL:
        lines.append(f"🌀 Main channel: {CHANNEL_URL}")
    if SECONDARY_CHANNEL_URL:
        lines.append(f"♠ Backup channel: {SECONDARY_CHANNEL_URL}")
    lines.append("")
    lines.append("After joining, please send your command again.")

    buttons = []
    if CHANNEL_URL:
        buttons.append([InlineKeyboardButton("🌀 Join main channel", url=CHANNEL_URL)])
    if SECONDARY_CHANNEL_URL:
        buttons.append([InlineKeyboardButton("♠ Join backup channel", url=SECONDARY_CHANNEL_URL)])

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    if getattr(update, "message", None):
        await update.message.reply_text("\n".join(lines), reply_markup=reply_markup)
    elif getattr(update, "callback_query", None) and update.callback_query.message:
        await update.callback_query.message.reply_text("\n".join(lines), reply_markup=reply_markup)

    return False
