from datetime import datetime
from pathlib import Path
import json
import re


def sanitize_filename(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    return stem or "unnamed_image"


def store_evidence(evidence: dict, base_dir="storage/analyses") -> str:
    folder = Path(base_dir) / sanitize_filename(evidence["file"]["name"])
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone()
    stamp = now.strftime("%Y%m%d_%H%M%S")
    path = folder / f"{stamp}.json"
    n = 1
    while path.exists():
        path = folder / f"{stamp}_{n:02d}.json"
        n += 1
    payload = dict(evidence)
    payload["analysis"] = {
        "timestamp": now.isoformat(),
        "engine": "AI Image Forensics",
        "version": "Layers 1-3",
        "evidence_file": str(path),
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return str(path)
