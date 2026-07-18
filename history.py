from dataclasses import dataclass
from datetime import datetime

@dataclass(unsafe_hash=True)
class ClipboardItem:
    text: str
    copied_at: datetime
    is_favorite: bool = False


class ClipboardHistory:
    def __init__(self, clipboard_items: list[ClipboardItem] | None = None):
        self._clipboard_items = clipboard_items if clipboard_items is not None else []


    def add(self, text: str) -> bool:
        if len(self._clipboard_items) == 0 or not self._clipboard_items[len(self._clipboard_items) - 1].text == text:
            self._clipboard_items.append(ClipboardItem(text, datetime.now()))
            return True
        return False


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


    def grouped(self) -> dict[ClipboardItem, int]:
        grouped_clipboards_with_count: dict[ClipboardItem, int] = {}
        for clipboard_item in self._clipboard_items:
            if clipboard_item not in grouped_clipboards_with_count:
                grouped_clipboards_with_count[clipboard_item] = 1
            else:
                grouped_clipboards_with_count[clipboard_item] = grouped_clipboards_with_count[clipboard_item] + 1

        return grouped_clipboards_with_count


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