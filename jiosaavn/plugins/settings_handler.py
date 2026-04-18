import logging
import random
import asyncio

from jiosaavn.bot import Bot
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import MessageNotModified

logger = logging.getLogger(__name__)

VALID_REACTION_EMOJIS = ["👍", "👎", "😊", "😢", "😍", "🔥", "🎉"]

@Bot.on_message(filters.command("settings"))
@Bot.on_callback_query(filters.regex(r"^settings"))
async def settings(client: Bot, message: Message|CallbackQuery):
    try:
        from jiosaavn.plugins.text import TEXT
        random_emoji = random.choice(TEXT.EMOJI_LIST)
    except (ImportError, AttributeError) as e:
        logger.warning(f"ғᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇss ᴛᴇxᴛ.ᴇᴍᴏᴊɪ_ʟɪsᴛ: {e}. ᴜsɪɴɢ ᴅᴇғᴀᴜʟᴛ ᴇᴍᴏᴊɪ ʟɪsᴛ.")
        random_emoji = random.choice(VALID_REACTION_EMOJIS)

    if getattr(message, "text", None):
        try:
            await client.send_reaction(
                chat_id=message.chat.id,
                message_id=message.id,
                emoji=random_emoji,
                big=True
            )
        except AttributeError:
            logger.warning("ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ʀᴇᴀᴄᴛɪᴏɴ ᴅᴜᴇ ᴛᴏ ᴀᴛᴛʀɪʙᴜᴛᴇᴇʀʀᴏʀ")
        except Exception as e:
            logger.error(f"ᴇʀʀᴏʀ sᴇɴᴅɪɴɢ ʀᴇᴀᴄᴛɪᴏɴ: {e}")

    await asyncio.sleep(0.5)
    if isinstance(message, Message):
        msg = await message.reply("**ᴘʀᴏᴄᴇssɪɴɢ...**", quote=True)
    else:
        msg = message.message
        await message.answer()
        data = message.data.split("#")
        if len(data) > 1:
            try:
                _, key, value = data
                if key in ["type", "quality"] and value:
                    await client.db.update_user(message.from_user.id, key, value)
                    logger.info(f"ᴜᴘᴅᴀᴛᴇᴅ ᴜsᴇʀ {message.from_user.id} ᴡɪᴛʜ {key}={value}")
                else:
                    logger.warning(f"ɪɴᴠᴀʟɪᴅ ᴄᴀʟʟʙᴀᴄᴋ ᴅᴀᴛᴀ: {message.data}")
            except Exception as e:
                logger.error(f"ғᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴜsᴇʀ sᴇᴛᴛɪɴɢs: {e}")
                await msg.edit("ᴇʀʀᴏʀ ᴜᴘᴅᴀᴛɪɴɢ sᴇᴛᴛɪɴɢs. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

    user = await client.db.get_user(message.from_user.id)
    user_type = user.get('type', 'all')
    quality = user.get('quality', '320kbps')

    all_btn      = '✅ ᴀʟʟ'      if user_type == 'all'       else 'ᴀʟʟ'
    albums_btn   = '✅ ᴀʟʙᴜᴍs'   if user_type == 'albums'    else 'ᴀʟʙᴜᴍs'
    songs_btn    = '✅ sᴏɴɢs'    if user_type == 'songs'     else 'sᴏɴɢs'
    playlists_btn= '✅ ᴘʟᴀʏʟɪsᴛ' if user_type == 'playlists' else 'ᴘʟᴀʏʟɪsᴛ'

    quality_320  = '✅ 320ᴋʙᴘs'  if quality == '320kbps'     else '320ᴋʙᴘs'
    quality_160  = '✅ 160ᴋʙᴘs'  if quality == '160kbps'     else '160ᴋʙᴘs'

    buttons = [
        [
            InlineKeyboardButton("sᴇᴀʀᴄʜ ᴛʏᴘᴇ", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(all_btn,       callback_data='settings#type#all'),
            InlineKeyboardButton(albums_btn,    callback_data='settings#type#albums'),
        ],
        [
            InlineKeyboardButton(songs_btn,     callback_data='settings#type#songs'),
            InlineKeyboardButton(playlists_btn, callback_data='settings#type#playlists'),
        ],
        [
            InlineKeyboardButton("ᴀᴜᴅɪᴏ Qᴜᴀʟɪᴛʏ", callback_data="dummy"),
        ],
        [
            InlineKeyboardButton(quality_320, callback_data='settings#quality#320kbps'),
            InlineKeyboardButton(quality_160, callback_data='settings#quality#160kbps'),
        ],
        [
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close'),
        ]
    ]

    text = '**sᴇʟᴇᴄᴛ ᴛʜᴇ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛ ᴛʏᴘᴇ ᴀɴᴅ ᴍᴜsɪᴄ Qᴜᴀʟɪᴛʏ**'
    try:
        if msg.text != text or msg.reply_markup != InlineKeyboardMarkup(buttons):
            await msg.edit(text, reply_markup=InlineKeyboardMarkup(buttons))
    except MessageNotModified:
        logger.warning("ᴍᴇssᴀɢᴇ ɴᴏᴛ ᴍᴏᴅɪғɪᴇᴅ ɪɴ sᴇᴛᴛɪɴɢs_ʜᴀɴᴅʟᴇʀ")
    except Exception as e:
        logger.error(f"ғᴀɪʟᴇᴅ ᴛᴏ ᴇᴅɪᴛ sᴇᴛᴛɪɴɢs ᴍᴇssᴀɢᴇ: {e}")
        await msg.edit("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴜᴘᴅᴀᴛɪɴɢ sᴇᴛᴛɪɴɢs.")


@Bot.on_callback_query(filters.regex(r"^dummy$"))
async def dummy(client: Bot, callback: CallbackQuery):
    await callback.answer("ᴘʟᴇᴀsᴇ ᴄʜᴏᴏsᴇ ᴀɴᴏᴛʜᴇʀ ʙᴜᴛᴛᴏɴ", show_alert=True)
