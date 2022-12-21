import json
import time
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InputMedia, InputMediaPhoto
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from bot_token import token
import constants
import  bot_functions


class NewsForPeriod(StatesGroup):
    step_1 = State()

class CountAbbs(StatesGroup):
    step_1 = State()
    
class ActiveCommentators(StatesGroup):
    step_1 = State()



# инициализируем бота
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start', 'help'])
async def help_message(message: types.Message):
    await message.answer(constants.hello_message)
    
    
@dp.message_handler(commands=['news_for_period'])
async def news_for_period_required(message: types.Message):
    await message.answer(constants.news_for_period_description)
    await NewsForPeriod.step_1.set()
    
    
@dp.message_handler(state=NewsForPeriod.step_1)
async def return_news_for_period(message: types.Message, state: FSMContext):
    try:
        assert len(message.text.split(' ')) == 2
        start, end = message.text.split(' ')
        await bot_functions.news_for_period(start_date=start, end_date=end, message=message)
    except:
        await message.answer('Ошибка. Возможно, аргументы введены неправильно. Возвращаемся в главное меню')
    
    await state.finish()
    
    
@dp.message_handler(commands=['count_abbs'])
async def count_abbs_required(message: types.Message):
    await message.answer(constants.count_abbs_description)
    await CountAbbs.step_1.set()
    
    
@dp.message_handler(state=CountAbbs.step_1)
async def return_count_abbs(message: types.Message, state: FSMContext):
    try:
        assert len(message.text.split(' ')) == 3
        start, end, theme = message.text.split(' ')
        await bot_functions.count_abbs(start_date=start, end_date=end, theme=theme, message=message)
    except:
        await message.answer('Ошибка. Возможно, аргументы введены неправильно. Возвращаемся в главное меню')
    
    await state.finish()
    
    
@dp.message_handler(commands=['active_commentators'])
async def active_commentators_required(message: types.Message):
    await message.answer(constants.active_commentators_description)
    await ActiveCommentators.step_1.set()
    
    
@dp.message_handler(state=ActiveCommentators.step_1)
async def return_active_commentators(message: types.Message, state: FSMContext):
    try:
        assert len(message.text.split(' ')) == 2
        start, end = message.text.split(' ')
        await bot_functions.active_commentators(start_date=start, end_date=end, message=message)
    except:
        await message.answer('Ошибка. Возможно, аргументы введены неправильно. Возвращаемся в главное меню')
    
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
