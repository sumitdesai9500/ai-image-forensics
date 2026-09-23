from app.services.evidence_service import EvidenceService
def test_c2pa_absence_is_not_human_proof():
    f=EvidenceService().build({"extension_format_consistency":"PASS"},{"integrity":"PASS"},
      {"ai_disclosure":False,"manifest_detected":False},{},{})
    assert "not evidence" in next(x for x in f if x["code"]=="NO_C2PA_MANIFEST")["message"]
