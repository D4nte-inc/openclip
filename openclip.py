import storage
from gui import OpenClipWindow

def main():
    path = storage.default_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    history = storage.load_history(path)
    OpenClipWindow(history).mainloop()



if __name__ == "__main__":
    main()