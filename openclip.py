from gui import OpenClipWindow
from history import ClipboardHistory

def main():
    history = ClipboardHistory()
    window = OpenClipWindow(history)
    window.mainloop()

if __name__ == "__main__":
    main()