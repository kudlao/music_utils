import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession
from pydub import AudioSegment
from pytubefix import YouTube


logging.basicConfig(level=logging.INFO)


bot_token = "bot_token"

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg"


max_file_size_bytes = 45 * 1024 * 1024
chunk_duration_ms = 25 * 60 * 1000


session = AiohttpSession()
bot = Bot(token=bot_token, session=session)
bot.session.timeout = 600

dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Hi! I download audio from YouTube as voice messages. 🎙\n\n"
        "📈 If the podcast is small (up to 40 MB), I'll send it as a single voice message.\n"
        "✂️ If the video is long, I'll automatically split it into 20-minute segments!\n"
        "⚡️ A speed control button (0.5x – 2x) will be available right in the chat."
    )


@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    url = message.text
    user_id = message.from_user.id
    status_msg = await message.answer("⏳ Authorization and search...")


    download_filename = f"audio_{user_id}"
    raw_file_path = None

    try:

        yt = YouTube(url, client='WEB_EMBED', use_oauth=True)
        audio_stream = yt.streams.filter(only_audio=True).first()

        if not audio_stream:
            await status_msg.edit_text("❌ Audio track not found.")
            return

        await status_msg.edit_text(f"📥 Downloading: *{yt.title}*...", parse_mode="Markdown")


        raw_file_path = audio_stream.download(filename=download_filename, max_retries=2)
        raw_file_path = os.path.abspath(raw_file_path)


        file_size = os.path.getsize(raw_file_path)
        logging.info(f"File downloaded. Size: {file_size} byte. Limit: {max_file_size_bytes} byte.")

        await status_msg.edit_text("⚙️ I process audio and encode it into a voice message...")
        sound = AudioSegment.from_file(raw_file_path)


        if file_size <= max_file_size_bytes:
            await status_msg.edit_text("🚀 Sending voice...")

            ogg_name = f"ogg_{user_id}.ogg"
            sound.export(ogg_name, format="ogg", codec="libopus")

            audio_file = FSInputFile(ogg_name, filename=f"{yt.title}.ogg")


            await message.reply_voice(
                voice=audio_file,
                caption=f"🎙 {yt.title}"
            )

            os.remove(raw_file_path)
            os.remove(ogg_name)


        else:
            await status_msg.edit_text("✂️ Big file. I’m cutting it into 20-minute segments....")

            duration = len(sound)


            chunks = [sound[i:i + chunk_duration_ms] for i in range(0, duration, chunk_duration_ms)]
            await status_msg.edit_text(f"📦 Total parts: {len(chunks)}. Start sending voices..")

            for idx, chunk in enumerate(chunks):
                chunk_name = f"chunk_{user_id}_{idx}.ogg"


                chunk.export(chunk_name, format="ogg", codec="libopus")

                await status_msg.edit_text(f"🚀 Send chunk {idx + 1} from {len(chunks)}...")


                audio_file = FSInputFile(chunk_name, filename=f"{yt.title} - Chunk {idx + 1}.ogg")


                await message.reply_voice(
                    voice=audio_file,
                    caption=f"🎙 {yt.title} — Chunk {idx + 1} from {len(chunks)}"
                )

                os.remove(chunk_name)
                await asyncio.sleep(2)


            try:
                os.remove(raw_file_path)
                logging.info("The source file has been successfully deleted from the disk.")
            except Exception as rm_error:
                logging.error(f"Failed to delete the source file: {rm_error}")

        await status_msg.delete()

    except Exception as e:
        logging.error(f"Processing error: {e}")
        await message.answer(f"❌ Error: {e}")


        if raw_file_path and os.path.exists(raw_file_path):
            try:
                os.remove(raw_file_path)
            except:
                pass
        if 'ogg_name' in locals() and os.path.exists(ogg_name):
            try:
                os.remove(ogg_name)
            except:
                pass


async def main():
    print("🤖 The bot has been successfully launched.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopping...")