# SheerID Auto-Verification Telegram Bot

![Stars](https://img.shields.io/github/stars/PastKing/tgbot-verify?style=social)
![Forks](https://img.shields.io/github/forks/PastKing/tgbot-verify?style=social)
![Issues](https://img.shields.io/github/issues/PastKing/tgbot-verify)
![License](https://img.shields.io/github/license/PastKing/tgbot-verify)

> 🤖 Automated SheerID student/teacher verification Telegram bot  
> Based on [@auto_sheerid_bot](https://t.me/auto_sheerid_bot) (GGBond) with improvements.

---

## 📋 Overview

This is a Python-based Telegram bot that automates SheerID student/teacher verification for multiple platforms.  
The bot automatically generates identity information, creates verification documents, and submits them to the SheerID platform, greatly simplifying the process.

> **⚠️ Important:**
>
> - Services such as **Gemini One Pro**, **ChatGPT Teacher K12**, **Spotify Student**, and **YouTube Premium Student** require updating verification data such as `programId` in each module’s configuration file before use. See the **“Must Read Before Use”** section below.
> - This project also includes an implementation approach and API documentation for **ChatGPT Military verification**. See [`military/README.md`](military/README.md) for details.

### 🎯 Supported Services

| Command   | Service                  | Type    | Status   | Description                                           |
|----------|--------------------------|---------|----------|-------------------------------------------------------|
| `/verify`  | Gemini One Pro           | Teacher | ✅ Stable | Google AI Studio Education Discount                  |
| `/verify2` | ChatGPT Teacher K12      | Teacher | ✅ Stable | OpenAI ChatGPT Education Discount                    |
| `/verify3` | Spotify Student          | Student | ✅ Stable | Spotify Student Subscription Discount                |
| `/verify4` | Bolt.new Teacher         | Teacher | ✅ Stable | Bolt.new Education Discount (auto reward code)       |
| `/verify5` | YouTube Premium Student  | Student | ⚠️ Beta  | YouTube Premium Student Discount (see notes below)   |

> **⚠️ YouTube Verification Notes**
>
> YouTube verification is currently in **beta**. Please read [`youtube/HELP.MD`](youtube/HELP.MD) carefully before using.
>
> **Key differences:**
> - YouTube’s original link format differs from other services
> - You must manually extract `programId` and `verificationId` from browser network logs
> - You then manually construct a standard SheerID verification URL
>
> **Usage steps:**
> 1. Visit the YouTube Premium student verification page
> 2. Open browser DevTools (F12) → Network tab
> 3. Start the verification process and search for `https://services.sheerid.com/rest/v2/verification/`
> 4. Extract `programId` from the request payload and `verificationId` from the response
> 5. Construct a link: `https://services.sheerid.com/verify/{programId}/?verificationId={verificationId}`
> 6. Submit this URL to the bot via `/verify5`

> **💡 ChatGPT Military Verification**
>
> This project documents the approach and APIs for ChatGPT Military SheerID verification.  
> The flow differs from normal student/teacher verification: you must call `collectMilitaryStatus` first to set the military status, then submit personal info.  
> See [`military/README.md`](military/README.md) for full details; you can integrate it into the bot based on that document.

### ✨ Key Features

- 🚀 **Automated flow**: One command to generate data, create documents, and submit verification
- 🎨 **Smart generation**: Auto-generates student/teacher ID PNG images
- 💰 **Credit system**: Multiple ways to earn (check-ins, invites, redemption codes, manual top-up)
- 🔐 **Reliable storage**: MySQL database with environment-based configuration
- ⚡ **Concurrency control**: Manages concurrent verification requests for stability
- 👥 **Admin tools**: Full user and credit management, broadcast, and card key system

---

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Bot Framework**: python-telegram-bot 20.0+
- **Database**: MySQL 5.7+
- **Browser Automation**: Playwright
- **HTTP Client**: httpx
- **Image/PDF**: Pillow, reportlab, xhtml2pdf
- **Env Management**: python-dotenv

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/PastKing/tgbot-verify.git
cd tgbot-verify
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure Environment Variables

Copy `env.example` to `.env` and fill in your values:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here
CHANNEL_USERNAME=your_channel
CHANNEL_URL=https://t.me/your_channel
CHANNEL_ID=0
SECONDARY_CHANNEL_URL=
ADMIN_USER_ID=your_admin_id

# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=tgbot_verify
```

### 4. Start the Bot

```bash
python bot.py
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# 1. Configure .env
cp env.example .env
nano .env

# 2. Start services
docker-compose up -d

# 3. View logs
docker-compose logs -f
```

### Manual Docker Deployment

```bash
# Build image
docker build -t tgbot-verify .

# Run container
docker run -d \
  --name tgbot-verify \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  tgbot-verify
```

---

## 📖 Usage

### User Commands

```bash
/start              # Start using (register)
/about              # Learn about bot features
/balance            # Show current credit balance
/qd                 # Daily check-in (+1 credit)
/invite             # Generate invite link (1 extra credit per 10 successful invites)
/use <code>         # Redeem credits with a card key
/verify <url>       # Gemini One Pro verification
/verify2 <url>      # ChatGPT Teacher K12 verification
/verify3 <url>      # Spotify Student verification
/verify4 <url>      # Bolt.new Teacher verification
/verify5 <url>      # YouTube Premium Student verification
/getV4Code <id>     # Get Bolt.new verification code
/help               # Show help and inline buttons
```

### Admin Commands

```bash
/addbalance <user_id> <credits>           # Add credits to a user
/block <user_id>                          # Block a user
/white <user_id>                          # Unblock a user
/blacklist                                # View blacklist
/genkey <code> <credits> [uses] [days]    # Create card key (optional multi-use and expiry)
/listkeys                                 # List card keys
/broadcast <text>                         # Broadcast a message to all users
/admin                                    # Open admin panel (inline help buttons)
```

### Typical Verification Flow

1. **Get a verification link**
   - Visit the relevant service’s verification page
   - Start the verification flow
   - Copy the full URL from your browser address bar (must contain `verificationId`)

2. **Submit to the bot**
   ```text
   /verify3 https://services.sheerid.com/verify/xxx/?verificationId=yyy
   ```

3. **Bot processing**
   - Bot generates identity information
   - Creates student/teacher ID image(s)
   - Submits everything to SheerID

4. **Receive result**
   - Review usually completes within a few minutes
   - On success, you receive a redirect URL (or reward code for some flows)

---

## 📁 Project Structure

```text
tgbot-verify/
├── bot.py                  # Main bot entrypoint
├── config.py               # Global configuration
├── database_mysql.py       # MySQL storage layer
├── .env                    # Environment variables (not committed)
├── env.example             # Environment variable template
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose config
├── handlers/               # Command handlers
│   ├── user_commands.py    # User-facing commands
│   ├── admin_commands.py   # Admin commands
│   └── verify_commands.py  # Verification commands
├── one/                    # Gemini One Pro verification module
├── k12/                    # ChatGPT K12 verification module
├── spotify/                # Spotify Student verification module
├── youtube/                # YouTube Premium Student verification module
├── Boltnew/                # Bolt.new Teacher verification module
├── military/               # ChatGPT Military verification docs/approach
└── utils/                  # Utility helpers
    ├── messages.py         # User-facing message templates
    ├── concurrency.py      # Concurrency control
    └── checks.py           # Permission & channel checks
```

---

## ⚙️ Configuration

### Environment Variables

| Variable              | Required | Description                                              | Default                 |
|-----------------------|----------|----------------------------------------------------------|-------------------------|
| `BOT_TOKEN`           | ✅       | Telegram Bot token                                       | -                       |
| `CHANNEL_USERNAME`    | ❌       | Public channel username (without `@`)                    | `pk_oa`                 |
| `CHANNEL_URL`         | ❌       | Public channel link                                      | `https://t.me/pk_oa`    |
| `CHANNEL_ID`          | ❌       | Numeric channel ID for membership checks (private OK)    | treated as disabled     |
| `SECONDARY_CHANNEL_URL` | ❌    | Backup channel link                                      | empty                   |
| `ADMIN_USER_ID`       | ✅       | Admin Telegram user ID                                   | -                       |
| `MYSQL_HOST`          | ✅       | MySQL host                                               | `localhost`             |
| `MYSQL_PORT`          | ❌       | MySQL port                                               | `3306`                  |
| `MYSQL_USER`          | ✅       | MySQL username                                           | -                       |
| `MYSQL_PASSWORD`      | ✅       | MySQL password                                           | -                       |
| `MYSQL_DATABASE`      | ✅       | Database name                                            | `tgbot_verify`          |

### Credit Configuration

You can customize credit rules in `config.py`:

```python
VERIFY_COST = 1         # Credits consumed per verification
CHECKIN_REWARD = 1      # Credits granted per daily check-in
# INVITE_REWARD is used as an internal coefficient.
# Current effective rule: every 10 successful invites = +1 credit.
INVITE_REWARD = 2
REGISTER_REWARD = 1     # Credits granted on first registration
```

---

## ⚠️ Must Read Before Use

**Before running the bot in production, you must review and update each module’s verification configuration.**

Because SheerID’s `programId` values may change over time, the following modules **must** be checked and updated:

- `one/config.py`      – **Gemini One Pro** (update `PROGRAM_ID` as needed)
- `k12/config.py`      – **ChatGPT Teacher K12**
- `spotify/config.py`  – **Spotify Student**
- `youtube/config.py`  – **YouTube Premium Student**
- `Boltnew/config.py`  – **Bolt.new Teacher** (recommended to verify `PROGRAM_ID`)

**How to get the latest `programId`:**

1. Visit the relevant service’s verification page.
2. Open DevTools → Network tab.
3. Start the verification flow.
4. Look for requests to `https://services.sheerid.com/rest/v2/verification/`.
5. Extract `programId` from the URL or request payload.
6. Update the corresponding `PROGRAM_ID` in that module’s `config.py`.

> If verification suddenly starts failing across all users for one service, it is very likely the `programId` has changed.

---

## 🔗 Links

- 📺 **Telegram Channel**: https://t.me/pk_oa  
- 🐛 **Issue Tracker**: <https://github.com/PastKing/tgbot-verify/issues>  
- 📖 **Deployment Guide**: [DEPLOY.md](DEPLOY.md)

---

## 🤝 Secondary Development

Contributions and forks are welcome. Please follow these rules:

1. **Preserve original author info**
   - Keep the original repository URL in code and documentation.
   - Explicitly mention that your project is based on this one.

2. **Open-source license**
   - This project uses the MIT License.
   - Derivative projects must remain open source as well.

3. **Commercial use**
   - Free for personal use.
   - For commercial use, you are responsible for your own modifications and maintenance.
   - No warranty or official support is provided.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

```text
MIT License

Copyright (c) 2025 PastKing

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Acknowledgments

- Thanks to [@auto_sheerid_bot](https://t.me/auto_sheerid_bot) (GGBond) for the original codebase.
- Thanks to all contributors who helped improve this project.
- Thanks to the SheerID platform for providing the verification infrastructure.

---

## 📊 Stats

[![Star History Chart](https://api.star-history.com/svg?repos=PastKing/tgbot-verify&type=Date)](https://star-history.com/#PastKing/tgbot-verify&Date)

---

## 📝 Changelog

### v2.0.0 (2025-01-12)

- ✨ Added Spotify Student and YouTube Premium Student flows (YouTube is beta, see `youtube/HELP.MD`)
- 🚀 Improved concurrency and performance
- 📝 Expanded documentation and deployment guide
- 🐛 Fixed known bugs

### v1.0.0

- 🎉 Initial release
- ✅ Support for Gemini, ChatGPT, Bolt.new flows

---

<p align="center">
  <strong>⭐ If this project helps you, please consider giving it a Star.</strong>
</p>

<p align="center">
  Made with ❤️ by <a href="https://github.com/PastKing">PastKing</a>
</p>
