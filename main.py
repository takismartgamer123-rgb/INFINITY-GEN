import sys
import traceback

print("🚀 [START] بديت نقرا main.py")

try:
    from flask import Flask
    import threading
    import os
    print("✅ [IMPORTS] كل الـ imports نجحو")
except Exception:
    print("💀 [IMPORTS] كراش في الـ imports:")
    traceback.print_exc()
    sys.exit(1)

app = Flask(__name__)

@app.route('/')
def home():
    return "INFINITY GEN شغال"

def run_stream_safe():
    print("📺 [STREAM-1] دخلت لدالة البث")
    try:
        from stream import run_stream_thread
        print("📺 [STREAM-2] درت import تاع stream")
        run_stream_thread()
        print("📺 [STREAM-3] البث شغال")
    except Exception:
        print("💀 [STREAM-ERROR] البث مات:")
        traceback.print_exc()

def run_chat_safe():
    print("🤖 [CHAT-1] دخلت لدالة الشات")
    try:
        from chat_handler import start_chat_loop
        print("🤖 [CHAT-2] درت import تاع chat_handler")
        start_chat_loop()
        print("🤖 [CHAT-3] بوت الشات خرج من الحلقة")
    except Exception:
        print("💀 [CHAT-ERROR] بوت الشات مات:")
        traceback.print_exc()

if __name__ == '__main__':
    print("🔧 [MAIN-1] راح نطلق ثريد البث")
    threading.Thread(target=run_stream_safe, daemon=True).start()

    print("🔧 [MAIN-2] راح نطلق ثريد الشات") 
    threading.Thread(target=run_chat_safe).start()

    port_str = os.environ.get('PORT', '').strip()
    port = int(port_str) if port_str else 10000
    print(f"🌐 [MAIN-3] السيرفر شغال على البورت {port}")
    app.run(host='0.0.0.0', port=port)
