import subprocess
from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Я живий!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    print("🤖 Запускаю bot.py...")
    subprocess.Popen(["python", "bot.py"])
    
    print("📝 Запускаю autopost.py...")
    # ОСЬ ЦЕЙ РЯДОК МАЄ БУТИ ОБОВ'ЯЗКОВО!
    subprocess.Popen(["python", "autopost.py"])
    
    # Запускаємо сервер-заглушку для Render
    run_flask()
