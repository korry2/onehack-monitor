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
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    except Exception as e:
        print(f"Dosya okuma hatası: {e}")
        return []

def save_history(links):
    """Gönderilen linkleri dosyaya kaydeder (Son 100 tanesini tutar)."""
    trimmed_links = links[-100:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            for link in trimmed_links:
                f.write(f"{link}\n")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

def main():
    print("OneHack Monitor Başlatılıyor...")
    
    # --- KRİTİK DEĞİŞİKLİK: User-Agent Eklemesi ---
    # OneHack gibi siteler botları engelleyebilir. Bu başlık tarayıcı taklidi yapar.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Önce requests ile veriyi çekiyoruz
        response = requests.get(RSS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Gelen veriyi feedparser'a veriyoruz
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"RSS çekilirken hata oluştu: {e}")
        return

    if not feed.entries:
        print("RSS beslemesi boş veya çekilemedi.")
        return

    # Geçmişi yükle
    sent_links = load_history()
    new_links_found = []
    
    # RSS'deki girdileri tersten (eskiden yeniye) kontrol et
    for entry in reversed(feed.entries):
        link = entry.link
        title = entry.title
        
        # Eğer bu link daha önce gönderilmediyse
        if link not in sent_links:
            print(f"Yeni içerik bulundu: {title}")
            
            # HTML formatında mesaj (Güvenlik için title karakterlerini kaçırabiliriz ama şimdilik gerek yok)
            message = f"🚨 <b>Yeni OneHack Konusu!</b>\n\n📌 <b>{title}</b>\n\n🔗 <a href='{link}'>Konuya Gitmek İçin Tıkla</a>"
            
            send_telegram_message(message)
            
            sent_links.append(link)
            new_links_found.append(link)
            
            time.sleep(1)
    
    if new_links_found:
        print(f"Toplam {len(new_links_found)} yeni içerik gönderildi.")
        save_history(sent_links)
    else:
        print("Yeni içerik yok.")

if __name__ == "__main__":
    main()
