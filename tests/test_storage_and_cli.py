import json
from pathlib import Path
from app.services.evidence_storage_service import store_evidence
from app.views.cli_view import print_report
from app.models.result import ForensicEvidence


def test_storage_uses_human_filename_and_timestamp(tmp_path):
    payload = {"file": {"name": "clean copy.jpg", "sha256": "abc"}}
    path = Path(store_evidence(payload, tmp_path / "analyses"))
    assert path.parent.name == "clean_copy"
    assert path.suffix == ".json"
    assert len(path.stem) >= 15
    assert json.loads(path.read_text())["file"]["name"] == "clean copy.jpg"


def test_cli_has_no_json_dump(capsys):
    evidence = ForensicEvidence(
        file={"name":"clean_copy.jpg","detected_format":"JPEG","extension_format_consistency":"PASS"},
        provenance={"manifest_detected":False,"ai_disclosure":False},
        metadata={"has_exif":False,"has_xmp":False,"has_iptc":False},
        container={"supported":True,"encoding":"Baseline"},
        pixel={"width":1048,"height":1501,"validation":{"status":"PASS"},"fft":{}},
    )
    assessment={"result":"NO STRONG AI EVIDENCE","confidence":"Not available","ai_probability":"Not available"}
    print_report(evidence, assessment, "storage/analyses/clean_copy/20260922_192845.json")
    out=capsys.readouterr().out
    assert "JSON:" not in out
    assert '"file"' not in out
    assert "DETERMINISTIC_STATE" not in out
    assert "NO STRONG AI EVIDENCE" in out
