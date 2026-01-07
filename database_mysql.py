"""MySQL database implementation.

Uses a MySQL server for persistent storage.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)


class MySQLDatabase:
    """MySQL database management helper."""

    def __init__(self):
        """Initialize database configuration and ensure tables exist."""
        import os

        # Read configuration from environment (recommended) or use defaults
        self.config = {
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "port": int(os.getenv("MYSQL_PORT", 3306)),
            "user": os.getenv("MYSQL_USER", "tgbot_user"),
            "password": os.getenv("MYSQL_PASSWORD", "your_password_here"),
            "database": os.getenv("MYSQL_DATABASE", "tgbot_verify"),
            "charset": "utf8mb4",
            "autocommit": False,
        }
        logger.info(
            "Initializing MySQL connection: %s@%s/%s",
            self.config["user"],
            self.config["host"],
            self.config["database"],
        )
        self.init_database()

    def get_connection(self):
        """Return a new database connection."""
        return pymysql.connect(**self.config)

    def init_database(self):
        """Create tables if they do not exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    full_name VARCHAR(255),
                    balance INT DEFAULT 1,
                    is_blocked TINYINT(1) DEFAULT 0,
                    invited_by BIGINT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_checkin DATETIME NULL,
                    INDEX idx_username (username),
                    INDEX idx_invited_by (invited_by)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            # Invitation records
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS invitations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    inviter_id BIGINT NOT NULL,
                    invitee_id BIGINT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_inviter (inviter_id),
                    INDEX idx_invitee (invitee_id),
                    FOREIGN KEY (inviter_id) REFERENCES users(user_id),
                    FOREIGN KEY (invitee_id) REFERENCES users(user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            # Verification records
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS verifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    verification_type VARCHAR(50) NOT NULL,
                    verification_url TEXT,
                    verification_id VARCHAR(255),
                    status VARCHAR(50) NOT NULL,
                    result TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_type (verification_type),
                    INDEX idx_created (created_at),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            # Card key table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS card_keys (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    key_code VARCHAR(100) UNIQUE NOT NULL,
                    balance INT NOT NULL,
                    max_uses INT DEFAULT 1,
                    current_uses INT DEFAULT 0,
                    expire_at DATETIME NULL,
                    created_by BIGINT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_key_code (key_code),
                    INDEX idx_created_by (created_by)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            # Card key usage table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS card_key_usage (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    key_code VARCHAR(100) NOT NULL,
                    user_id BIGINT NOT NULL,
                    used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_key_code (key_code),
                    INDEX idx_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            conn.commit()
            logger.info("MySQL table initialization completed")

        except Exception as e:
            logger.error("Failed to initialize MySQL tables: %s", e)
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def create_user(
        self, user_id: int, username: str, full_name: str, invited_by: Optional[int] = None
    ) -> bool:
        """Create a new user and optionally record the inviter."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (user_id, username, full_name, invited_by, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (user_id, username, full_name, invited_by),
            )

            if invited_by:
                # Record invitation relation
                cursor.execute(
                    """
                    INSERT INTO invitations (inviter_id, invitee_id, created_at)
                    VALUES (%s, %s, NOW())
                    """,
                    (invited_by, user_id),
                )

                # For every 10 valid invitations, grant +1 credit
                cursor.execute(
                    "SELECT COUNT(*) FROM invitations WHERE inviter_id = %s",
                    (invited_by,),
                )
                total_row = cursor.fetchone()
                try:
                    total_invites = int(total_row[0]) if total_row and total_row[0] is not None else 0
                except (TypeError, ValueError):
                    total_invites = 0

                if total_invites > 0 and total_invites % 10 == 0:
                    cursor.execute(
                        "UPDATE users SET balance = balance + 1 WHERE user_id = %s",
                        (invited_by,),
                    )

            conn.commit()
            return True

        except pymysql.err.IntegrityError:
            conn.rollback()
            return False
        except Exception as e:
            logger.error("Failed to create user: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Fetch a user record as a dict, converting datetimes to ISO strings."""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()

            if row:
                # Create a copy and convert datetime fields to ISO strings
                result = dict(row)
                if result.get("created_at"):
                    result["created_at"] = result["created_at"].isoformat()
                if result.get("last_checkin"):
                    result["last_checkin"] = result["last_checkin"].isoformat()
                return result
            return None

        finally:
            cursor.close()
            conn.close()

    def user_exists(self, user_id: int) -> bool:
        """Return True if the user exists."""
        return self.get_user(user_id) is not None

    def is_user_blocked(self, user_id: int) -> bool:
        """Return True if the user is blocked."""
        user = self.get_user(user_id)
        return bool(user and user["is_blocked"] == 1)

    def block_user(self, user_id: int) -> bool:
        """Block a user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE users SET is_blocked = 1 WHERE user_id = %s", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error("Failed to block user: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def unblock_user(self, user_id: int) -> bool:
        """Unblock a user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE users SET is_blocked = 0 WHERE user_id = %s", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error("Failed to unblock user: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def get_blacklist(self) -> List[Dict]:
        """Return a list of all blocked users."""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            cursor.execute("SELECT * FROM users WHERE is_blocked = 1")
            return list(cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    def get_invitation_stats(self, inviter_id: int) -> Dict[str, int]:
        """Return invitation stats for an inviter."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT COUNT(*) FROM invitations WHERE inviter_id = %s",
                (inviter_id,),
            )
            row = cursor.fetchone()
            total_invites = int(row[0]) if row and row[0] is not None else 0

            invite_credits = total_invites // 10
            next_threshold = (invite_credits + 1) * 10
            invites_to_next_credit = (
                max(next_threshold - total_invites, 0) if total_invites < next_threshold else 0
            )

            return {
                "total_invites": total_invites,
                "invite_credits": invite_credits,
                "invites_to_next_credit": invites_to_next_credit,
            }
        except Exception as e:
            logger.error("Failed to get invitation stats: %s", e)
            return {
                "total_invites": 0,
                "invite_credits": 0,
                "invites_to_next_credit": 0,
            }
        finally:
            cursor.close()
            conn.close()

    def add_balance(self, user_id: int, amount: int) -> bool:
        """Increase a user's credit balance."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE users SET balance = balance + %s WHERE user_id = %s",
                (amount, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error("Failed to add credits: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def deduct_balance(self, user_id: int, amount: int) -> bool:
        """Deduct credits from a user if they have enough."""
        user = self.get_user(user_id)
        if not user or user["balance"] < amount:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE users SET balance = balance - %s WHERE user_id = %s",
                (amount, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error("Failed to deduct credits: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def can_checkin(self, user_id: int) -> bool:
        """Return True if the user can check in today."""
        user = self.get_user(user_id)
        if not user:
            return False

        last_checkin = user.get("last_checkin")
        if not last_checkin:
            return True

        last_date = datetime.fromisoformat(last_checkin).date()
        today = datetime.now().date()

        return last_date < today

    def checkin(self, user_id: int) -> bool:
        """Perform daily check-in using an atomic SQL update."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Use an atomic SQL update to avoid race conditions:
            # only update when last_checkin is NULL or earlier than today.
            cursor.execute(
                """
                UPDATE users
                SET balance = balance + 1, last_checkin = NOW()
                WHERE user_id = %s 
                AND (
                    last_checkin IS NULL 
                    OR DATE(last_checkin) < CURDATE()
                )
                """,
                (user_id,),
            )
            conn.commit()

            # If affected_rows > 0, the check-in succeeded
            success = cursor.rowcount > 0
            return success

        except Exception as e:
            logger.error("Check-in failed: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def add_verification(
        self,
        user_id: int,
        verification_type: str,
        verification_url: str,
        status: str,
        result: str = "",
        verification_id: str = "",
    ) -> bool:
        """Insert a verification record."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO verifications
                (user_id, verification_type, verification_url, verification_id, status, result, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (user_id, verification_type, verification_url, verification_id, status, result),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error("Failed to add verification record: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user_verifications(self, user_id: int) -> List[Dict]:
        """Return a list of verifications for a given user."""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            cursor.execute(
                """
                SELECT * FROM verifications
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return list(cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    def create_card_key(
        self,
        key_code: str,
        balance: int,
        created_by: int,
        max_uses: int = 1,
        expire_days: Optional[int] = None,
    ) -> bool:
        """Create a new card key."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            expire_at = None
            if expire_days:
                expire_at = datetime.now() + timedelta(days=expire_days)

            cursor.execute(
                """
                INSERT INTO card_keys (key_code, balance, max_uses, created_by, created_at, expire_at)
                VALUES (%s, %s, %s, %s, NOW(), %s)
                """,
                (key_code, balance, max_uses, created_by, expire_at),
            )
            conn.commit()
            return True

        except pymysql.err.IntegrityError:
            logger.error("Card key already exists: %s", key_code)
            conn.rollback()
            return False
        except Exception as e:
            logger.error("Failed to create card key: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def use_card_key(self, key_code: str, user_id: int) -> Optional[int]:
        """Use a card key and return the number of credits granted."""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            # Find card key
            cursor.execute(
                "SELECT * FROM card_keys WHERE key_code = %s",
                (key_code,),
            )
            card = cursor.fetchone()

            if not card:
                return None

            # Check expiry
            if card["expire_at"] and datetime.now() > card["expire_at"]:
                return -2

            # Check usage limit
            if card["current_uses"] >= card["max_uses"]:
                return -1

            # Check whether this user has already used this key
            cursor.execute(
                "SELECT COUNT(*) as count FROM card_key_usage WHERE key_code = %s AND user_id = %s",
                (key_code, user_id),
            )
            count = cursor.fetchone()
            if count["count"] > 0:
                return -3

            # Increment usage count
            cursor.execute(
                "UPDATE card_keys SET current_uses = current_uses + 1 WHERE key_code = %s",
                (key_code,),
            )

            # Record usage
            cursor.execute(
                "INSERT INTO card_key_usage (key_code, user_id, used_at) VALUES (%s, %s, NOW())",
                (key_code, user_id),
            )

            # Add credits to the user
            cursor.execute(
                "UPDATE users SET balance = balance + %s WHERE user_id = %s",
                (card["balance"], user_id),
            )

            conn.commit()
            return card["balance"]

        except Exception as e:
            logger.error("Failed to use card key: %s", e)
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def get_card_key_info(self, key_code: str) -> Optional[Dict]:
        """Return a single card key record."""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            cursor.execute("SELECT * FROM card_keys WHERE key_code = %s", (key_code,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def get_all_card_keys(self, created_by: Optional[int] = None) -> List[Dict]:
        """Return all card keys, optionally filtered by creator."""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            if created_by:
                cursor.execute(
                    "SELECT * FROM card_keys WHERE created_by = %s ORDER BY created_at DESC",
                    (created_by,),
                )
            else:
                cursor.execute("SELECT * FROM card_keys ORDER BY created_at DESC")

            return list(cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    def get_all_user_ids(self) -> List[int]:
        """Return a list of all user IDs."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT user_id FROM users")
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            cursor.close()
            conn.close()


# Global alias to keep compatibility with previous SQLite-based code
Database = MySQLDatabase

