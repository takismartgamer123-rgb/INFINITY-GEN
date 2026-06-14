from flask import Flask
from stream import run_stream_thread
from chat_handler import start_chat_loop
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "INFINITY GEN شغال 24/7 من قالمة 🚫💸🗿"

@app.route('/health')
def health():
    return "OK", 200

def run_all_services():
    print("🚀 جاري تشغيل خدمات INFINITY GEN...")
    
    # 1. شغل بث الفيديو 24/7
    run_stream_thread()
    print("✅ بث الفيديو انطلق")
    
    # 2. شغل بوت الشات في ثريد منفصل
    chat_thread = threading.Thread(target=start_chat_loop, daemon=True)
    chat_thread.start()
    print("✅ بوت الشات انطلق")

if __name__ == '__main__':
    run_all_services()
    
    # هذا هو السطر لي كان فيه المشكل - صححناه
    port = int(os.environ.get('PORT', '10000').strip())
    print(f"🌐 السيرفر شغال على البورت {port}")
    app.run(host='0.0.0.0', port=port)
