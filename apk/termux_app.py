#!/usr/bin/env python3
"""MasterNet - Gerador de contas via Termux"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proxy_manager import ProxyManager
from account_gen import AccountGenerator

proxy_mgr = ProxyManager()
account_gen = AccountGenerator(proxy_mgr)

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def print_header():
    print("=" * 40)
    print("       MASTERNET - GERADOR DE CONTAS")
    print("=" * 40)

async def main():
    asyncio.create_task(proxy_mgr.start())
    await asyncio.sleep(2)

    while True:
        clear()
        print_header()
        print()
        print("Proxies disponiveis:", len(proxy_mgr.working_proxies))
        print()
        print("[1] Gerar nova conta")
        print("[2] Status dos proxies")
        print("[3] Sair")
        print()

        op = input("Escolha: ").strip()

        if op == "1":
            print()
            print("Gerando conta...")
            result = await account_gen.generate()
            print()
            if "error" in result:
                print(f"ERRO: {result['error']}")
            else:
                print(f"Login: {result['login']}")
                print(f"Senha: {result['senha']}")
                print(f"Validade: {result['validade']}")
            print()
            input("Pressione ENTER para continuar...")

        elif op == "2":
            print()
            print(f"Proxies disponiveis: {len(proxy_mgr.working_proxies)}")
            print(f"Proxies banidos: {len(proxy_mgr.banned)}")
            print()
            input("Pressione ENTER para continuar...")

        elif op == "3":
            break

    print("Saindo...")

if __name__ == "__main__":
    asyncio.run(main())
