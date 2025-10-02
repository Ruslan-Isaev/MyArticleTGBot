import asyncio
import aiogram
import random
import logging
import os
from aiohttp import web
from dotenv import load_dotenv
from assets.laws import law_list
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "your_token")

# Настройки вебхука
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://yourdomain.com")  # Ваш домен
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST", "127.0.0.1")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT", 8080))

# Режим работы: webhook или polling
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для команды <code>Моя статья</code>. Напишите команду и я вам отправлю случайную статью УК РФ с вашим ником.", parse_mode=ParseMode.HTML)

@dp.message(F.text.lower().contains('моя статья'))
async def cmd_mc(message: Message):
    user_id = message.from_user.id
    user_fullname = message.from_user.full_name
    user_link = f'tg://user?id={user_id}'
    await message.answer(f"🤷‍♂️ Сегодня <a href='{user_link}'>{user_fullname}</a> приговаривается к статье {random.choice(law_list)}", parse_mode=ParseMode.HTML)

@dp.message()
async def cmd_error(message: Message):
    if message.chat.type == 'private':
        await message.answer("Я понимаю только команду <code>Моя статья</code>, других команд я не знаю.", parse_mode=ParseMode.HTML)
    else:
        pass

@dp.inline_query()
async def inline_query_handler(query: InlineQuery):
    results = [
        InlineQueryResultArticle(
            id="1",
            title="Моя статья",
            input_message_content=InputTextMessageContent(
                message_text=f"🤷‍♂️ Сегодня я приговариваюсь к статье {random.choice(law_list)}", parse_mode=ParseMode.HTML
            )
        )
    ]
    await query.answer(results=results, is_personal=True, cache_time=0)

async def health_check(request):
    return web.Response(text="OK")

async def on_shutdown():
    logger.info("Завершение работы бота...")
    await bot.session.close()

async def on_startup():
    if USE_WEBHOOK:
        logger.info(f"Настройка вебхука: {WEBHOOK_URL}")
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "inline_query"]
        )
        logger.info("Вебхук успешно настроен!")
    else:
        # Удаляем вебхук если используем polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Вебхук удален, используется polling")

async def start_webhook():
    app = web.Application()
    app.router.add_get("/health", health_check)
    app.router.add_get("/", health_check)
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    await on_startup()

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)

    logger.info(f"Запуск сервера на {WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
    logger.info(f"Вебхук URL: {WEBHOOK_URL}")

    try:
        await site.start()
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await on_shutdown()
        await runner.cleanup()

async def start_polling():
    await on_startup()

    try:
        logger.info("Запуск бота в режиме polling...")
        await dp.start_polling(bot, drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await on_shutdown()

async def main():
    logger.info("Бот запускается...")
    logger.info(f"Версия aiogram: {aiogram.__version__}")
    logger.info(f"Режим работы: {'Webhook' if USE_WEBHOOK else 'Polling'}")

    if USE_WEBHOOK:
        await start_webhook()
    else:
        await start_polling()

if __name__ == "__main__":
    import aiogram
    asyncio.run(main())
