from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from core.api_client import ApiError


class LoginScreen(Screen):
    error_text = StringProperty("")

    def do_login(self):
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text

        if not email or not password:
            self.error_text = "Заполните оба поля"
            return

        app = self.manager.app_ref
        try:
            app.api_client.login(email, password)
        except ApiError as e:
            self.error_text = "Неверный email или пароль"
            return

        self.error_text = ""
        self.manager.current = "notes_list"

    def go_to_register(self):
        # Заглушка — экран регистрации можно добавить по этому же паттерну
        self.error_text = "Регистрация пока не подключена"
