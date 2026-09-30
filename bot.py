import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import db
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

START="🟢 Start Work"
OFF="🔴 Off Work"
EAT="🍽️ Eat"
SMOKE="🚬 Smoke"
TOILET="🚻 Toilet"
BACK="🟢 Back to Seat"

def keyboard():
    return ReplyKeyboardMarkup([[START,OFF],[EAT,SMOKE,TOILET],[BACK]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u=update.effective_user
    db.register_employee(u.id,u.full_name,u.username)
    await update.message.reply_text("Choose an action:", reply_markup=keyboard())

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u=update.effective_user
    text=(update.message.text or "").strip()
    db.register_employee(u.id,u.full_name,u.username)
    current=db.active_event(u.id)

    if text==START:
        if current:
            await update.message.reply_text("⚠️ You already have an active status.")
            return
        db.start_active(u.id,"work")
        await update.message.reply_text("🟢 Start Work recorded.")

    elif text==OFF:
        if not current:
            await update.message.reply_text("You are not currently working.")
            return
        if current["event_type"]!="work":
            await update.message.reply_text("⚠️ Finish your break with Back to Seat first.")
            return
        db.close_active(u.id)
        await update.message.reply_text("🔴 Off Work recorded.")

    elif text in (EAT,SMOKE,TOILET):
        if not current:
            await update.message.reply_text("⚠️ Press Start Work first.")
            return
        if current["event_type"]!="work":
            await update.message.reply_text("⚠️ You are already on a break.")
            return
        kind={EAT:"eat",SMOKE:"smoke",TOILET:"toilet"}[text]
        db.start_active(u.id,kind)
        limit=db.get_limits()[kind]
        await update.message.reply_text(
            f"{text} started. Allowed: {limit} minutes.\n"
            "Press Back to Seat when you return."
        )

    elif text==BACK:
        if not current:
            await update.message.reply_text("There is no active break.")
            return
        if current["event_type"]=="work":
            await update.message.reply_text("You are already at your seat.")
            return
        _,duration,late=db.close_active(u.id)
        db.start_active(u.id,"work")
        if late:
            await update.message.reply_text(
                f"🟢 Back to Seat recorded.\nDuration: {duration} min\n⚠️ Late by {late} min."
            )
        else:
            await update.message.reply_text(
                f"🟢 Back to Seat recorded.\nDuration: {duration} min\n✅ On time."
            )
    else:
        await update.message.reply_text("Please use the buttons.",reply_markup=keyboard())

def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN is missing.")
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle))
    print("Office bot is running...")
    app.run_polling()

if __name__=="__main__":
    main()
