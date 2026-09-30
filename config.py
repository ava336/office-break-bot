import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me")
DB_PATH = os.environ.get("DB_PATH", "office.db")

DEFAULT_BREAK_LIMITS = {"eat": 30, "smoke": 10, "toilet": 10}
