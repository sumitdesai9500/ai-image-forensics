from app.models.result import ForensicEvidence
from app.services.file_service import FileService
from app.services.exif_service import ExifService
from app.services.c2pa_service import C2PAService
from app.services.container_service import ContainerService
from app.services.pixel_service import PixelService
from app.services.evidence_service import EvidenceService
from app.services.evidence_storage_service import store_evidence


class DetectionController:
    def __init__(self):
        self.file_service = FileService()
        self.exif_service = ExifService()
        self.c2pa_service = C2PAService()
        self.container_service = ContainerService()
        self.pixel_service = PixelService()
        self.evidence_service = EvidenceService()

    def analyze(self, path):
        f = self.file_service.analyze(path)
        m = self.exif_service.analyze(path)
        p = self.c2pa_service.analyze(path)
        c = self.container_service.analyze(path)
        x = self.pixel_service.analyze(path)
        findings = self.evidence_service.build(f, m, p, c, x)
        evidence = ForensicEvidence(
            file=f, provenance=p, metadata=m, container=c, pixel=x,
            transformations={}, findings=findings
        )
        assessment = self._assessment(f, p, x)
        payload = evidence.to_dict()
        payload["assessment"] = assessment
        stored_path = store_evidence(payload)
        return evidence, assessment, stored_path

    @staticmethod
    def _assessment(file_info, provenance, pixel):
        if provenance.get("ai_disclosure"):
            result = "AI PROVENANCE DETECTED"
        elif pixel.get("validation", {}).get("status") != "PASS":
            result = "IMAGE VALIDATION FAILED"
        elif file_info.get("extension_format_consistency") not in ("PASS", None):
            result = "FORENSIC REVIEW REQUIRED"
        else:
            result = "NO STRONG AI EVIDENCE"
        return {"result": result, "confidence": "Not available", "ai_probability": "Not available"}
