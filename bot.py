from model import Model
import os, argparse, asyncio

from telegram import Update
from telegram.ext import MessageHandler
from telegram.ext import filters, Application

parser = argparse.ArgumentParser()
parser.add_argument('id', type=int, help='bot owner id')
parser.add_argument('token', type=str, help='bot token')

args = parser.parse_args()
model = Model('vox.csv', 'ecapa_vox.npy')

async def handle_text(update, context):

    usage = "Please, send me a voice message."
    await update.message.reply_text(usage)

async def handle_voice(update, context):

    loop = asyncio.get_running_loop()

    voice = update.message.voice
    user = update.message.from_user
    chat_id = update.message.chat_id

    file = await context.bot.get_file(voice)
    path = voice['file_unique_id'] + '.ogg'
    await file.download_to_drive(path)

    result = await loop.run_in_executor(None, model.predict, path)
    await update.message.reply_text(result, disable_web_page_preview=True)

    if user['id'] == args.id:
        msg = f"@{user['username']} {user['id']}"
        await context.bot.send_message(args.id, msg)
        await context.bot.send_voice(args.id, voice['file_id'])

    os.remove(path)

app = Application.builder().token(args.token).build()
app.add_handler(MessageHandler(filters.TEXT, handle_text))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.run_polling(allowed_updates=Update.ALL_TYPES)