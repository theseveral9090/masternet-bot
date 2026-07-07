import os

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "8623078956:AAGnR94NKH1NbrY9RHOCgWYf7kpdK5-XX_g"

TARGET_URL = "https://masternet.store/teste/"
API_URL = "https://masternet.store/teste/processar_teste.php"
WHATSAPP_BASE = "319777"

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text",
]

PROXY_TEST_TIMEOUT = 5
PROXY_POOL_MIN = 10
PROXY_REFRESH_INTERVAL = 300
