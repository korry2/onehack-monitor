import feedparser
import requests
import os
import time

# Ayarlar (GitHub Secrets'tan gelecek)
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
RSS_URL = "https://onehack.us/latest.rss"
HISTORY_FILE = "history.txt"

def send_telegram_message(text):
    """Telegram'a mesaj gönderir."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Hata: Mesaj gönderilemedi. Kod: {response.status_code}")
    except Exception as e:
        print(f"Hata: {e}")

def load_history():
    """Daha önce gönderilen linkleri dosyadan okur."""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def save_history(links):
    """Gönderilen linkleri dosyaya kaydeder (Son 100 tanesini tutar)."""
    # Listeyi son 100 elemanla sınırla ki dosya şişmesin
    trimmed_links = links[-100:]
    with open(HISTORY_FILE, "w") as f:
        for link in trimmed_links:
            f.write(f"{link}\n")

def main():
    print("OneHack Monitor Başlatılıyor...")
    
    # RSS beslemesini çek
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("RSS beslemesi boş veya çekilemedi.")
        return

    # Geçmişi yükle
    sent_links = load_history()
    new_links_found = []
    
    # RSS'deki girdileri tersten (eskiden yeniye) kontrol et
    # Böylece sırayla bildirim gelir
    for entry in reversed(feed.entries):
        link = entry.link
        title = entry.title
        
        # Eğer bu link daha önce gönderilmediyse
        if link not in sent_links:
            print(f"Yeni içerik bulundu: {title}")
            
            # Mesajı hazırla
            message = f"🚨 <b>Yeni OneHack Konusu!</b>\n\n📌 <b>{title}</b>\n\n🔗 <a href='{link}'>Konuya Gitmek İçin Tıkla</a>"
            
            # Gönder
            send_telegram_message(message)
            
            # Listeye ekle
            sent_links.append(link)
            new_links_found.append(link)
            
            # Telegram API limitine takılmamak için kısa bir bekleme
            time.sleep(1)
    
    if new_links_found:
        print(f"Toplam {len(new_links_found)} yeni içerik gönderildi.")
        save_history(sent_links)
    else:
        print("Yeni içerik yok.")

if __name__ == "__main__":
    main()
