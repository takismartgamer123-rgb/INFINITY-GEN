from flask import Flask
import threading
import os
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return "INFINITY GEN شغال 24/7 من قالمة 🚫💸🗿"

def run_chat():
    try:
        from chat_handler import start_chat_loop
        print("🤖 راح نطلق بوت الشات ضرك...")
        start_chat_loop()
    except Exception as e:
        print(f"💀 بوت الشات مات: {e}")
        import traceback
        traceback.print_exc()

def run_stream():
    try:
        from stream import run_stream_thread
        print("📺 راح نطلق البث ضرك...")
        run_stream_thread()
    except Exception as e:
        print(f"💀 البث مات: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # شغل البث أول
    threading.Thread(target=run_stream, daemon=True).start()
    
    # شغل الشات ثاني - بلا daemon باه نشوف الكراش
    chat_thread = threading.Thread(target=run_chat)
    chat_thread.start()
    
    port_str = os.environ.get('PORT', '').strip()
    port = int(port_str) if port_str else 10000
    print(f"🌐 السيرفر شغال على البورت {port}")
    app.run(host='0.0.0.0', port=port)
