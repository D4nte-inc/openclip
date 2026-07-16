import customtkinter as ctk
import tkinter as tk

from history import ClipboardHistory

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

class OpenClipWindow(ctk.CTk):
    CLIPBOARD_MONITOR_CALL = 1000

    def __init__(self, history: ClipboardHistory):
        super().__init__()
        self._history = history
        self._last_clip = None
        self.title("OpenClip")
        self.geometry("400x500")


        self._list_area = ctk.CTkScrollableFrame(self)
        self._list_area.pack(fill="both", expand=True, padx=10, pady=10)

        self._monitor_clipboard()


    def _refresh_history(self):
        for child in self._list_area.winfo_children():
            child.destroy()

        items = self._history.grouped().items()

        if not items:
            ctk.CTkLabel(
                master=self._list_area, text="no elements on clipboard",
                text_color="gray"
            ).pack(pady=20)
            return

        for text, count in items: # history.grouped().items()
            row = ctk.CTkFrame(self._list_area)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                master=row, text=text,
                anchor="w",
                justify="left"
            ).grid(row=0, column=0, sticky="ew", padx=8, pady=6)

            if count > 1:
                ctk.CTkLabel(
                    master=row, text=str(count),
                    width=26,
                    corner_radius=12,
                    fg_color=("gray75", "gray30"),
                ).grid(row=0, column=1, sticky="e", padx=8)


    def _monitor_clipboard(self):
        try:
            clipboard_data = self.clipboard_get()
        except tk.TclError:  # empty clipboard or non-text content
            clipboard_data = None

        if clipboard_data and clipboard_data != self._last_clip:
            if self._history.get_items() and self._history.get_items()[len(self._history.get_items()) - 1] != clipboard_data:
                self._refresh_history()
            self._history.add(clipboard_data)

        self.after(self.CLIPBOARD_MONITOR_CALL, self._monitor_clipboard)

