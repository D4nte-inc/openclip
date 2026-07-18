import customtkinter as ctk
import tkinter as tk

from history import ClipboardHistory


class OpenClipWindow(ctk.CTk):
    def __init__(self, history: ClipboardHistory):
        super().__init__()
        self._history = history
        self.title("OpenClip")
        self.geometry("400x500")

        self._list_area = ctk.CTkScrollableFrame(self)
        self._list_area.pack(fill="both", expand=True, padx=10, pady=10)

        self._monitor_clipboard()


    def _monitor_clipboard(self):
        try:
            clipboard_data = self.clipboard_get()
        except tk.TclError:  # empty clipboard or non-text content
            clipboard_data = None
        self._history.add(clipboard_data)
        self._refresh_history()
        self.after(1000, self._monitor_clipboard)


    def _refresh_history(self):
        for child in self._list_area.winfo_children():
            child.destroy()

        for text, count in self._history.grouped().items():
            row = ctk.CTkFrame(self._list_area)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=text).pack(side="left", padx=5)
            if count > 1:
                ctk.CTkLabel(row, text=f"{count}").pack(side="right", padx=5)