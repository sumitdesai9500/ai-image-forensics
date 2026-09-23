class EvidenceService:
    def build(self,file_info,exif,c2pa,container,pixel):
        f=[]
        if file_info.get("extension_format_consistency") in ("ANOMALY","FAIL"):
            f.append({"layer":2,"severity":"WARNING","code":"FORMAT_EXTENSION_MISMATCH","message":"File extension does not match detected image format."})
        if exif.get("integrity")=="WARNING":
            f.append({"layer":1,"severity":"INFO","code":"METADATA_INCONSISTENCY","message":"Camera metadata is incomplete or inconsistent."})
        if c2pa.get("ai_disclosure"):
            f.append({"layer":1,"severity":"STRONG","code":"C2PA_AI_PROVENANCE","message":"C2PA content indicates AI/generative provenance."})
        elif c2pa.get("validation_status")=="NOT_PRESENT" or c2pa.get("manifest_detected") is False:
            f.append({"layer":1,"severity":"INFO","code":"NO_C2PA_MANIFEST","message":"No C2PA manifest detected; this is not evidence that the image is human-generated."})
        if pixel.get("validation",{}).get("status") not in (None,"PASS"):
            f.append({"layer":3,"severity":"WARNING","code":"PIXEL_VALIDATION","message":pixel["validation"].get("error","Pixel analysis was not completed.")})
        return f
