import threading, os
from flask import Flask
from chat_handler import start_chat_loop

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ INFINITY GEN خدام من قالمة 🚫💸 | 16 لعبة + متجر + مافيا"

def run_bot():
    print("🔥 نشغلو لوب الشات...")
    start_chat_loop()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))