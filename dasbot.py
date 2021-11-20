# TODO: use Motor for Mongo?

import logging

import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from pymongo import MongoClient

from dasbot.db.dict_repo import DictRepo
from dasbot.db.chats_repo import ChatsRepo
from dasbot.db.stats_repo import StatsRepo
from dasbot.interface import Interface
from dasbot.broadcaster import Broadcaster
from dasbot.controller import Controller
from dasbot.menu_controller import MenuController

from dynaconf import settings

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m.%d %H:%M:%S')
log = logging.getLogger(__name__)


if __name__ == '__main__':

    # Initialize bot & dispatcher
    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher(bot)

    # /help command handler
    @dp.message_handler(commands='help')
    async def help_command(message: types.Message):
        log.debug('/help received: %s', message)
        await chatcon.help(message)

    # /start command handler
    @dp.message_handler(commands='start')
    async def start_command(message: types.Message):
        log.debug('/start received: %s', message)
        await chatcon.start(message)

    # /settings command handler
    @dp.message_handler(commands='settings')
    async def settings_command(message: types.Message):
        log.debug('/settings received: %s', message)
        await menucon.main(message)

    # handler for the settings menu callbacks
    @dp.callback_query_handler()
    async def settings_select(query: types.CallbackQuery):
        log.debug('callback query received: %s', query)
        await menucon.navigate(query)

    # /stats command handler
    @dp.message_handler(commands='stats')
    async def stats_command(message: types.Message):
        log.debug('/stats received: %s', message)
        await chatcon.stats(message, dictionary)

    # generic message handler; should be last
    @dp.message_handler()
    async def all_other_messages(message: types.Message):
        log.debug('generic message received: %s', message)
        await chatcon.generic(message)

    # TODO: Add DB auth
    log.debug('connecting to database: %s', settings.DB_ADDRESS)
    client = MongoClient(settings.DB_ADDRESS)
    db = client[settings.DB_NAME]
    
    dictionary = DictRepo(db['dictionary']).load()
    chats_repo = ChatsRepo(db['chats'], db['scores'])
    stats_repo = StatsRepo(db['scores'], db['stats'])
    chatcon = Controller(bot, chats_repo, stats_repo, dictionary)
    broadcaster = Broadcaster(Interface(bot), chats_repo, dictionary)
    menucon = MenuController(Interface(bot), chats_repo)

    loop = asyncio.get_event_loop()
    loop.create_task(broadcaster.run())
    executor.start_polling(dp)
