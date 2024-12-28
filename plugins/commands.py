from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.errors import UserNotParticipant
from pyrogram.enums import ChatMemberStatus  # Fixed import
from database import db
from pytube import YouTube
import re
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

id_pattern = re.compile(r"^.\d+$")

CHANNEL_USERNAME = "MOVIEZ_BOTZ"
auth_channel = '-1002437864651'
AUTH_CHANNEL = (
    int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
)

START_TEXT = """**Hello {} 😌
I am a Bot**

I can generate YouTube video thumbnails. Just send me a valid YouTube link!
"""

HELP_TEXT = """**Hey, Follow these steps:**

1. Send me a valid YouTube video link.
2. I'll fetch the thumbnail for you.

**Available Commands:**

/start - Checking Bot Online
/help - For more help
/about - For more about me
/status - For bot status"""

ABOUT_TEXT = """--**About Me 😎**--

🤖 **Name :** [YouTube Thumbnail Bot](https://telegram.me/{})

👨‍💻 **Developer :** [GitHub](https://github.com/mufaztg) | [Telegram](https://telegram.me/moviez_botz)

🖋 **Language :** [Python3](https://python.org)

🤰 **Framework :** [Pyrogram](https://pyrogram.org)"""

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
        ],
        [
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
    [[
        InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
    ], [
        InlineKeyboardButton("Check Again ✅", callback_data="check_fsub")
    ]]
)


async def is_subscribed(bot, user_id):
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, user_id)
        return user.status not in [ChatMemberStatus.BANNED, None]
    except UserNotParticipant:
        return False
    except Exception as e:
        logger.exception(e)
        return False


@Client.on_message(filters.private & filters.command(["hello","hey","status"]))
async def handle_commands(bot, update):
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
        await update.reply_text(
            text=HELP_TEXT,
            disable_web_page_preview=True,
            reply_markup=HELP_BUTTONS,
            quote=True
        )
    elif update.text.startswith("/about"):
        await update.reply_text(
            text=ABOUT_TEXT,
            disable_web_page_preview=True,
            reply_markup=ABOUT_BUTTONS,
            quote=True
        )
    elif update.text.startswith("/status"):
        total_users = await db.total_users_count()
        text = "**Bot Status**\n"
        text += f"\n**Total Users:** `{total_users}`"
        await update.reply_text(
            text=text,
            quote=True,
            disable_web_page_preview=True
        )


@Client.on_message(filters.private & filters.text & ~filters.command)
async def handle_youtube_link(bot, message):
    if not await is_subscribed(bot, message.from_user.id):
        await message.reply_text(
            text="⚠️ **You must join our channel to use this bot!**",
            reply_markup=FSub_BUTTONS,
            quote=True
        )
        return

    youtube_url = message.text.strip()
    try:
        yt = YouTube(youtube_url)
        thumbnail_url = yt.thumbnail_url

        await message.reply_photo(
            photo=thumbnail_url,
            caption=f"🎥 **Title:** {yt.title}\n"
                    f"📺 **Channel:** {yt.author}\n"
                    f"🔗 [Watch Video]({youtube_url})",
            parse_mode="markdown"
        )
    except Exception as e:
        logger.exception("Error processing YouTube link: %s", e)
        await message.reply_text(
            text="❌ Invalid YouTube link or an error occurred. Please try again!",
            quote=True
        )


@Client.on_callback_query()
async def cb_handler(bot, update):
    if update.data == "home":
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
    elif update.data == "close":
        await update.message.delete()
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
