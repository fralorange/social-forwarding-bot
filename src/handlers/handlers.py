from telegram import MessageEntity
from telegram.ext import filters, MessageHandler
from handlers.message.url_handler import url

handlers = []

# Initialize handlers

url_handler = MessageHandler(
   filters.TEXT & (
      filters.Entity(MessageEntity.URL) |
      filters.Entity(MessageEntity.TEXT_LINK)
   ), 
   url
)

# Append handlers

handlers.append(url_handler)
