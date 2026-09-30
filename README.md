# Office Break & Attendance Bot

1. Install:
   `pip install -r requirements.txt`

2. Create a bot with Telegram @BotFather using `/newbot`.

3. Set environment variables:
   - `BOT_TOKEN` = your BotFather token
   - `ADMIN_PASSWORD` = your admin panel password

4. Run:
   - `python bot.py`
   - `python admin.py`

5. Open `http://127.0.0.1:5000`

Employee buttons:
Start Work / Off Work / Eat / Smoke / Toilet / Back to Seat

Default limits:
Eat 30 min, Smoke 10 min, Toilet 10 min.

Never share your bot token.
For production, use HTTPS and a stronger admin authentication setup.
