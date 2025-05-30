import re
import sys
import os
import io
from telegram import Update, InputFile
from telegram.ext import ContextTypes
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..')
    )
)
from utilities.downloaders.reddit import download_reddit_post_async

#INSTAGRAM_PATTERN = re.compile(
#    r'https?://(?:www\.)?instagram\.com/[A-Za-z0-9_.-]+/?', 
#    re.IGNORECASE
#)
REDDIT_PATTERN = re.compile(
    r'https?://(?:www\.)?'
    r'(?:'
      r'reddit\.com/r/[A-Za-z0-9_]+/'
        r'(?:comments|s)/[A-Za-z0-9]+'
      r'|redd\.it/[A-Za-z0-9]+'
    r')'
    r'/?',
    re.IGNORECASE
)


async def url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    video_bytes = None

    if REDDIT_PATTERN.match(url):
        video_bytes = await download_reddit_post_async(url)

    if not video_bytes:
        await update.message.reply_text("Video download failed")
        return

    bio = io.BytesIO(video_bytes)
    bio.name = "video.mp4"

    await context.bot.send_video(
        chat_id = update.effective_chat.id,
        message_thread_id = update.message.message_thread_id,
        supports_streaming = True,
        video = InputFile(bio, filename='video.mp4')
    )
