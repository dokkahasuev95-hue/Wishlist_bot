import json
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os

# Берём токен из переменных окружения
TOKEN = os.environ.get("TOKEN")
DB_FILE = "database.json"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ====== Клавиатура ======
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("📋 Посмотреть список хотелок"))
keyboard.add(KeyboardButton("➕ Добавить ссылку"))

# ====== Работа с БД ======
def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ====== Парсинг ссылок ======
def parse_link(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("title").text.strip() if soup.find("title") else "Название не найдено"
    img = soup.find("img")
    image = img["src"] if img and img.get("src") else None
    price = None

    if "wildberries" in url:
        price_tag = soup.find("ins", {"class": "price-block__final-price"})
        if price_tag:
            price = price_tag.text.strip()
    if "ozon" in url:
        price_tag = soup.find("span", {"class": "c3015-a1"})
        if price_tag:
            price = price_tag.text.strip()
    if "market.yandex" in url:
        price_tag = soup.find("span", {"data-auto": "mainPrice"})
        if price_tag:
            price = price_tag.text.strip()

    return {
        "title": title,
        "price": price if price else "Цена не найдена",
        "image": image,
        "url": url
    }

# ====== Команды ======
@dp.message_handler(commands=['start'])
async def start_msg(msg: types.Message):
    await msg.reply("Писулик, отправь мне ссылку на хотелку или воспользуйся кнопками ниже ♥️", reply_markup=keyboard)

@dp.message_handler()
async def handle_buttons(msg: types.Message):
    text = msg.text.strip()

    if text == "📋 Посмотреть список хотелок":
        data = load_db()
        if not data:
            return await msg.reply("Список пуст, Писулик 🤍", reply_markup=keyboard)
        for item in data:
            # Красивое отображение с картинкой и подписью
            caption = f"🛍 *{item['title']}*\n💸 {item['price']}\n🔗 [Ссылка]({item['url']})"
            if item["image"]:
                await msg.answer_photo(item["image"], caption=caption, parse_mode="Markdown")
            else:
                await msg.answer(caption, parse_mode="Markdown")
        return

    if text == "➕ Добавить ссылку":
        return await msg.reply("Писулик, пришли ссылку на хотелку 🖤", reply_markup=keyboard)

    # Если пришла обычная ссылка
    if text.startswith("http"):
        item = parse_link(text)
        data = load_db()
        data.append(item)
        save_db(data)

        caption = f"Готово, Писулик! Добавил:\n\n🛍 *{item['title']}*\n💸 {item['price']}\n🔗 [Ссылка]({item['url']})"
        if item["image"]:
            await msg.reply_photo(item["image"], caption=caption, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await msg.reply(caption, parse_mode="Markdown", reply_markup=keyboard)
        return

    # Если текст не распознан
    await msg.reply("Писулик, я не понял 😅. Используй кнопки или пришли ссылку", reply_markup=keyboard)

# ====== Запуск ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
