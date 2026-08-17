from kivy.uix.screenmanager import Screen

from core.models import Note
from widgets.note_card import NoteCard


class NotesListScreen(Screen):
    def on_pre_enter(self):
        self.refresh_list()

    def refresh_list(self):
        app = self.manager.app_ref
        notes = app.storage.get_all()

        container = self.ids.notes_container
        container.clear_widgets()

        for note in notes:
            preview = note.content[:60] or "(пустая заметка)"
            card = NoteCard(
                note_id=note.id,
                preview_text=preview,
                on_card_press=self.open_note,
            )
            container.add_widget(card)

    def open_note(self, note_id: str):
        editor = self.manager.get_screen("note_editor")
        editor.load_note(note_id)
        self.manager.current = "note_editor"

    def create_new_note(self):
        app = self.manager.app_ref
        note = Note(content="")
        app.storage.save(note)

        editor = self.manager.get_screen("note_editor")
        editor.load_note(note.id)
        self.manager.current = "note_editor"

    def sync_now(self):
        app = self.manager.app_ref
        success = app.sync_manager.sync()
        self.ids.sync_status.text = "Синхронизировано" if success else "Нет сети — сохранено локально"
        self.refresh_list()
