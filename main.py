import subprocess
import os
import threading
from flask import Flask

# Створюємо мікро-сервер для хостингу
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот Perfum4k працює 24/7! 🚀"

def run_scripts():
    print("🤖 Запускаю bot.py...")
    subprocess.Popen(["python", "bot.py"])
    
    print("📝 Запускаю autopost.py...")
    subprocess.Popen(["python", "autopost.py"])

if __name__ == "__main__":
    # Запускаємо твої скрипти у фоновому режимі
    threading.Thread(target=run_scripts).start()
    
    # Запускаємо сервер на порту, який видасть хостинг
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)