import telebot
import time
import schedule
import requests
from bs4 import BeautifulSoup
import os
import json
import base64

# --- НАЛАШТУВАННЯ ---
TOKEN = "8971210949:AAHKowj9amdSdvxxzfL2JFox6T9avGnRWuo" 
CHANNEL_NAME = "@Perfum4k_channel" 
BOT_LINK = "https://t.me/Perfum4k_bot/store" 

# СТОРІНКА КАТАЛОГУ, ЗВІДКИ БОТ БУДЕ БРАТИ ТОВАРИ (Можеш змінити на свою)
CATALOG_URL = "https://gurtom.biz/Search?f_nomenclature_path=%d0%9f%d0%90%d0%a0%d0%a4%d0%a3%d0%9c%d0%95%d0%a0%d0%86%d0%af%2f%d0%9d%d0%98%d0%a8%d0%90&page=1&display=list" 
POSTED_FILE = "posted_links.txt" # Файл пам'яті бота

# --- НАЛАШТУВАННЯ GITHUB ---
GITHUB_TOKEN = "ТВІЙ_GITHUB_ТОКЕН_ТУТ" 
GITHUB_REPO = "ТВІЙ_НІК/НАЗВА_РЕПОЗИТОРІЮ" 
# --------------------

bot = telebot.TeleBot(TOKEN)

def add_product_to_github(title, price, img_url, brand):
    """Додає новий товар у products.json на GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/products.json"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return

    data = response.json()
    sha = data['sha'] 
    content_str = base64.b64decode(data['content']).decode('utf-8')
    
    try:
        products = json.loads(content_str)
    except:
        products = []

    new_product = {"name": title, "price": price, "image": img_url, "brand": brand}
    products.append(new_product)

    new_content_str = json.dumps(products, ensure_ascii=False, indent=2)
    new_content_b64 = base64.b64encode(new_content_str.encode('utf-8')).decode('utf-8')

    put_data = {
        "message": f"Авто-додавання товару: {title}",
        "content": new_content_b64,
        "sha": sha
    }
    requests.put(url, headers=headers, json=put_data)


def get_new_product_link():
    """Сканує каталог і повертає перше посилання, якого ще не було в пості"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(CATALOG_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Знаходимо ВСІ посилання на сторінці каталогу
        all_links = soup.find_all('a', href=True)
        product_links = []
        
        for a in all_links:
            href = a['href']
            # Відбираємо тільки ті, що ведуть на сторінку товару
            if '/Products/Show/' in href:
                full_url = f"https://gurtom.biz{href}" if href.startswith('/') else href
                product_links.append(full_url)
                
        # Читаємо пам'ять бота
        posted = set()
        if os.path.exists(POSTED_FILE):
            with open(POSTED_FILE, 'r', encoding='utf-8') as f:
                posted = set(f.read().splitlines())
                
        # Шукаємо свіжий товар
        for link in product_links:
            if link not in posted:
                return link
                
        return None # Якщо всі товари на сторінці вже опубліковані
    except Exception as e:
        print(f"Помилка сканування каталогу: {e}")
        return None

def mark_as_posted(link):
    """Записує посилання в пам'ять, щоб не постити його знову"""
    with open(POSTED_FILE, 'a', encoding='utf-8') as f:
        f.write(link + '\n')

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

        # Спроба витягнути бренд (якщо його немає в CSV, пробуємо знайти на сайті)
        brand = "Парфумерія" # Заглушка
        # Зазвичай бренд пишеться перед назвою або в хлібних крихтах
        breadcrumb = soup.find('ul', class_='breadcrumb')
        if breadcrumb:
            links = breadcrumb.find_all('a')
            if len(links) > 2:
                brand = links[-1].text.strip() # Останній елемент перед товаром часто є брендом

        # БРУТФОРС ОПИСУ
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
            
            add_product_to_github(title, price, img_url, brand)
            
            # ЗАПИСУЄМО В ПАМ'ЯТЬ, ТІЛЬКИ ЯКЩО ПОСТ УСПІШНИЙ!
            mark_as_posted(product_url)
        else:
            print(f"❌ Не вдалося знайти фото для: {title}")
            
    except Exception as e:
        print(f"❌ Сталася помилка: {e}")

schedule.every(1).minutes.do(parse_and_post)

if __name__ == "__main__":
    print("🚀 Автопостинг-Скрапер запущено! Шукаю товари прямо на сайті...")
    while True:
        schedule.run_pending()
        time.sleep(1)
