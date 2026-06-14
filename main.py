from flask import Flask
import threading
import os
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return "INFINITY GEN شغال 24/7 من قالمة 🚫💸🗿"

def run_all_services():
    try:
        print("🚀 جاري تشغيل خدمات INFINITY GEN...")
        
        from stream import run_stream_thread
        from chat_handler import start_chat_loop
        
        # 1. شغل بث الفيديو 24/7
        run_stream_thread()
        print("✅ بث الفيديو انطلق")
        
        # 2. شغل بوت الشات في ثريد منفصل
        chat_thread = threading.Thread(target=start_chat_loop, daemon=True)
        chat_thread.start()
        print("✅ بوت الشات انطلق")
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل الخدمات: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_all_services()
    
    try:
        port = int(os.environ.get('PORT', '10000').strip())
        print(f"🌐 السيرفر شغال على البورت {port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"❌ خطأ في تشغيل Flask: {e}")
        sys.exit(1)
