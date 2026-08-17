from kivy.uix.screenmanager import Screen


class NoteEditorScreen(Screen):
    current_note_id = None

    def load_note(self, note_id: str):
        self.current_note_id = note_id
        app = self.manager.app_ref
        note = app.storage.get_by_id(note_id)
        self.ids.content_input.text = note.content if note else ""

    def save_and_back(self):
        app = self.manager.app_ref
        note = app.storage.get_by_id(self.current_note_id)
        if note:
            note.content = self.ids.content_input.text
            note.touch()
            app.storage.save(note)
        self.manager.current = "notes_list"

    def delete_note(self):
        app = self.manager.app_ref
        app.storage.soft_delete(self.current_note_id)
        self.manager.current = "notes_list"
