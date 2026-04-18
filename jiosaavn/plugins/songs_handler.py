import os
import html
import logging
import traceback

from jiosaavn.bot import Bot
from api.jiosaavn import Jiosaavn
from jiosaavn.config.settings import HOST, PORT

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


logger = logging.getLogger(__name__)

@Bot.on_callback_query(filters.regex(r"^song#"))
async def handle_song_callback(client: Bot, callback: CallbackQuery):
    msg = callback.message
    await callback.answer()

    data = callback.data.split("#")
    song_id = data[1]
    item_id, search_type, back_type = (None, "songs", None)
    if len(data) == 3:
        search_type = data[2]
    elif len(data) >= 4:
        item_id, search_type = (data[2], data[3])
        if len(data) == 5:
            back_type = data[4]

    try:
        response = await Jiosaavn().get_song(song_id=song_id)
        if not response or not response.get("songs"):
            return await msg.edit("**ᴛʜᴇ ʀᴇQᴜᴇsᴛᴇᴅ sᴏɴɢ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ғᴏᴜɴᴅ.**")
    except RuntimeError as e:
        logger.error(e)
        traceback.print_exc()
        return await msg.edit("ᴄᴏɴɴᴇᴄᴛɪᴏɴ ʀᴇғᴜsᴇᴅ ʙʏ ᴊɪᴏsᴀᴀᴠɴ ᴀᴘɪ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ")

    song_data = response["songs"][0]

    title = song_data.get("title", "ᴜɴᴋɴᴏᴡɴ")
    title = html.unescape(title)
    formatted_title = title.replace(" ", "-")
    language = song_data.get("language", "ᴜɴᴋɴᴏᴡɴ")
    play_count = song_data.get("play_count", "0")
    play_count = int(play_count) if play_count else 0
    more_info = song_data.get("more_info", {})
    album = more_info.get("album", "ᴜɴᴋɴᴏᴡɴ")
    artist_map = more_info.get("artistMap", {})
    artists = artist_map.get("artists", [])

    def get_artist_by_role(role: str) -> str:
        return ", ".join(artist.get("name") for artist in artists if artist.get("role") == role)

    music = more_info.get("music") or get_artist_by_role("music")
    singers = get_artist_by_role("singer")
    lyricists = get_artist_by_role("lyricist")
    actors = get_artist_by_role("starring")
    release_date = more_info.get("release_date")
    release_year = song_data.get("year")
    album_url = more_info.get("album_url", "")
    image_url = song_data.get("image", "").replace("150x150", "500x500")
    song_url = song_data.get('perma_url', f"https://jiosaavn.com/songs/{formatted_title}/{song_id}")

    text_data = [
        f"[\u2063]({image_url})"
        f"**sᴏɴɢ:** [{title}]({song_url})" if title else '',
        f"**ᴀʟʙᴜᴍ:** [{album}]({album_url})" if album else '',
        f"**ᴍᴜsɪᴄ:** {music}" if music else '',
        f"**ᴘʟᴀʏs:** {play_count:,}" if play_count else '',
        f"**sɪɴɢᴇʀs:** {singers}" if singers else '',
        f"**ʟʏʀɪᴄɪsᴛ:** {lyricists}" if lyricists else '',
        f"**ᴀᴄᴛᴏʀs:** {actors}" if actors else '',
        f"**ʟᴀɴɢᴜᴀɢᴇ:** {language}" if language else '',
        f"**ʀᴇʟᴇᴀsᴇ ᴅᴀᴛᴇ:** __{release_date}__" if release_date else '',
        f"**ʀᴇʟᴇᴀsᴇ ʏᴇᴀʀ:** __{release_year}__" if not release_date and release_year else '',
    ]
    text = "\n\n".join(filter(None, text_data))

    if item_id:
        back_button_callback_data = f"{search_type}#{item_id}"
        if back_type:
            back_button_callback_data += f"#{back_type}"
    else:
        back_button_callback_data = f"search#{search_type}"

    buttons = [[
        InlineKeyboardButton('ᴜᴘʟᴏᴀᴅ ᴛᴏ ᴛɢ', callback_data=f'upload#{song_id}#song')
    ], [
        InlineKeyboardButton('ʙᴀᴄᴋ', callback_data=back_button_callback_data)
    ], [
        InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data="close")
    ]]

    if more_info.get('has_lyrics') == 'true':
        lyrics_id = song_data.get("id")
        lyrics_button_callback_data = f"lyrics#{lyrics_id}#{song_id}#{search_type}"
        if item_id:
            lyrics_button_callback_data += f"#{item_id}#{back_type}"
        buttons[0].insert(0, InlineKeyboardButton("ʟʏʀɪᴄs", callback_data=lyrics_button_callback_data))

    await msg.edit(text=text[:4096], reply_markup=InlineKeyboardMarkup(buttons))

    await Jiosaavn()._request_data(url=f"http://{HOST}:{PORT}")


@Bot.on_callback_query(filters.regex(r"^lyrics#"))
async def lyrics(client: Bot, callback: CallbackQuery):
    data = callback.data.split('#')
    lyrics_id = data[1]

    response = await Jiosaavn().get_song_lyrics(lyrics_id=lyrics_id)
    lyrics_text = response.get("lyrics", "")
    lyrics_text = lyrics_text.replace("<br>", "\n")
    if not lyrics_text:
        await callback.answer("ᴛʜᴇ ʀᴇQᴜᴇsᴛᴇᴅ sᴏɴɢ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ғᴏᴜɴᴅ.", show_alert=True)
        return

    if len(lyrics_text) <= 4096:
        callback_data = "song#" + "#".join(data[2:])
        button = [[InlineKeyboardButton('ʙᴀᴄᴋ', callback_data=callback_data)]]
        try:
            await callback.answer()
            await callback.message.edit(lyrics_text, reply_markup=InlineKeyboardMarkup(button))
        except:
            pass
    else:
        await callback.answer("sᴇɴᴅɪɴɢ ᴀ sᴏɴɢ ʟʏʀɪᴄs ᴅᴏᴄᴜᴍᴇɴᴛ")
        file_location = f'{response.get("snippet")} song lyrics.txt'
        with open(file_location, 'w') as f:
            f.write(lyrics_text)

        await client.send_document(
            chat_id=callback.from_user.id,
            document=file_location
        )

        os.remove(file_location)
