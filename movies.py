import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
import requests

from config import TOKEN, TMDB_API_KEY

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

router = Router()

@router.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply("Привет, Женечка! Я твой бот для поиска фильмов. Вот что я умею:\n"
                       "/find <название> - найти фильм\n"
                       "/popular - популярные фильмы")

# Команда /find - поиск фильма по названию
@router.message(Command("find"))
async def find_movie(message: Message):
    try:
        command, *args = message.text.split(maxsplit=1)  # Разделяем команду и аргументы
        movie_name = args[0] if args else None  # Берём первый аргумент (название фильма)

        if not movie_name:
            await message.reply("Пожалуйста, укажи название фильма после команды /find.")
            return

        await search_and_send_movie(message, movie_name)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply(f"Что-то пошло не так: {e}")

async def search_and_send_movie(message: Message, movie_name: str):
    try:
        logging.info(f"Поиск фильма: {movie_name}")

        # Запрос к TMDb API с русским языком
        url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}&language=ru'
        response = requests.get(url)
        if response.status_code == 200:
            movies = response.json()['results']
            if movies:
                movie = movies[0]
                title = movie['title']
                overview = movie['overview']
                rating = movie['vote_average']
                poster_path = movie['poster_path']
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

                reply_text = f"🎬 <b>{title}</b>\n\n"
                reply_text += f"⭐ Рейтинг: {rating}\n\n"
                reply_text += f"📝 Описание: {overview}\n\n"

                if poster_url:
                    await message.reply_photo(poster_url, caption=reply_text, parse_mode=ParseMode.HTML)
                else:
                    await message.reply(reply_text, parse_mode=ParseMode.HTML)
            else:
                await message.reply("Фильм не найден. Попробуй ещё раз!")
        else:
            await message.reply("Ошибка при запросе к API. Попробуй позже.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply(f"Что-то пошло не так: {e}")

@router.message(Command("popular"))
async def popular_movies(message: Message):
    logging.info("Обработчик команды /popular вызван")
    try:
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=ru'
        response = requests.get(url)

        logging.info(f"Ответ от API: {response.json()}")

        if response.status_code == 200:
            movies = response.json().get('results', [])[:5]
            if not movies:
                await message.reply("Не удалось получить список популярных фильмов.")
                return

            reply_text = "🍿 <b>Популярные фильмы:</b>\n\n"
            for movie in movies:
                title = movie.get('title', 'Название неизвестно')
                rating = movie.get('vote_average', 'Рейтинг неизвестен')
                reply_text += f"🎬 <b>{title}</b> (⭐ {rating})\n"

            await message.reply(reply_text, parse_mode=ParseMode.HTML)
        else:
            await message.reply("Ошибка при запросе к API. Попробуй позже.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply(f"Что-то пошло не так: {e}")

@router.message()
async def handle_movie_name(message: Message):
    try:
        if message.text.startswith("/"):
            return

        movie_name = message.text
        await search_and_send_movie(message, movie_name)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply(f"Что-то пошло не так: {e}")

dp.include_router(router)


if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=True)