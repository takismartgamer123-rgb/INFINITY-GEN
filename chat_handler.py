import os, json, time, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from games import handle_command
print("🔥🔥🔥 [FILE] بديت نقرا chat_handler.py")
import os, json, time, sys
print("🔥🔥🔥 [IMPORT-1] كملت import os,json,time,sys")

from google.oauth2.credentials import Credentials
print("🔥🔥🔥 [IMPORT-2] كملت import Credentials")

from google.auth.transport.requests import Request
print("🔥🔥🔥 [IMPORT-3] كملت import Request")

from googleapiclient.discovery import build
print("🔥🔥🔥 [IMPORT-4] كملت import build")

from games import handle_command
print("🔥🔥🔥 [IMPORT-5] كملت import games")

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
print("🔥🔥🔥 [FILE] كملت نقرا الملف كامل")

def get_youtube():
    print("🔑 [AUTH-1] بديت نقرا TOKEN_JSON")
    # ... باقي الكود لي عطيتهولك من قبل

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube():
    print("🔑 [AUTH-1] بديت نقرا TOKEN_JSON")

    token_str = os.environ.get('TOKEN_JSON')
    if not token_str:
        print("💀 [AUTH-ERROR] TOKEN_JSON مش موجود في Environment")
        sys.exit(1)

    try:
        token_info = json.loads(token_str)
        print("🔑 [AUTH-2] TOKEN_JSON تقرا بنجاح")
    except Exception as e:
        print(f"💀 [AUTH-ERROR] TOKEN_JSON غالط: {e}")
        sys.exit(1)

    creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    if creds.expired and creds.refresh_token:
        print("🔄 [AUTH-3] راح نجدد التوكن...")
        creds.refresh(Request())
        print("🔄 [AUTH-4] تم تجديد التوكن")

    print("🔑 [AUTH-5] راح نبني youtube object")
    return build('youtube', 'v3', credentials=creds)

def send_message(youtube, live_chat_id, message):
    try:
        youtube.liveChatMessages().insert(
            part="snippet",
            body={"snippet": {"liveChatId": live_chat_id, "type": "textMessageEvent", "textMessageDetails": {"messageText": message}}}
        ).execute()
        print(f"📤 بعثت: {message}")
    except Exception as e:
        print(f"❌ خطأ إرسال: {e}")

def wait_for_live(youtube):
    print("🔍 [LIVE-1] راح ندور على بث مباشر")
    while True:
        try:
            live = youtube.liveBroadcasts().list(part="snippet", broadcastStatus="active", mine=True).execute()
            if live['items']:
                live_chat_id = live['items'][0]['snippet']['liveChatId']
                title = live['items'][0]['snippet']['title']
                print(f"✅ [LIVE-2] متصل بالبث: {title}")
                return live_chat_id
            else:
                print("⏳ [LIVE-3] مكاش بث مباشر... نستنى 30 ثانية")
                time.sleep(30)
        except Exception as e:
            print(f"❌ [LIVE-ERROR] خطأ جلب البث: {e}")
            time.sleep(30)

def start_chat_loop():
    print("🤖 [LOOP-1] دخلت start_chat_loop")
    youtube = get_youtube()
    print("🤖 [LOOP-2] درت youtube object")

    live_chat_id = wait_for_live(youtube)
    print(f"🤖 [LOOP-3] لقيت live_chat_id: {live_chat_id}")

    send_message(youtube, live_chat_id, "✅ INFINITY GEN دخل للشات من قالمة 🚫💸 | اكتب متجر")

    next_page_token = None
    while True:
        try:
            response = youtube.liveChatMessages().list(
                liveChatId=live_chat_id,
                part="snippet,authorDetails",
                pageToken=next_page_token
            ).execute()

            for item in response['items']:
                msg = item['snippet']['displayMessage']
                author = item['authorDetails']['displayName']
                author_id = item['authorDetails']['channelId']
                print(f"💬 {author}: {msg}")
                reply = handle_command(author_id, author, msg)
                if reply:
                    send_message(youtube, live_chat_id, reply)

            next_page_token = response['nextPageToken']
            time.sleep(response['pollingIntervalMillis'] / 1000)

        except Exception as e:
            print(f"❌ [LOOP-ERROR] خطأ في اللوب: {e}")
            if "liveChatId not found" in str(e):
                live_chat_id = wait_for_live(youtube)
                send_message(youtube, live_chat_id, "🔄 INFINITY GEN رجع للشات 🚫💸")
            time.sleep(10)
