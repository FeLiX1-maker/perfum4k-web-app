print("⚡ Файл autopost.py почав завантаження...")
import telebot
import time
import schedule
import requests
from bs4 import BeautifulSoup
import os
import json
import base64

# --- НАЛАШТУВАННЯ ---
TOKEN = os.environ.get("BOT_TOKEN") 
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 

CHANNEL_NAME = "@Perfum4k_channel" # ЗАМІНИ НА СВІЙ КАНАЛ
BOT_LINK = "https://t.me/Perfum4k_bot/store" 
CATALOG_URL = "https://surli.cc/kwzaqp" 

# --- НАЛАШТУВАННЯ GITHUB ---
GITHUB_REPO = "FeLiX1-maker/perfum4k-web-app" # Наприклад: lki-l/Perfum4k_Bot
# --------------------

bot = telebot.TeleBot(TOKEN)

def get_posted_urls_from_github():
    """Отримує список вже опублікованих посилань прямо з вітрини магазину"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/products.json"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            content_str = base64.b64decode(data['content']).decode('utf-8')
            products = json.loads(content_str)
            # Беремо всі посилання з бази
            return set(p.get("url", "") for p in products)
    except Exception as e:
        print(f"Помилка читання бази GitHub: {e}")
    return set()

def add_product_to_github(title, price, img_url, brand, product_url):
    """Додає товар у базу GitHub і показує помилки, якщо вони є"""
    print(f"🔄 Спроба додати '{title}' у вітрину GitHub...")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/products.json"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Крок 1: Читаємо файл
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ ПОМИЛКА ЧИТАННЯ GitHub: {response.status_code} - {response.text}")
        print("💡 Підказка: Можливо файл products.json не існує, або токен не має доступу.")
        return

    data = response.json()
    sha = data['sha'] 
    content_str = base64.b64decode(data['content']).decode('utf-8')
    
    try:
        products = json.loads(content_str)
    except:
        products = []

    # Крок 2: Додаємо товар
    new_product = {"name": title, "price": price, "image": img_url, "brand": brand, "url": product_url}
    products.append(new_product)

    new_content_str = json.dumps(products, ensure_ascii=False, indent=2)
    new_content_b64 = base64.b64encode(new_content_str.encode('utf-8')).decode('utf-8')

    put_data = {
        "message": f"Авто-додавання товару: {title}",
        "content": new_content_b64,
        "sha": sha
    }
    
    # Крок 3: Зберігаємо оновлений файл
    put_response = requests.put(url, headers=headers, json=put_data)
    if put_response.status_code in [200, 201]:
        print("✅ Товар УСПІШНО додано до вітрини Web App!")
    else:
        print(f"❌ ПОМИЛКА ЗАПИСУ на GitHub: {put_response.status_code} - {put_response.text}")
    """Шукає нове посилання, якого ще немає на вітрині магазину"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(CATALOG_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_links = soup.find_all('a', href=True)
        product_links = []
        
        for a in all_links:
            href = a['href']
            if '/Products/Show/' in href:
                full_url = f"https://gurtom.biz{href}" if href.startswith('/') else href
                product_links.append(full_url)
                
        # Зчитуємо пам'ять з GitHub
        posted = get_posted_urls_from_github()
                
        for link in product_links:
            if link not in posted:
                return link
                
        return None 
    except Exception as e:
        print(f"Помилка сканування каталогу: {e}")
        return None

def parse_and_post():
    product_url = get_new_product_link()
    
    if not product_url:
        print("📭 Нових товарів у каталозі поки не знайдено.")
        return 

    print(f"🌐 Знайшов новий товар! Заходжу на сайт: {product_url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(product_url, headers=headers)
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

       # --- ШУКАЄМО РЕАЛЬНИЙ БРЕНД ---
        brand = "Невідомий бренд" 
        breadcrumb = soup.find('div', class_='breadcrumb_header')
        if breadcrumb:
            links = breadcrumb.find_all('a')
            if len(links) > 0:
                # Повертаємо [-1], бо останнім посиланням є саме бренд
                brand = links[-1].text.strip()

        description = ""
        longest_text = ""
        for tag in soup.find_all(['div', 'p', 'span', 'td']):
            if not tag.find('div'):
                text = tag.get_text(separator=' ', strip=True)
                if 60 < len(text) < 2000:
                    text_lower = text.lower()
                    if "грн" not in text_lower and "кошик" not in text_lower and "реєстрація" not in text_lower:
                        if len(text) > len(longest_text):
                            longest_text = text

        if longest_text:
            description = " ".join(longest_text.split())
            if len(description) > 300:
                description = description[:297] + "..."
        else:
            description = "Неймовірний аромат, який підкреслить вашу індивідуальність."

        caption = (
            f"✨ <b>{title}</b> ✨\n\n"
            f"🏷 <b>Бренд:</b> {brand}\n"
            f"📝 <i>{description}</i>\n\n"
            f"💰 <b>Ціна:</b> {price}\n\n"
            f"👇 <b>Замовити:</b>\n"
            f"<a href='{BOT_LINK}'>Відкрити магазин Perfum4k</a>"
        )
        
        if img_url:
            bot.send_photo(CHANNEL_NAME, photo=img_url, caption=caption, parse_mode='HTML')
            print(f"✅ Опубліковано: {title}")
            
            # ЗАПИСУЄМО В ПАМ'ЯТЬ GITHUB РАЗОМ З ТОВАРОМ!
            add_product_to_github(title, price, img_url, brand, product_url)
        else:
            print(f"❌ Не вдалося знайти фото для: {title}")
            
    except Exception as e:
        print(f"❌ Сталася помилка: {e}")

schedule.every(1).minutes.do(parse_and_post)

if __name__ == "__main__":
    print("🚀 Автопостинг-Скрапер запущено! Роблю ПЕРШИЙ запуск прямо зараз...")

    # ЗМУШУЄМО БОТА ПРАЦЮВАТИ ОДРАЗУ, НЕ ЧЕКАЮЧИ ХВИЛИНУ:
    parse_and_post() 

    while True:
        schedule.run_pending()
        time.sleep(1)
