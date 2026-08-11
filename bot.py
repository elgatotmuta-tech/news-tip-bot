import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
EDITOR_GROUP_ID = os.getenv("EDITOR_GROUP_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📰 သတင်းပေးပို့ရန်"],
        ["🚨 အရေးပေါ်သတင်း"],
        ["ℹ️ သတင်းပေးပို့နည်း"],
    ]

    await update.message.reply_text(
        "မင်္ဂလာပါ။ သင့်သတင်းအချက်အလက်ကို "
        "ကျွန်ုပ်တို့သတင်းဌာနသို့ ပေးပို့နိုင်ပါတယ်။\n\n"
        "ကျေးဇူးပြု၍ အောက်ပါခလုတ်တစ်ခုကို ရွေးပါ။",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        ),
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text or ""

    if text == "📰 သတင်းပေးပို့ရန်":
        await update.message.reply_text(
            "သတင်းဖြစ်စဉ်ကို အသေးစိတ်ရေးပေးပါ။\n\n"
            "ဥပမာ - ဘာဖြစ်ခဲ့သလဲ၊ ဘယ်နေရာမှာဖြစ်သလဲ၊ "
            "ဘယ်အချိန်မှာဖြစ်သလဲ စသည်တို့ကို ရေးပေးပါ။"
        )
        context.user_data["submitting_news"] = True
        return

    if text == "🚨 အရေးပေါ်သတင်း":
        await update.message.reply_text(
            "🚨 အရေးပေါ်သတင်းအတွက် ဖြစ်စဉ်၊ နေရာ၊ အချိန်နဲ့ "
            "သိရှိထားသမျှကို ချက်ချင်းပေးပို့ပါ။"
        )
        context.user_data["submitting_news"] = True
        return

    if text == "ℹ️ သတင်းပေးပို့နည်း":
        await update.message.reply_text(
            "သတင်းပေးပို့ရာတွင် ဖြစ်စဉ်၊ နေရာ၊ အချိန်နှင့် "
            "ဓာတ်ပုံ/ဗီဒီယိုရှိပါက ပေးပို့နိုင်ပါတယ်။"
        )
        return

    if context.user_data.get("submitting_news"):
        user = update.effective_user

        report = (
            "🆕 NEW NEWS TIP\n\n"
            f"👤 User: {user.first_name or 'Unknown'}\n"
            f"🆔 Telegram ID: {user.id}\n\n"
            f"📝 သတင်း:\n{text}"
        )

        if EDITOR_GROUP_ID:
            try:
                await context.bot.send_message(
                    chat_id=int(EDITOR_GROUP_ID),
                    text=report,
                )
            except Exception as e:
                print(f"Editor group error: {e}")

        await update.message.reply_text(
            "✅ သတင်းကို လက်ခံရရှိပါပြီ။\n"
            "အယ်ဒီတာအဖွဲ့က စိစစ်ပြီး လိုအပ်ပါက "
            "ပြန်လည်ဆက်သွယ်ပါမယ်။"
        )

        context.user_data["submitting_news"] = False
        return

    await update.message.reply_text(
        "သတင်းပေးပို့လိုပါက /start ကိုနှိပ်ပါ။"
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("News Tip Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
