class C2PAService:
    def __init__(self):
        try:
            import c2pa  # noqa: F401
            self._available = True
        except Exception:
            self._available = False

    @staticmethod
    def _manifest_missing(exc):
        s = f"{type(exc).__name__}: {exc}".lower()
        return any(x in s for x in ("manifestnotfound", "no jumbf data found", "manifest not found", "no manifest"))

    def analyze(self, path):
        r = {"detector_available": self._available, "manifest_detected": False,
             "validation_status": "UNAVAILABLE" if not self._available else "NOT_PRESENT",
             "ai_disclosure": False, "generator": None, "actions": [],
             "source_types": [], "details": {}}
        if not self._available:
            return r
        try:
            from c2pa import Context, Reader
            with Context() as ctx:
                raw = Reader(ctx, path).json()
            r["details"] = raw if isinstance(raw, dict) else {"raw": raw}
            r["manifest_detected"] = bool(raw)
            r["validation_status"] = "PRESENT" if raw else "NOT_PRESENT"
            text = str(raw).lower()
            r["ai_disclosure"] = any(x in text for x in (
                "trainedalgorithmicmedia", "generative", "ai-generated",
                "ai generated", "gpt-image", "openai media service"))
            return r
        except Exception as e:
            if self._manifest_missing(e):
                return r
            r["validation_status"] = "ERROR"
            r["error"] = f"{type(e).__name__}: {e}"
            return r
