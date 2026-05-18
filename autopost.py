import telebot
import time
import schedule
import requests
from bs4 import BeautifulSoup
import csv
import os

# --- НАЛАШТУВАННЯ ---
TOKEN = "8971210949:AAHKowj9amdSdvxxzfL2JFox6T9avGnRWuo" 
CHANNEL_NAME = "@Perfum4k_channel" 
BOT_LINK = "https://t.me/Perfum4k_bot/store" 

CSV_FILE = "Прайслінки_2.csv" 
# --------------------

bot = telebot.TeleBot(TOKEN)

def get_first_valid_link_and_update_csv():
    if not os.path.exists(CSV_FILE):
        return None
    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = list(csv.reader(file))
    valid_url = None
    rows_to_keep = []
    for row in reader:
        if not valid_url:
            found_link = None
            for cell in row:
                cell_text = cell.strip()
                if cell_text.startswith("http"):
                    found_link = cell_text
                    break
            if found_link:
                valid_url = found_link
                continue 
        rows_to_keep.append(row)
    with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows_to_keep)
    return valid_url

def parse_and_post():
    product_url = get_first_valid_link_and_update_csv()
    if not product_url:
        print("📭 У таблиці більше немає рядків із посиланнями. Додайте нові!")
        return 

    print(f"🌐 Заходжу на сайт: {product_url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(product_url, headers=headers)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Назва
        title_element = soup.find('h1')
        title = title_element.text.strip() if title_element else "Невідомий парфум"
        
        # 2. Ціна
        price_element = soup.find(class_='price') 
        price = price_element.text.strip() if price_element else "Ціну уточнюйте"
        
        # 3. Фото
        img_url = ""
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and not any(x in src.lower() for x in ["logo", "icon", "banner", "avatar"]):
                img_url = f"https://gurtom.biz{src}" if src.startswith('/') else src
                break

        # 4. АБСОЛЮТНИЙ БРУТФОРС ОПИСУ
        description = ""
        longest_text = ""
        
        # Перевіряємо всі блоки на сторінці
        for tag in soup.find_all(['div', 'p', 'span', 'td']):
            # Беремо тільки "кінцеві" тексти (всередині яких немає інших блоків)
            if not tag.find('div'):
                text = tag.get_text(separator=' ', strip=True)
                # Шукаємо абзаци середньої та великої довжини
                if 60 < len(text) < 2000:
                    # Фільтруємо непотрібне: кнопки, ціни, реєстрацію
                    text_lower = text.lower()
                    if "грн" not in text_lower and "кошик" not in text_lower and "реєстрація" not in text_lower:
                        # Зберігаємо НАЙДОВШИЙ знайдений текст
                        if len(text) > len(longest_text):
                            longest_text = text

        if longest_text:
            description = longest_text
            # Прибираємо зайві пробіли
            description = " ".join(description.split())
            if len(description) > 300:
                description = description[:297] + "..."
        else:
            description = "Неймовірний аромат, який підкреслить вашу індивідуальність."

        # Формуємо текст посту
        caption = (
            f"✨ <b>{title}</b> ✨\n\n"
            f"📝 <i>{description}</i>\n\n"
            f"💰 <b>Ціна:</b> {price}\n\n"
            f"👇 <b>Замовити цей аромат можна в нашому боті:</b>\n"
            f"<a href='{BOT_LINK}'>Відкрити магазин Perfum4k</a>"
        )
        
        if img_url:
            bot.send_photo(CHANNEL_NAME, photo=img_url, caption=caption, parse_mode='HTML')
            print(f"✅ Успішно опубліковано: {title}")
            print(f"📝 Знайдено опис: {description[:60]}...") # Виводимо шматочок опису в термінал
        else:
            print(f"❌ Не вдалося знайти фото для: {title}")
            
    except Exception as e:
        print(f"❌ Сталася помилка під час публікації: {e}")

schedule.every(1).minutes.do(parse_and_post)

if __name__ == "__main__":
    print("🚀 Автопостинг (Режим 'Брутфорс Опису') запущено! Очікую...")
    while True:
        schedule.run_pending()
        time.sleep(1)