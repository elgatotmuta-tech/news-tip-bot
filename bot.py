import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY is missing")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

TOKEN = os.environ["BOT_TOKEN"]
EDITOR_GROUP_ID = os.getenv("EDITOR_GROUP_ID")

RENDER_URL = os.environ.get(
    "RENDER_EXTERNAL_URL",
    "http://localhost:10000"
)

WEBHOOK_PATH = "/telegram/webhook"
WEBHOOK_URL = RENDER_URL + WEBHOOK_PATH

telegram_app = Application.builder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📰 သတင်းပေးပို့ရန်"],
        ["🚨 အရေးပေါ်သတင်း"],
        ["ℹ️ သတင်းပေးပို့နည်း"],
    ]

    await update.message.reply_text(
        "မင်္ဂလာပါ။\n\n"
        "သင့်ထံမှ သတင်းအချက်အလက်၊ ဓာတ်ပုံနှင့် "
        "ဗီဒီယိုများကို ကျွန်ုပ်တို့သတင်းဌာနသို့ ပေးပို့နိုင်ပါတယ်။\n\n"
        "အောက်ပါခလုတ်ကို ရွေးချယ်ပါ။",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        ),
    )

async def handle_message(update, context):
    user = update.effective_user
    message = update.message

    data = {
        "telegram_user_id": user.id if user else None,
        "telegram_username": user.username if user else None,
        "telegram_name": user.full_name if user else None,
        "message": message.text or message.caption or "",
    }

    supabase.table("news_tips").insert(data).execute()

response = (
    supabase
    .table("news_tips")
    .insert (data) = {
    "telegram_user_id": user.id if user else None,
    "telegram_username": user.username if user else None,
    "telegram_name": user.full_name if user else None,
    "message": message.text or message.caption or "",
    "photo_file_id": photo_file_id,
}
    .execute()
)
    if not update.message:
        return

    text = update.message.text or ""

    if text == "📰 သတင်းပေးပို့ရန်":
        context.user_data["submitting_news"] = True

        await update.message.reply_text(
            "📰 သတင်းပေးပို့ရန်\n\n"
            "ဖြစ်စဉ်ကို အသေးစိတ်ရေးပေးပါ။\n\n"
            "ဥပမာ -\n"
            "• ဘာဖြစ်ခဲ့သလဲ\n"
            "• ဘယ်နေရာမှာဖြစ်သလဲ\n"
            "• ဘယ်အချိန်မှာဖြစ်သလဲ\n"
            "• သိရှိထားသမျှ အချက်အလက်များ"
        )
        return

    if text == "🚨 အရေးပေါ်သတင်း":
        context.user_data["submitting_news"] = True

        await update.message.reply_text(
            "🚨 အရေးပေါ်သတင်း\n\n"
            "ဖြစ်စဉ်၊ နေရာ၊ အချိန်နဲ့ "
            "သိရှိထားသမျှကို ပေးပို့ပါ။"
        )
        return

    if text == "ℹ️ သတင်းပေးပို့နည်း":
        await update.message.reply_text(
            "ℹ️ သတင်းပေးပို့နည်း\n\n"
            "သတင်းဖြစ်စဉ်၊ နေရာ၊ အချိန်၊ "
            "ဓာတ်ပုံနှင့် ဗီဒီယိုများကို ပေးပို့နိုင်ပါတယ်။\n\n"
            "သတင်းအချက်အလက် မမှန်ကန်ပါက "
            "သတင်းမီဒီယာမှ စိစစ်ပြီးမှသာ အသုံးပြုပါမယ်။"
        )
        return

    if context.user_data.get("submitting_news"):
        user = update.effective_user

        report = (
            "🆕 NEW NEWS TIP\n"
            "━━━━━━━━━━━━━━\n\n"
            f"👤 ပေးပို့သူ: {user.first_name or 'Unknown'}\n"
            f"🆔 Telegram ID: {user.id}\n\n"
            f"📝 သတင်းအချက်အလက်:\n{text}\n\n"
            "━━━━━━━━━━━━━━\n"
            "Status: NEW"
        )

        if EDITOR_GROUP_ID:
            try:
                await context.bot.send_message(
                    chat_id=int(EDITOR_GROUP_ID),
                    text=report,
                )
            except Exception as e:
                print("EDITOR GROUP ERROR:", e)

        await update.message.reply_text(
            "✅ သတင်းကို လက်ခံရရှိပါပြီ။\n\n"
            "အယ်ဒီတာအဖွဲ့က စိစစ်ပြီး "
            "လိုအပ်ပါက ပြန်လည်ဆက်သွယ်ပါမယ်။"
        )

        context.user_data["submitting_news"] = False
        return

    await update.message.reply_text(
        "သတင်းပေးပို့လိုပါက /start ကိုနှိပ်ပါ။"
    )


telegram_app.add_handler(
    CommandHandler("start", start)
)
async def group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    await update.message.reply_text(
        f"ဒီ Group ရဲ့ ID က:\n`{chat.id}`",
        parse_mode="Markdown"
    )


telegram_app.add_handler(
    CommandHandler("id", group_id)
)

telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await telegram_app.initialize()
    await telegram_app.start()

    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL
    )

    print("Telegram webhook set to:")
    print(WEBHOOK_URL)

    yield

    await telegram_app.bot.delete_webhook()
    await telegram_app.stop()
    await telegram_app.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home():
    return {
        "status": "online",
        "service": "News Tip Bot"
    }


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):

    data = await request.json()

    update = Update.de_json(
        data,
        telegram_app.bot
    )

    await telegram_app.process_update(update)

    return {"ok": True}
