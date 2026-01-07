# SheerID Auto-Verification Bot – Deployment Guide

This document explains how to deploy the SheerID Auto-Verification Telegram Bot.

---

## 📋 Table of Contents

1. [Requirements](#-requirements)
2. [Quick Deploy](#-quick-deploy)
3. [Docker Deployment](#-docker-deployment)
4. [Manual Deployment](#-manual-deployment)
5. [Configuration](#-configuration)
6. [FAQ](#-faq)
7. [Maintenance & Updates](#-maintenance--updates)

---

## 🔧 Requirements

### Minimum

- **OS**: Linux (Ubuntu 20.04+ recommended) / Windows 10+ / macOS 10.15+
- **Python**: 3.11+
- **MySQL**: 5.7+
- **Memory**: 512MB RAM (1GB+ recommended)
- **Disk**: 2GB+
- **Network**: Stable internet connection

### Recommended

- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.11
- **MySQL**: 8.0
- **Memory**: 2GB+ RAM
- **Disk**: 5GB+
- **Network**: 10 Mbps+ bandwidth

---

## 🚀 Quick Deploy

### Using Docker Compose (easiest)

```bash
# 1. Clone repository
git clone https://github.com/PastKing/tgbot-verify.git
cd tgbot-verify

# 2. Configure environment variables
cp env.example .env
nano .env  # fill in your values

# 3. Start services
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Stop services
docker-compose down
```

Once the containers are up and no obvious errors show in the logs, the bot should be running.

---

## 🐳 Docker Deployment

### Method 1: Docker Compose (recommended)

#### 1. Prepare `.env`

Create `.env` in the project root:

```env
# Telegram Bot
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
CHANNEL_USERNAME=pk_oa
CHANNEL_URL=https://t.me/pk_oa
ADMIN_USER_ID=123456789

# MySQL
MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_USER=tgbot_user
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=tgbot_verify
```

You can also add `CHANNEL_ID` and `SECONDARY_CHANNEL_URL` here if you use a private channel or a backup channel.

#### 2. Start services

```bash
docker-compose up -d
```

#### 3. Check status

```bash
# Show container status
docker-compose ps

# Follow live logs
docker-compose logs -f

# Show the last 50 lines of logs
docker-compose logs --tail=50
```

#### 4. Restart

```bash
# Restart all services
docker-compose restart

# Restart a single service
docker-compose restart tgbot
```

#### 5. Update code

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Method 2: Manual Docker run

```bash
# 1. Build image
docker build -t tgbot-verify:latest .

# 2. Run container
docker run -d \
  --name tgbot-verify \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  tgbot-verify:latest

# 3. Follow logs
docker logs -f tgbot-verify

# 4. Stop container
docker stop tgbot-verify

# 5. Remove container
docker rm tgbot-verify
```

---

## 🔨 Manual Deployment

### Linux / macOS

#### 1. Install dependencies

```bash
# Ubuntu/Debian example
sudo apt update
sudo apt install -y python3.11 python3.11-pip python3.11-venv mysql-server

# macOS with Homebrew
brew install python@3.11 mysql
```

#### 2. Create virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
```

#### 3. Install Python packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

#### 4. Set up MySQL database

```bash
# Login to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE tgbot_verify CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tgbot_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON tgbot_verify.* TO 'tgbot_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 5. Configure environment

```bash
cp env.example .env
nano .env  # edit configuration
```

#### 6. Run the bot

```bash
# Foreground (testing)
python bot.py

# Background (using nohup)
nohup python bot.py > bot.log 2>&1 &

# Background (using screen)
screen -S tgbot
python bot.py
# Ctrl+A then D to detach
# screen -r tgbot to reattach
```

### Windows

#### 1. Install dependencies

- Install [Python 3.11+](https://www.python.org/downloads/)
- Install [MySQL](https://dev.mysql.com/downloads/installer/)

#### 2. Create virtual environment

```cmd
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Python packages

```cmd
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

#### 4. Create database

Use MySQL Workbench or the MySQL command line to create the `tgbot_verify` database and user as in the Linux example.

#### 5. Configure `.env`

Copy `env.example` to `.env` and edit your values.

#### 6. Run the bot

```cmd
python bot.py
```

---

## ⚙️ Configuration

### Environment Variables

#### Telegram

```env
# Bot Token (required) – obtain from @BotFather
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Channel username (optional) – without @
CHANNEL_USERNAME=pk_oa

# Channel URL (optional)
CHANNEL_URL=https://t.me/pk_oa

# Private channel ID (optional) – used for membership checks, 0 disables this
CHANNEL_ID=0

# Backup channel URL (optional)
SECONDARY_CHANNEL_URL=

# Admin Telegram user ID (required) – use @userinfobot to get this
ADMIN_USER_ID=123456789
```

#### MySQL

```env
# Database host (required)
MYSQL_HOST=localhost         # local DB
# MYSQL_HOST=192.168.1.100  # remote DB
# MYSQL_HOST=mysql          # Docker Compose service name

# Database port (optional, default 3306)
MYSQL_PORT=3306

# Database user (required)
MYSQL_USER=tgbot_user

# Database password (required)
MYSQL_PASSWORD=your_secure_password

# Database name (required)
MYSQL_DATABASE=tgbot_verify
```

### Credit System

Configure in `config.py`:

```python
# Credit configuration
VERIFY_COST = 1         # Credits consumed per verification
CHECKIN_REWARD = 1      # Credits for daily check-in
# INVITE_REWARD is used internally; current effective rule:
# every 10 successful invites = +1 credit
INVITE_REWARD = 2
REGISTER_REWARD = 1     # Credits for first-time registration
```

### Concurrency Control

Adjust in `utils/concurrency.py` if needed:

```python
# Calculate concurrency based on system resources
_base_concurrency = _calculate_max_concurrency()

# Semaphore limits per verification type
_verification_semaphores = {
    "gemini_one_pro": Semaphore(_base_concurrency // 5),
    "chatgpt_teacher_k12": Semaphore(_base_concurrency // 5),
    "spotify_student": Semaphore(_base_concurrency // 5),
    "youtube_student": Semaphore(_base_concurrency // 5),
    "bolt_teacher": Semaphore(_base_concurrency // 5),
}
```

---

## 🔍 FAQ

### 1. Invalid Bot Token

**Error**: `telegram.error.InvalidToken: The token was rejected by the server.`

**Fix:**

- Check that `BOT_TOKEN` in `.env` is correct
- Ensure there are no extra spaces or quotes
- Regenerate the token via @BotFather if necessary

---

### 2. Database Connection Failed

**Error**: `pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")`

**Fix:**

- Check if MySQL is running: `systemctl status mysql`
- Verify host/port/user/password in `.env`
- Check firewall rules
- Confirm that the database user has proper privileges

---

### 3. Playwright Browser Not Installed

**Error**: `playwright._impl._api_types.Error: Executable doesn't exist`

**Fix:**

```bash
playwright install chromium
# Or, for extra system dependencies:
playwright install-deps chromium
```

---

### 4. Port in Use

**Symptom**: Docker container fails to start due to port conflicts.

**Fix:**

```bash
# Check which process uses the port
netstat -tlnp | grep :3306

# Adjust port mappings in docker-compose.yml if necessary
```

---

### 5. Out of Memory

**Symptom**: The server crashes due to low memory.

**Fix:**

- Upgrade server RAM
- Reduce concurrency in `utils/concurrency.py`
- Add swap:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

### 6. Log Files Too Large

**Symptom**: Logs consume too much disk space.

**Fix:**

- Docker already limits logs (see `docker-compose.yml`)
- Manually truncate logs:
  ```bash
  truncate -s 0 logs/*.log
  ```
- Or configure log rotation (logrotate, Docker log options, etc.)

---

## 🔄 Maintenance & Updates

### View Logs

```bash
# Docker Compose
docker-compose logs -f --tail=100

# Manual deployment
tail -f bot.log
tail -f logs/bot.log
```

### Backup the Database

```bash
# Full backup
mysqldump -u tgbot_user -p tgbot_verify > backup_$(date +%Y%m%d).sql

# Data-only backup
mysqldump -u tgbot_user -p --no-create-info tgbot_verify > data_backup.sql

# Restore from backup
mysql -u tgbot_user -p tgbot_verify < backup.sql
```

### Update Code

```bash
# Pull latest code
git pull origin main

# Docker deployment
docker-compose down
docker-compose up -d --build

# Manual deployment
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

### Service Monitoring

#### Using systemd (recommended on Linux)

Create `/etc/systemd/system/tgbot-verify.service`:

```ini
[Unit]
Description=SheerID Telegram Verification Bot
After=network.target mysql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/tgbot-verify
ExecStart=/path/to/tgbot-verify/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tgbot-verify
sudo systemctl start tgbot-verify
sudo systemctl status tgbot-verify
```

#### Using supervisor

Install:

```bash
sudo apt install supervisor
```

Create `/etc/supervisor/conf.d/tgbot-verify.conf`:

```ini
[program:tgbot-verify]
directory=/path/to/tgbot-verify
command=/path/to/tgbot-verify/venv/bin/python bot.py
autostart=true
autorestart=true
stderr_logfile=/var/log/tgbot-verify.err.log
stdout_logfile=/var/log/tgbot-verify.out.log
user=ubuntu
```

Start:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start tgbot-verify
```

---

## 🔒 Security Recommendations

1. **Use strong passwords**
   - Rotate your Bot Token periodically
   - Use a strong DB password (16+ characters)
   - Do not use default credentials

2. **Limit DB access**

   ```sql
   -- Only allow local connections
   CREATE USER 'tgbot_user'@'localhost' IDENTIFIED BY 'password';

   -- Or allow specific IP
   CREATE USER 'tgbot_user'@'192.168.1.100' IDENTIFIED BY 'password';
   ```

3. **Configure a firewall**

   ```bash
   # Only open necessary ports
   sudo ufw allow 22/tcp      # SSH
   sudo ufw enable
   ```

4. **Keep system and dependencies updated**

   ```bash
   sudo apt update && sudo apt upgrade
   pip install --upgrade -r requirements.txt
   ```

5. **Backup strategy**
   - Schedule daily DB backups
   - Keep at least 7 days of backups
   - Periodically test backup restore

---

## 📞 Support

- 📺 Telegram channel: https://t.me/pk_oa  
- 🐛 Issues & bug reports: <https://github.com/PastKing/tgbot-verify/issues>

---

<p align="center">
  <strong>Good luck with your deployment!</strong>
</p>
