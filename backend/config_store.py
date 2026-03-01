from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LISTTYPE_BLOCK = "blocklist"
LISTTYPE_ALLOW = "allowlist"

BLOCKMODE_STRICT = "strict"
BLOCKMODE_WARN = "warn"


class ConfigStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def default_db(self) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
        return {
            LISTTYPE_BLOCK: {BLOCKMODE_STRICT: {}, BLOCKMODE_WARN: {}},
            LISTTYPE_ALLOW: {BLOCKMODE_STRICT: {}, BLOCKMODE_WARN: {}},
        }

    def ensure_db_file(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            with self.db_path.open("w", encoding="utf-8") as f:
                json.dump(self.default_db(), f, indent=2)

    def load_db(self) -> dict:
        self.ensure_db_file()
        try:
            with self.db_path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
        except json.JSONDecodeError:
            loaded = {}

        db = self.default_db()
        if not isinstance(loaded, dict):
            return db

        for list_type in (LISTTYPE_BLOCK, LISTTYPE_ALLOW):
            source = loaded.get(list_type, {})
            if not isinstance(source, dict):
                continue
            for block_mode in (BLOCKMODE_STRICT, BLOCKMODE_WARN):
                bucket = source.get(block_mode, {})
                if isinstance(bucket, dict):
                    db[list_type][block_mode] = bucket
        return db

    def save_db(self, db: dict) -> None:
        self.ensure_db_file()
        with self.db_path.open("w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)

    def upsert_record(self, name: str, list_type: str, block_mode: str, record: dict[str, Any]) -> None:
        db = self.load_db()
        db[list_type][block_mode][name] = record
        self.save_db(db)

    def delete_record(self, name: str, list_type: str, block_mode: str) -> bool:
        db = self.load_db()

        bucket = db.get(list_type, {}).get(block_mode, {})
        if not isinstance(bucket, dict) or name not in bucket:
            return False

        del bucket[name]
        self.save_db(db)
        return True

    def iter_records(self):
        db = self.load_db()
        for list_type in (LISTTYPE_BLOCK, LISTTYPE_ALLOW):
            for block_mode in (BLOCKMODE_STRICT, BLOCKMODE_WARN):
                bucket = db.get(list_type, {}).get(block_mode, {})
                if not isinstance(bucket, dict):
                    continue
                for _, record in bucket.items():
                    if isinstance(record, dict):
                        yield list_type, block_mode, record

    def configs_as_list(self) -> list[dict[str, Any]]:
        configs_list: list[dict[str, Any]] = []
        for list_type, block_mode, record in self.iter_records():
            configs_list.append(
                {
                    "name": record.get("name", ""),
                    "desc": record.get("initial_definition", ""),
                    "blockMode": record.get("blockMode", block_mode),
                    "listType": record.get("listType", list_type),
                    "positiveTags": record.get("positive_definitions", []),
                    "negativeTags": record.get("negative_definitions", []),
                }
            )
        return configs_list
