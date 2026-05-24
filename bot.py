import telebot
from telebot import types
import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = "551866720" # <--- ВСТАВ СВІЙ ID (щоб отримувати замовлення)

bot = telebot.TeleBot(TOKEN)

# Тимчасова база даних у пам'яті для збереження кроків користувача
USER_ORDERS = {}

# Розумний словник об'ємів для брендів
BRAND_VOLUMES = {
    "chanel": ["50 мл", "100 мл"],
    "creed": ["30 мл", "50 мл", "100 мл"],
    "dior": ["60 мл", "100 мл", "200 мл"],
    "tom_ford": ["30 мл", "50 мл", "100 мл"],
    "загальний": ["30 мл", "50 мл", "100 мл"]
}

@bot.message_handler(commands=['start'])
def start_command(message):
    args = message.text.split()
    if len(args) > 1:
        # Клієнт прийшов по кнопці "Замовити" з каналу
        product_name = args[1].replace("_", " ")
        chat_id = message.chat.id
        
        # Ініціалізуємо замовлення
        USER_ORDERS[chat_id] = {
            "product": product_name,
            "step": "volume"
        }
        
        # Визначаємо бренд для підбору об'єму
        detected_brand = "загальний"
        product_lower = product_name.lower()
        for b in BRAND_VOLUMES.keys():
            if b in product_lower:
                detected_brand = b
                break
                
        # Створюємо кнопки вибору об'єму
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for vol in BRAND_VOLUMES[detected_brand]:
            markup.add(types.KeyboardButton(vol))
            
        bot.send_message(chat_id, f"Привіт! Оформлюємо замовлення на парфум:\n🛍 <b>{product_name}</b>\n\n<b>Крок 1:</b> Оберіть бажаний об'єм:", parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Привіт! Я бот магазину Perfum4k. Ти можеш замовити парфуми безпосередньо з нашого Telegram-каналу, просто натиснувши кнопку під ними!")

@bot.message_handler(func=lambda msg: msg.chat.id in USER_ORDERS)
def process_order_steps(message):
    chat_id = message.chat.id
    step = USER_ORDERS[chat_id]["step"]
    text = message.text.strip()

    if step == "volume":
        USER_ORDERS[chat_id]["volume"] = text
        USER_ORDERS[chat_id]["step"] = "pib"
        # Прибираємо кнопки об'єму
        bot.send_message(chat_id, "<b>Крок 2:</b> Введіть ваше Прізвище, Ім'я та По батькові (ПІБ):", parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())

    elif step == "pib":
        USER_ORDERS[chat_id]["pib"] = text
        USER_ORDERS[chat_id]["step"] = "phone"
        bot.send_message(chat_id, "<b>Крок 3:</b> Введіть ваш номер телефону для зв'язку:")

    elif step == "phone":
        USER_ORDERS[chat_id]["phone"] = text
        USER_ORDERS[chat_id]["step"] = "address"
        bot.send_message(chat_id, "<b>Крок 4:</b> Вкажіть адресу доставки (Місто та номер відділення Нової Пошти):")

    elif step == "address":
        USER_ORDERS[chat_id]["address"] = text
        order = USER_ORDERS[chat_id]
        
        # 1. Повідомлення клієнту
        bot.send_message(chat_id, "🎉 <b>Дякуємо, ваше замовлення прийнято!</b>\nНаш менеджер зв'яжеться з вами найближчим часом для підтвердження.", parse_mode="HTML")
        
        # 2. Формуємо чек для АДМІНІСТРАТОРА (тебе)
        admin_text = (
            f"🚨 <b>НОВЕ ЗАМОВЛЕННЯ!</b> 🚨\n\n"
            f"📦 <b>Товар:</b> {order['product']}\n"
            f"🧪 <b>Об'єм:</b> {order['volume']}\n"
            f"👤 <b>Клієнт:</b> {order['pib']}\n"
            f"📞 <b>Телефон:</b> {order['phone']}\n"
            f"📍 <b>Доставка:</b> {order['address']}\n"
        )
        
        try:
            bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
        except Exception as e:
            print(f"Не вдалося надіслати сповіщення адміну: {e}. Перевірте ADMIN_ID.")
            
        # Очищуємо сесію замовлення
        del USER_ORDERS[chat_id]

if __name__ == "__main__":
    print("🤖 Бот-приймальник замовлень запущений...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
