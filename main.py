from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
import asyncio

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Привет"), KeyboardButton(text="Пока")]
        ],
        resize_keyboard=True
    )

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Новости", url="https://news.google.com")],
            [InlineKeyboardButton(text="Музыка", url="https://music.youtube.com")],
            [InlineKeyboardButton(text="Видео", url="https://youtube.com")],
            [InlineKeyboardButton(text="Показать больше", callback_data="show_more")]
        ]
    )

    await message.answer("Выберите действие:", reply_markup=keyboard)
    await message.answer("Дополнительные опции:", reply_markup=inline_keyboard)


@dp.message()
async def button_response(message: types.Message):
    if message.text == "Привет":
        await message.answer(f"Привет, {message.from_user.first_name}!")
    elif message.text == "Пока":
        await message.answer(f"До свидания, {message.from_user.first_name}!")


@dp.callback_query(lambda c: c.data == "show_more")
async def show_more_buttons(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Опция 1", callback_data="option_1")],
            [InlineKeyboardButton(text="Опция 2", callback_data="option_2")]
        ]
    )
    await callback.message.edit_text("Выберите опцию:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith("option_"))
async def option_selected(callback: types.CallbackQuery):
    option = "Опция 1" if callback.data == "option_1" else "Опция 2"
    await callback.message.answer(f"Вы выбрали: {option}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
