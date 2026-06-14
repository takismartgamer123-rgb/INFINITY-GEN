import os, time, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import games # نستدعي ملف الألعاب

def start_chat_loop():
    print("🤖 [BOT] بوت الألعاب بدا")
    creds = Credentials.from_authorized_user_info(json.loads(os.environ.get('TOKEN_JSON')))
    youtube = build('youtube', 'v3', credentials=creds)

    broadcasts = youtube.liveBroadcasts().list(part="snippet", broadcastStatus="active").execute()
    if not broadcasts['items']:
        print("💀 [BOT] ما كاش بث شغال")
        return

    live_chat_id = broadcasts['items'][0]['snippet']['liveChatId']
    print(f"🤖 [BOT] Chat ID: {live_chat_id}")

    # رسالة بداية البوت
    games.send_msg(live_chat_id, "🚫💸 بوت الألعاب شغال! جرب!نقاط!حظ!توب")
    next_page_token = None

    while True:
        try:
            response = youtube.liveChatMessages().list(
                liveChatId=live_chat_id, part="snippet,authorDetails", pageToken=next_page_token
            ).execute()

            for item in response['items']:
                msg = item['snippet']['displayMessage']
                author = item['authorDetails']['displayName']
                author_id = item['authorDetails']['channelId']
                print(f"💬 {author}: {msg}")

                # نبعتو الأوامر لـ games.py
                if msg.startswith('!'):
                    games.handle_command(author_id, author, msg, live_chat_id)

            next_page_token = response.get('nextPageToken')
            time.sleep(5)
        except Exception as e:
            print(f"💀 [BOT] Error: {e}")
            time.sleep(15)