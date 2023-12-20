import time

from aiogram import Router, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from re import findall

import config


class Register(StatesGroup):
    trip = State()
    number_of_members = State()
    mail = State()
    screen = State()


sended = dict()


router = Router()
inline_kb_screen = InlineKeyboardButton(text="Отправить скриншот оплаты", callback_data="screen")
inline_kb_about = InlineKeyboardButton(text='Наш сайт', url='https://www.39dereven.ru/')
markup = InlineKeyboardMarkup(inline_keyboard=[[inline_kb_screen], [inline_kb_about]])

pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"
me = 290326560


@router.callback_query()
async def screen(call, state: FSMContext):
    if call.data == "screen":
        text = "Отправьте, пожалуйста, скриншот с подтверждением оплаты счета"
        await call.message.answer(chat_id=call.from_user.id, text=text)
        await state.set_state(Register.screen)


@router.message(Register.screen)
async def screen_1(msg: Message, state: FSMContext):
    if type(msg.photo) is not None:
        global sended
        print(f"sended start: {sended}")
        if sended[str(msg.from_user.id)]['sended'] == 1:
            print('vhod')
            await msg.forward(chat_id=me)
        else:
            text = f"⬆️#оплата \n@{msg.from_user.username}\n#{msg.from_user.username}"
            await msg.answer(chat_id=me, text=text)
            await msg.forward(chat_id=me)
            sended[str(msg.from_user.id)]['sended'] = 1
            print(f"sended set up: {sended}")
            time.sleep(0.2)
    else:
        await msg.answer(chat_id=msg.from_user.id, text="Кажется, в этом сообщении нет "
                                                        "фото, попробуйте еще раз")


@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(chat_id=msg.from_user.id, text=config.start_text, reply_markup=markup)


@router.message(Command("register"))
async def register_trip(msg: Message, state: FSMContext):
    global sended
    sended[str(msg.from_user.id)] = dict()
    sended[str(msg.from_user.id)]['sended'] = 0
    await msg.answer(chat_id=msg.from_user.id, text=config.trip_text, reply_markup=markup)
    await state.set_state(Register.trip)


@router.message(Register.trip)
async def register_members(msg: Message, state: FSMContext):
    await state.update_data(trip=msg.text)
    await msg.answer(chat_id=msg.from_user.id, text=config.members_text, reply_markup=markup)
    await state.set_state(Register.number_of_members)


@router.message(Register.number_of_members)
async def register_mail(msg: Message, state: FSMContext):
    await state.update_data(members=msg.text)
    await msg.answer(chat_id=msg.from_user.id, text=config.mail_text, reply_markup=markup)
    await state.set_state(Register.mail)


@router.message(Register.mail)
async def register_mail(msg: Message, state: FSMContext):
    if not findall(pattern=pattern, string=msg.text):
        await msg.answer(chat_id=msg.from_user.id, text="Неверный email, попробуйте снова",
                         reply_markup=markup)
        return
    await state.update_data(mail=msg.text)
    await state.update_data(username=msg.from_user.username)
    await state.update_data(user_id=msg.from_user.id)
    await state.update_data(user_full_name=msg.from_user.full_name)
    data = await state.get_data()
    await msg.answer(chat_id=msg.from_user.id, text=config.done, reply_markup=markup)
    text = (f"#Регистрация \n"
            f"#{data['username']}\n\n"
            f"@{data['username']}\n"
            f"id: {data['user_id']}\n"
            f"Имя: {data['user_full_name']}\n\n"
            f"Поездка: {data['trip']}\n"
            f"Кол-во людей: {data['members']}\n"
            f"Почта: {data['mail']}")
    await msg.answer(chat_id=me, text=text)
    await state.clear()
