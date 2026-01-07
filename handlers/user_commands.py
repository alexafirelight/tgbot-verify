"""User command handlers."""
import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID, OWNER_USERNAME
from database_mysql import Database
from utils.checks import reject_group_command, ensure_channel_member
from utils.messages import (
    get_welcome_message,
    get_about_message,
    get_help_message,
    get_buy_message,
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /start command."""
    if await reject_group_command(update):
        return

    if not await ensure_channel_member(update, context):
        return

    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    full_name = user.full_name or ""

    # If user already exists, just greet
    if db.user_exists(user_id):
        await update.message.reply_text(
            f"Welcome back, {full_name}!\n"
            "Your account has already been initialized.\n"
            "Send /help to see available commands."
        )
        return

    # Invitation tracking
    invited_by: Optional[int] = None
    if context.args:
        try:
            invited_by = int(context.args[0])
            if not db.user_exists(invited_by):
                invited_by = None
        except Exception:
            invited_by = None

    # Create user
    if db.create_user(user_id, username, full_name, invited_by):
        welcome_msg = get_welcome_message(full_name, bool(invited_by))
        await update.message.reply_text(welcome_msg)
    else:
        await update.message.reply_text("Registration failed, please try again later.")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /about command."""
    if await reject_group_command(update):
        return

    if not await ensure_channel_member(update, context):
        return

    await update.message.reply_text(get_about_message())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /help command."""
    if await reject_group_command(update):
        return

    if not await ensure_channel_member(update, context):
        return

    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_USER_ID

    keyboard = [
        [
            InlineKeyboardButton("Gemini One Pro", callback_data="help_verify1"),
            InlineKeyboardButton("Teacher K12", callback_data="help_verify2"),
        ],
        [
            InlineKeyboardButton("Spotify Student", callback_data="help_verify3"),
            InlineKeyboardButton("YouTube Student", callback_data="help_verify5"),
        ],
        [
            InlineKeyboardButton("Bolt.new Teacher", callback_data="help_verify4"),
        ],
        [
            InlineKeyboardButton("🛒 Buy Credits", callback_data="help_buy"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(get_help_message(is_admin), reply_markup=reply_markup)


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /balance command."""
    if await reject_group_command(update):
        return

    if not await ensure_channel_member(update, context):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please use /start first to register.")
        return

    invite_stats = db.get_invitation_stats(user_id)

    msg = (
        "💰 Credit balance\n\n"
        f"Current credits: {user['balance']}\n"
        f"Total invites: {invite_stats['total_invites']}\n"
        "Invite rewards: +1 credit for every 10 successful invites\n"
    )
    if invite_stats["total_invites"] > 0 and invite_stats["invites_to_next_credit"] > 0:
        msg += (
            "Invites remaining until next reward: "
            f"{invite_stats['invites_to_next_credit']}\n"
        )

    await update.message.reply_text(msg)


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /qd daily check-in command."""
    if not await ensure_channel_member(update, context):
        return

    user_id = update.effective_user.id

    # If you want to temporarily disable check-in, you can early-return here.

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please use /start first to register.")
        return

    # First-level check in handler layer
    if not db.can_checkin(user_id):
        await update.message.reply_text("❌ You have already checked in today. Please come back tomorrow.")
        return

    # Second-level check in DB (atomic SQL operation)
    if db.checkin(user_id):
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"✅ Check-in successful!\nCredits earned: +1\nCurrent credits: {user['balance']}"
        )
    else:
        # If DB returns False, user has already checked in today (double check)
        await update.message.reply_text("❌ You have already checked in today. Please come back tomorrow.")


async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /invite command."""
    if await reject_group_command(update):
        return

    if not await ensure_channel_member(update, context):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please use /start first to register.")
        return

    bot_username = context.bot.username
    invite_link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(
        f"🎁 Your personal invite link:\n{invite_link}\n\n"
        "For every new user who registers via this link, your invite count increases by 1.\n"
        "Each time you reach 10 successful invites, you automatically receive 1 extra credit."
    )


async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /use command - redeem a code."""
    if await reject_group_command(update):
        return

    if not await ensure_channel_member(update, context):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please use /start first to register.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /use <code>\n\nExample: /use wandouyu"
        )
        return

    key_code = context.args[0].strip()
    result = db.use_card_key(key_code, user_id)

    if result is None:
        await update.message.reply_text("Code does not exist. Please check and try again.")
    elif result == -1:
        await update.message.reply_text("This code has reached its maximum number of uses.")
    elif result == -2:
        await update.message.reply_text("This code has expired.")
    elif result == -3:
        await update.message.reply_text("You have already redeemed this code.")
    else:
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"Code redeemed successfully!\nCredits added: {result}\nCurrent credits: {user['balance']}"
        )


async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /buy command - explain how to purchase credits."""
    if await reject_group_command(update):
        return

    if not await ensure_channel_member(update, context):
        return

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
    await update.message.reply_text(text, reply_markup=keyboard)
