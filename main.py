import asyncio
from logging import basicConfig, INFO

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import token
from handlers import router


async def main():
    bot = Bot(token=token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=False)


if __name__ == "__main__":
    basicConfig(level=INFO)
    asyncio.run(main())
