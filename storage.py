from datetime import datetime

from history import ClipboardHistory, ClipboardItem
import json
import os

def save_history(history: ClipboardHistory):
    clipboard_history = history.get_items()
    json_file_path = f"{os.getcwd()}/clipboard-data/clipboard_data.json"
    entry_number = 0
    json_data_header = {
        "clipboard_header": {
            "openclip_version": 0.4,
            "date_added": f"{datetime.now()}",
            "entries_number": len(clipboard_history)
        },
        "clipboard_body": []
    }
    for clipboard_entry in clipboard_history:
        entry_number += 1
        json_data_header["clipboard_body"].append({
            f"entry{entry_number}": {
                "clipboard_data": clipboard_entry.text,
                "timestamp": f"{clipboard_entry.copied_at}",
                "favorite": clipboard_entry.is_favorite
            }
        })

    with open(json_file_path, "a") as f:
        json.dump(json_data_header, f, indent=4)

def load_history():
    json_file_path = f"{os.getcwd()}/clipboard-data/clipboard_data.json"
    file_content = {}
    with open(json_file_path, "r") as f:
        file_content = json.load(f)

    return file_content



