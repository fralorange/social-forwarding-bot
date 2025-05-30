import logging
from telegram.ext import ApplicationBuilder
from utilities.token import get_token
from handlers.handlers import handlers
from handlers.error.error_handler import error_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

    
if __name__ == '__main__':
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
    
    application.add_handlers(handlers=handlers)
    application.add_error_handler(error_handler)

    application.run_polling()