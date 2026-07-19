"""
    Author: d4nte
    Date: 19/07/2026

    Title: OpenClip - application entry point.
    OpenClip is an open source clipboard manager for GNU/Linux: it
    watches the system clipboard and lets the user search, filter,
    group and organize the copied items over time.
"""
import storage
from gui import OpenClipWindow

def main():
    """
    Function: main
    Creates the data folder if it does not exist yet, loads the
    history saved on disk and opens the OpenClip window.
    Formal parameters:
        None
    Return value:
        None
    """
    path = storage.default_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    history = storage.load_history(path)
    OpenClipWindow(history).mainloop()

"""
Main program
Starts the application. We run it only if this .py file is
launched as a program: if it were imported, the instructions
inside the if would not be executed.
"""
if __name__ == "__main__":
    main()
