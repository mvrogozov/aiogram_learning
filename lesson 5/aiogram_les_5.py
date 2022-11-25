import asyncio
import logging
import emoji
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, PAYMENTS_PROVIDER_TOKEN, TIME_MACHINE_IMAGE_URL

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

button_hi = KeyboardButton('Hi!')
greet_kb = ReplyKeyboardMarkup()
greet_kb.add(button_hi)
greet_kb1 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_hi)
greet_kb2 = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_hi)

button1 = KeyboardButton(emoji.emojize(':keycap_1:'))
button2 = KeyboardButton(emoji.emojize(':keycap_2:'))
button3 = KeyboardButton(emoji.emojize(':keycap_3:'))

markup3 = ReplyKeyboardMarkup().add(button1).add(button2).add(button3)
markup4 = ReplyKeyboardMarkup().row(
    button1, button2, button3
)

markup5 = ReplyKeyboardMarkup().row(
    button1, button2, button3
).add(KeyboardButton('Middle row'))

button4 = KeyboardButton(emoji.emojize(':keycap_4:'))
button5 = KeyboardButton(emoji.emojize(':keycap_5:'))
button6 = KeyboardButton(emoji.emojize(':keycap_6:'))

markup5.row(button4, button5)
markup5.insert(button6)

markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(emoji.emojize('Send your contact :telephone:'), request_contact=True)
).add(
    KeyboardButton(emoji.emojize('Send your location :world_map:'), request_location=True))


markup_big = ReplyKeyboardMarkup()
markup_big.add(
    button1,
    button2,
    button3,
    button4,
    button5,
    button6
)
markup_big.row(
    button1,
    button2,
    button3,
    button4,
    button5,
    button6
)
markup_big.row(button4, button2)
markup_big.add(button3, button2)
markup_big.insert(button1)
markup_big.insert(button6)
markup_big.insert(KeyboardButton(emoji.emojize(':keycap_9:')))

# inline keyboards

inline_btn_1 = InlineKeyboardButton('First button', callback_data='Button 1')
inline_kb_1 = InlineKeyboardMarkup().add(inline_btn_1)


inline_kb_full = InlineKeyboardMarkup(row_width=2).add(inline_btn_1)
inline_kb_full.add(InlineKeyboardButton('Вторая кнопка', callback_data='btn2'))
inline_btn_3 = InlineKeyboardButton('кнопка 3', callback_data='btn3')
inline_btn_4 = InlineKeyboardButton('кнопка 4', callback_data='btn4')
inline_btn_5 = InlineKeyboardButton('кнопка 5', callback_data='btn5')
inline_kb_full.add(inline_btn_3, inline_btn_4, inline_btn_5)
inline_kb_full.row(inline_btn_3, inline_btn_4, inline_btn_5)
inline_kb_full.insert(InlineKeyboardButton("query=''", switch_inline_query=''))
inline_kb_full.insert(InlineKeyboardButton("query='qwerty'", switch_inline_query='qwerty'))
inline_kb_full.insert(InlineKeyboardButton("Inline в этом же чате", switch_inline_query_current_chat='wasd'))
inline_kb_full.add(InlineKeyboardButton('Уроки aiogram', url='https://surik00.gitbooks.io/aiogram-lessons/content/'))





@dp.message_handler(commands='1')
async def process_command_1(message: types.Message):
    await message.reply('1st inline button', reply_markup=inline_kb_1)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)
    if code == 2:
        await bot.answer_callback_query(
            callback_query.id,
            text='Pressed number 2'
        )
    elif code == 5:
        await bot.answer_callback_query(
            callback_query.id,
            text='Pressed button number 5',
            show_alert=True
        )
    else:
        await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        f'Pressed inline button code = {code}'
        )


@dp.message_handler(commands=['2'])
async def process_command_2(message: types.Message):
    await message.reply(
        'Sending all possible buttons',
        reply_markup=inline_kb_full
    )


#await bot.answer_callback_query(callback_query.id)
#await bot.send_message(callback_query.from_user.id, 'Pressed 1st button')


@dp.message_handler(commands=['rm'])
async def process_rm_command(message: types.Message):
    await message.reply('Removing templates', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['hi7'])
async def process_hi7_command(message: types.Message):
    await message.reply('7th - all together', reply_markup=markup_big)



@dp.message_handler(commands=['hi6'])
async def process_hi6_command(message: types.Message):
    await message.reply(
        '6th - request contact and location',
        reply_markup=markup_request
        )

@dp.message_handler(commands=['hi3'])
async def process_hi3_command(message: types.Message):
    await message.reply('Third - add more buttons', reply_markup=markup3)


@dp.message_handler(commands=['hi4'])
async def process_hi4_command(message: types.Message):
    await message.reply('Fourth - inline buttons', reply_markup=markup4)

@dp.message_handler(commands=['hi5'])
async def process_hi5_command(message: types.Message):
    await message.reply('Fivth - inline buttons', reply_markup=markup5)



@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('Hi!!!', reply_markup=greet_kb)


@dp.message_handler(commands=['hi1'])
async def process_hi1_command(message: types.Message):
    await message.reply('First - change keyboard size', reply_markup=greet_kb1)



@dp.message_handler(commands=['hi2'])
async def process_hi2_command(message: types.Message):
    await message.reply(emoji.emojize('Second - hide keyboard :sunglasses:'), reply_markup=greet_kb2)

executor.start_polling(dp)