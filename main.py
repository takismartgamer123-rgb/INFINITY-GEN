from flask import Flask
import threading
import os
import sys
import traceback

app = Flask(__name__)

@app.route('/')
def home():
    return "INFINITY GEN شغال 24/7 من قالمة 🚫💸🗿"

def run_stream_safe():
    try:
        from stream import run_stream_thread
        print("📺 جاري تشغيل FFmpeg...")
        run_stream_thread()
    except Exception:
        print("💀 البث مات:")
        traceback.print_exc()

def run_chat_safe():
    try:
        from chat_handler import start_chat_loop
        print("🤖 جاري تشغيل بوت الشات...")
        start_chat_loop()
        print("⚠️ بوت الشات خرج من الحلقة بدون Error")
    except Exception:
        print("💀 بوت الشات مات:")
        traceback.print_exc()

if __name__ == '__main__':
    # شغل البث في الخلفية
    threading.Thread(target=run_stream_safe, daemon=True).start()
    
    # شغل الشات - بلا daemon باه نشوف الكراش
    threading.Thread(target=run_chat_safe).start()
    
    port_str = os.environ.get('PORT', '').strip()
    port = int(port_str) if port_str else 10000
    print(f"🌐 السيرفر شغال على البورت {port}")
    app.run(host='0.0.0.0', port=port)
