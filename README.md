# Layers 1-3 Build (Semi Finished)

This is the initial Build V1.0 which forms the base for the Finial Service AI Image identifier.

Backend AI image forensics engine for Layers 1-3:

1. Provenance and metadata
2. File/container forensics
3. Pixel/signal forensics

## Important behavior

- Normal CLI output is a concise end-user report only.
- Full forensic evidence is stored internally as JSON.
- JSON evidence is stored at `storage/analyses/<sanitized_original_filename>/<timestamp>.json`.
- Repeated analyses create separate timestamped files and do not overwrite prior evidence.
- SHA-256 and detailed forensic features remain in the stored evidence.
- Layers 1-3 do not produce a calibrated AI probability.
- Absence of C2PA does not establish human authorship.

## Windows setup

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv2\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m app.main analyze "C:\path\to\image.jpg"
```

Or without activating the virtual environment:

```powershell
.\.venv2\Scripts\python.exe -m pip install -r requirements.txt
.\.venv2\Scripts\python.exe -m pytest -q
.\.venv2\Scripts\python.exe -m app.main analyze "C:\path\to\image.jpg"
```
