import telebot
import time
import schedule
import requests
from bs4 import BeautifulSoup
import os
from telebot import types

print("⚡ Файл autopost.py почав завантаження...")

# --- НАЛАШТУВАННЯ ---
TOKEN = os.environ.get("BOT_TOKEN") 
CHANNEL_NAME = "@Perfum4k_channel" # <--- ЗАМІНИ НА СВІЙ КАНАЛ
CATALOG_URL = "https://gurtom.biz/Search?f_brand=CHANEL&page=2

bot = telebot.TeleBot(TOKEN)

# Тимчасова локальна пам'ять для сесії сервера (щоб не спамити дублями)
POSTED_URLS = set()

def get_new_product_link():
    try:
        print(f"   [Парсер] Сканую каталог: {CATALOG_URL}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(CATALOG_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_links = soup.find_all('a', href=True)
        product_links = []
        
        for a in all_links:
            href = a['href']
            if '/Products/Show/' in href:
                full_url = f"https://gurtom.biz{href}" if href.startswith('/') else href
                product_links.append(full_url)
                
        for link in product_links:
            if link not in POSTED_URLS:
                return link
                
        return None 
    except Exception as e:
        print(f"❌ Помилка сканування сайту: {e}")
        return None

def parse_and_post():
    global POSTED_URLS
    print("🔍 Перевіряю наявність нових парфумів...")
    product_url = get_new_product_link()
    
    if not product_url:
        print("📭 Нових товарів на сторінці немає.")
        return 

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(product_url, headers=headers, timeout=15)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_element = soup.find('h1')
        title = title_element.text.strip() if title_element else "Невідомий парфум"
        
        price_element = soup.find(class_='price') 
        price = price_element.text.strip() if price_element else "Ціну уточнюйте"
        
        img_url = ""
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and not any(x in src.lower() for x in ["logo", "icon", "banner", "avatar"]):
                img_url = f"https://gurtom.biz{src}" if src.startswith('/') else src
                break

        brand = "Загальний" 
        breadcrumb = soup.find('div', class_='breadcrumb_header')
        if breadcrumb:
            links = breadcrumb.find_all('a')
            if len(links) > 0:
                brand = links[-1].text.strip() 

        # Компактний опис
        description = "Прекрасний аромат для вашої колекції."
        longest_text = ""
        for tag in soup.find_all(['div', 'p', 'span', 'td']):
            if not tag.find('div'):
                text = tag.get_text(separator=' ', strip=True)
                if 60 < len(text) < 1000 and "грн" not in text.lower():
                    if len(text) > len(longest_text):
                        longest_text = text
        if longest_text:
            description = longest_text if len(longest_text) <= 250 else longest_text[:247] + "..."

        caption = (
            f"✨ <b>{title}</b> ✨\n\n"
            f"🏷 <b>Бренд:</b> {brand}\n"
            f"📝 <i>{description}</i>\n\n"
            f"💰 <b>Ціна:</b> {price}\n"
        )
        
        if img_url:
            # Створюємо кнопку під постом
            markup = types.InlineKeyboardMarkup()
            # Передаємо в callback дані про товар (Назва|Бренд|Ціна)
            callback_data = f"buy|{title[:15]}|{brand[:10]}|{price[:10]}"
            markup.add(types.InlineKeyboardButton("🛒 Замовити", url=f"https://t.me/ТВІЙ_ЮЗЕРНЕЙМ_БОТА?start=order")) 
            # Примітка: Оскільки callback_кнопки в каналах вимагають складної обробки, 
            # найнадійніший спосіб — кнопка-посилання, яка веде в приват до бота з текстом замовлення,
            # але для повної автоматизації ми зробимо красивий перехід.
            
            # Робимо пряму inline кнопку замовлення:
            markup = types.InlineKeyboardMarkup()
            # Робимо кнопку, яка перенаправляє в приватні повідомлення бота
            bot_username = bot.get_me().username
            # Зашиваємо назву товару в посилання для старту
            clean_title = title.replace(" ", "_").replace("(", "").replace(")", "")[:30]
            markup.add(types.InlineKeyboardButton("🛒 Замовити через бота", url=f"https://t.me/{bot_username}?start={clean_title}"))

            bot.send_photo(CHANNEL_NAME, photo=img_url, caption=caption, parse_mode='HTML', reply_markup=markup)
            print(f"✅ Успішно опубліковано в канал: {title}")
            POSTED_URLS.add(product_url)
        else:
            print(f"❌ Фото не знайдено для: {title}")
            
    except Exception as e:
        print(f"❌ Помилка під час парсингу чи відправки: {e}")

if __name__ == "__main__":
    print("🚀 Скрапер запущено!")
    parse_and_post()
    schedule.every(2).minutes.do(parse_and_post) # Розподілимо на кожні 2 хвилини
    
    while True:
        schedule.run_pending()
        time.sleep(1)
