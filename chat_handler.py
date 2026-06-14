import os, json, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from games import handle_command

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube():
    token_info = json.loads(os.environ['TOKEN_JSON'])
    creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        print("🔄 تم تجديد التوكن")
    return build('youtube', 'v3', credentials=creds)

def send_message(youtube, live_chat_id, message):
    try:
        youtube.liveChatMessages().insert(
            part="snippet",
            body={"snippet": {"liveChatId": live_chat_id, "type": "textMessageEvent", "textMessageDetails": {"messageText": message}}}
        ).execute()
        print(f"📤 {message}")
    except Exception as e:
        print(f"خطأ إرسال: {e}")

def wait_for_live(youtube):
    while True:
        try:
            live = youtube.liveBroadcasts().list(part="snippet", broadcastStatus="active", mine=True).execute()
            if live['items']:
                live_chat_id = live['items'][0]['snippet']['liveChatId']
                title = live['items'][0]['snippet']['title']
                print(f"✅ متصل بالبث: {title}")
                return live_chat_id
            else:
                print("⏳ مكاش بث مباشر... نستنى 30 ثانية")
                time.sleep(30)
        except Exception as e:
            print(f"❌ خطأ جلب البث: {e}")
            time.sleep(30)

def start_chat_loop():
    youtube = get_youtube()
    live_chat_id = wait_for_live(youtube)

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
            print(f"خطأ في اللوب: {e}")
            if "liveChatId not found" in str(e):
                live_chat_id = wait_for_live(youtube)
                send_message(youtube, live_chat_id, "🔄 INFINITY GEN رجع للشات 🚫💸")
            time.sleep(10)