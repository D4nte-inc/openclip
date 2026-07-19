from typing import is_typeddict

import storage
import customtkinter as ctk
import tkinter.filedialog
import tkinter as tk

from tkinter import ttk
from pathlib import Path

from history import ClipboardHistory, ClipboardItem

class OpenClipWindow(ctk.CTk):
    def __init__(self, history: ClipboardHistory):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        ctk.ThemeManager.theme["CTkFont"]["family"] = "Noto Sans"
        super().__init__()
        self._history = history
        self.title("OpenClip")
        self.geometry("400x500")
        self._style_tk_dialogs()


        self._search_box = ctk.CTkEntry(self, placeholder_text="Search…")
        self._search_box.pack(fill="x", expand=True, padx=10)
        self._search_box.bind("<KeyRelease>", self._search)
        self._search_box.pack(fill="x", expand=True, padx=10)

        self._import_export_area = ctk.CTkFrame(self, fg_color="transparent")
        self._import_export_area.pack(fill="x", padx=10, pady=10)

        self._export_button = ctk.CTkButton(self._import_export_area,
                                            text="Export", command=self.export_history)
        self._export_button.pack(side="right", fill="x", expand=True, padx=(0, 5))

        self._import_button = ctk.CTkButton(self._import_export_area,
                                            text="Import", command=self.import_history)
        self._import_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self._clear_all_button = ctk.CTkButton(self, text="Clear all", command=self._clear_history)
        self._clear_all_button.pack(fill="x", padx=10, pady=(0, 10))

        self._filters_area = ctk.CTkFrame(self, fg_color="transparent")
        self._filters_area.pack(fill="x", padx=10, pady=10)

        self._optionmenu = ctk.CTkOptionMenu(self._filters_area,
                                             values=["All", "Last hour", "Last 24h", "Last week", "Last Month"],
                                             command=self._filter_by_date)
        self._optionmenu.pack(side="left")

        self._only_favorites_button = ctk.CTkSwitch(self._filters_area, text="View favorites", command=self.show_favorites,
                                                    onvalue=True, offvalue=False)
        self._only_favorites_button.pack(side="right")

        self._list_area = ctk.CTkScrollableFrame(self)
        self._list_area.pack(fill="both", expand=True, padx=10, pady=10)

        self._counter_label = ctk.CTkLabel(self, text="")
        self._counter_label.pack(pady=(0, 5))

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
        self.after(1000, self._monitor_clipboard)


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
                hover=True,
                command=lambda t=clipboard_item.text: self.toggle_favorite(t),
            ).pack(side="right", padx=5)

            ctk.CTkButton(
                row, text="⧉", width=32,
                hover=True,
                command=lambda t=clipboard_item.text: self._copy_to_clipboard(t),
            ).pack(side="right", padx=5)

            ctk.CTkButton(
                row,
                text="🗑", width=32,
            command = lambda t=clipboard_item.text: self._delete_item(t),
            ).pack(side="right", padx=5)

            ctk.CTkLabel(row, text=f"{clipboard_item.text} - {clipboard_item.copied_at.strftime("%d/%m/%Y %H:%M:%S")}").pack(side="left", padx=5)
            if count > 1:
                ctk.CTkLabel(row, text=f"{count}").pack(side="right", padx=5)

        self._counter_label.configure(text=f"{len(self._history.get_items())} items")


    def override_list_area(self, query_result: list[ClipboardItem]):
        self.clean_list_area()

        for clipboard_item in query_result:
            row = ctk.CTkFrame(self._list_area)
            row.pack(fill="x", pady=2)
            star = "⭐" if clipboard_item.is_favorite else "☆"
            ctk.CTkButton(
                row, text=star, width=32,
                command=lambda t=clipboard_item.text: self.toggle_favorite(t),
            ).pack(side="right", padx=5)

            ctk.CTkButton(
                row, text="⧉", width=32,
                hover=True,
                command=lambda t=clipboard_item.text: self._copy_to_clipboard(t),
            ).pack(side="right", padx=5)

            ctk.CTkButton(
                row,
                text="🗑", width=32,
                command=lambda t=clipboard_item.text: self._delete_item(t),
            ).pack(side="right", padx=5)

            ctk.CTkLabel(row, text=clipboard_item.text).pack(side="left", padx=5)

    def _search(self, *_):
        query = self._query.get()
        if not query:
            self._refresh_history()
            return
        query_result = self._history.search(query)
        self.override_list_area(query_result)


    def _filter_by_date(self, choice):
        query_result = self._history.get_items_since(choice)
        self.override_list_area(query_result)


    def toggle_favorite(self, text: str):
        self._history.toggle_favorite(text)
        self._only_favorites_button.deselect()
        self._refresh_history()


    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)


    def show_favorites(self):
        if self._only_favorites_button.get():
            result = self._history.favorites()
            self.override_list_area(result)
        else:
            self._refresh_history()


    def export_history(self):
        path = tk.filedialog.asksaveasfilename(
            title="Export history",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")])
        if path:
            storage.export(path)


    def import_history(self):
        path = tk.filedialog.askopenfilename(
            title="Import history",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if path:
            self._history = storage.load_history(Path(path))
            self._refresh_history()


    def _clear_history(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Clear all")
        dialog.geometry("400x120")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog,
                     text="Clear all clipboard history?\n"
                          "Be sure to save a copy first, this operations cannot be undone").pack(pady=15)

        def confirm():
            self._history.clear()
            self._refresh_history()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Yes", command=confirm).pack(side="left", expand=True, padx=20, pady=10)
        ctk.CTkButton(dialog, text="Cancel", command=dialog.destroy).pack(side="right", expand=True, padx=20, pady=10)

    def _delete_item(self, text: str):
        self._history.remove(text)
        self._refresh_history()


    def _style_tk_dialogs(self):
        # Dark defaults for the built-in Tk file dialogs (CTk colors).
        style = ttk.Style()
        style.theme_use( "clam")  # clam honors color overrides; default/alt ignore them
        style.configure(".", background="#2b2b2b", foreground="#ffffff",
                        fieldbackground="#343638",
                        selectbackground="#1f6aa5", selectforeground="#ffffff")
