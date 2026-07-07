import asyncio
import aiohttp
import random
import re
from config import PROXY_SOURCES, PROXY_TEST_TIMEOUT, PROXY_POOL_MIN, PROXY_REFRESH_INTERVAL

class ProxyManager:
    def __init__(self):
        self.working_proxies = []
        self.banned = set()
        self._lock = asyncio.Lock()
        self._testing = False
        self._pool_ready = asyncio.Event()

    async def start(self):
        asyncio.create_task(self._maintain_pool())

    async def _maintain_pool(self):
        while True:
            self._testing = True
            try:
                await self._fetch_and_test()
            except Exception as e:
                print(f"[ProxyManager] Error: {e}")

            if len(self.working_proxies) > 0:
                self._pool_ready.set()

            self._testing = False

            wait = PROXY_REFRESH_INTERVAL
            if len(self.working_proxies) < PROXY_POOL_MIN:
                wait = 15

            await asyncio.sleep(wait)

    async def _fetch_and_test(self):
        print(f"[ProxyManager] Buscando proxies... (pool atual: {len(self.working_proxies)})")
        raw = await self._fetch_sources()
        random.shuffle(raw)
        print(f"[ProxyManager] {len(raw)} proxies brutos para testar")

        sem = asyncio.Semaphore(50)
        tested = 0
        added = 0

        async def test_one(proto, addr):
            nonlocal tested, added
            async with sem:
                ok = await self._test(proto, addr)
                tested += 1
                if ok:
                    async with self._lock:
                        self.working_proxies.append((proto, addr))
                        added += 1
                if tested % 200 == 0:
                    print(f"[ProxyManager] Testados {tested}/{len(raw)}, funcionais: {added}")

        tasks = []
        seen = set()
        for proto, addr in raw:
            if addr not in seen and addr not in self.banned:
                seen.add(addr)
                tasks.append(test_one(proto, addr))

        await asyncio.gather(*tasks)

        async with self._lock:
            random.shuffle(self.working_proxies)

        print(f"[ProxyManager] Pool atual: {len(self.working_proxies)} proxies funcionais")

    async def _fetch_sources(self):
        all_proxies = []
        async with aiohttp.ClientSession() as session:
            for url in PROXY_SOURCES:
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            for line in text.strip().split("\n"):
                                line = line.strip()
                                if not line or line.startswith("#"):
                                    continue
                                clean = re.sub(r"^socks5://|^socks4://|^http://|^https://", "", line)
                                if ":" in clean and len(clean.split(":")) == 2:
                                    all_proxies.append(("socks5", clean))
                                    all_proxies.append(("http", clean))
                except Exception:
                    pass
        return list(set(all_proxies))

    async def _test(self, proto, addr):
        url = f"{proto}://{addr}"
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get("https://masternet.store/teste/",
                    proxy=url,
                    timeout=aiohttp.ClientTimeout(total=PROXY_TEST_TIMEOUT),
                    ssl=False) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def get_proxy(self):
        while True:
            async with self._lock:
                if self.working_proxies:
                    proto, addr = self.working_proxies.pop(0)
                    return f"{proto}://{addr}"
            await asyncio.sleep(0.5)

    async def mark_bad(self, proxy_url):
        async with self._lock:
            addr = re.sub(r"^socks5://|^socks4://|^http://|^https://", "", proxy_url)
            self.banned.add(addr)
