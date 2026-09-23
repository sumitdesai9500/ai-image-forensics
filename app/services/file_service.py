from pathlib import Path
import hashlib
import mimetypes

class FileService:
    def analyze(self, path: str) -> dict:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(path)
        data = p.read_bytes()
        if data.startswith(b"\xff\xd8\xff"):
            detected = "JPEG"
        elif data.startswith(b"\x89PNG\r\n\x1a\n"):
            detected = "PNG"
        elif data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
            detected = "WEBP"
        else:
            detected = "UNKNOWN"
        ext = p.suffix.lower()
        expected = {".jpg":"JPEG",".jpeg":"JPEG",".png":"PNG",".webp":"WEBP"}.get(ext)
        return {
            "name": p.name, "path": str(p.resolve()), "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "extension": ext,
            "mime_type_guess": mimetypes.guess_type(p.name)[0] or "application/octet-stream",
            "detected_format": detected,
            "extension_format_consistency": "PASS" if expected is None or expected == detected else "ANOMALY",
        }
