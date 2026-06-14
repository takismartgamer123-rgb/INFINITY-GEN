import threading, os
from flask import Flask
from chat_handler import start_chat_loop
from stream import run_stream_thread

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ INFINITY GEN خدام من قالمة 🚫💸 | 16 لعبة + متجر + مافيا + بث 24/7"

def run_bot():
    print("🔥 نشغلو لوب الشات...")
    start_chat_loop()

# نشغلو البث 24/7
run_stream_thread()

# نشغلو البوت
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))