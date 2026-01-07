"""Message templates for user-facing texts."""
from config import (
    CHANNEL_URL,
    SECONDARY_CHANNEL_URL,
    VERIFY_COST,
    HELP_NOTION_URL,
    REGISTER_REWARD,
    OWNER_USERNAME,
    CREDIT_BRONZE_PRICE,
    CREDIT_BRONZE_CREDITS,
    CREDIT_SILVER_PRICE,
    CREDIT_SILVER_CREDITS,
)


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Return the welcome message shown after /start registration."""
    msg = (
        f"🎉 Welcome, {full_name}!\n"
        f"You have successfully registered and received {REGISTER_REWARD} credit(s).\n"
    )
    if invited_by:
        msg += (
            "Thank you for joining via an invite link.\n"
            "The inviter's invite count has increased by 1. "
            "For every 10 successful invites, they automatically receive 1 extra credit.\n"
        )

    msg += (
        "\nThis bot can automatically complete SheerID verification.\n"
        "Quick start:\n"
        "/about  - Learn what this bot can do\n"
        "/balance - Check your credit balance\n"
        "/help   - View the full command list\n\n"
        "Earn more credits:\n"
        "/qd      - Daily check-in\n"
        "/invite  - Invite friends (every 10 successful invites = +1 credit)\n"
        "/use <code> - Redeem a gift/credit code\n"
        "/buy     - Buy credit packages\n"
        f"Join the channel: {CHANNEL_URL}"
    )
    if SECONDARY_CHANNEL_URL:
        msg += f"\nBackup channel: {SECONDARY_CHANNEL_URL}"
    return msg


def get_about_message() -> str:
    """Return the /about message."""
    msg = (
        "🤖 SheerID Auto Verification Bot\n"
        "\n"
        "What this bot does:\n"
        "- Automatically completes SheerID student/teacher verification\n"
        "- Supports Gemini One Pro, ChatGPT Teacher K12, Spotify Student, "
        "YouTube Student, and Bolt.new Teacher\n"
        "\n"
        "How to get credits:\n"
        f"- Registration bonus: {REGISTER_REWARD} credit(s)\n"
        "- Daily check-in: +1 credit\n"
        "- Invite friends: every 10 successful invites = +1 credit\n"
        "- Redeem codes (according to code rules)\n"
        "- Buy credits with /buy (Bronze / Silver packages)\n"
        f"- Main channel: {CHANNEL_URL}\n"
    )
    if SECONDARY_CHANNEL_URL:
        msg += f"- Backup channel: {SECONDARY_CHANNEL_URL}\n"

    msg += (
        "\n"
        "How to use verification commands:\n"
        "1. Start verification on the website and copy the full SheerID URL\n"
        "2. Send /verify, /verify2, /verify3, /verify4 or /verify5 with that URL\n"
        "3. Wait for processing and then open the result link\n"
        "4. For Bolt.new, the code is fetched automatically; "
        "you can also use /getV4Code <verification_id> later\n"
        "\n"
        "You can also send /help and tap the buttons below to see detailed guides "
        "for each verification type."
    )
    return msg


def get_help_message(is_admin: bool = False) -> str:
    """Return the main help text."""
    msg = (
        "📖 SheerID Auto Verification Bot - Help\n"
        "\n"
        "User commands:\n"
        "/start   - Start using the bot (register)\n"
        "/about   - Learn what this bot can do\n"
        "/balance - View your credit balance\n"
        "/qd      - Daily check-in (+1 credit)\n"
        "/invite  - Generate an invite link "
        "(every 10 successful invites = +1 credit)\n"
        "/use <code> - Redeem a gift/credit code\n"
        "/buy     - View how to buy credits\n"
        f"/verify <url>  - Gemini One Pro verification (-{VERIFY_COST} credit)\n"
        f"/verify2 <url> - ChatGPT Teacher K12 verification "
        f"(-{VERIFY_COST} credit)\n"
        f"/verify3 <url> - Spotify Student verification "
        f"(-{VERIFY_COST} credit)\n"
        f"/verify4 <url> - Bolt.new Teacher verification "
        f"(-{VERIFY_COST} credit)\n"
        f"/verify5 <url> - YouTube Student Premium verification "
        f"(-{VERIFY_COST} credit)\n"
        "/getV4Code <verification_id> - Get Bolt.new verification code\n"
        "/help    - Show this help message\n"
        f"If verification fails, please read: {HELP_NOTION_URL}\n"
        "\n"
        "👇 You can also tap the buttons below to see detailed usage guides "
        "for each verification type, or to buy credits."
    )

    if is_admin:
        msg += (
            "\n\nAdmin commands:\n"
            "/addbalance <user_id> <amount> - Add credits to a user\n"
            "/block <user_id>    - Block a user\n"
            "/white <user_id>    - Unblock a user\n"
            "/blacklist          - View blocked users\n"
            "/genkey <code> <credits> [uses] [days] - Create a gift/credit code\n"
            "/listkeys           - List existing codes\n"
            "/broadcast <text>   - Broadcast a message to all users\n"
            "/admin              - Open admin panel (button-based help)\n"
        )

    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """Return the 'insufficient credits' message."""
    return (
        f"Not enough credits. {VERIFY_COST} credit(s) are required, "
        f"you currently have {current_balance}.\n\n"
        "How to get more credits:\n"
        "- Daily check-in: /qd\n"
        "- Invite friends: /invite (every 10 successful invites = +1 credit)\n"
        "- Redeem a code: /use <code>\n"
        "- Buy credits: /buy or tap the 🛒 Buy Credits button in /help"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Return usage instructions for a specific verification command."""
    return (
        f"Usage: {command} <SheerID URL>\n\n"
        "Example:\n"
        f"{command} https://services.sheerid.com/verify/xxx/?verificationId=xxx\n\n"
        "How to get the verification URL:\n"
        f"1. Open the {service_name} verification page\n"
        "2. Start the verification flow\n"
        "3. Copy the full URL from your browser's address bar\n"
        f"4. Send it together with the {command} command"
    )


def get_buy_message() -> str:
    """Return an explanation of credit purchase options."""
    return (
        "🛒 Credit packages\n\n"
        f"🥉 Bronze: {CREDIT_BRONZE_CREDITS} credit(s) - {CREDIT_BRONZE_PRICE}\n"
        f"🥈 Silver: {CREDIT_SILVER_CREDITS} credit(s) - {CREDIT_SILVER_PRICE}\n"
        "🥇 Gold / 💎 Diamond: Large/custom packages, please contact the admin\n\n"
        "📌 Notes:\n"
        "• 1 credit = 1 verification (for all /verify commands)\n"
        "• Every 10 successful invites = +1 extra credit (automatic)\n\n"
        f"To buy credits, please contact the admin @{OWNER_USERNAME}."
    )
