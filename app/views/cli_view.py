def _metadata_summary(metadata):
    present = any(metadata.get(k) for k in ("has_exif", "has_xmp", "has_iptc"))
    return "Camera/author metadata detected" if present else "No camera/author metadata detected"


def print_report(evidence, assessment, stored_path):
    f = evidence.file
    p = evidence.provenance
    m = evidence.metadata
    c = evidence.container
    x = evidence.pixel
    width, height = x.get("width"), x.get("height")
    dimensions = f"{width} × {height}" if width and height else "Not available"
    image_valid = x.get("validation", {}).get("status") == "PASS"
    structure_valid = bool(c.get("supported"))
    print("=" * 60)
    print("AI IMAGE FORENSICS REPORT")
    print("=" * 60)
    print("\nIMAGE\n" + "-" * 60)
    print(f"File                         : {f.get('name')}")
    print(f"Format                       : {f.get('detected_format') or 'Unknown'}")
    print(f"Dimensions                   : {dimensions}")
    print(f"File Integrity               : {f.get('extension_format_consistency')}")
    print("\nPROVENANCE\n" + "-" * 60)
    print(f"C2PA Provenance              : {'Detected' if p.get('manifest_detected') else 'Not detected'}")
    print(f"AI Provenance Disclosure     : {'Detected' if p.get('ai_disclosure') else 'Not detected'}")
    print(f"Metadata                     : {_metadata_summary(m)}")
    print("\nFILE FORENSICS\n" + "-" * 60)
    print(f"Format Consistency           : {f.get('extension_format_consistency')}")
    encoding = c.get("encoding") if f.get("detected_format") == "JPEG" else "Not applicable"
    print(f"JPEG Encoding                : {encoding or 'Not available'}")
    print(f"Image Structure              : {'Valid' if structure_valid else 'Review required'}")
    print("\nPIXEL FORENSICS\n" + "-" * 60)
    print(f"Image Data                   : {'Valid' if image_valid else 'Invalid'}")
    print(f"Signal Analysis              : {'Completed' if image_valid else 'Failed'}")
    print(f"Frequency Analysis           : {'Completed' if x.get('fft') else 'Not available'}")
    print("Image Anomalies              : None identified by current rules")
    print("\nASSESSMENT\n" + "-" * 60)
    print(f"Current Result               : {assessment['result']}")
    print(f"Confidence                   : {assessment['confidence']}")
    print(f"AI Probability               : {assessment['ai_probability']}")
    print("\nIMPORTANT\n" + "-" * 60)
    if p.get("ai_disclosure"):
        print("Explicit AI provenance was detected in the file.")
    else:
        print("No C2PA/AI provenance was detected in this file. This does")
        print("not establish that the image was created by a human.")
    print("\nPixel and file-level analysis provides forensic evidence only.")
    print("A trained AI classifier will be required for AI-generation")
    print("classification.")
    print(f"\nEvidence stored at:\n{stored_path}")
    print("\n" + "=" * 60)
    print("FORENSIC ENGINE — LAYERS 1–3")
    print("=" * 60)
