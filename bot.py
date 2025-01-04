import ukrf
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
import random
import config
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

# Инициализация бота и диспетчера
bot = Bot(token=config.TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для команды <code>Моя статья</code>. Напишите команду и я вам отправлю случайную статью УК РФ с вашим ником.", parse_mode=ParseMode.HTML)

@dp.message(F.text.lower().contains('моя статья'))
async def cmd_mc(message: Message):
    user_id = message.from_user.id
    user_fullname = message.from_user.full_name
    user_link = f'tg://user?id={user_id}'
    await message.answer(f"🤷‍♂️ Сегодня <a href='{user_link}'>{user_fullname}</a> приговаривается к статье {random.choice(ukrf.ukrflist)}", parse_mode=ParseMode.HTML)

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
                message_text=f"🤷‍♂️ Сегодня я приговариваюсь к статье {random.choice(ukrf.ukrflist)}", parse_mode=ParseMode.HTML
            )
        )
    ]
    await query.answer(results=results, is_personal=True, cache_time=0)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
