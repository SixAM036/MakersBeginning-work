import network, urequests, time, random

# Wi-Fi 設定
ssid = '網路名稱'
password = '網路密碼'

# Telegram Bot 設定
BOT_TOKEN = 'BOT的TOKEN'
CHAT_ID = 'CHAT的ID'
URL = f'https://api.telegram.org/bot{BOT_TOKEN}/'

# 建立 Wi-Fi 連線
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected():
    pass
print('WiFi connected:', wlan.ifconfig())

# 遊戲變數
answer = []
last_update_id = 0
game_active = False

# 正確版：產生不重複 4 位數字
def generate_answer():
    digits = "0123456789"
    result = []
    while len(result) < 4:
        d = digits[random.randint(0, 9)]
        if d not in result:
            result.append(d)
    return result

# 比對玩家猜測與答案，回傳幾A幾B
def check_guess(guess, answer):
    A = sum([1 for i in range(4) if guess[i] == answer[i]])
    B = sum([1 for i in guess if i in answer]) - A
    return A, B

# 傳送訊息
def send_message(chat_id, text):
    try:
        url = URL + f'sendMessage?chat_id={chat_id}&text={text}'
        urequests.get(url).close()
    except Exception as e:
        print("Error sending message:", e)

# 取得訊息
def get_updates():
    global last_update_id
    try:
        url = URL + f'getUpdates?offset={last_update_id + 1}'
        r = urequests.get(url)
        updates = r.json().get('result', [])
        r.close()
        return updates
    except:
        return []

# 主遊戲迴圈
while True:
    updates = get_updates()
    for update in updates:
        last_update_id = update['update_id']
        message = update.get('message', {})
        text = message.get('text', '')
        chat_id = message['chat']['id']

        if text == '/start':
            answer = generate_answer()
            game_active = True
            send_message(chat_id, "🎮 幾A幾B猜數字遊戲開始！請輸入一個不重複的4位數字：")
            continue

        if not game_active:
            send_message(chat_id, "請先輸入 /start 開始新遊戲")
            continue

        if len(text) == 4 and text.isdigit():
            guess = list(text)
            if len(set(guess)) < 4:
                send_message(chat_id, "請輸入『不重複』的4位數字。")
                continue
            A, B = check_guess(guess, answer)
            if A == 4:
                send_message(chat_id, f"🎉 恭喜你猜對了！答案是 {''.join(answer)}，你贏了！輸入 /start 開始新一局。")
                game_active = False
            else:
                send_message(chat_id, f"{text} ➜ {A}A{B}B，再試試看！")
        else:
            send_message(chat_id, "請輸入正確格式：4位不重複的整數，如 5823。")
    
    time.sleep(1)
