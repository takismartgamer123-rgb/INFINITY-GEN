import redis, random, os, json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

r = redis.from_url(os.environ.get('REDIS_URL'))

def get_youtube_service():
    creds = Credentials.from_authorized_user_info(json.loads(os.environ.get('TOKEN_JSON')))
    return build('youtube', 'v3', credentials=creds)

def send_msg(live_chat_id, message):
    try:
        youtube = get_youtube_service()
        youtube.liveChatMessages().insert(
            part="snippet",
            body={"snippet": {"liveChatId": live_chat_id, "type": "textMessageEvent", "textMessageDetails": {"messageText": message}}}
        ).execute()
        print(f"🎮 [GAME] بعثت: {message}")
    except Exception as e:
        print(f"💀 [GAME] ما قدرتش نبعث: {e}")

def handle_command(author_id, author, msg, live_chat_id):
    msg = msg.lower().strip()

    # 1. لعبة النقاط
    if msg == '!نقاط':
        points = r.get(f"points:{author_id}") or 0
        send_msg(live_chat_id, f"@{author} رصيدك {int(points)} نقطة 🚫💸")

    # 2. لعبة الحظ
    elif msg == '!حظ':
        if random.randint(1, 2) == 1:
            new_points = r.incr(f"points:{author_id}")
            send_msg(live_chat_id, f"@{author} ربحت! صار عندك {new_points} نقطة 🎉")
        else:
            send_msg(live_chat_id, f"@{author} خسرت هاذ المرة 😢")

    # 3. لعبة سرقة النقاط
    elif msg.startswith('!سرقة @'):
        target_name = msg.split('@')[1].strip()
        # نجيبو كل الناس لي عندهم نقاط
        all_users = r.keys("points:*")
        target_id = None
        for user_key in all_users:
            user_id = user_key.decode().split(':')[1]
            # هذي معقدة شوية. نخليها مبعد. ضرك نديرو سرقة عشوائية
            pass

        # سرقة عشوائية أسهل
        if len(all_users) > 1:
            target_key = random.choice(all_users)
            target_points = int(r.get(target_key) or 0)
            if target_points > 0:
                stolen = random.randint(1, min(5, target_points))
                r.decrby(target_key, stolen)
                r.incrby(f"points:{author_id}", stolen)
                send_msg(live_chat_id, f"@{author} سرقت {stolen} نقطة! 🚫💸")
            else:
                send_msg(live_chat_id, f"@{author} ما لقيت حتى واحد تسرق منو")
        else:
            send_msg(live_chat_id, f"@{author} ما كاش لي تسرق منو ضرك")

    # 4. التوب
    elif msg == '!توب':
        all_users = r.keys("points:*")
        leaderboard = []
        for user_key in all_users:
            user_id = user_key.decode().split(':')[1]
            points = int(r.get(user_key) or 0)
            name = r.get(f"name:{user_id}")
            name = name.decode() if name else user_id[:6]
            leaderboard.append((name, points))

        leaderboard.sort(key=lambda x: x[1], reverse=True)
        top3 = leaderboard[:3]

        if top3:
            msg = "🏆 التوب 3: "
            for i, (name, points) in enumerate(top3):
                msg += f"{i+1}. {name} {points} | "
            send_msg(live_chat_id, msg[:-3])
        else:
            send_msg(live_chat_id, "ما كاش نقاط حتى واحد ضرك")

    # نخزنو اسم اللاعب باه نستعملوه في التوب
    r.set(f"name:{author_id}", author)