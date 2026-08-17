from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty


class NoteCard(BoxLayout):
    """
    Карточка одной заметки в списке.
    Разметка — в widgets/note_card.kv (Kivy подхватывает
    файл автоматически по имени класса).
    """

    note_id = StringProperty("")
    preview_text = StringProperty("")
    on_card_press = ObjectProperty(None)

    def handle_press(self):
        if self.on_card_press:
            self.on_card_press(self.note_id)
