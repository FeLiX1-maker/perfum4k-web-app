import telebot
import os

# --- НАЛАШТУВАННЯ ---
TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привіт! Я бот Perfum4k. Натисни кнопку 'Магазин', щоб побачити каталог!")

# Якщо у тебе є інші обробники (handlers) для кошика, вони мають бути тут

if __name__ == "__main__":
    print("🤖 Бот успішно запущений і готовий до роботи!")
    bot.infinity_polling()
