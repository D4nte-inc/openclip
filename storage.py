from datetime import datetime

from history import ClipboardHistory, ClipboardItem
import json
import os


def save_history(history: ClipboardHistory):
    clipboard_history = history.get_items()
    json_file_path = f"{os.getcwd()}/clipboard-data/clipboard_data.json"
    entry_number = 0
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

    with open(json_file_path, "a") as f:
        json.dump(json_data, f, indent=4)


def clipboard_history_from_json(json_file: dict[str, dict | list]) -> ClipboardHistory:
    clipboard_items: list[ClipboardItem] = []
    for json_entry in json_file["clipboard_body"]:
        clipboard_item = ClipboardItem(json_entry["clipboard_data"],
                                       json_entry["timestamp"],
                                       json_entry["favorite"])
        clipboard_items.append(clipboard_item)

    return ClipboardHistory(clipboard_items)


def load_history() -> ClipboardHistory:
    json_file_path = f"{os.getcwd()}/clipboard-data/clipboard_data.json"
    try:
        with open(json_file_path, "r") as f:
            file_content = json.load(f)
            return clipboard_history_from_json(file_content)
    except (FileNotFoundError, json.JSONDecodeError):
        return ClipboardHistory([])
