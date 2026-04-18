import logging
import asyncio
import random
from jiosaavn.bot import Bot
from jiosaavn.plugins.text import TEXT
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

#################### COMMAND ##########
@Bot.on_callback_query(filters.regex('^home$'))
@Bot.on_message(filters.command('start') & filters.private & filters.incoming)
async def start(c, m):
    last_name = f' {m.from_user.last_name}' if m.from_user.last_name else ''
    mention = f"[{m.from_user.first_name}{last_name}](tg://user?id={m.from_user.id})" if m.from_user.first_name else f"[ᴜsᴇʀ](tg://user?id={m.from_user.id})"
    msg = m.message if getattr(m, "data", None) else await m.reply("**ᴘʀᴏᴄᴇssɪɴɢ....⌛**", quote=True)
    try:
        buttons = [
            [InlineKeyboardButton('ᴏᴡɴᴇʀ', url='https://t.me/sexyshnwaz')],
            [InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
             InlineKeyboardButton('sᴇᴛᴛɪɴɢs', callback_data='settings')],
            [InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close')]
        ]
        await msg.edit(
            text=TEXT.START_MSG.format(mention=mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except KeyError as e:
        logger.error(f"ᴇʀʀᴏʀ ɪɴ sᴛᴀʀᴛ ᴄᴏᴍᴍᴀɴᴅ: {e}")
        await msg.edit(text="ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇQᴜᴇsᴛ.")
    except Exception as e:
        logger.error(f"ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ: {e}")
        await msg.edit(text="ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇQᴜᴇsᴛ.")


@Bot.on_callback_query(filters.regex('^help$'))
@Bot.on_message(filters.command('help') & filters.private & filters.incoming)
async def help_handler(client: Bot, message: Message | CallbackQuery):
    msg = message.message if getattr(message, "data", None) else await message.reply("**ᴘʀᴏᴄᴇssɪɴɢ....⌛**", quote=True)
    try:
        buttons = [
            [InlineKeyboardButton('sᴇᴛᴛɪɴɢs', callback_data='settings')],
            [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='home'),
             InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close')]
        ]
        if isinstance(message, Message):
            await msg.edit(
                text=TEXT.HELP_MSG,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await msg.edit(
                text=TEXT.HELP_MSG,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        logger.error(f"ᴇʀʀᴏʀ ɪɴ ʜᴇʟᴘ_ʜᴀɴᴅʟᴇʀ ᴄᴏᴍᴍᴀɴᴅ: {e}")
        if isinstance(message, Message):
            await msg.edit("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇQᴜᴇsᴛ.")
        else:
            await msg.edit("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇQᴜᴇsᴛ.")


@Bot.on_callback_query(filters.regex('^about$'))
@Bot.on_message(filters.command('about') & filters.private & filters.incoming)
async def about(client: Bot, message: Message | CallbackQuery):
    try:
        msg = message.message if getattr(message, "data", None) else await message.reply("**ᴘʀᴏᴄᴇssɪɴɢ....⌛**", quote=True)
        me = await client.get_me()
        buttons = [
            [InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
             InlineKeyboardButton('sᴇᴛᴛɪɴɢs', callback_data='settings')],
            [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='home'),
             InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close')]
        ]
        if isinstance(message, Message):
            await msg.edit(
                text=TEXT.ABOUT_MSG.format(me=me),
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
        else:
            await msg.edit(
                text=TEXT.ABOUT_MSG.format(me=me),
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"ᴇʀʀᴏʀ ɪɴ ᴀʙᴏᴜᴛ ᴄᴏᴍᴍᴀɴᴅ: {e}")
        if isinstance(message, Message):
            await msg.edit("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇQᴜᴇsᴛ.")
        else:
            await msg.edit("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇQᴜᴇsᴛ.")


@Bot.on_callback_query(filters.regex('^close$'))
async def close_cb(client: Bot, callback: CallbackQuery):
    try:
        await callback.answer()
        await callback.message.delete()
        await callback.message.reply_to_message.delete()
    except Exception as e:
        logger.error(f"ᴇʀʀᴏʀ ɪɴ ᴄʟᴏsᴇ_ᴄʙ ᴄᴏᴍᴍᴀɴᴅ: {e}")
        await callback.message.edit("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴄʟᴏsɪɴɢ ᴛʜᴇ ᴍᴇssᴀɢᴇ.")
