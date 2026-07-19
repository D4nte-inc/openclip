"""
    Author: d4nte
    Date: 19/07/2026

    Title: OpenClip - JSON persistence layer.
    Saves and loads the clipboard history to/from a JSON file and
    handles the export of the user data to a custom path.

    The JSON file has two sections:
        clipboard_header -> openclip version, save date, entries count
        clipboard_body   -> one entry per item: progressive number,
                            text, timestamp and favorite flag
"""
import json

from datetime import datetime
from pathlib import Path
from history import ClipboardHistory, ClipboardItem

def default_history_path() -> Path:
    """
    Function: default_history_path
    Builds the path of the JSON file where the history is saved.
    Formal parameters:
        None
    Return value:
        Path -> <current working dir>/clipboard-data/clipboard_data.json
    """
    return Path.cwd() / "clipboard-data" / "clipboard_data.json"


def save_history(history: ClipboardHistory):
    """
    Function: save_history
    Writes the whole history to the default JSON file, overwriting
    the previous content.
    Formal parameters:
        ClipboardHistory history -> the history to persist
    """
    clipboard_history = history.get_items()
    json_file_path = default_history_path()
    # Progressive number assigned to each entry of the body
    entry_number = 0
    # Skeleton of the JSON document: header filled now, body filled below
    json_data = {
        "clipboard_header": {
            "openclip_version": 0.4,
            "date_added": f"{datetime.now()}",
            "entries_number": len(clipboard_history)
        },
        "clipboard_body": []
    }
    for clipboard_entry in clipboard_history:
        entry_number += 1
        json_data["clipboard_body"].append({
            "entry_number": entry_number,
            "clipboard_data": clipboard_entry.text,
            "timestamp": f"{clipboard_entry.copied_at}",
            "favorite": clipboard_entry.is_favorite
        })

    with open(json_file_path, "w") as f:
        json.dump(json_data, f, indent=4)


def clipboard_history_from_json(json_file: dict[str, dict | list]) -> ClipboardHistory:
    """
    Function: clipboard_history_from_json
    Rebuilds a ClipboardHistory object from an already parsed JSON
    document. Entries with empty text are skipped.
    Formal parameters:
        dict[str, dict | list] json_file -> the parsed JSON document,
            with the clipboard_header / clipboard_body structure
    Return value:
        ClipboardHistory -> the history holding one ClipboardItem per
            valid entry of the body
    """
    clipboard_items: list[ClipboardItem] = []
    for json_entry in json_file["clipboard_body"]:
        if not json_entry["clipboard_data"]:
            continue
        clipboard_item = ClipboardItem(json_entry["clipboard_data"],
                                       datetime.fromisoformat(json_entry["timestamp"]),
                                       bool(json_entry["favorite"]))
        clipboard_items.append(clipboard_item)

    return ClipboardHistory(clipboard_items)


def load_history(path: Path | None = None) -> ClipboardHistory:
    """
    Function: load_history
    Reads the history from a JSON file. The load is safe: if the file
    does not exist or holds broken JSON, an empty history is returned
    instead of crashing.
    Formal parameters:
        Path | None path -> the file to read; None uses the default path
    Return value:
        ClipboardHistory -> the loaded history, empty on error
    """
    path = path or default_history_path()
    try:
        with open(path, "r") as f:
            file_content = json.load(f)
            return clipboard_history_from_json(file_content)
    except (FileNotFoundError, json.JSONDecodeError):
        return ClipboardHistory([])


def export(export_path: str) -> bool:
    """
    Function: export
    Copies the current history file to a path chosen by the user,
    so the data can be backed up or moved to another machine.
    Formal parameters:
        str export_path -> destination file chosen by the user
    Return value:
        bool -> True if everything goes well, False otherwise
            (missing or corrupted history file)
    """
    json_file_path = default_history_path()
    try:
        with open(json_file_path, "r") as original_json:
            with open(export_path, "a") as new_json:
                json.dump(json.load(original_json), new_json, indent=4)
                return True
    except (FileNotFoundError, json.JSONDecodeError):
        return False
