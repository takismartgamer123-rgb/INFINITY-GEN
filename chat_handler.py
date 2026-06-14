print("✅ CHAT_HANDLER START")

import os, json, time

print("✅ IMPORTS BASIC OK")

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    print("✅ GOOGLE LIBS OK")
except Exception as e:
    print(f"💀 GOOGLE IMPORT FAIL: {e}")

try:
    from games import handle_command
    print("✅ GAMES IMPORT OK")
except Exception as e:
    print(f"💀 GAMES IMPORT FAIL: {e}")

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube():
    print("🔑 TRYING TOKEN_JSON")
    token_str = os.environ.get('TOKEN_JSON')
    if not token_str:
        print("💀 TOKEN_JSON MISSING")
        return None
    token_info = json.loads(token_str)
    creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    return build('youtube', 'v3', credentials=creds)

def start_chat_loop():
    print("🤖 CHAT LOOP START")
    youtube = get_youtube()
    if not youtube:
        print("💀 NO YOUTUBE OBJECT")
        return
    print("✅ YOUTUBE OBJECT OK - BOT READY")
    # نحبس هنا ضرك، المهم نعرفو اذا وصلنا لهنا ولا لا
    while True:
        print("💤 Bot alive, sleeping 60s")
        time.sleep(60)
