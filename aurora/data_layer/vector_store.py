import json
import os
from pathlib import Path
from typing import Any, Dict, List

class LocalIncidentStore:
    def __init__(self):
        self.data_dir = Path("data/classifications")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_incident(self, incident_id: str, data: Dict[str, Any]):
        """Saves diagnosed failure incident as JSON to filesystem."""
        # Sanitize data prior to saving
        clean_data = dict(data)
        if "topic" in clean_data:
            clean_data.pop("topic")
            
        file_path = self.data_dir / f"{incident_id}.json"
        try:
            file_path.write_text(json.dumps(clean_data, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"Failed to write classification file {file_path}: {e}")

    def load_all_incidents(self) -> List[Dict[str, Any]]:
        """Loads and parses all saved JSON incident logs from the classifications directory."""
        records = []
        for file in self.data_dir.glob("*.json"):
            try:
                with open(file, encoding="utf-8") as f:
                    obj = json.load(f)
                    obj["incident_id"] = obj.get("incident_id", file.stem)
                    obj["timestamp"] = obj.get("timestamp", file.stat().st_mtime)
                    records.append(obj)
            except Exception as e:
                print(f"Failed loading index file {file}: {e}")
        return records

    def clear_all(self):
        """Clears index database."""
        for file in self.data_dir.glob("*.json"):
            try:
                os.remove(file)
            except Exception:
                pass
