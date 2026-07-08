import asyncio
import json
import os
import logging
from aiohttp import web

from telegram import Update, InlineKeyboardButton, CopyTextButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

from config import BOT_TOKEN
from proxy_manager import ProxyManager
from account_gen import AccountGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

USER_FILE = "users.json"
AUTO_TASKS = {}

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

proxy_mgr = ProxyManager()
account_gen = AccountGenerator(proxy_mgr)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "MasterNet Bot\n\n"
        "Comandos:\n"
        "/getlogin - Gera uma conta premium nova\n"
        "/autoget N - Envia automaticamente a cada N minutos\n"
        "/stop - Para o envio automatico\n"
        "/status - Status do bot e proxies",
    )

async def getlogin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Gerando conta premium...")
    result = await account_gen.generate()

    if "error" in result:
        await msg.edit_text(f"Erro: {result['error']}")
    else:
        text = (
            f"Login: <code>{result['login']}</code>\n"
            f"Senha: <code>{result['senha']}</code>\n"
            f"Validade: {result['validade']}"
        )
        keyboard = [
            [
                InlineKeyboardButton("Copiar Login", copy_text=CopyTextButton(result['login'])),
                InlineKeyboardButton("Copiar Senha", copy_text=CopyTextButton(result['senha'])),
            ]
        ]
        await msg.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def autoget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Use: /autoget <minutos>\nEx: /autoget 30")
        return

    try:
        interval = int(args[0])
        if interval < 1:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Intervalo invalido. Use minutos (min 1).")
        return

    users = load_users()
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id

    users[user_id] = {"chat_id": chat_id, "interval": interval, "active": True}
    save_users(users)

    if user_id in AUTO_TASKS:
        AUTO_TASKS[user_id].cancel()

    task = asyncio.create_task(auto_send_loop(user_id, chat_id, interval, context.application.bot))
    AUTO_TASKS[user_id] = task

    await update.message.reply_text(
        f"Auto-get ativado! Conta nova a cada {interval} minuto(s).\n/stop para cancelar."
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    if user_id in users:
        users[user_id]["active"] = False
        save_users(users)
    if user_id in AUTO_TASKS:
        AUTO_TASKS[user_id].cancel()
        del AUTO_TASKS[user_id]
        await update.message.reply_text("Auto-get desativado.")
    else:
        await update.message.reply_text("Nenhum auto-get ativo.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool_size = len(proxy_mgr.working_proxies)
    used = len(proxy_mgr.banned)
    users = load_users()
    active = sum(1 for u in users.values() if u.get("active"))
    await update.message.reply_text(
        f"Status\n\n"
        f"Proxies disponiveis: {pool_size}\n"
        f"Proxies banidos: {used}\n"
        f"Usuarios ativos: {active}",
    )

async def auto_send_loop(user_id, chat_id, interval, bot):
    while True:
        await asyncio.sleep(interval * 60)
        users = load_users()
        if not users.get(str(user_id), {}).get("active"):
            break
        try:
            result = await account_gen.generate()
            if "error" in result:
                await bot.send_message(chat_id, text=f"Erro: {result['error']}")
            else:
                text = (
                    f"Login: <code>{result['login']}</code>\n"
                    f"Senha: <code>{result['senha']}</code>\n"
                    f"Validade: {result['validade']}"
                )
                keyboard = [
                    [
                        InlineKeyboardButton("Copiar Login", copy_text=CopyTextButton(result['login'])),
                        InlineKeyboardButton("Copiar Senha", copy_text=CopyTextButton(result['senha'])),
                    ]
                ]
                await bot.send_message(chat_id, text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            log.error(f"auto_send_loop error: {e}")

async def post_init(app: Application):
    asyncio.create_task(proxy_mgr.start())
    log.info("ProxyManager iniciado em background. Proxies sendo testados...")

async def restore_tasks(app: Application):
    users = load_users()
    for uid, cfg in users.items():
        if cfg.get("active"):
            t = asyncio.create_task(
                auto_send_loop(uid, cfg["chat_id"], cfg["interval"], app.bot)
            )
            AUTO_TASKS[uid] = t
            log.info(f"Auto-get restaurado: {uid} a cada {cfg['interval']}min")

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getlogin", getlogin))
    app.add_handler(CommandHandler("autoget", autoget))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(restore_tasks(app))

    log.info("Iniciando polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
