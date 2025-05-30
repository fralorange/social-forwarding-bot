import logging
from telegram import Update
from telegram.ext import ContextTypes

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Error in Update %s: %s", update, context.error, exc_info=context.error)
