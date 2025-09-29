import time
import requests
from pypresence import Presence

# === Настройки ===
CLIENT_ID = "1421901017150259260"  # твой Discord App ID
API_URL = "https://azura.hpsbassline.myftp.biz/api/station/haapsaly_bassline/nowplaying"
LISTEN_URL = "https://hpsbassline.myftp.biz/"
ASSET_KEY = "full_logo"  # имя картинки из Rich Presence Assets

# === Подключение к Discord ===
rpc = Presence(CLIENT_ID)
rpc.connect()
print("✅ Подключено к Discord RPC")

def fetch_nowplaying():
    r = requests.get(API_URL, timeout=5)
    r.raise_for_status()
    data = r.json()
    np = data.get("now_playing", {})
    song = np.get("song", {}) or {}
    return {
        "title": song.get("title") or "Unknown Title",
        "artist": song.get("artist") or "Unknown Artist",
        "duration": np.get("duration"),
        "elapsed": np.get("elapsed"),
    }
    

def compute_timestamps(duration, elapsed):
    if not (isinstance(duration, int) and isinstance(elapsed, int)):
        return None, None
    if duration <= 0 or elapsed < 0:
        return None, None
    now = int(time.time())
    start_time = now - elapsed
    end_time = start_time + duration
    if end_time <= start_time:
        return None, None
    return start_time, end_time

last_payload = None

while True:
    try:
        np = fetch_nowplaying()
        start, end = compute_timestamps(np["duration"], np["elapsed"])

        payload = {
    "details": np.get("title") or "Offline",  # всегда есть текст
    "state": np.get("artist") or "Offline",
    "large_image": ASSET_KEY,
    "large_text": "HPS Bassline Radio",
    "buttons": [{"label": "🎧 Listen", "url": LISTEN_URL}],
}
        if start and end:
            payload["start"] = start
            payload["end"] = end

        if payload != last_payload:
            rpc.update(**payload)
            last_payload = payload
            print(f"🎵 Обновлено: {np['title']} — {np['artist']} (таймер: {bool(start and end)})")
        else:
            print("⏸️ Без изменений")

    except Exception as e:
        print("⚠️ Ошибка:", e)

    time.sleep(15)
