import json
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types

TOKEN = "8518290458:AAEEGM4Crh2alNeC6PvLPETLq8R3wcIWFy8"
DB_FILE = "database.json"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

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

# ====== Парсинг ======
def parse_link(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    # === Название ===
    title = soup.find("title").text.strip() if soup.find("title") else "Название не найдено"

    # === Картинка ===
    img = soup.find("img")
    image = img["src"] if img and img.get("src") else None

    # === Цена ===
    price = None

    # Wildberries
    if "wildberries" in url:
        price_tag = soup.find("ins", {"class": "price-block__final-price"})
        if price_tag:
            price = price_tag.text.strip()

    # Ozon
    if "ozon" in url:
        price_tag = soup.find("span", {"class": "c3015-a1"})
        if price_tag:
            price = price_tag.text.strip()

    # Yandex Market
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
    await msg.reply("Писушк, отправь мне ссылку на свою хотелку — я всё сам добавлю ♥️")

@dp.message_handler(commands=["list"])
async def show_list(msg: types.Message):
    data = load_db()
    if not data:
        return await msg.answer("Писулик, список пуст, его стоило бы заполнить 🥹")

    for item in data:
        text = f"🛍 *{item['title']}*\n💸 {item['price']}\n🔗 {item['url']}"
        if item["image"]:
            await msg.answer_photo(item["image"], caption=text, parse_mode="Markdown")
        else:
            await msg.answer(text, parse_mode="Markdown")


# ====== Добавление по ссылке ======
@dp.message_handler()
async def add_wishlist(msg: types.Message):
    url = msg.text.strip()

    if not url.startswith("http"):
        return await msg.reply("Пису, это не ссылка 😅")

    item = parse_link(url)

    data = load_db()
    data.append(item)
    save_db(data)

    await msg.reply(
        f"Готово, Пису! Добавил:\n\n"
        f"🛍 {item['title']}\n"
        f"💸 {item['price']}\n"
        f"🔗 {item['url']}"
    )

# ====== Запуск ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
