import subprocess
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Я живий!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    print("🤖 Запускаю bot.py...")
    # Додали -u для миттєвого виводу тексту
    subprocess.Popen(["python", "-u", "bot.py"])
    
    print("📝 Запускаю autopost.py...")
    # Додали -u для миттєвого виводу тексту
    subprocess.Popen(["python", "-u", "autopost.py"])
    
    # Запускаємо сервер-заглушку для Render
    run_flask()
