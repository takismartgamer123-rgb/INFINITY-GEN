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
WORDS = ["قالمة", "انفينيتي", "يوتيوب", "جلاد", "تقي", "مافيا", "ثورة", "بونق"]

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

# ========== لعبة XO ==========
def game_xo(user_id, username, msg):
    key = "game:xo:active"
    if msg == "start":
        if r.exists(key): return "كاين XO شغال. ادخل تنضم"
        board = ["1","2","3","4","5","6","7","8","9"]
        game_data = {"p1": username, "p1_id": user_id, "p2": None, "p2_id": None, "turn": user_id, "board": board, "started": False}
        r.setex(key, 300, json.dumps(game_data))
        bot_join_timeout(key, lambda d: None, 80)
        return f"❌⭕ {username} فتح طاولة XO في قالمة! ادخل تنضم | INFINITY GEN يدخل بعد 80ث\n{' | '.join(board[:3])}\n{' | '.join(board[3:6])}\n{' | '.join(board[6:])}"

    if msg == "ادخل":
        if not r.exists(key): return "مكاش XO. xo start"
        data = json.loads(r.get(key))
        if data["started"]: return "بدا الجيم"
        if user_id == data["p1_id"]: return "راك مولاها 😂"
        data["p2"] = username; data["p2_id"] = user_id; data["started"] = True
        r.setex(key, 300, json.dumps(data))
        b = data["board"]
        return f"🔥 {username} ضد {data['p1']}!\n{' | '.join(b[:3])}\n{' | '.join(b[3:6])}\n{' | '.join(b[6:])}\nدور {data['p1']}"

    # لعب البوت
    if r.exists(key):
        data = json.loads(r.get(key))
        if data["p2_id"] == "BOT" and data["turn"] == "BOT":
            available = [i for i, v in enumerate(data["board"]) if v not in ["❌", "⭕"]]
            if available:
                idx = random.choice(available)
                data["board"][idx] = "⭕"
                data["turn"] = data["p1_id"]
                r.setex(key, 300, json.dumps(data))

    # لعب عادي
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

# ========== لعبة مافيا ==========
MAFIA_ROLES = ["مافيا", "شرطي", "طبيب", "مدني", "مدني"]

def game_mafia(user_id, username, msg):
    key = "game:mafia"
    if msg == "start":
        if r.exists(key): return "كاين مافيا شغالة"
        r.setex(key, 300, json.dumps({"players": {user_id: username}, "phase": "lobby", "roles": {}, "alive": [], "votes": {}, "night_actions": {}, "boosters": {}}))
        return f"🔪 {username} فتح لوبي مافيا في قالمة! ادخل تنضم | 4+ لاعبين\nاللعبة تبدا تلقائيا بعد 80ث"

    if msg == "ادخل":
        if not r.exists(key): return "مكاش لوبي. مافيا start"
        data = json.loads(r.get(key))
        if data["phase"]!= "lobby": return "اللعبة بدات"
        if user_id in data["players"]: return "راك داخل"
        data["players"][user_id] = username
        r.setex(key, 300, json.dumps(data))
        if len(data["players"]) >= 4:
            bot_join_timeout(key, lambda d: start_mafia_game(key), 80)
        return f"✅ {username} دخل! العدد: {len(data['players'])}"

    if msg == "بدا" and r.exists(key):
        return start_mafia_game(key)
    return None

def start_mafia_game(key):
    data = json.loads(r.get(key))
    if data["phase"]!= "lobby" or len(data["players"]) < 4: return "لازم 4+"
    players = list(data["players"].keys())
    random.shuffle(players)
    roles = dict(zip(players, MAFIA_ROLES[:len(players)]))
    data["roles"] = roles; data["phase"] = "night"; data["alive"] = players
    r.setex(key, 300, json.dumps(data))
    return f"🌙 الليل جا في قالمة! {len(players)} لاعبين\nالمافيا: قتل اسم | الشرطي: فتش اسم | الطبيب: احمي اسم"

# ========== معالج الأوامر الرئيسي ==========
GAMES = {"xo": game_xo, "مافيا": game_mafia}

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
        res = game_xo(user_id, username, "ادخل")
        if res: return res
        res = game_mafia(user_id, username, "ادخل")
        if res: return res
        return "مكاش لعبة تستنى"

    return None