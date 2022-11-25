import asyncio
import os
import csv
import emoji
from dotenv import load_dotenv

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InputFile, ChatActions
from aiogram.types.message import ContentType
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.markdown import text, bold, pre, italic, code
from aiogram.types import ParseMode
from messages import MESSAGES
from utils import TestStates
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


URL_TEMPLATE = 'https://spb.hh.ru/search/vacancy?area=2&clusters=true&enable_snippets=true&experience=noExperience&ored_clusters=true&text=python+django+%7C+python&order_by=publication_time&hhtmFrom=vacancy_search_list'
FILE_NAME = 'result.csv'

TOKEN = '5219303623:AAHVY3MChKpwrMtLbhzyRCrXHjMvGLtHmLs'


def parse(url=URL_TEMPLATE):
    result_list = []
    ser = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=ser)
    driver.get(url)
    html = driver.page_source
    result_list = []

    soup = bs(html, 'html.parser')
    vacancies_names = soup.find_all('a', attrs={'data-qa': 'serp-item__title'})
    vacancies_employers = soup.find_all(
        'a',
        attrs={'data-qa': 'vacancy-serp__vacancy-employer'}
    )
    vacancies_descriptions = soup.find_all(
        'div',
        attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}
    )
    vacancies_requirements = soup.find_all(
        'div',
        attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}
    )
    for name, employer, description, requirements in zip(
        vacancies_names,
        vacancies_employers,
        vacancies_descriptions,
        vacancies_requirements
    ):
        result_list.append({
            'Vacancy': name.text,
            'Employer': employer.text,
            'Description': description.text,
            'Requirements': requirements.text,
            'Link': name['href']
        })
    driver.close()
    return result_list


def create_csv_file(data):
    with open(FILE_NAME, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


# data = parse()
VOICE = 'voicefile'
CAT_BIG_EYES = ''#InputFile('nice.png')
CSV_FILE = InputFile('result.csv')


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())




@dp.message_handler(commands=['start'])
async def process_start_command(message):
    await message.reply(MESSAGES['start'])


@dp.message_handler(commands=['help_old'])
async def process_help_old_command(message):
    msg = text(bold('I can answer on:'), '/text', '/file', '/group', sep='\n')
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['help'])
async def process_help_command(message):
    await message.reply(MESSAGES['help'])




@dp.message_handler(state='*', commands=['setstate'])
async def process_setstate_command(message):
    argument = message.get_args()
    state = dp.current_state(user=message.from_user.id)
    if not argument:
        await state.reset_state()
        return await message.reply(MESSAGES['state_reset'])
    if (not argument.isdigit()) or (not int(argument) < len(TestStates.all())):
        return await message.reply(MESSAGES['invalid_key'].format(key=argument))
    await state.set_state(TestStates.all()[int(argument)])
    await message.reply(MESSAGES['state_change'], reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_1)
async def first_test_state_case_met(message):
    await message.reply('First!!!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_2[0])
async def second_test_state_case_met(message):
    await message.reply('Second!!!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_3 | TestStates.TEST_STATE_4)
async def third_or_fourth_test_state_case_met(message: types.Message):
    await message.reply('Третий или четвертый!', reply=False)


@dp.message_handler(commands=['voice'])
async def process_voice_command(message):
    await bot.send_voice(
        message.from_user.id,
        VOICE,
        reply_to_message_id=message.message_id
        )


@dp.message_handler(state=TestStates.all())
async def some_test_state_case_met(message: types.Message):
    state =  dp.current_state(user=message.from_user.id)
    text = MESSAGES['current_state'].format(
        current_state=await state.get_state(),
        states=TestStates.all()
    )
    await message.reply(text, reply=False)


async def shutdown(dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()



@dp.message_handler(commands=['photo'])
async def process_photo_command(message):
    caption = emoji.emojize('Nice! :eyes:')
    id_photo = CAT_BIG_EYES
    print(f'file_id= {id_photo}')
    await bot.send_photo(
        message.from_user.id,
        CAT_BIG_EYES,
        caption=caption,
        reply_to_message_id=message.message_id
        )


@dp.message_handler(commands=['file'])
async def process_file_command(message):
    user_id = message.from_user.id
    await bot.send_chat_action(user_id, ChatActions.UPLOAD_DOCUMENT)
    await asyncio.sleep(1)
    await bot.send_document(
        user_id,
        CSV_FILE,
        caption=' csv file ready'
    )


@dp.message_handler()
async def echo_message(msg):
    await bot.send_message(msg.from_user.id, msg.text)


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(msg: types.Message):
    message_text = text(emoji.emojize('Я не знаю, что с этим делать :eyes:'),
                        italic('\nЯ просто напомню,'), 'что есть',
                        code('команда'), '/help')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
