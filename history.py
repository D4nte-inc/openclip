from dataclasses import dataclass
from datetime import datetime

@dataclass
class ClipboardItem:
    text: str
    copied_at: datetime
    is_favorite: bool = False


class ClipboardHistory:
    def __init__(self, clipboard_items: list[ClipboardItem] | None = None):
        self._clipboard_items = clipboard_items if clipboard_items is not None else []


    def add(self, text: str):
        if len(self._clipboard_items) == 0 or not self._clipboard_items[len(self._clipboard_items) - 1].text == text:
            self._clipboard_items.append(ClipboardItem(text, datetime.now()))


    def search(self, query: str) -> list[ClipboardItem]:
        matching_items: list[ClipboardItem] = []
        for clipboard_item in self._clipboard_items:
            if query.lower() in clipboard_item.text.lower():
                matching_items.append(clipboard_item)

        if not matching_items:
            return self._clipboard_items
        return matching_items


    def get_items_since(self, date_query: datetime) -> list[ClipboardItem]:
        matching_items: list[ClipboardItem] = []
        for clipboard_item in self._clipboard_items:
            if clipboard_item.copied_at >= date_query:
                matching_items.append(clipboard_item)

        matching_items.sort(key=lambda item: item.copied_at)
        return matching_items


    def grouped(self) -> dict[str, int]:
        grouped_clipboard_texts_with_count: dict[str, int] = {}
        for clipboard_item in self._clipboard_items:
            if clipboard_item.text not in grouped_clipboard_texts_with_count:
                grouped_clipboard_texts_with_count[clipboard_item.text] = 1
            else:
                grouped_clipboard_texts_with_count[clipboard_item.text] = grouped_clipboard_texts_with_count[clipboard_item.text] + 1

        return grouped_clipboard_texts_with_count


    def toggle_favorite(self, text: str):
        for clipboard_items in self._clipboard_items:
            if clipboard_items.text == text:
                clipboard_items.is_favorite = not clipboard_items.is_favorite


    def favorites(self) -> list[ClipboardItem]:
        favorite_items: list[ClipboardItem] = []
        for clipboard_item in self._clipboard_items:
            if clipboard_item.is_favorite:
                favorite_items.append(clipboard_item)

        return favorite_items

    def get_items(self) -> list[ClipboardItem]:
        return self._clipboard_items