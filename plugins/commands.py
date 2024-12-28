from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from database import db
import re
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

id_pattern = re.compile(r"^.\d+$")

CHANNEL_USERNAME = "MOVIEZ_BOTZ"
auth_channel = '-1002437864651'
AUTH_CHANNEL = (
    int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
)

START_TEXT = """**Hello {} 😌
I am a QR Code Bot**

>> `I can generate text to QR Code with QR Code decode to text support.`"""

HELP_TEXT = """**Hey, Follow these steps:**

➞ Send me a link/text I will generate the QR code of that text
➞ Send me a QR code image I will decode that image and convert to text

**Available Commands**

/start - Checking Bot Online
/help - For more help
/about - For more about me
/settings - For bot settings
/reset - For reset settings
/status - For bot status"""

ABOUT_TEXT = """--**About Me 😎**--

🤖 **Name :** [QR Code Bot](https://telegram.me/{})

👨‍💻 **Developer :** [GitHub](https://github.com/FayasNoushad) | [Telegram](https://telegram.me/FayasNoushad)

🌐 **Source :** [👉 Click here](https://github.com/FayasNoushad/QR-Code-bot)

🖋 **Language :** [Python3](https://python.org)

🤰 **Framework :** [Pyrogram](https://pyrogram.org)"""

SETTINGS_TEXT = "**Settings**"

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('⚙ Help', callback_data='help'),
            InlineKeyboardButton('About 🔰', callback_data='about'),
            InlineKeyboardButton('Close ✖️', callback_data='close')
        ]
    ]
)

HELP_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('🏠 Home', callback_data='home'),
            InlineKeyboardButton('About 🔰', callback_data='about')
        ],[
            InlineKeyboardButton('⚒ Settings', callback_data='settings'),
            InlineKeyboardButton('Close ✖️', callback_data='close')
        ]
    ]
)

ABOUT_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('🏠 Home', callback_data='home'),
            InlineKeyboardButton('Help ⚙', callback_data='help'),
            InlineKeyboardButton('Close ✖️', callback_data='close')
        ]
    ]
)

FSub_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
        ],
        [
            InlineKeyboardButton("Check Again ✅", callback_data="check_fsub")
        ]
    ]
)

async def is_subscribed(bot, query):
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        await __(bot, AUTH_CHANNEL)
        return query.from_user.id in temp.REQUESTERS.get(AUTH_CHANNEL, {}).get(
            "list", []
        )

    except Exception as e:
        logger.exception(e)
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True

    return False


@Client.on_callback_query()
async def cb_handler(bot, update):
    if update.data == "lol":
        await update.answer(
            text="Select a button below",
            show_alert=True
        )
    elif update.data == "home":
        await update.message.edit_text(
            text=START_TEXT.format(update.from_user.mention),
            reply_markup=START_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=HELP_TEXT,
            reply_markup=HELP_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=ABOUT_TEXT,
            reply_markup=ABOUT_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "settings":
        await display_settings(bot, update, db, cb=True, cb_text=True)
    elif update.data == "close":
        await update.message.delete()
    elif update.data == "set_af":
        as_file = await db.is_as_file(update.from_user.id)
        await db.update_as_file(update.from_user.id, not as_file)
        if as_file:
            alert_text = "Upload mode changed to file successfully"
        else:
            alert_text = "Upload mode changed to photo successfully"
        await update.answer(text=alert_text, show_alert=True)
        await display_settings(bot, update, db, cb=True)
    elif update.data == "check_fsub":
        if await is_subscribed(bot, update.from_user.id):
            await update.message.edit_text(
                text="🎉 **Thank you for subscribing!** You can now use the bot.",
                reply_markup=None
            )
        else:
            await update.answer(
                text="❌ You are still not subscribed. Please join the channel and try again.",
                show_alert=True
            )

@Client.on_message(filters.private & filters.command(["start", "help", "about", "reset", "settings", "status"]))
async def check_fsub(bot, update):
    if not await is_subscribed(bot, update.from_user.id):
        await update.reply_text(
            text="⚠️ **You must join our channel to use this bot!**",
            reply_markup=FSub_BUTTONS,
            quote=True
        )
        return

    if update.text.startswith("/start"):
        if not await db.is_user_exist(update.from_user.id):
            await db.add_user(update.from_user.id)
        await update.reply_text(
            text=START_TEXT.format(update.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=START_BUTTONS,
            quote=True
        )
    elif update.text.startswith("/help"):
        if not await db.is_user_exist(update.from_user.id):
            await db.add_user(update.from_user.id)
        await update.reply_text(
            text=HELP_TEXT,
            disable_web_page_preview=True,
            reply_markup=HELP_BUTTONS,
            quote=True
        )
    elif update.text.startswith("/about"):
        if not await db.is_user_exist(update.from_user.id):
            await db.add_user(update.from_user.id)
        await update.reply_text(
            text=ABOUT_TEXT,
            disable_web_page_preview=True,
            reply_markup=ABOUT_BUTTONS,
            quote=True
        )
    elif update.text.startswith("/reset"):
        await db.delete_user(update.from_user.id)
        await db.add_user(update.from_user.id)
        await update.reply_text("Settings reset successfully")
    elif update.text.startswith("/settings"):
        if not await db.is_user_exist(update.from_user.id):
            await db.add_user(update.from_user.id)
        await display_settings(bot, update, db)
    elif update.text.startswith("/status"):
        total_users = await db.total_users_count()
        text = "**Bot Status**\n"
        text += f"\n**Total Users:** `{total_users}`"
        await update.reply_text(
            text=text,
            quote=True,
            disable_web_page_preview=True
        )

async def display_settings(bot, update, db, cb=False, cb_text=False):
    chat_id = update.from_user.id
    as_file = await db.is_as_file(chat_id)
    as_file_btn = [
        InlineKeyboardButton("Upload Mode", callback_data="lol")
    ]
    if as_file:
        as_file_btn.append(
            InlineKeyboardButton('Upload as File', callback_data='set_af')
        )
    else:
        as_file_btn.append(
            InlineKeyboardButton('Upload as Photo', callback_data='set_af')
        )
    close_btn = [
        InlineKeyboardButton('Close ✖️', callback_data='close')
    ]
    settings_buttons = [as_file_btn, close_btn]
    try:
        if cb:
            if cb and cb_text:
                await update.message.edit_text(
                    text=SETTINGS_TEXT,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(settings_buttons)
                )
            else:
                await update.edit_message_reply_markup(
                    InlineKeyboardMarkup(settings_buttons)
                )
        else:
            await update.reply_text(
                text=SETTINGS_TEXT,
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(settings_buttons)
            )
    except Exception as error:
        print(error)
