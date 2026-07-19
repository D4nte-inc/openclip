import tkinter.filedialog
from pathlib import Path

import customtkinter as ctk
import tkinter as tk
import storage

from history import ClipboardHistory, ClipboardItem


class OpenClipWindow(ctk.CTk):
    def __init__(self, history: ClipboardHistory):
        super().__init__()
        self._history = history
        self.title("OpenClip")
        self.geometry("400x500")

        self._query = ctk.StringVar()
        self._query.trace_add("write", self._search)
        self._search_box = ctk.CTkEntry(self, textvariable=self._query)
        self._search_box.pack(fill="x", expand=True, padx=10)

        self._export_button = ctk.CTkButton(self, text="Export", command=self.export_history)
        self._export_button.pack(fill="x", expand=True, padx=10, pady=10)

        self._import_button = ctk.CTkButton(self, text="Import", command=self.import_history)
        self._import_button.pack(fill="x", expand=True, padx=10, pady=10)

        self._optionmenu = ctk.CTkOptionMenu(self, values=["All", "Last hour", "Last 24h", "Last week", "Last Month"],
                                             command=self._filter_by_date)
        self._optionmenu.pack(fill="x", expand=True, padx=10, pady=10)

        self._only_favorites_button = ctk.CTkSwitch(self, text="View favorites", command=self.show_favorites,
                                                    onvalue=True, offvalue=False)
        self._only_favorites_button.pack(fill="x", expand=True, padx=10, pady=10)

        self._list_area = ctk.CTkScrollableFrame(self)
        self._list_area.pack(fill="both", expand=True, padx=10, pady=10)

        self._refresh_history()
        self._monitor_clipboard()


    def _monitor_clipboard(self):
        try:
            clipboard_data = self.clipboard_get()
        except tk.TclError:  # empty clipboard or non-text content
            clipboard_data = None
        item_added = self._history.add(clipboard_data)
        if item_added:
            self._refresh_history()
        self.after(500, self._monitor_clipboard)


    def clean_list_area(self):
        for child in self._list_area.winfo_children():
            child.destroy()


    def _refresh_history(self):
        self.clean_list_area()

        for clipboard_item, count in self._history.grouped().items():
            row = ctk.CTkFrame(self._list_area)
            row.pack(fill="x", pady=2)
            star = "⭐" if clipboard_item.is_favorite else "☆"
            ctk.CTkButton(
                row, text=star, width=32,
                command=lambda t=clipboard_item.text: self.toggle_favorite(t),
            ).pack(side="right", padx=5)

            ctk.CTkLabel(row, text=f"{clipboard_item.text} - {clipboard_item.copied_at.strftime("%d/%m/%Y %H:%M:%S")}").pack(side="left", padx=5)
            if count > 1:
                ctk.CTkLabel(row, text=f"{count}").pack(side="right", padx=5)


    def override_list_area(self, query_result: list[ClipboardItem]):
        self.clean_list_area()

        for clipboard_item in query_result:
            row = ctk.CTkFrame(self._list_area)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=clipboard_item.text).pack(side="left", padx=5)


    def _search(self, *_):
        query_result = self._history.search(self._query.get())
        self.override_list_area(query_result)


    def _filter_by_date(self, choice):
        query_result = self._history.get_items_since(choice)
        self.override_list_area(query_result)


    def toggle_favorite(self, text: str):
        self._history.toggle_favorite(text)
        self._refresh_history()

    def show_favorites(self):
        if self._only_favorites_button.get():
            result = self._history.favorites()
            self.override_list_area(result)
        else:
            self._refresh_history()


    def export_history(self):
        path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")])
        if path:
            storage.export(path)

    def import_history(self):
        path = tk.filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if path:
            self._history = storage.load_history(Path(path))
            self._refresh_history()
