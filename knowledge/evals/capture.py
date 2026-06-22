from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SESSIONS_DIR = Path(__file__).parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def log_event(event: dict[str, Any], path: Path | None = None) -> Path:
    p = path or (SESSIONS_DIR / f"session_{int(time.time())}.jsonl")
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": _now(), **event}) + "\n")
    return p

def capture(command: list[str], *, output: Path | None = None) -> Path:
    p = output or (SESSIONS_DIR / f"capture_{int(time.time())}.jsonl")
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in proc.stdout or []:
        log_event({"type": "stdout", "line": line.rstrip()}, p)
    proc.wait()
    log_event({"type": "exit", "code": proc.returncode}, p)
    return p

try:
    import boto3
    def _dynamo_writer(table_name: str = "praxis-sessions"):
        client = boto3.client("dynamodb")
        def write(item: dict[str, Any]) -> None:
            client.put_item(TableName=table_name, Item={k: {"S": str(v)} for k, v in item.items()})
        return write
except ImportError:
    def _dynamo_writer(table_name: str = "praxis-sessions"):
        def write(item: dict[str, Any]) -> None:
            pass
        return write
