from flask import Flask
import threading
import os
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return "INFINITY GEN شغال 24/7 من قالمة 🚫💸🗿"

@app.route('/health')
def health():
    return "OK", 200

def run_all_services():
    try:
        print("🚀 جاري تشغيل خدمات INFINITY GEN...")
        
        from stream import run_stream_thread
        from chat_handler import start_chat_loop
        
        run_stream_thread()
        print("✅ بث الفيديو انطلق")
        
        chat_thread = threading.Thread(target=start_chat_loop, daemon=True)
        chat_thread.start()
        print("✅ بوت الشات انطلق")
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل الخدمات: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_all_services()
    
    # هذا هو السطر الصحيح 100% - يتعامل مع PORT الفارغ
    port_str = os.environ.get('PORT', '').strip()
    port = int(port_str) if port_str else 10000
    
    print(f"🌐 السيرفر شغال على البورت {port}")
    app.run(host='0.0.0.0', port=port)
