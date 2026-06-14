import redis, os, random, time, json, threading
r = redis.from_url(os.environ['REDIS_URL'])

# ========== نظام النقاط ==========
def add_points(user_id, pts):
    if pts > 0: pts = pts * check_multiplier(user_id)
    if pts!= 0:
        r.incrby(f"points:{user_id}", pts)
        r.zincrby("leaderboard", pts, user_id)

def get_points(user_id):
    return int(r.get(f"points:{user_id}") or 0)

def check_multiplier(user_id):
    return 2 if r.exists(f"multiplier:{user_id}") else 1

# ========== متجر النقاط + بوسترات المافيا 😈 ==========
SHOP_ITEMS = {
    "درع": {"cost": 200, "desc": "يمنع سرقة نقاطك مرة واحدة"},
    "مضاعف": {"cost": 500, "desc": "x2 نقاط لمدة 10 دقايق"},
    "كشف": {"cost": 150, "desc": "تلميح إضافي في كلمة السر"},
    "قنبلة": {"cost": 400, "desc": "تفجر نقاط خصم عشوائي -50"},
    "كاتم": {"cost": 600, "desc": "المافيا: اقتل بدون كشف اسمك ليلة وحدة"},
    "درع_شرطي": {"cost": 500, "desc": "الشرطي: حماية من القتل ليلة وحدة"},
    "إنعاش": {"cost": 700, "desc": "الطبيب: ترجع ميت للحياة مرة وحدة"},
    "تصويت_ذهبي": {"cost": 350, "desc": "صوتك = 2 في تصويت الإعدام"},
    "جاسوس": {"cost": 800, "desc": "المدني: تعرف دور لاعب عشوائي"},
    "انتحاري": {"cost": 1000, "desc": "لو مت تدي معاك مافيا عشوائي للقبر 😈"}
}

def buy_item(user_id, username, item):
    if item not in SHOP_ITEMS: return "العنصر مكاش 😂"
    cost = SHOP_ITEMS[item]["cost"]
    if get_points(user_id) < cost: return f"نقاطك ناقصة. لازمك {cost} نقطة 🚫💸"
    add_points(user_id, -cost)
    r.incrby(f"item:{item}:{user_id}", 1)
    return f"✅ شريت {item}! {SHOP_ITEMS[item]['desc']} | -{cost} نقطة"

def has_item(user_id, item):
    return int(r.get(f"item:{item}:{user_id}") or 0) > 0

def use_item(user_id, item):
    if has_item(user_id, item):
        r.decrby(f"item:{item}:{user_id}", 1)
        return True
    return False

# ========== بنك الكلمات ==========
WORDS = ["قالمة", "انفينيتي", "يوتيوب", "جلاد", "تقي", "مافيا", "ثورة", "بونق", "سحابة", "ريندر", "بوت", "نووي"]

# ========== نظام دخول البوت بعد 80 ثانية ==========
def bot_join_timeout(game_key, check_func, delay=80):
    def check_timeout():
        time.sleep(delay)
        if r.exists(game_key):
            data = json.loads(r.get(game_key))
            if not data.get("started", False) and not data.get("p2_id"):
                data["p2"] = "INFINITY_GEN_BOT"
                data["p2_id"] = "BOT"
                data["started"] = True
                r.setex(game_key, 300, json.dumps(data))
                check_func(data)
    threading.Thread(target=check_timeout, daemon=True).start()

# ========== 1. لعبة XO ==========
def game_xo(user_id, username, msg):
    key = "game:xo:active"
    if msg == "start":
        if r.exists(key): return "كاين XO شغال. ادخل تنضم"
        board = ["1","2","3","4","5","6","7","8","9"]
        game_data = {"p1": username, "p1_id": user_id, "p2": None, "p2_id": None, "turn": user_id, "board": board, "started": False}
        r.setex(key, 300, json.dumps(game_data))
        bot_join_timeout(key, lambda d: None, 80)
        return f"❌⭕ {username} فتح طاولة XO! ادخل تنضم | البوت يدخل بعد 80ث\n{' | '.join(board[:3])}\n{' | '.join(board[3:6])}\n{' | '.join(board[6:])}"

    if msg == "ادخل":
        if not r.exists(key): return "مكاش XO. xo start"
        data = json.loads(r.get(key))
        if data["started"]: return "بدا الجيم"
        if user_id == data["p1_id"]: return "راك مولاها 😂"
        data["p2"] = username; data["p2_id"] = user_id; data["started"] = True
        r.setex(key, 300, json.dumps(data))
        b = data["board"]
        return f"🔥 {username} ضد {data['p1']}!\n{' | '.join(b[:3])}\n{' | '.join(b[3:6])}\n{' | '.join(b[6:])}\nدور {data['p1']}"

    if r.exists(key):
        data = json.loads(r.get(key))
        if data["p2_id"] == "BOT" and data["turn"] == "BOT":
            available = [i for i, v in enumerate(data["board"]) if v not in ["❌", "⭕"]]
            if available:
                idx = random.choice(available)
                data["board"][idx] = "⭕"
                data["turn"] = data["p1_id"]
                r.setex(key, 300, json.dumps(data))

    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if not data["started"] or user_id not in [data["p1_id"], data["p2_id"]] or user_id!= data["turn"]: return None
    if msg.isdigit() and 1 <= int(msg) <= 9:
        idx = int(msg) - 1
        if data["board"][idx] in ["❌", "⭕"]: return "محجوزة 😂"
        symbol = "❌" if user_id == data["p1_id"] else "⭕"
        data["board"][idx] = symbol
        b = data["board"]
        wins = [b[0]==b[1]==b[2]!=" ", b[3]==b[4]==b[5]!=" ", b[6]==b[7]==b[8]!=" ", b[0]==b[3]==b[6]!=" ", b[1]==b[4]==b[7]!=" ", b[2]==b[5]==b[8]!=" ", b[0]==b[4]==b[8]!=" ", b[2]==b[4]==b[6]!=" "]
        board_text = f"{' | '.join(b[:3])}\n{' | '.join(b[3:6])}\n{' | '.join(b[6:])}"
        if any(wins):
            r.delete(key); add_points(user_id, 50)
            return f"🏆 {username} فاز! +50 🚫💸\n{board_text}"
        if all(cell in ["❌", "⭕"] for cell in b):
            r.delete(key); return f"تعادل 🤝\n{board_text}"
        data["turn"] = data["p2_id"] if user_id == data["p1_id"] else data["p1_id"]
        next_player = data["p2"] if user_id == data["p1_id"] else data["p1"]
        r.setex(key, 300, json.dumps(data))
        return f"{board_text}\nدور {next_player}"
    return None

# ========== 2. مافيا ==========
MAFIA_ROLES = ["مافيا", "شرطي", "طبيب", "مدني", "مدني"]
def game_mafia(user_id, username, msg):
    key = "game:mafia"
    if msg == "start":
        if r.exists(key): return "كاين مافيا شغالة"
        r.setex(key, 300, json.dumps({"players": {user_id: username}, "phase": "lobby"}))
        return f"🔪 {username} فتح لوبي مافيا! ادخل تنضم | 4+ لاعبين"
    if msg == "ادخل":
        if not r.exists(key): return "مكاش لوبي. مافيا start"
        data = json.loads(r.get(key))
        if data["phase"]!= "lobby": return "اللعبة بدات"
        if user_id in data["players"]: return "راك داخل"
        data["players"][user_id] = username
        r.setex(key, 300, json.dumps(data))
        if len(data["players"]) >= 4: bot_join_timeout(key, lambda d: start_mafia_game(key), 80)
        return f"✅ {username} دخل! العدد: {len(data['players'])}"
    return None

def start_mafia_game(key):
    data = json.loads(r.get(key))
    if data["phase"]!= "lobby" or len(data["players"]) < 4: return "لازم 4+"
    players = list(data["players"].keys())
    random.shuffle(players)
    roles = dict(zip(players, MAFIA_ROLES[:len(players)]))
    data["roles"] = roles; data["phase"] = "night"; data["alive"] = players
    r.setex(key, 300, json.dumps(data))
    return f"🌙 الليل جا! {len(players)} لاعبين"

# ========== 3. حجرة ورقة مقص ==========
def game_rps(user_id, username, msg):
    key = "game:rps:active"
    if msg == "start":
        if r.exists(key): return "كاين RPS شغال. ادخل تنضم"
        game_data = {"p1": username, "p1_id": user_id, "p2": None, "p2_id": None, "started": False}
        r.setex(key, 300, json.dumps(game_data))
        bot_join_timeout(key, lambda d: None, 80)
        return f"✂️ {username} فتح طاولة RPS! ادخل تنضم | البوت يدخل بعد 80ث"
    if msg == "ادخل":
        if not r.exists(key): return "مكاش RPS. rps start"
        data = json.loads(r.get(key))
        if data["started"]: return "بدا الجيم"
        if user_id == data["p1_id"]: return "راك مولاها 😂"
        data["p2"] = username; data["p2_id"] = user_id; data["started"] = True
        r.setex(key, 300, json.dumps(data))
        return f"🔥 {username} ضد {data['p1']}! اكتبو: حجرة / ورقة / مقص"
    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if not data["started"] or user_id not in [data["p1_id"], data["p2_id"]]: return None
    if msg not in ["حجرة", "ورقة", "مقص"]: return None
    if user_id == data["p1_id"]: data["p1_choice"] = msg
    else: data["p2_choice"] = msg
    if data["p2_id"] == "BOT" and "p2_choice" not in data:
        data["p2_choice"] = random.choice(["حجرة", "ورقة", "مقص"])
    if "p1_choice" in data and "p2_choice" in data:
        p1, p2 = data["p1_choice"], data["p2_choice"]
        winner = None
        if p1 == p2: result = "تعادل 🤝"
        elif (p1=="حجرة" and p2=="مقص") or (p1=="ورقة" and p2=="حجرة") or (p1=="مقص" and p2=="ورقة"):
            winner = data["p1_id"]; result = f"🏆 {data['p1']} فاز! +30 🚫💸"
        else:
            winner = data["p2_id"]; result = f"🏆 {data['p2']} فاز! +30 🚫💸"
        if winner: add_points(winner, 30)
        r.delete(key)
        return f"{data['p1']}: {p1} | {data['p2']}: {p2}\n{result}"
    r.setex(key, 300, json.dumps(data))
    return f"✅ {username} اختار. نستناو الخصم..."

# ========== 4. تخمين رقم ==========
def game_guess(user_id, username, msg):
    key = f"game:guess:{user_id}"
    if msg == "start":
        number = random.randint(1, 100)
        r.setex(key, 300, json.dumps({"number": number, "tries": 0}))
        return f"🔢 {username} بديت تخمين رقم! من 1 لـ 100 | اكتب رقم"
    if not r.exists(key): return None
    if not msg.isdigit(): return None
    data = json.loads(r.get(key))
    data["tries"] += 1
    guess = int(msg)
    number = data["number"]
    if guess == number:
        pts = max(50 - data["tries"] * 5, 5)
        add_points(user_id, pts)
        r.delete(key)
        return f"🎯 صحيح! الرقم {number} | المحاولة {data['tries']} | +{pts} نقطة 🚫💸"
    elif guess < number:
        r.setex(key, 300, json.dumps(data))
        return f"⬆️ أكبر من {guess} | المحاولة {data['tries']}"
    else:
        r.setex(key, 300, json.dumps(data))
        return f"⬇️ أصغر من {guess} | المحاولة {data['tries']}"

# ========== 5. كلمة السر ==========
def game_password(user_id, username, msg):
    key = "game:password:active"
    if msg == "start":
        if r.exists(key): return "كاين كلمة سر شغالة"
        word = random.choice(WORDS)
        hint = word[0] + "*" * (len(word)-1)
        r.setex(key, 300, json.dumps({"word": word, "hint": hint, "winner": None}))
        return f"🔐 كلمة السر: {hint} | أول واحد يكتبها يربح 40 نقطة"
    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if data["winner"]: return None
    if msg.strip() == data["word"]:
        data["winner"] = user_id
        add_points(user_id, 40)
        r.delete(key)
        return f"🏆 {username} جابها! الكلمة: {data['word']} | +40 نقطة 🚫💸"
    return None

# ========== 6. عجلة الحظ ==========
def game_wheel(user_id, username, msg):
    if msg == "start":
        prizes = [5, 10, -10, 20, 0, 50, -5, 15, 100, -20]
        prize = random.choice(prizes)
        add_points(user_id, prize)
        if prize > 0: return f"🎡 {username} دور العجلة وربح +{prize} نقطة! 🚫💸"
        elif prize < 0: return f"🎡 {username} دور العجلة وخسر {prize} نقطة 😂"
        else: return f"🎡 {username} دور العجلة... ولا شي 😂 صفر"
    return None

# ========== 7. سؤال وجواب ==========
QUESTIONS = [
    {"q": "عاصمة الجزائر؟", "a": "الجزائر"},
    {"q": "5+5؟", "a": "10"},
    {"q": "لون السماء؟", "a": "ازرق"},
    {"q": "كم رجل للعنكبوت؟", "a": "8"}
]
def game_quiz(user_id, username, msg):
    key = "game:quiz:active"
    if msg == "start":
        if r.exists(key): return "كاين سؤال شغال"
        q = random.choice(QUESTIONS)
        r.setex(key, 300, json.dumps({"q": q["q"], "a": q["a"], "winner": None}))
        return f"❓ سؤال: {q['q']} | أول إجابة صحيحة +35 نقطة"
    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if data["winner"]: return None
    if msg.strip().lower() == data["a"].lower():
        add_points(user_id, 35)
        r.delete(key)
        return f"✅ {username} جاوب صح! {data['a']} | +35 نقطة 🚫💸"
    return None

# ========== 8. سباق كتابة ==========
SENTENCES = ["انفينيتي جن من قالمة", "البوت النووي لا يتوقف", "جلادين يوتيوب متجمعين", "ريندر اقوى من i3"]
def game_type(user_id, username, msg):
    key = "game:type:active"
    if msg == "start":
        if r.exists(key): return "كاين سباق شغال"
        sentence = random.choice(SENTENCES)
        r.setex(key, 300, json.dumps({"sentence": sentence, "start": time.time(), "winner": None}))
        return f"⌨️ اكتب بسرعة: {sentence} | أول واحد +45 نقطة"
    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if data["winner"]: return None
    if msg.strip() == data["sentence"]:
        elapsed = round(time.time() - data["start"], 1)
        pts = max(45 - int(elapsed), 10)
        add_points(user_id, pts)
        r.delete(key)
        return f"🏁 {username} كتبها في {elapsed}ث! +{pts} نقطة 🚫💸"
    return None

# ========== 9. حرب كلمات ==========
def game_words(user_id, username, msg):
    key = f"game:words:{user_id}"
    if msg == "start":
        r.setex(key, 60, json.dumps({"words": 0, "start": time.time()}))
        return f"💬 {username} عندك 60 ثانية! اكتب أكبر عدد كلمات مختلفة | كل كلمة +2 نقطة"
    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if time.time() - data["start"] > 60:
        total = data["words"] * 2
        add_points(user_id, total)
        r.delete(key)
        return f"⏰ الوقت خلاص! {username} كتب {data['words']} كلمات | +{total} نقطة 🚫💸"
    data["words"] += 1
    r.setex(key, 60, json.dumps(data))
    return None

# ========== 10. من سيربح النقاط ==========
def game_million(user_id, username, msg):
    key = f"game:million:{user_id}"
    if msg == "start":
        q = random.choice(QUESTIONS)
        r.setex(key, 300, json.dumps({"q": q, "level": 1}))
        return f"💰 من سيربح النقاط؟ المستوى 1: {q['q']} | جاوب تربح 10 نقاط"
    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if msg.strip().lower() == data["q"]["a"].lower():
        pts = data["level"] * 10
        add_points(user_id, pts)
        r.delete(key)
        return f"✅ صحيح! {data['q']['a']} | +{pts} نقطة 🚫💸"
    return None

# ========== 11. كنز قالمة ==========
def game_treasure(user_id, username, msg):
    if msg == "start":
        found = random.randint(0, 100)
        if found > 70:
            prize = random.randint(20, 100)
            add_points(user_id, prize)
            return f"💎 {username} لقيت كنز في قالمة! +{prize} نقطة 🚫💸"
        else:
            return f"🗿 {username} حفرت و ملقيت والو 😂 صفر"
    return None

# ========== 12. سجن و جلاد ==========
def game_jail(user_id, username, msg):
    key = "game:jail"
    if msg == "start":
        if r.exists(key): return "كاين سجن شغال"
        r.setex(key, 300, json.dumps({"prisoners": [], "jailer": user_id}))
        return f"⛓️ {username} هو الجلاد! اكتب سجن @اسم باه تسجن واحد"
    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if msg.startswith("سجن "):
        target = msg[4:].strip()
        if user_id == data["jailer"] and target not in data["prisoners"]:
            data["prisoners"].append(target)
            r.setex(key, 300, json.dumps(data))
            return f"🔒 {username} سجن {target}! | +15 نقطة للجلاد"
    return None

# ========== 13. تحدي سرعة ==========
def game_speed(user_id, username, msg):
    key = "game:speed:active"
    if msg == "start":
        if r.exists(key): return "كاين تحدي شغال"
        num = random.randint(100, 999)
        r.setex(key, 30, json.dumps({"num": num, "start": time.time(), "winner": None}))
        return f"⚡ تحدي سرعة! اكتب الرقم: {num} | أول واحد +50 نقطة"
    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if data["winner"]: return None
    if msg.strip() == str(data["num"]):
        elapsed = round(time.time() - data["start"], 2)
        add_points(user_id, 50)
        r.delete(key)
        return f"🏆 {username} الأسرع! {elapsed}ث | +50 نقطة 🚫💸"
    return None

# ========== 14. من القاتل ==========
def game_killer(user_id, username, msg):
    key = "game:killer:active"
    if msg == "start":
        if r.exists(key): return "كاين جريمة شغالة"
        suspects = ["تقي", "جلاد1", "جلاد2", "بوت"]
        killer = random.choice(suspects)
        r.setex(key, 300, json.dumps({"killer": killer, "winner": None}))
        return f"🔪 جريمة في قالمة! المشتبهين: {', '.join(suspects)} | اكتب اسم القاتل +25 نقطة"
    if not r.exists(key): return None
    data = json.loads(r.get(key))
    if data["winner"]: return None
    if msg.strip() == data["killer"]:
        add_points(user_id, 25)
        r.delete(key)
        return f"🕵️ {username} كشف القاتل! كان {data['killer']} | +25 نقطة 🚫💸"
    return None

# ========== 15. بورصة النقاط ==========
def game_stock(user_id, username, msg):
    if msg == "start":
        change = random.randint(-30, 50)
        add_points(user_id, change)
        if change > 0: return f"📈 {username} البورصة طلعت! +{change} نقطة 🚫💸"
        elif change < 0: return f"📉 {username} البورصة طاحت! {change} نقطة 😂"
        else: return f"📊 {username} البورصة مستقرة... صفر"
    return None

# ========== 16. مملكة الجلادين ==========
def game_kingdom(user_id, username, msg):
    key = "game:kingdom"
    if msg == "start":
        if not r.exists(key): r.set(key, user_id)
        king = r.get(key).decode()
        king_name = r.get(f"username:{king}").decode() if r.get(f"username:{king}") else "مجهول"
        if user_id == king: return f"👑 {username} راك الملك الحالي! +10 نقطة يوميا"
        else: return f"👑 الملك الحالي: {king_name} | اهجم عليه ب: هجوم مملكة"
    if msg == "هجوم مملكة":
        if not r.exists(key): return "مكاش مملكة"
        king = r.get(key).decode()
        if user_id == king: return "راك الملك 😂"
        chance = random.randint(1, 100)
        if chance > 70:
            r.set(key, user_id)
            add_points(user_id, 100)
            return f"⚔️ {username} انقلبت على الملك! صرت الملك الجديد +100 نقطة 🚫💸"
        else:
            add_points(user_id, -20)
            return f"💥 {username} فشل الهجوم! -20 نقطة"
    return None

# ========== معالج الأوامر الرئيسي ==========
GAMES = {
    "xo": game_xo,
    "مافيا": game_mafia,
    "rps": game_rps,
    "تخمين": game_guess,
    "كلمة": game_password,
    "عجلة": game_wheel,
    "سؤال": game_quiz,
    "كتابة": game_type,
    "كلمات": game_words,
    "مليون": game_million,
    "كنز": game_treasure,
    "سجن": game_jail,
    "سرعة": game_speed,
    "قاتل": game_killer,
    "بورصة": game_stock,
    "مملكة": game_kingdom
}

def handle_command(user_id, username, msg):
    add_points(user_id, 1)
    r.set(f"username:{user_id}", username)
    parts = msg.strip().split(" ", 1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    # أساسي
    if cmd == "سلام": return f"وعليكم السلام {username} 🔥 INFINITY GEN يرحب بيك من قالمة 🚫💸"
    if cmd == "نقاطي": return f"💰 {username} نقاطك: {get_points(user_id)} 🚫💸"
    if cmd == "توب":
        top = r.zrevrange("leaderboard", 0, 9, withscores=True)
        if not top: return "مكاش جلادين 🏜️"
        text = "🏆 توب 10:\n" + "\n".join([f"{i+1}. {r.get(f'username:{u.decode()}').decode() if r.get(f'username:{u.decode()}') else u.decode()[:12]}: {int(s)}" for i,(u,s) in enumerate(top)])
        return text
    if cmd == "بنق": return "بونق! 🏓"

    # متجر
    if cmd == "متجر":
        text = "🛒 متجر INFINITY GEN النووي 🚫💸\n"
        for item, data in SHOP_ITEMS.items():
            text += f"{item}: {data['cost']} - {data['desc']}\n"
        return text + "\nشراء درع"
    if cmd == "شراء": return buy_item(user_id, username, arg)
    if cmd == "شنطة":
        items = [f"{item} x{int(r.get(f'item:{item}:{user_id}') or 0)}" for item in SHOP_ITEMS if has_item(user_id, item)]
        return f"🎒 {username}: " + ", ".join(items) if items else "شنطتك فاضية"
    if cmd == "مضاعف":
        if not has_item(user_id, "مضاعف"): return "ما عندكش مضاعف"
        use_item(user_id, "مضاعف"); r.setex(f"multiplier:{user_id}", 600, 1)
        return f"⚡ {username} فعل x2 نقاط 10د!"

    # ألعاب
    if cmd in GAMES: return GAMES[cmd](user_id, username, arg)
    if cmd == "ادخل":
        for game_cmd in ["xo", "مافيا", "rps"]:
            res = GAMES[game_cmd](user_id, username, "ادخل")
            if res: return res
        return "مكاش لعبة تستنى"
    return None