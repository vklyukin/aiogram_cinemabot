import aiohttp
import argparse
import asyncio
import logging
import os
import sys
import typing as tp

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor, markdown
from aiogram.dispatcher.webhook import SendMessage

import speech
from fetch_movie import fetch_movie, imdb_random_from_top


def parse_arguments() -> tp.Tuple[str, tp.Optional[str], tp.Optional[aiohttp.BasicAuth]]:
    """
    Parse arguments and return them.
    :return: tuple of bot_token, optional host and `aiohttp.BasicAuth` with proxy authentication
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('bot_token', metavar='token', type=str, help='telegram bot token')
    parser.add_argument('--proxy_host', type=str, help='proxy host')
    parser.add_argument('--proxy_creds', type=str, help='proxy credentials')

    args = parser.parse_args()
    proxy_host = args.proxy_host
    proxy_credentials = args.proxy_creds
    if proxy_credentials:
        login, password = proxy_credentials.split(':')
        proxy_auth = aiohttp.BasicAuth(login=login, password=password)
    else:
        proxy_auth = None
    return args.bot_token, proxy_host, proxy_auth


bot_token, proxy_host, proxy_auth = parse_arguments()
bot = Bot(token=bot_token, proxy=proxy_host, proxy_auth=proxy_auth)
dp = Dispatcher(bot)

logger = logging.getLogger('bot_logger')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
logger.setLevel(logging.DEBUG)

event_loop = asyncio.get_event_loop()

WEBHOOK_HOST = os.environ.get('HOST')
WEBHOOK_PATH = os.environ.get('PATH')
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = 'localhost'
WEBAPP_PORT = 3001


@dp.message_handler(commands=['start'])
async def send_start(message: types.Message):
    """

    :param message: user's message
    """
    logger.debug(f'start: {message.from_user.username}')
    # await message.reply(speech.lines['start'])
    return SendMessage(message.chat.id, speech.lines['start'], parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    """
    Tells user what can this bot do
    :param message: user's message
    """
    logger.debug(f'help: {message.from_user.username}')
    # await message.reply(speech.lines['help'], parse_mode=types.ParseMode.MARKDOWN)
    return SendMessage(message.chat.id, speech.lines['help'], parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['random'])
async def send_randomly_picked(message: types.Message) -> SendMessage:
    """
    Randomly picks movie from IMDb top-250
    :param message: user's message
    """
    logger.debug(f'random: {message.from_user.username}')
    result = await imdb_random_from_top(event_loop)
    if result is not None:
        title, link, rating = result
        link = markdown.link('IMDb url', link)
        # await message.reply(speech.lines['random_movie'].format(title, link, rating),
        #                     parse_mode=types.ParseMode.MARKDOWN)
        logger.debug(f'random: {message.from_user.username} - result: {result}')
        return SendMessage(message.chat.id, speech.lines['random_movie'].format(title, link, rating),
                           parse_mode=types.ParseMode.MARKDOWN)
    else:
        # await message.reply(speech.lines['not_available'], parse_mode=types.ParseMode.MARKDOWN)
        logger.debug(f'random: {message.from_user.username} - result: not_available')
        return SendMessage(message.chat.id, speech.lines['not_available'], parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(content_types=types.ContentType.TEXT)
async def browse_movie(message: types.Message) -> SendMessage:
    """
    Finds link forwarding to the website where user could watch film
    :param message: user's message
    """
    logger.debug(f'browsing: {message.from_user.username}')
    result = await fetch_movie(event_loop, message.text)
    if result is not None:
        # await message.reply(speech.lines['film_found'].format(*result), parse_mode=types.ParseMode.MARKDOWN)
        logger.debug(f'browsing: {message.from_user.username} - result: {result}')
        return SendMessage(message.chat.id, speech.lines['film_found'].format(*result),
                           parse_mode=types.ParseMode.MARKDOWN)
    else:
        # await message.reply(speech.lines['no_such_film'].format(message.text), parse_mode=types.ParseMode.MARKDOWN)
        logger.debug(f'browsing: {message.from_user.username} - result: not_found')
        return SendMessage(message.chat.id, speech.lines['no_such_film'].format(message.text),
                           parse_mode=types.ParseMode.MARKDOWN)


async def on_startup(dp: Dispatcher) -> None:
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp: Dispatcher) -> None:
    logging.warning('Shutting down..')


if __name__ == '__main__':
    logger.debug('starting bot...')
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
