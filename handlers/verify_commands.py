"""Verification command handlers."""
import asyncio
import logging
import httpx
import time
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import VERIFY_COST
from database_mysql import Database
from one.sheerid_verifier import SheerIDVerifier as OneVerifier
from k12.sheerid_verifier import SheerIDVerifier as K12Verifier
from spotify.sheerid_verifier import SheerIDVerifier as SpotifyVerifier
from youtube.sheerid_verifier import SheerIDVerifier as YouTubeVerifier
from Boltnew.sheerid_verifier import SheerIDVerifier as BoltnewVerifier
from utils.messages import get_insufficient_balance_message, get_verify_usage_message
from utils.checks import ensure_channel_member

# Try to import concurrency control; if unavailable, fall back to a simple semaphore
try:
    from utils.concurrency import get_verification_semaphore
except ImportError:
    def get_verification_semaphore(verification_type: str):
        return asyncio.Semaphore(3)

logger = logging.getLogger(__name__)


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify - Gemini One Pro."""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    if not await ensure_channel_member(update, context):
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please use /start first to register.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify", "Gemini One Pro")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = OneVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct credits. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"Starting Gemini One Pro verification...\n"
        f"Verification ID: {verification_id}\n"
        f"{VERIFY_COST} credit(s) have been deducted.\n\n"
        "Please wait, this may take 1–2 minutes..."
    )

    try:
        verifier = OneVerifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "gemini_one_pro",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verification successful!\n\n"
            if result.get("pending"):
                result_msg += "Documents have been submitted and are pending manual review.\n"
            if result.get("redirect_url"):
                result_msg += f"Redirect URL:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verification failed: {result.get('message', 'Unknown error')}\n\n"
                f"{VERIFY_COST} credit(s) have been refunded."
            )
    except Exception as e:
        logger.error("Verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing: {str(e)}\n\n"
            f"{VERIFY_COST} credit(s) have been refunded."
        )


async def verify2_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify2 - ChatGPT Teacher K12."""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    if not await ensure_channel_member(update, context):
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please use /start first to register.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify2", "ChatGPT Teacher K12")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = K12Verifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct credits. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"Starting ChatGPT Teacher K12 verification...\n"
        f"Verification ID: {verification_id}\n"
        f"{VERIFY_COST} credit(s) have been deducted.\n\n"
        "Please wait, this may take 1–2 minutes..."
    )

    try:
        verifier = K12Verifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "chatgpt_teacher_k12",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verification successful!\n\n"
            if result.get("pending"):
                result_msg += "Documents have been submitted and are pending manual review.\n"
            if result.get("redirect_url"):
                result_msg += f"Redirect URL:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verification failed: {result.get('message', 'Unknown error')}\n\n"
                f"{VERIFY_COST} credit(s) have been refunded."
            )
    except Exception as e:
        logger.error("Verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing: {str(e)}\n\n"
            f"{VERIFY_COST} credit(s) have been refunded."
        )


async def verify3_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify3 - Spotify Student."""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    if not await ensure_channel_member(update, context):
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please use /start first to register.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify3", "Spotify Student")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # Parse verificationId
    verification_id = SpotifyVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct credits. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"🎵 Starting Spotify Student verification...\n"
        f"{VERIFY_COST} credit(s) have been deducted.\n\n"
        "📝 Generating student information...\n"
        "🎨 Generating student ID PNG...\n"
        "📤 Submitting documents..."
    )

    # Use semaphore to control concurrency
    semaphore = get_verification_semaphore("spotify_student")

    try:
        async with semaphore:
            verifier = SpotifyVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "spotify_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Spotify Student verification successful!\n\n"
            if result.get("pending"):
                result_msg += "✨ Documents submitted, waiting for SheerID review.\n"
                result_msg += "⏱️ Estimated review time: a few minutes.\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Redirect URL:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verification failed: {result.get('message', 'Unknown error')}\n\n"
                f"{VERIFY_COST} credit(s) have been refunded."
            )
    except Exception as e:
        logger.error("Spotify verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing: {str(e)}\n\n"
            f"{VERIFY_COST} credit(s) have been refunded."
        )


async def verify4_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify4 - Bolt.new Teacher (auto code retrieval)."""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    if not await ensure_channel_member(update, context):
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please use /start first to register.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify4", "Bolt.new Teacher")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # Parse externalUserId or verificationId
    external_user_id = BoltnewVerifier.parse_external_user_id(url)
    verification_id = BoltnewVerifier.parse_verification_id(url)

    if not external_user_id and not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct credits. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"🚀 Starting Bolt.new Teacher verification...\n"
        f"{VERIFY_COST} credit(s) have been deducted.\n\n"
        "📤 Submitting documents..."
    )

    # Use semaphore to control concurrency
    semaphore = get_verification_semaphore("bolt_teacher")

    try:
        async with semaphore:
            # Step 1: submit documents
            verifier = BoltnewVerifier(url, verification_id=verification_id)
            result = await asyncio.to_thread(verifier.verify)

        if not result.get("success"):
            # Submission failed, refund
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Document submission failed: {result.get('message', 'Unknown error')}\n\n"
                f"{VERIFY_COST} credit(s) have been refunded."
            )
            return

        vid = result.get("verification_id", "")
        if not vid:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Could not obtain verification ID.\n\n"
                f"{VERIFY_COST} credit(s) have been refunded."
            )
            return

        # Update message
        await processing_msg.edit_text(
            f"✅ Documents submitted!\n"
            f"📋 Verification ID: `{vid}`\n\n"
            "🔍 Automatically fetching the verification code...\n"
            "(Waiting up to 20 seconds)"
        )

        # Step 2: automatically get reward code (max 20 seconds)
        code = await _auto_get_reward_code(vid, max_wait=20, interval=5)

        if code:
            # Successfully obtained code
            result_msg = (
                "🎉 Verification successful!\n\n"
                "✅ Documents submitted\n"
                "✅ Review approved\n"
                "✅ Verification code obtained\n\n"
                f"🎁 Code: `{code}`\n"
            )
            if result.get("redirect_url"):
                result_msg += f"\n🔗 Redirect URL:\n{result['redirect_url']}"

            await processing_msg.edit_text(result_msg)

            # Save success record
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "success",
                f"Code: {code}",
                vid,
            )
        else:
            # No code within 20 seconds, ask user to query later
            await processing_msg.edit_text(
                "✅ Documents submitted successfully!\n\n"
                "⏳ The verification code has not been generated yet "
                "(review may take 1–5 minutes).\n\n"
                f"📋 Verification ID: `{vid}`\n\n"
                "💡 Please query later using:\n"
                f"`/getV4Code {vid}`\n\n"
                "Note: credits have already been charged; querying later does not cost extra."
            )

            # Save pending record
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "pending",
                "Waiting for review",
                vid,
            )

    except Exception as e:
        logger.error("Bolt.new verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing: {str(e)}\n\n"
            f"{VERIFY_COST} credit(s) have been refunded."
        )


async def _auto_get_reward_code(
    verification_id: str,
    max_wait: int = 20,
    interval: int = 5,
) -> Optional[str]:
    """
    Automatically poll SheerID for a reward code (lightweight polling).

    Args:
        verification_id: Verification ID returned by SheerID
        max_wait: Maximum time to wait in seconds
        interval: Polling interval in seconds

    Returns:
        The reward code as a string, or None if not available.
    """
    start_time = time.time()
    attempts = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            elapsed = int(time.time() - start_time)
            attempts += 1

            # Check timeout
            if elapsed >= max_wait:
                logger.info(f"Auto-fetch of reward code timed out after {elapsed}s; user should query manually.")
                return None

            try:
                # Query verification status
                response = await client.get(
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                )

                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep")

                    if current_step == "success":
                        # Get reward code
                        code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
                        if code:
                            logger.info(f"✅ Auto-fetched reward code: {code} (in {elapsed}s)")
                            return code
                    elif current_step == "error":
                        # Review failed
                        logger.warning(f"Verification review failed: {data.get('errorIds', [])}")
                        return None
                    # else: pending, continue polling

                # Wait for next poll
                await asyncio.sleep(interval)

            except Exception as e:
                logger.warning(f"Error while querying reward code: {e}")
                await asyncio.sleep(interval)

    return None


async def verify5_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify5 - YouTube Student Premium."""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    if not await ensure_channel_member(update, context):
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please use /start first to register.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify5", "YouTube Student Premium")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # Parse verificationId
    verification_id = YouTubeVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct credits. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"📺 Starting YouTube Student Premium verification...\n"
        f"{VERIFY_COST} credit(s) have been deducted.\n\n"
        "📝 Generating student information...\n"
        "🎨 Generating student ID PNG...\n"
        "📤 Submitting documents..."
    )

    # Use semaphore to control concurrency
    semaphore = get_verification_semaphore("youtube_student")

    try:
        async with semaphore:
            verifier = YouTubeVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "youtube_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ YouTube Student Premium verification successful!\n\n"
            if result.get("pending"):
                result_msg += "✨ Documents submitted, waiting for SheerID review.\n"
                result_msg += "⏱️ Estimated review time: a few minutes.\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Redirect URL:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verification failed: {result.get('message', 'Unknown error')}\n\n"
                f"{VERIFY_COST} credit(s) have been refunded."
            )
    except Exception as e:
        logger.error("YouTube verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing: {str(e)}\n\n"
            f"{VERIFY_COST} credit(s) have been refunded."
        )


async def getV4Code_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /getV4Code - get Bolt.new Teacher verification code."""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You have been blocked and cannot use this feature.")
        return

    if not await ensure_channel_member(update, context):
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please use /start first to register.")
        return

    # Check if verification_id is provided
    if not context.args:
        await update.message.reply_text(
            "Usage: /getV4Code <verification_id>\n\n"
            "Example: /getV4Code 6929436b50d7dc18638890d0\n\n"
            "The verification_id is returned to you after using /verify4."
        )
        return

    verification_id = context.args[0].strip()

    processing_msg = await update.message.reply_text(
        "🔍 Querying verification code, please wait..."
    )

    try:
        # Query SheerID API for the reward code
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
            )

            if response.status_code != 200:
                await processing_msg.edit_text(
                    f"❌ Query failed, status code: {response.status_code}\n\n"
                    "Please try again later or contact the admin."
                )
                return

            data = response.json()
            current_step = data.get("currentStep")
            reward_code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
            redirect_url = data.get("redirectUrl")

            if current_step == "success" and reward_code:
                result_msg = "✅ Verification successful!\n\n"
                result_msg += f"🎉 Code: `{reward_code}`\n\n"
                if redirect_url:
                    result_msg += f"Redirect URL:\n{redirect_url}"
                await processing_msg.edit_text(result_msg)
            elif current_step == "pending":
                await processing_msg.edit_text(
                    "⏳ Verification is still under review. Please try again later.\n\n"
                    "It usually takes 1–5 minutes. Please be patient."
                )
            elif current_step == "error":
                error_ids = data.get("errorIds", [])
                await processing_msg.edit_text(
                    "❌ Verification failed\n\n"
                    f"Error details: {', '.join(error_ids) if error_ids else 'Unknown error'}"
                )
            else:
                await processing_msg.edit_text(
                    f"⚠️ Current status: {current_step}\n\n"
                    "The verification code has not been generated yet. Please try again later."
                )

    except Exception as e:
        logger.error("Failed to get Bolt.new verification code: %s", e)
        await processing_msg.edit_text(
            f"❌ An error occurred while querying: {str(e)}\n\n"
            "Please try again later or contact the admin."
        )
