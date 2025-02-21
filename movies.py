import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
import requests

# Импорт токена и API-ключа из config.py
from config import TOKEN, TMDB_API_KEY

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаём роутер
router = Router()

# Команда /start
@router.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply("Привет, Женечка! Я твой бот для поиска фильмов. Вот что я умею:\n"
                       "/find <название> - найти фильм\n"
                       "/popular - популярные фильмы")

# Команда /find - поиск фильма по названию
@router.message(Command("find"))
async def find_movie(message: Message):
    try:
        # Получаем название фильма из сообщения
        command, *args = message.text.split(maxsplit=1)  # Разделяем команду и аргументы
        movie_name = args[0] if args else None  # Берём первый аргумент (название фильма)

        # Если название фильма не указано, ждём следующее сообщение
        if not movie_name:
            await message.reply("Пожалуйста, укажи название фильма после команды /find.")
            return

        # Ищем фильм
        await search_and_send_movie(message, movie_name)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply(f"Что-то пошло не так: {e}")

# Обработка отдельного сообщения с названием фильма
@router.message()
async def handle_movie_name(message: Message):
    try:
        movie_name = message.text  # Название фильма — это текст сообщения
        await search_and_send_movie(message, movie_name)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply(f"Что-то пошло не так: {e}")

# Функция для поиска и отправки информации о фильме
async def search_and_send_movie(message: Message, movie_name: str):
    try:
        logging.info(f"Поиск фильма: {movie_name}")

        # Запрос к TMDb API с русским языком
        url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}&language=ru'
        response = requests.get(url)
        if response.status_code == 200:
            movies = response.json()['results']
            if movies:
                movie = movies[0]  # Берём первый результат
                title = movie['title']
                overview = movie['overview']
                rating = movie['vote_average']
                poster_path = movie['poster_path']
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

                # Формируем сообщение
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

# Команда /popular - популярные фильмы
@router.message(Command("popular"))
async def popular_movies(message: Message):
    try:
        # Запрос к TMDb API для получения популярных фильмов
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=ru'
        response = requests.get(url)

        # Логируем ответ от API
        logging.info(f"Ответ от API: {response.json()}")

        if response.status_code == 200:
            movies = response.json().get('results', [])  # Берём список фильмов
            if not movies:
                await message.reply("Не удалось получить список популярных фильмов.")
                return

            # Берём топ-5 фильмов
            top_movies = movies[:5]
            reply_text = "🍿 <b>Популярные фильмы:</b>\n\n"
            for movie in top_movies:
                title = movie.get('title', 'Название неизвестно')
                rating = movie.get('vote_average', 'Рейтинг неизвестен')
                reply_text += f"🎬 <b>{title}</b> (⭐ {rating})\n"

            await message.reply(reply_text, parse_mode=ParseMode.HTML)
        else:
            await message.reply("Ошибка при запросе к API. Попробуй позже.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply(f"Что-то пошло не так: {e}")
# Подключаем роутер к диспетчеру
dp.include_router(router)

# Запуск бота
if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=True)