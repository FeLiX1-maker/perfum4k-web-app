import telebot
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# --- НАЛАШТУВАННЯ ---
# 1. Твій токен від BotFather
TOKEN = "8971210949:AAHKowj9amdSdvxxzfL2JFox6T9avGnRWuo" 

# 2. Твоє посилання на GitHub Pages
WEB_APP_URL = "https://felix1-maker.github.io/perfum4k-web-app/" 

# 3. Твій особистий ID, який ти отримав від @userinfobot
ADMIN_ID = "551866720" 
# --------------------

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    web_app_btn = KeyboardButton(
        text="Магазин Парфумів 🌊", 
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    markup.add(web_app_btn)
    
    bot.send_message(
        message.chat.id, 
        "Привіт! Натисни кнопку нижче, щоб відкрити вітрину ароматів.", 
        reply_markup=markup
    )

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    data = json.loads(message.web_app_data.data)
    
    perfume = data.get('item')
    address = data.get('delivery')
    
    # --- 1. Відповідаємо клієнту ---
    user_text = (
        f"🎉 <b>Дякуємо за замовлення!</b>\n\n"
        f"<b>Аромат:</b> {perfume}\n"
        f"<b>Доставка:</b> {address}\n\n"
        f"Ми зв'яжемося з вами найближчим часом для підтвердження."
    )
    bot.send_message(message.chat.id, user_text, parse_mode='HTML')

    # --- 2. Відправляємо сповіщення тобі (Адміну) ---
    # Пробуємо отримати нікнейм клієнта (наприклад, @felix), щоб ти міг йому написати
    username = message.from_user.username
    if username:
        client_contact = f"@{username}"
    else:
        # Якщо в людини немає @нікнейму, покажемо її ID
        client_contact = f"ID: {message.from_user.id}"

    admin_text = (
        f"🚨 <b>НОВЕ ЗАМОВЛЕННЯ!</b> 🚨\n\n"
        f"👤 <b>Клієнт:</b> {client_contact}\n"
        f"📦 <b>Товар:</b> {perfume}\n"
        f"📍 <b>Адреса:</b> {address}"
    )
    
    # Відправляємо повідомлення за твоїм ADMIN_ID
    try:
        bot.send_message(ADMIN_ID, admin_text, parse_mode='HTML')
    except Exception as e:
        print(f"Помилка відправки повідомлення адміністратору: {e}")
        print("Перевір, чи правильно вказано ADMIN_ID і чи запускав ти (як користувач) цього бота раніше.")

if __name__ == "__main__":
    print("Бот запущено. Очікую на замовлення...")
    bot.infinity_polling()