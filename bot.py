```python
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
from supabase import create_client


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EDITOR_GROUP_ID = os.getenv("EDITOR_GROUP_ID")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")


# ============================================================
# CHECK REQUIRED ENVIRONMENT VARIABLES
# ============================================================

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is missing")

if not RENDER_EXTERNAL_URL:
    raise RuntimeError("RENDER_EXTERNAL_URL is missing")


# ============================================================
# SUPABASE
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


# ============================================================
# WEBHOOK URL
# ============================================================

RENDER_EXTERNAL_URL = RENDER_EXTERNAL_URL.rstrip("/")

WEBHOOK_URL = (
    RENDER_EXTERNAL_URL
    + "/telegram/webhook"
)


# ============================================================
# TELEGRAM APPLICATION
# ============================================================

telegram_app = (
    Application.builder()
    .token(BOT_TOKEN)
    .build()
)


# ============================================================
# /START COMMAND
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handle /start command.
    """

    if not update.message:
        return

    # Clear previous user state
    context.user_data.clear()

    keyboard = [
        ["📰 သတင်းပို့ရန်"],
        ["✉️ အယ်ဒီတာထံပေးစာ"],
        ["ℹ️ သတင်းပေးပို့နည်း"],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )

    await update.message.reply_text(
        "မင်္ဂလာပါ။ 👋\n\n"
        "သတင်းအချက်အလက်များ၊ ဓာတ်ပုံနှင့် "
        "ဗီဒီယိုများကို ပေးပို့နိုင်ပါတယ်။\n\n"
        "အောက်ပါခလုတ်မှ ရွေးချယ်ပါ။",
        reply_markup=reply_markup,
    )


# ============================================================
# /ID COMMAND
# ============================================================

async def group_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Return current chat/group ID.
    """

    if not update.message:
        return

    chat = update.effective_chat

    if not chat:
        await update.message.reply_text(
            "Chat information မတွေ့ပါ။"
        )
        return

    await update.message.reply_text(
        "ဒီ Chat / Group ရဲ့ ID က:\n"
        + str(chat.id)
    )


# ============================================================
# SAVE NEWS TO SUPABASE
# ============================================================

async def save_news(
    update: Update,
    text: str,
) -> bool:
    """
    Save news tip to Supabase.
    """

    user = update.effective_user

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

    try:
        result = (
            supabase
            .table("news_tips")
            .insert(data)
            .execute()
        )

        print("NEWS SAVED TO SUPABASE")
        print(result.data)

        return True

    except Exception as error:
        print("SUPABASE ERROR:")
        print(repr(error))

        return False


# ============================================================
# SEND NEWS TO EDITOR GROUP
# ============================================================

async def send_to_editor(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> bool:
    """
    Send submitted news to editor group.
    """

    if not EDITOR_GROUP_ID:
        print("EDITOR_GROUP_ID is missing")
        return False

    user = update.effective_user

    user_name = (
        user.full_name
        if user
        else "Unknown"
    )

    user_id = (
        str(user.id)
        if user
        else "Unknown"
    )

    report = (
        "🆕 NEW NEWS TIP\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "👤 ပေးပို့သူ: "
        + user_name
        + "\n"
        "🆔 Telegram ID: "
        + user_id
        + "\n\n"
        "📝 သတင်းအချက်အလက်:\n"
        + text
        + "\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "Status: NEW"
    )

    try:
        await context.bot.send_message(
            chat_id=int(EDITOR_GROUP_ID),
            text=report,
        )

        print("NEWS SENT TO EDITOR GROUP")

        return True

    except Exception as error:
        print("EDITOR GROUP ERROR:")
        print(repr(error))

        return False


# ============================================================
# SEND EDITOR LETTER
# ============================================================

async def send_editor_letter(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> bool:
    """
    Send a letter to editor group.
    """

    if not EDITOR_GROUP_ID:
        print("EDITOR_GROUP_ID is missing")
        return False

    user = update.effective_user

    user_name = (
        user.full_name
        if user
        else "Unknown"
    )

    user_id = (
        str(user.id)
        if user
        else "Unknown"
    )

    editor_message = (
        "✉️ အယ်ဒီတာထံပေးစာ\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "👤 ပေးပို့သူ: "
        + user_name
        + "\n"
        "🆔 Telegram ID: "
        + user_id
        + "\n\n"
        "📝 စာသား:\n"
        + text
        + "\n\n"
        "━━━━━━━━━━━━━━━━"
    )

    try:
        await context.bot.send_message(
            chat_id=int(EDITOR_GROUP_ID),
            text=editor_message,
        )

        print("EDITOR LETTER SENT")

        return True

    except Exception as error:
        print("EDITOR LETTER ERROR:")
        print(repr(error))

        return False


# ============================================================
# MAIN MESSAGE HANDLER
# ============================================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handle normal Telegram messages.
    """

    if not update.message:
        return

    message = update.message

    # Get text or caption
    text = (
        message.text
        or message.caption
        or ""
    ).strip()

    # ========================================================
    # NEWS BUTTON
    # ========================================================

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
            "ဓာတ်ပုံ သို့မဟုတ် ဗီဒီယိုရှိပါက "
            "စာနဲ့အတူ ပေးပို့နိုင်ပါတယ်။"
        )

        return

    # ========================================================
    # EDITOR LETTER BUTTON
    # ========================================================

    if text == "✉️ အယ်ဒီတာထံပေးစာ":

        context.user_data["submitting_news"] = False
        context.user_data["submitting_editor_letter"] = True

        await message.reply_text(
            "✉️ အယ်ဒီတာထံပေးစာ\n\n"
            "အယ်ဒီတာထံ ပေးပို့လိုသောစာကို "
            "ရေးပေးပါ။"
        )

        return

    # ========================================================
    # INFORMATION BUTTON
    # ========================================================

    if text == "ℹ️ သတင်းပေးပို့နည်း":

        context.user_data["submitting_news"] = False
        context.user_data["submitting_editor_letter"] = False

        await message.reply_text(
            "ℹ️ သတင်းပေးပို့နည်း\n\n"
            "သတင်းဖြစ်စဉ်၊ နေရာ၊ အချိန်၊ "
            "ဓာတ်ပုံနှင့် ဗီဒီယိုများကို "
            "ပေးပို့နိုင်ပါတယ်။\n\n"
            "အယ်ဒီတာအဖွဲ့မှ စိစစ်ပြီးမှသာ "
            "အသုံးပြုပါမယ်။"
        )

        return

    # ========================================================
    # EDITOR LETTER
    # ========================================================

    if context.user_data.get(
        "submitting_editor_letter",
        False,
    ):

        if not text:
            await message.reply_text(
                "ပေးပို့လိုသောစာကို ရေးပေးပါ။"
            )
            return

        success = await send_editor_letter(
            update,
            context,
            text,
        )

        if success:
            await message.reply_text(
                "✅ အယ်ဒီတာထံပေးစာကို "
                "ပေးပို့ပြီးပါပြီ။"
            )
        else:
            await message.reply_text(
                "❌ အယ်ဒီတာထံ ပေးပို့ရာမှာ "
                "အမှားတစ်ခု ဖြစ်သွားပါတယ်။"
            )

        context.user_data[
            "submitting_editor_letter"
        ] = False

        return

    # ========================================================
    # NEWS SUBMISSION
    # ========================================================

    if context.user_data.get(
        "submitting_news",
        False,
    ):

        if not text:
            await message.reply_text(
                "သတင်းအချက်အလက်ကို ရေးပေးပါ။"
            )
            return

        # Save to Supabase
        saved = await save_news(
            update,
            text,
        )

        if not saved:
            await message.reply_text(
                "❌ သတင်းကို Supabase ထဲ "
                "သိမ်းဆည်းလို့ မရပါ။\n\n"
                "ခဏအကြာ ပြန်လည်ပေးပို့ကြည့်ပါ။"
            )
            return

        # Send to editor group
        editor_sent = await send_to_editor(
            update,
            context,
            text,
        )

        if editor_sent:
            await message.reply_text(
                "✅ သတင်းကို လက်ခံရရှိပါပြီ။\n\n"
                "အယ်ဒီတာအဖွဲ့က စိစစ်ပြီး "
                "လိုအပ်ပါက ပြန်လည်ဆက်သွယ်ပါမယ်။"
            )
        else:
            await message.reply_text(
                "✅ သတင်းကို လက်ခံရရှိပြီး "
                "Supabase ထဲ သိမ်းဆည်းထားပါတယ်။\n\n"
                "သို့သော် အယ်ဒီတာအဖွဲ့ထံ "
                "ပေးပို့ရာမှာ အခက်အခဲရှိနေပါတယ်။"
            )

        context.user_data[
            "submitting_news"
        ] = False

        return

    # ========================================================
    # DEFAULT
    # ========================================================

    await message.reply_text(
        "သတင်းပေးပို့လိုပါက /start ကိုနှိပ်ပါ။"
    )


# ============================================================
# TELEGRAM HANDLERS
# ============================================================

telegram_app.add_handler(
    CommandHandler(
        "start",
        start,
    )
)

telegram_app.add_handler(
    CommandHandler(
        "id",
        group_id,
    )
)

telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message,
    )
)


# ============================================================
# FASTAPI LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Start Telegram application and configure webhook.
    """

    print("========================================")
    print("Starting Telegram application...")
    print("========================================")

    try:
        # Initialize Telegram application
        await telegram_app.initialize()

        # Start Telegram application
        await telegram_app.start()

        # Set Telegram webhook
        await telegram_app.bot.set_webhook(
            url=WEBHOOK_URL
        )

        print("Telegram webhook set successfully:")
        print(WEBHOOK_URL)

    except Exception as error:
        print("TELEGRAM STARTUP ERROR:")
        print(repr(error))

        raise

    # Keep FastAPI running
    yield

    # ========================================================
    # SHUTDOWN
    # ========================================================

    print("========================================")
    print("Stopping Telegram application...")
    print("========================================")

    try:
        await telegram_app.bot.delete_webhook()

        print("Telegram webhook deleted.")

    except Exception as error:
        print("WEBHOOK DELETE ERROR:")
        print(repr(error))

    try:
        await telegram_app.stop()

    except Exception as error:
        print("TELEGRAM STOP ERROR:")
        print(repr(error))

    try:
        await telegram_app.shutdown()

    except Exception as error:
        print("TELEGRAM SHUTDOWN ERROR:")
        print(repr(error))


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="News Tip Telegram Bot",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# HOME / HEALTH CHECK
# ============================================================

@app.get("/")
async def home():
    """
    Render health check endpoint.
    """

    return {
        "status": "online",
        "service": "News Tip Bot",
    }


# ============================================================
# TELEGRAM WEBHOOK
# ============================================================

@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
):
    """
    Receive Telegram webhook updates.
    """

    try:
        # Read JSON from Telegram
        data = await request.json()

        # Convert JSON to Telegram Update
        update = Update.de_json(
            data,
            telegram_app.bot,
        )

        # Process update
        await telegram_app.process_update(
            update
        )

        return {
            "ok": True,
        }

    except Exception as error:

        print("========================================")
        print("WEBHOOK ERROR:")
        print(repr(error))
        print("========================================")

        return {
            "ok": False,
            "error": str(error),
        }
```
