import asyncio
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock, mainthread
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, RoundedRectangle

from proxy_manager import ProxyManager
from account_gen import AccountGenerator

proxy_mgr = ProxyManager()
account_gen = AccountGenerator(proxy_mgr)
loop = None

def start_loop():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(proxy_mgr.start())
    loop.run_forever()

threading.Thread(target=start_loop, daemon=True).start()

class AccountScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)
        with self.canvas.before:
            Color(0.043, 0.059, 0.102, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.status = Label(
            text="Iniciando...",
            size_hint_y=0.1,
            color=(0.58, 0.64, 0.72, 1),
        )
        self.add_widget(self.status)

        self.add_widget(Label(text="", size_hint_y=0.05))

        self.login_label = Label(
            text="Login:",
            size_hint_y=0.08,
            color=(0.13, 0.77, 0.37, 1),
            halign="center",
        )
        self.add_widget(self.login_label)

        self.login_value = TextInput(
            text="",
            readonly=True,
            size_hint_y=0.1,
            background_color=(0.1, 0.12, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            halign="center",
            font_size=18,
        )
        self.add_widget(self.login_value)

        self.copy_login = Button(
            text="Copiar Login",
            size_hint_y=0.08,
            background_color=(0.13, 0.77, 0.37, 1),
            color=(1, 1, 1, 1),
        )
        self.copy_login.bind(on_press=lambda _: self.copy(self.login_value.text, "Login copiado!"))
        self.add_widget(self.copy_login)

        self.senha_label = Label(
            text="Senha:",
            size_hint_y=0.08,
            color=(0.13, 0.77, 0.37, 1),
            halign="center",
        )
        self.add_widget(self.senha_label)

        self.senha_value = TextInput(
            text="",
            readonly=True,
            size_hint_y=0.1,
            background_color=(0.1, 0.12, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            halign="center",
            font_size=18,
        )
        self.add_widget(self.senha_value)

        self.copy_senha = Button(
            text="Copiar Senha",
            size_hint_y=0.08,
            background_color=(0.13, 0.77, 0.37, 1),
            color=(1, 1, 1, 1),
        )
        self.copy_senha.bind(on_press=lambda _: self.copy(self.senha_value.text, "Senha copiada!"))
        self.add_widget(self.copy_senha)

        self.add_widget(Label(text="", size_hint_y=0.05))

        self.gerar_btn = Button(
            text="GERAR CONTA",
            size_hint_y=0.12,
            background_color=(0.20, 0.40, 0.90, 1),
            color=(1, 1, 1, 1),
            font_size=20,
            bold=True,
        )
        self.gerar_btn.bind(on_press=self.gerar)
        self.add_widget(self.gerar_btn)

    def _update_rect(self, *_):
        self.rect.size = self.size
        self.rect.pos = self.pos

    @mainthread
    def copy(self, text, msg):
        Clipboard.copy(text)
        self.status.text = msg
        Clock.schedule_once(lambda _: self._reset_status(), 2)

    def _reset_status(self):
        if self.login_value.text:
            self.status.text = "Pronto!"
        else:
            self.status.text = "Clique em GERAR CONTA"

    def gerar(self, _):
        self.gerar_btn.disabled = True
        self.gerar_btn.text = "Gerando..."
        self.status.text = "Buscando proxy..."
        asyncio.run_coroutine_threadsafe(self._generate(), loop)

    async def _generate(self):
        result = await account_gen.generate()
        Clock.schedule_once(lambda _: self._show_result(result))

    @mainthread
    def _show_result(self, result):
        self.gerar_btn.disabled = False
        self.gerar_btn.text = "GERAR CONTA"
        if "error" in result:
            self.login_value.text = ""
            self.senha_value.text = ""
            self.status.text = f"Erro: {result['error']}"
        else:
            self.login_value.text = result["login"]
            self.senha_value.text = result["senha"]
            self.status.text = f"Conta gerada! Validade: {result['validade']}"

class MasterNetApp(App):
    def build(self):
        self.title = "MasterNet"
        return AccountScreen()

if __name__ == "__main__":
    MasterNetApp().run()
