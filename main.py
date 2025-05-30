import logging
import json
from telegram import Update
from telegram.ext import Application, ContextTypes
from utilities.token import get_token
from handlers.handlers import handlers
from handlers.error.error_handler import error_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

application = Application.builder().token(get_token()).build()
application.add_handlers(handlers)
application.add_error_handler(error_handler)

async def handler(event, context):
    body = json.loads(event['body'])

    update = Update.de_json(body, application.bot)
    await application.initialize()
    await application.process_update(update)
    await application.shutdown()

    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'ok'})
    }
