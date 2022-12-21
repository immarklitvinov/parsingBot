from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InputMedia, InputMediaPhoto
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


from datetime import datetime, timedelta
import datetime
from bs4 import BeautifulSoup
import requests
import re
import aiohttp
import asyncio


async def news_for_period(start_date, end_date, message):
    # 'dates in string format: "%d-%m-%Y"'
    # '01-12-2022', '03-12-2022'
    # news_for_period('01-12-2022', '03-12-2022')
    
    start = datetime.datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.datetime.strptime(end_date, "%d-%m-%Y")
    assert end > start

    
    tmp = start
    day = timedelta(days=1)
    
    async with aiohttp.ClientSession() as session:
    
        while tmp <= end:
            counter = 1
            string_date = tmp.strftime('%d-%m-%Y')
            
            url = 'https://panorama.pub/news/' + string_date
            day_news = f'Новости на  {string_date} \n'
            
            async with session.get(url) as resp:
                source = await resp.text()
                counter = 1
                soup = BeautifulSoup(source, 'html.parser')
                for elem in soup.find_all("a", {"class": "flex flex-col rounded-md hover:text-secondary hover:bg-accent/[.1] mb-2"}):
                    
                    message_text = f'\n{counter}: ' + elem.find_all("div", {"class": "pt-2 text-xl lg:text-lg xl:text-base text-center font-semibold"})[0].text.strip() + '\n' + \
                                    "https://panorama.pub" + elem.get("href") + '\n'
                    for child in elem.find_all("div", {"class": "mt-3 flex flex-row gap-x-4 text-sm text-gray-500 justify-center"})[0].children:
                        if child.text.strip():
                            message_text += child.text.strip() + '\n'
                            
                    counter += 1
                    day_news += message_text
            
            await message.answer(day_news)
            tmp = tmp + day



async def count_abbs(start_date, end_date, theme, message):
    # 'dates in string format: "%d-%m-%Y"'
    # '01-12-2022', '03-12-2022'
    
    theme_dict = {'Политика': 'politics', 'Экономика': 'economics', 'Общество': 'society', 'Наука': 'science'}
    str_theme = theme_dict[theme]
    start = datetime.datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.datetime.strptime(end_date, "%d-%m-%Y")
    assert end > start
    
    ans = dict()
    
    tmp = start
    day = timedelta(days=1)
    
    async with aiohttp.ClientSession() as session:
        while tmp <= end:
            string_date = tmp.strftime('%d-%m-%Y')
            
            url = f'https://panorama.pub/{str_theme}/{string_date}'
            async with session.get(url) as resp:
                
                source = await resp.text()
                soup = BeautifulSoup(source, 'html.parser')
                
                for elem in soup.find_all("a", {"class": "flex flex-col rounded-md hover:text-secondary hover:bg-accent/[.1] mb-2"}):
                    page_url = "https://panorama.pub" + elem.get("href")
                    async with session.get(page_url) as page_resp:
                        page_source = await page_resp.text()
                        page_soup = BeautifulSoup(page_source, 'html.parser')
                
                        local_abbs = dict()
                        heading = page_soup.find_all("h1")[0].text
                        main_text = page_soup.find_all("div", {"class": "entry-contents pr-0 md:pr-8"})[0].text
                        
                        for abb in re.findall('[А-ЯA-Z]{2,}', heading + main_text):
                            local_abbs[abb] = 1
                            
                        for abb in local_abbs.keys():
                            ans[abb] = ans.get(abb, 0) + 1
                        
            tmp = tmp + day


        
    ans = ans.items()
    ans = sorted(ans, key=lambda x: -x[1])[:10]
    output = f'Самые популярные аббревиатуры по теме {theme}\n\n' + '\n'.join(map(lambda x: x[0] + ': ' + str(x[1]), ans))
    await message.answer(output)


async def active_commentators(start_date, end_date, message):
    # 'dates in string format: "%d-%m-%Y"'
    # '19-10-2022', '20-10-2022'
    
    start = datetime.datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.datetime.strptime(end_date, "%d-%m-%Y")
    assert end > start

    
    ans = dict()
    
    tmp = start
    day = timedelta(days=1)
    
    async with aiohttp.ClientSession() as session:
        
        while tmp <= end:
            string_date = tmp.strftime('%d-%m-%Y')
            
            url = f'https://panorama.pub/news/' + string_date
            async with session.get(url) as resp:
            
                source = await resp.text()
                soup = BeautifulSoup(source, 'html.parser')
                for elem in soup.find_all("a", {"class": "flex flex-col rounded-md hover:text-secondary hover:bg-accent/[.1] mb-2"}):
                    
                    page_url = "https://panorama.pub" + elem.get("href")
                    async with session.get(page_url) as page_resp:
                        page_source = await page_resp.text()     
                        page_soup = BeautifulSoup(page_source, 'html.parser')
                        
                        for each in page_soup.find_all("strong", {"itemprop": "author"}): # итерируемся по именам всех комментаторов
                            ans[each.text.strip()] = ans.get(each.text.strip(), 0) + 1
                    
            tmp = tmp + day
        
    ans = ans.items()
    ans = sorted(ans, key=lambda x: -x[1])[:5]
    output = f'Самые активные комментаторы за период {start_date}-{end_date}\n\n' + '\n'.join(map(lambda x: x[0] + ': ' + str(x[1]), ans))
    await message.answer(output)


            
# asyncio.run(news_for_period('19-10-2022', '19-10-2022'))
# asyncio.run(count_abbs('19-10-2022', '30-10-2022', 'Политика'))
# asyncio.run(active_users('19-10-2022', '30-10-2022'))