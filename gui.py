"""
    Author: d4nte
    Date: 19/07/2026

    Title: OpenClip - graphical user interface.
    Defines the main window of the application: search box,
    import/export buttons, clear-all button, date filter, favorites
    switch and the scrollable list of copied items. The window also
    polls the system clipboard once per second to catch new copies.
"""
from typing import is_typeddict

import storage
import customtkinter as ctk
import tkinter.filedialog
import tkinter as tk

from tkinter import ttk
from pathlib import Path

from history import ClipboardHistory, ClipboardItem

class OpenClipWindow(ctk.CTk):
    """
    Class OpenClipWindow
    The class models the MAIN WINDOW entity of OpenClip.
    It has one logical attribute:
        _history: ClipboardHistory -> the history shown and updated
            by the window
    plus the widgets that compose the layout (search box,
    import/export buttons, clear-all button, date filter, favorites
    switch, scrollable list area and items counter).
    """

    def __init__(self, history: ClipboardHistory):
        """
        Constructor of the object.
        Applies the dark theme, builds every widget of the window,
        shows the loaded history and starts the clipboard polling.
        Formal parameters:
            ClipboardHistory history -> the history to display,
                usually loaded from disk at startup
        """
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        ctk.ThemeManager.theme["CTkFont"]["family"] = "Noto Sans"
        super().__init__()
        self._history = history
        self.title("OpenClip")
        self.geometry("400x500")
        self._style_tk_dialogs()

        # Search bar: filters the list on every keystroke
        self._search_box = ctk.CTkEntry(self, placeholder_text="Search…")
        self._search_box.pack(fill="x", expand=True, padx=10)
        self._search_box.bind("<KeyRelease>", self._search)

        # Import/export area: backup and restore of the history file
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

        # Filters area: date filter dropdown and favorites-only switch
        self._filters_area = ctk.CTkFrame(self, fg_color="transparent")
        self._filters_area.pack(fill="x", padx=10, pady=10)

        self._optionmenu = ctk.CTkOptionMenu(self._filters_area,
                                             values=["All", "Last hour", "Last 24h", "Last week", "Last Month"],
                                             command=self._filter_by_date)
        self._optionmenu.pack(side="left")

        self._only_favorites_button = ctk.CTkSwitch(self._filters_area, text="View favorites", command=self.show_favorites,
                                                    onvalue=True, offvalue=False)
        self._only_favorites_button.pack(side="right")

        # List area: one row per history entry, filled by _refresh_history
        self._list_area = ctk.CTkScrollableFrame(self)
        self._list_area.pack(fill="both", expand=True, padx=10, pady=10)

        self._counter_label = ctk.CTkLabel(self, text="")
        self._counter_label.pack(pady=(0, 5))

        self._refresh_history()
        self._monitor_clipboard()


    def _monitor_clipboard(self):
        """
        Method: _monitor_clipboard
        Polls the system clipboard: reads its content, stores it in
        the history if it is a new copy, then reschedules itself
        after one second. Called once from the constructor, it keeps
        re-arming itself for the whole life of the window.
        """
        try:
            clipboard_data = self.clipboard_get()
        except tk.TclError:  # empty clipboard or non-text content
            clipboard_data = None
        item_added = self._history.add(clipboard_data)
        if item_added:
            self._refresh_history()
        self.after(1000, self._monitor_clipboard)


    def clean_list_area(self):
        """
        Method: clean_list_area
        Destroys every row currently shown in the list area,
        leaving it empty and ready to be refilled.
        """
        for child in self._list_area.winfo_children():
            child.destroy()


    def _row_button(self, parent, text, command):
        """
        Method: _row_button
        Builds one of the small flat buttons shown on a history row
        (favorite star, copy, delete), styled for the dark theme.
        Formal parameters:
            parent -> the row frame that will hold the button
            text -> the symbol shown on the button
            command -> the callback fired on click
        Return value:
            tk.Button -> the styled button, not yet packed
        """
        return tk.Button(
            parent, text=text, command=command,
            relief="flat", bd=0, highlightthickness=0,
            bg="#343638", fg="#ffffff",
            activebackground="#1f6aa5", activeforeground="#ffffff",
            cursor="hand2", padx=8, pady=2,
        )


    def _refresh_history(self):
        """
        Method: _refresh_history
        Redraws the whole list from the grouped history: one row per
        distinct text with its copy date, a duplicates counter when
        the text was copied more than once, and the star/copy/delete
        buttons. Also updates the total items counter at the bottom.
        """
        self.clean_list_area()

        for clipboard_item, count in self._history.grouped().items():
            row = tk.Frame(self._list_area)
            row.pack(fill="x", pady=2)
            star = "⭐" if clipboard_item.is_favorite else "☆"
            self._row_button(row, star,
                             lambda t=clipboard_item.text: self.toggle_favorite(t)).pack(side="right", padx=5)

            self._row_button(row, "⧉",
                             lambda t=clipboard_item.text: self._copy_to_clipboard(t)).pack(side="right", padx=5)

            self._row_button(row, "🗑",
                             lambda t=clipboard_item.text: self._delete_item(t)).pack(side="right", padx=5)

            tk.Label(row, text=f"{clipboard_item.text} - {clipboard_item.copied_at.strftime("%d/%m/%Y %H:%M:%S")}").pack(side="left", padx=5)
            if count > 1:
                tk.Label(row, text=f"{count}").pack(side="right", padx=5)

        self._counter_label.configure(text=f"{len(self._history.get_items())} items")


    def override_list_area(self, query_result: list[ClipboardItem]):
        """
        Method: override_list_area
        Replaces the list content with the given items instead of the
        full history. Used to show the result of a search, a date
        filter or the favorites view.
        Formal parameters:
            list[ClipboardItem] query_result -> the items to display
        """
        self.clean_list_area()

        for clipboard_item in query_result:
            row = tk.Frame(self._list_area)
            row.pack(fill="x", pady=2)
            star = "⭐" if clipboard_item.is_favorite else "☆"
            self._row_button(row, star,
                             lambda t=clipboard_item.text: self.toggle_favorite(t)).pack(side="right", padx=5)

            self._row_button(row, "⧉",
                             lambda t=clipboard_item.text: self._copy_to_clipboard(t)).pack(side="right", padx=5)

            self._row_button(row, "🗑",
                             lambda t=clipboard_item.text: self._delete_item(t)).pack(side="right", padx=5)

            tk.Label(row, text=clipboard_item.text).pack(side="left", padx=5)

    def _search(self, *_):
        """
        Method: _search
        Fired on every keystroke in the search box: shows the items
        matching the typed query, or the full history when the box
        is empty.
        """
        query = self._search_box.get()
        if not query:
            self._refresh_history()
            return
        query_result = self._history.search(query)
        self.override_list_area(query_result)


    def _filter_by_date(self, choice):
        """
        Method: _filter_by_date
        Fired by the date dropdown: shows only the items copied
        inside the chosen period.
        Formal parameters:
            choice -> the selected label ("All", "Last hour", ...)
        """
        query_result = self._history.get_items_since(choice)
        self.override_list_area(query_result)


    def toggle_favorite(self, text: str):
        """
        Method: toggle_favorite
        Fired by the star button of a row: marks/unmarks the item as
        favorite, resets the favorites-only switch and redraws the
        full list.
        Formal parameters:
            str text -> the text of the clicked item
        """
        self._history.toggle_favorite(text)
        self._only_favorites_button.deselect()
        self._refresh_history()


    def _copy_to_clipboard(self, text: str):
        """
        Method: _copy_to_clipboard
        Fired by the copy button of a row: puts the item text back
        into the system clipboard.
        Formal parameters:
            str text -> the text to copy
        """
        self.clipboard_clear()
        self.clipboard_append(text)


    def show_favorites(self):
        """
        Method: show_favorites
        Fired by the favorites switch: shows only the favorite items
        when the switch is on, the full history when it is off.
        """
        if self._only_favorites_button.get():
            result = self._history.favorites()
            self.override_list_area(result)
        else:
            self._refresh_history()


    def export_history(self):
        """
        Method: export_history
        Fired by the Export button: asks the user for a destination
        file and copies the history JSON there.
        """
        path = tk.filedialog.asksaveasfilename(
            title="Export history",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")])
        if path:
            storage.export(path)


    def import_history(self):
        """
        Method: import_history
        Fired by the Import button: asks the user for a previously
        exported JSON file, loads it as the current history and
        redraws the list.
        """
        path = tk.filedialog.askopenfilename(
            title="Import history",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if path:
            self._history = storage.load_history(Path(path))
            self._refresh_history()


    def _clear_history(self):
        """
        Method: _clear_history
        Fired by the Clear all button: opens a modal confirmation
        dialog; on confirm, empties the whole history and redraws
        the list. The operation cannot be undone.
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Clear all")
        dialog.geometry("400x120")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog,
                     text="Clear all clipboard history?\n"
                          "Be sure to save a copy first, this operations cannot be undone").pack(pady=15)

        def confirm():
            self._history.clear_all()
            self._refresh_history()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Yes", command=confirm).pack(side="left", expand=True, padx=20, pady=10)
        ctk.CTkButton(dialog, text="Cancel", command=dialog.destroy).pack(side="right", expand=True, padx=20, pady=10)

    def _delete_item(self, text: str):
        """
        Method: _delete_item
        Fired by the trash button of a row: removes the item from the
        history and redraws the list.
        Formal parameters:
            str text -> the text of the item to delete
        """
        self._history.remove(text)
        self._refresh_history()


    def _style_tk_dialogs(self):
        """
        Method: _style_tk_dialogs
        Applies the dark palette to the plain tk/ttk widgets (file
        dialogs and history rows) so they match the customtkinter
        theme of the rest of the window.
        """
        style = ttk.Style()
        style.theme_use( "clam")
        style.configure(".", background="#2b2b2b", foreground="#ffffff",
                        fieldbackground="#343638",
                        selectbackground="#1f6aa5", selectforeground="#ffffff")
        # Dark defaults for plain tk widgets (the history rows).
        self.option_add("*background", "#2b2b2b")
        self.option_add("*foreground", "#ffffff")
        self.option_add("*activeBackground", "#1f6aa5")
        self.option_add("*activeForeground", "#ffffff")
