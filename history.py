"""
    Author: d4nte
    Date: 19/07/2026

    Title: OpenClip - clipboard history model.
    Defines the ClipboardItem entity and the ClipboardHistory class
    that stores, searches, filters, groups and manages the items
    copied to the clipboard over time.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import storage


@dataclass(unsafe_hash=True)
class ClipboardItem:
    """
    Class ClipboardItem
    The class models the CLIPBOARD ITEM entity:
    a single piece of text copied to the clipboard.
    It has three attributes:
        text: str -> the copied text
        copied_at: datetime -> the moment the text was copied
        is_favorite: bool -> True if the user marked the item as favorite

    Only the text attribute takes part in equality and hashing, so two
    items holding the same text are considered the same entry: this is
    what allows duplicates to be grouped and counted.
    """
    text: str
    copied_at: datetime = field(compare=False)
    is_favorite: bool = field(default=False, compare=False)


class ClipboardHistory:
    """
    Class ClipboardHistory
    The class models the CLIPBOARD HISTORY entity:
    the ordered collection of every item copied by the user.
    It has one attribute:
        _clipboard_items: list[ClipboardItem] -> the stored items,
        oldest first

    Every operation that changes the history (add, toggle_favorite,
    clear_all, remove) also saves it to disk through the storage module.
    """

    def __init__(self, clipboard_items: list[ClipboardItem] | None = None):
        """
        Constructor of the object.
        Formal parameters:
            list[ClipboardItem] | None clipboard_items -> initial items
                (e.g. loaded from disk); None starts an empty history
        """
        self._clipboard_items = clipboard_items if clipboard_items is not None else []


    def add(self, text: str) -> bool:
        """
        Method: add
        Appends the given text as a new item with the current time and
        saves the history to disk. If the text is empty or equal to the
        last stored item, nothing is added: the clipboard still holds
        the old copy, so it is not a new copy.
        Formal parameters:
            str text -> the clipboard content to store
        Return value:
            bool -> True if a new item was appended, False otherwise
        """
        if not text:
            return False
        if len(self._clipboard_items) == 0 or not self._clipboard_items[len(self._clipboard_items) - 1].text == text:
            self._clipboard_items.append(ClipboardItem(text, datetime.now()))
            storage.save_history(self)
            return True
        return False


    def search(self, query: str) -> list[ClipboardItem]:
        """
        Method: search
        Looks for the query inside the text of every item,
        ignoring upper/lower case and skipping duplicates.
        Formal parameters:
            str query -> the text to search for
        Return value:
            list[ClipboardItem] -> the matching items; if nothing
                matches, the whole history is returned
        """
        matching_items: list[ClipboardItem] = []
        for clipboard_item in self._clipboard_items:
            if query.lower() in clipboard_item.text.lower() and clipboard_item not in matching_items:
                matching_items.append(clipboard_item)

        if not matching_items:
            return self._clipboard_items
        return matching_items


    def get_items_since(self, since: str) -> list[ClipboardItem]:
        """
        Method: get_items_since
        Filters the history by time period, keeping only the items
        copied inside the chosen period.
        Formal parameters:
            str since -> one of the filter labels shown in the GUI:
                "All", "Last hour", "Last 24h", "Last week", "Last Month"
        Return value:
            list[ClipboardItem] -> the matching items sorted by copy
                date, oldest first
        """
        matching_items: list[ClipboardItem] = []
        # Lower bound of the period: items copied before this moment are excluded
        date_query: datetime = datetime.min

        match since:
            case "All":
                date_query = datetime.min
            case "Last hour":
                date_query = datetime.now() - timedelta(hours=1)
            case "Last 24h":
                date_query = datetime.now() - timedelta(days=1)
            case "Last week":
                date_query = datetime.now() - timedelta(weeks=1)
            case "Last Month":
                date_query = datetime.now() - timedelta(days=30)

        for clipboard_item in self._clipboard_items:
            if clipboard_item.copied_at >= date_query:
                matching_items.append(clipboard_item)

        matching_items.sort(key=lambda item: item.copied_at)
        return matching_items


    def grouped(self) -> dict[ClipboardItem, int]:
        """
        Method: grouped
        Groups the items by text and counts how many times each text
        was copied. Items are visited newest first, so the dictionary
        keeps the most recent copies at the top of the list.
        Formal parameters:
            None
        Return value:
            dict[ClipboardItem, int] -> one entry per distinct text
                with its copy count
        """
        grouped_clipboard_texts_with_count: dict[ClipboardItem, int] = {}
        for clipboard_item in reversed(self._clipboard_items):
            if clipboard_item not in grouped_clipboard_texts_with_count:
                grouped_clipboard_texts_with_count[clipboard_item] = 1
            else:
                grouped_clipboard_texts_with_count[clipboard_item] = grouped_clipboard_texts_with_count[clipboard_item] + 1

        return grouped_clipboard_texts_with_count


    def toggle_favorite(self, text: str):
        """
        Method: toggle_favorite
        Flips the is_favorite flag on every item holding the given
        text, then saves the history to disk.
        Formal parameters:
            str text -> the text of the item(s) to mark or unmark
        """
        for clipboard_items in self._clipboard_items:
            if clipboard_items.text == text:
                clipboard_items.is_favorite = not clipboard_items.is_favorite
        storage.save_history(self)


    def favorites(self) -> list[ClipboardItem]:
        """
        Method: favorites
        Return value:
            list[ClipboardItem] -> only the items marked as favorite
        """
        favorite_items: list[ClipboardItem] = []
        for clipboard_item in self._clipboard_items:
            if clipboard_item.is_favorite:
                favorite_items.append(clipboard_item)

        return favorite_items


    def get_items(self) -> list[ClipboardItem]:
        """
        Getter of the attribute _clipboard_items
        """
        return self._clipboard_items


    def clear_all(self):
        """
        Method: clear_all
        Removes every item from the history and saves the now
        empty history to disk.
        """
        self._clipboard_items.clear()
        storage.save_history(self)


    def remove(self, text: str):
        """
        Method: remove
        Deletes every item holding the given text, then saves the
        history to disk.
        Formal parameters:
            str text -> the text of the item(s) to delete
        """
        clipboard_items = []
        for clipboard_item in self._clipboard_items:
            if clipboard_item.text != text:
                clipboard_items.append(clipboard_item)
        self._clipboard_items = clipboard_items
        storage.save_history(self)
