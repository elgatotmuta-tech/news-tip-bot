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
from supabase import create_client, Client


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

TOKEN = os.environ["BOT_TOKEN"]

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

EDITOR_GROUP_ID = os.getenv("EDITOR_GROUP_ID")

RENDER_URL = os.environ.get(
    "RENDER_EXTERNAL_URL",
    "http://localhost:10000"
)


# =========================================================
# SUPABASE CONNECTION
# =========================================================

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# TELEGRAM WEBHOOK
# =========================================================

WEBHOOK_PATH = "/telegram/webhook"
WEBHOOK_URL = RENDER_URL + WEBHOOK_PATH


# =========================================================
# TELEGRAM APPLICATION
# =========================================================

telegram_app = (
    Application.builder()
    .token(TOKEN)
    .build()
)


# =========================================================
# /START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    keyboard = [
        ["📰 သတင်းပို့ရန်"],
        ["✉️ အယ်ဒီတာထံပေးစာ"],
        ["ℹ️ သတင်းပေးပို့နည်း"],
    ]

    # Reset previous states
    context.user_data["submitting_news"] = False
    context.user_data["submitting_editor_letter"] = False

    await update.message.reply_text(
        "မင်္ဂလာပါ။ 👋\n\n"
        "သတင်းအချက်အလက်များ၊ ဓာတ်ပုံနှင့် "
        "ဗီဒီယိုများကို ပေးပို့နိုင်ပါတယ်။\n\n"
        "အောက်ပါခလုတ်မှ သင့်လိုအပ်ချက်ကို ရွေးချယ်ပါ။",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        ),
    )


# =========================================================
# /ID
# =========================================================

async def group_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat = update.effective_chat

    await update.message.reply_text(
        f"ဒီ Chat / Group ရဲ့ ID က:\n`{chat.id}`",
        parse_mode="Markdown"
    )


# =========================================================
# MESSAGE HANDLER
# =========================================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    user = update.effective_user
    message = update.message

    text = (
        message.text
        or message.caption
        or ""
    ).strip()


    # =====================================================
    # NEWS BUTTON
    # =====================================================

    if text == "📰 သတင်းပို့ရန်":

        context.user_data["submitting_news"] = True
        context.user_data["submitting_editor_letter"] = False

        await message.reply_text(
            "📰 သတင်းပို့ရန်\n\n"
            "ဖြစ်စဉ်ကို အသေးစိတ်ရေးပေးပါ။\n\n"
            "ဥပမာ -\n"
            "• ဘာဖြစ်ခဲ့သလဲ\n"
            "• ဘယ်နေရာမှာဖြစ်သလဲ\n"
            "• ဘယ်အချိန်မှာဖြစ်သလဲ\n"
            "• သိရှိထားသမျှ အချက်အလက်များ\n\n"
            "ဓာတ်ပုံ သို့မဟုတ် ဗီဒီယိုရှိပါကလည်း "
            "ပေးပို့နိုင်ပါတယ်။"
        )

        return


    # =====================================================
    # EDITOR LETTER BUTTON
    # =====================================================

    if text == "✉️ အယ်ဒီတာထံပေးစာ":

        context.user_data["submitting_news"] = False
        context.user_data["submitting_editor_letter"] = True

        await message.reply_text(
            "✉️ အယ်ဒီတာထံပေးစာ\n\n"
            "အယ်ဒီတာထံ ပေးပို့လိုသောစာကို "
            "ရေးပေးပါ။"
        )

        return


    # =====================================================
    # INFORMATION BUTTON
    # =====================================================

    if text == "ℹ️ သတင်းပေးပို့နည်း":

        context.user_data["submitting_news"] = False
        context.user_data["submitting_editor_letter"] = False

        await message.reply_text(
            "ℹ️ သတင်းပေးပို့နည်း\n\n"
            "သတင်းဖြစ်စဉ်၊ နေရာ၊ အချိန်၊ "
            "ဓာတ်ပုံနှင့် ဗီဒီယိုများကို "
            "ပေးပို့နိုင်ပါတယ်။\n\n"
            "သတင်းအချက်အလက်များကို အယ်ဒီတာအဖွဲ့မှ "
            "စိစစ်ပြီးမှသာ အသုံးပြုပါမယ်။"
        )

        return


    # =====================================================
    # EDITOR LETTER
    # =====================================================

    if context.user_data.get(
        "submitting_editor_letter"
    ):

        if not text:
            await message.reply_text(
                "✉️ ပေးပို့လိုသောစာကို "
                "ရေးပေးပါ။"
            )
            return


        user_name = (
            user.full_name
            if user
            else "Unknown"
        )

        user_id = (
            user.id
            if user
            else "Unknown"
        )


        editor_message = (
            "✉️ အယ်ဒီတာထံပေးစာ\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"👤 ပေးပို့သူ: {user_name}\n"
            f"🆔 Telegram ID: {user_id}\n\n"
            "📝 စာသား:\n"
            f"{text}\n\n"
            "━━━━━━━━━━━━━━━━"
        )


        # Send to editor group
        if EDITOR_GROUP_ID:

            try:

                await context.bot.send_message(
                    chat_id=int(EDITOR_GROUP_ID),
                    text=editor_message
                )

            except Exception as e:

                print(
                    "EDITOR LETTER ERROR:",
                    e
                )

                await message.reply_text(
                    "❌ အယ်ဒီတာထံ ပေးပို့ရာမှာ "
                    "အမှားတစ်ခု ဖြစ်သွားပါတယ်။"
                )

                return


        await message.reply_text(
            "✅ အယ်ဒီတာထံ ပေးစာကို "
            "ပေးပို့ပြီးပါပြီ။\n\n"
            "ကျေးဇူးတင်ပါတယ်။"
        )


        context.user_data[
            "submitting_editor_letter"
        ] = False

        return


    # =====================================================
    # NEWS SUBMISSION
    # =====================================================

    if context.user_data.get(
        "submitting_news"
    ):

        if not text:

            await message.reply_text(
                "📝 သတင်းအချက်အလက်ကို "
                "ရေးပေးပါ။"
            )

            return


        # ---------------------------------------------
        # Prepare Supabase data
        # ---------------------------------------------

        data = {
            "telegram_user_id": (
                user.id
                if user
                else None
            ),

            "telegram_username": (
                user.username
                if user
                else None
            ),

            "telegram_name": (
                user.full_name
                if user
                else None
            ),

            "message": text,
        }


        # ---------------------------------------------
        # Save to Supabase
        # ---------------------------------------------

        try:

            response = (
                supabase
                .table("news_tips")
                .insert(data)
                .execute()
            )

            print(
                "NEWS TIP SAVED:",
                response.data
            )

        except Exception as e:

            print(
                "SUPABASE INSERT ERROR:",
                e
            )

            await message.reply_text(
                "❌ သတင်းသိမ်းဆည်းရာမှာ "
                "အမှားတစ်ခု ဖြစ်သွားပါတယ်။\n\n"
                "ခဏအကြာ ပြန်လည်ပေးပို့ကြည့်ပါ။"
            )

            return


        # ---------------------------------------------
        # Editor group message
        # ---------------------------------------------

        user_name = (
            user.full_name
            if user
            else "Unknown"
        )

        user_id = (
            user.id
            if user
            else "Unknown"
        )


        report = (
            "🆕 NEW NEWS TIP\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"👤 ပေးပို့သူ: {user_name}\n"
            f"🆔 Telegram ID: {user_id}\n\n"
            "📝 သတင်းအချက်အလက်:\n"
            f"{text}\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "Status: NEW"
        )


        # ---------------------------------------------
        # Send to editor group
        # ---------------------------------------------

        if EDITOR_GROUP_ID:

            try:

                await context.bot.send_message(
                    chat_id=int(EDITOR_GROUP_ID),
                    text=report
                )

            except Exception as e:

                print(
                    "EDITOR GROUP ERROR:",
                    e
                )


        # ---------------------------------------------
        # Confirmation
        # ---------------------------------------------

        await message.reply_text(
            "✅ သတင်းကို လက်ခံရရှိပါပြီ။\n\n"
            "အယ်ဒီတာအဖွဲ့က စိစစ်ပြီး "
            "လိုအပ်ပါက ပြန်လည်ဆက်သွယ်ပါမယ်။\n\n"
            "ကျေးဇူးတင်ပါတယ်။"
        )


        context.user_data[
            "submitting_news"
        ] = False

        return


    # =====================================================
    # DEFAULT MESSAGE
    # =====================================================

    await message.reply_text(
        "သတင်းပေးပို့လိုပါက /start ကိုနှိပ်ပါ။"
    )


# =========================================================
# REGISTER HANDLERS
# =========================================================

telegram_app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


telegram_app.add_handler(
    CommandHandler(
        "id",
        group_id
    )
)


telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)


# =========================================================
# FASTAPI LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    print("Starting Telegram application...")

    await telegram_app.initialize()
    await telegram_app.start()


    # ---------------------------------------------
    # Set Telegram webhook
    # ---------------------------------------------

    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL
    )


    print(
        "Telegram webhook set to:"
    )

    print(WEBHOOK_URL)


    yield


    # ---------------------------------------------
    # Shutdown
    # ---------------------------------------------

    print(
        "Stopping Telegram application..."
    )

    await telegram_app.bot.delete_webhook()

    await telegram_app.stop()
    await telegram_app.shutdown()


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    lifespan=lifespan
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
async def home():

    return {
        "status": "online",
        "service": "News Tip Bot"
    }


# =========================================================
# TELEGRAM WEBHOOK
# =========================================================

@app.post(
    "/telegram/webhook"
)
async def telegram_webhook(
    request: Request
):

    data = await request.json()


    update = Update.de_json(
        data,
        telegram_app.bot
    )


    await telegram_app.process_update(
        update
    )


    return {
        "ok": True
    }
