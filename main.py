import logging
import json
from telegram import Update
from telegram.ext import ApplicationBuilder
from utilities.token import get_token
from handlers.handlers import handlers
from handlers.error.error_handler import error_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

application = (
    ApplicationBuilder()
        .token(get_token())
        .pool_timeout(5)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(10)
        .media_write_timeout(120)
        .build()
    )
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
