"""
Точка входа приложения.

Здесь:
- создаются общие для всего приложения объекты (storage, api_client, sync_manager)
- регистрируется ScreenManager со всеми экранами
- подключаются .kv файлы каждого экрана
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from core.storage import Storage
from core.api_client import ApiClient
from core.sync import SyncManager

from screens.login_screen import LoginScreen
from screens.notes_list_screen import NotesListScreen
from screens.note_editor_screen import NoteEditorScreen


class AppScreenManager(ScreenManager):
    """
    Обычный ScreenManager, но с ссылкой на само приложение (app_ref),
    чтобы каждый экран мог достучаться до storage/api_client/sync_manager
    без лишних пробросов параметров через конструкторы.
    """
    app_ref = None


class NotesApp(App):
    def build(self):
        # общие объекты на всё приложение — создаются один раз
        self.storage = Storage()
        self.api_client = ApiClient()
        self.sync_manager = SyncManager(self.storage, self.api_client)

        # подключаем разметку каждого экрана явно
        Builder.load_file("screens/login_screen.kv")
        Builder.load_file("screens/notes_list_screen.kv")
        Builder.load_file("screens/note_editor_screen.kv")
        Builder.load_file("widgets/note_card.kv")

        sm = AppScreenManager()
        sm.app_ref = self

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(NotesListScreen(name="notes_list"))
        sm.add_widget(NoteEditorScreen(name="note_editor"))

        sm.current = "login"
        return sm


if __name__ == "__main__":
    NotesApp().run()
