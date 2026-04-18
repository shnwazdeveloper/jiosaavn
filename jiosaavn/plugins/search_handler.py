import html
import logging
import traceback

from api.jiosaavn import Jiosaavn
from jiosaavn.bot import Bot

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


logger = logging.getLogger(__name__)

@Bot.on_callback_query(filters.regex(r"^search#"))
@Bot.on_message(
    filters.text & filters.incoming & filters.private & 
    ~filters.regex(r'^http.*') & ~filters.via_bot & 
    ~filters.command(["start", "settings", "help", "about"])
)
async def search(client: Bot, message: Message|CallbackQuery):
    if isinstance(message, Message):
        send_msg = await message.reply("__**ᴘʀᴏᴄᴇssɪɴɢ...**__", quote=True)
    else:
        await message.answer()
        send_msg = message.message

    query = message.text if isinstance(message, Message) else message.message.reply_to_message.text
    page_no = 1
    if isinstance(message, Message):
        user_data = await client.db.get_user(message.from_user.id)
        search_type = user_data['type']
    else:
        data = message.data.split('#')
        search_type = data[1]
        if len(data) == 3:
            page_no = int(data[2])

    try:
        if search_type in ('all', 'topquery'):
            response = await Jiosaavn().search_all_types(query=query)
        else:
            response = await Jiosaavn().search(query=query, search_type=search_type, page_no=page_no)
    except RuntimeError as e:
        logger.error(e)
        traceback.print_exc()
        return await send_msg.edit("ᴄᴏɴɴᴇᴄᴛɪᴏɴ ʀᴇғᴜsᴇᴅ ʙʏ ᴊɪᴏsᴀᴀᴠɴ ᴀᴘɪ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ")

    if not response:
        return await send_msg.edit(f'ɴᴏ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛ ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ Qᴜᴇʀʏ `{query}`')

    buttons = []
    if search_type == "all" or search_type == "topquery":
        button_song_type_map = {
            "songs":     ("sᴏɴɢs",     "search#songs"),
            "albums":    ("ᴀʟʙᴜᴍs",    "search#albums"),
            "playlists": ("ᴘʟᴀʏʟɪsᴛs", "search#playlists"),
            "artists":   ("ᴀʀᴛɪsᴛs",   "search#artists"),
            "topquery":  ("ᴛᴏᴘ ʀᴇsᴜʟᴛ","search#topquery"),
        }

        if search_type == 'topquery':
            sub_sorted_data = sorted(
                response.get("topquery", {}).get("data", []),
                key=lambda x: x.get("position", 0)
            )
            for data in sub_sorted_data:
                title = data.get("title", "ᴜɴᴋɴᴏᴡɴ")
                title = html.unescape(title)
                album = data.get("album")
                item_type = data.get("type")
                item_id = data.get("url", "/").rsplit("/", 1)[1]
                type_label_map = {
                    "song":     "sᴏɴɢ",
                    "album":    "ᴀʟʙᴜᴍ",
                    "playlist": "ᴘʟᴀʏʟɪsᴛ",
                    "artist":   "ᴀʀᴛɪsᴛ",
                }
                if item_type not in type_label_map:
                    continue
                label = type_label_map[item_type]
                button_text = f"{label} - {title} ғʀᴏᴍ {album}" if album else f"{label} - {title}"
                callback_data = f"{item_type}#{item_id}#topquery"
                buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
        else:
            sorted_data = sorted(response.items(), key=lambda value: value[1].get("position", 0))
            for result_type, result in sorted_data:
                if result_type not in button_song_type_map:
                    continue
                if result.get("data"):
                    button_label, callback_data = button_song_type_map.get(result_type, (None, None))
                    buttons.append([InlineKeyboardButton(text=button_label, callback_data=callback_data)])

        text = f"**sᴇᴀʀᴄʜ Qᴜᴇʀʏ:** {query}\n\n__ᴘʟᴇᴀsᴇ sᴇʟᴇᴄᴛ ᴏɴᴇ ᴄᴀᴛᴇɢᴏʀʏ__"
    else:
        total_results = response.get("total", 0)

        for result in response.get("results", []):
            item_id = result.get("perma_url", "/").rsplit("/", 1)[1]
            title = result.get("title", "ᴜɴᴋɴᴏᴡɴ")
            title = html.unescape(title)
            result_type = result.get("type", "ᴜɴᴋɴᴏᴡɴ")
            artist = result.get("name", "ᴜɴᴋɴᴏᴡɴ")
            artist = html.unescape(artist)
            more_info = result.get("more_info", {})
            album = more_info.get("album", "")

            button_label_map = {
                "song":     f"sᴏɴɢ - {title} ғʀᴏᴍ '{album}'" if album else f"sᴏɴɢ - {title}",
                "album":    f"ᴀʟʙᴜᴍ - {title}",
                "playlist": f"ᴘʟᴀʏʟɪsᴛ - {title}",
                "artist":   f"ᴀʀᴛɪsᴛ - {artist}",
            }

            button_label = button_label_map.get(result_type)
            if button_label:
                buttons.append([InlineKeyboardButton(text=button_label, callback_data=f"{result_type}#{item_id}")])

        text = (
            f"**ᴛᴏᴛᴀʟ ʀᴇsᴜʟᴛs:** {total_results}\n\n"
            f"**sᴇᴀʀᴄʜ Qᴜᴇʀʏ:** {query}\n\n"
            f"**ᴘᴀɢᴇ ɴᴏ:** {page_no}"
        )
        navigation_buttons = []
        if page_no > 1:
            navigation_buttons.append(InlineKeyboardButton("ᴘʀᴇᴠɪᴏᴜs", callback_data=f"search#{search_type}#{page_no-1}"))
        if total_results > 10 * page_no:
            navigation_buttons.append(InlineKeyboardButton("ɴᴇxᴛ", callback_data=f"search#{search_type}#{page_no+1}"))
        if navigation_buttons:
            buttons.append(navigation_buttons)

    if not buttons:
        return await send_msg.edit(f'ɴᴏ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛ ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ Qᴜᴇʀʏ `{query}`')

    buttons.append([InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data="close")])
    await send_msg.edit(text, reply_markup=InlineKeyboardMarkup(buttons))
