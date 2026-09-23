import json
import shutil
import subprocess

class ExifService:
    def __init__(self, executable="exiftool"):
        self.executable = executable

    def available(self):
        return shutil.which(self.executable) is not None

    def analyze(self, path):
        if not self.available():
            return {"available": False, "error": "ExifTool was not found on PATH.",
                    "tags": {}, "integrity": "UNAVAILABLE"}
        cmd = [self.executable, "-a", "-u", "-g1", "-json",
               "-EXIF:*", "-XMP:*", "-IPTC:*", "-ICC_Profile:*",
               "-JFIF:*", "-PNG:*", "-File:*", path]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if p.returncode:
            return {"available": True, "error": p.stderr.strip() or "ExifTool failed.",
                    "tags": {}, "integrity": "ERROR"}
        try:
            tags = (json.loads(p.stdout or "[]") or [{}])[0]
        except json.JSONDecodeError:
            return {"available": True, "error": "Invalid ExifTool JSON.",
                    "tags": {}, "integrity": "ERROR"}
        make, model = tags.get("Make"), tags.get("Model")
        return {
            "available": True,
            "integrity": "WARNING" if bool(make) != bool(model) else "PASS",
            "has_exif": any(k.startswith("EXIF:") or k in ("Make","Model") for k in tags),
            "has_xmp": any(k.startswith("XMP:") for k in tags),
            "has_icc": any(k.startswith("ICC_Profile") for k in tags),
            "has_iptc": any(k.startswith("IPTC:") for k in tags),
            "camera_make": make, "camera_model": model,
            "software": tags.get("Software") or tags.get("XMP:CreatorTool"),
            "date_time_original": tags.get("DateTimeOriginal"),
            "orientation": tags.get("Orientation"),
            "color_space": tags.get("ColorSpace"),
            "width": tags.get("ImageWidth") or tags.get("ExifImageWidth"),
            "height": tags.get("ImageHeight") or tags.get("ExifImageHeight"),
            "tags": tags,
        }
