import re
import random
import aiohttp
from config import TARGET_URL, API_URL, WHATSAPP_BASE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Origin": "https://masternet.store",
    "Referer": "https://masternet.store/teste/",
    "Accept": "application/json, text/plain, */*",
}

class AccountGenerator:
    def __init__(self, proxy_manager):
        self.proxy_mgr = proxy_manager

    async def generate(self):
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector, headers=HEADERS) as sess:
            for attempt in range(50):
                proxy_url = await self.proxy_mgr.get_proxy()
                if not proxy_url:
                    continue

                try:
                    async with sess.get(TARGET_URL, proxy=proxy_url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        if resp.status != 200:
                            await self.proxy_mgr.mark_bad(proxy_url)
                            continue
                        html = await resp.text()
                except Exception:
                    await self.proxy_mgr.mark_bad(proxy_url)
                    continue

                match = re.search(r"csrf_token:'([^']+)'", html)
                if not match:
                    await self.proxy_mgr.mark_bad(proxy_url)
                    continue

                csrf = match.group(1)
                phone = f"{WHATSAPP_BASE}{random.randint(1000, 99999)}"

                try:
                    async with sess.post(API_URL, json={"csrf_token": csrf, "whatsapp": phone, "action": "check"}, proxy=proxy_url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        check_data = await resp.json()
                except Exception:
                    await self.proxy_mgr.mark_bad(proxy_url)
                    continue

                if check_data.get("rate_limited"):
                    await self.proxy_mgr.mark_bad(proxy_url)
                    continue

                if not check_data.get("success"):
                    continue

                payload = {
                    "csrf_token": csrf,
                    "whatsapp": phone,
                    "fluxo": "experiente",
                    "operadora": "vivo",
                    "saldo_status": None,
                    "plano_vivo": "outro",
                    "chip_tim": None,
                    "plano": "standard",
                }

                try:
                    async with sess.post(API_URL, json=payload, proxy=proxy_url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        data = await resp.json()
                except Exception:
                    await self.proxy_mgr.mark_bad(proxy_url)
                    continue

                if data.get("success") and data.get("data"):
                    d = data["data"]
                    return {
                        "login": d["login"],
                        "senha": d["senha"],
                        "validade": d.get("validade", "2 horas"),
                    }

                if data.get("rate_limited"):
                    await self.proxy_mgr.mark_bad(proxy_url)
                    continue

                return {"error": data.get("error", data.get("message", "Erro desconhecido"))}

        return {"error": "Nao foi possivel gerar conta"}
