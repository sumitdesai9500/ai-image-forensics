from pathlib import Path
from app.services.container_service import ContainerService
from app.services.file_service import FileService

def test_jpeg_structure():
    p=Path(__file__).parent/"fixtures"/"sample.jpg"; f=FileService().analyze(p); r=ContainerService().analyze(p)
    assert r["format"]=="JPEG" and r["supported"]
    assert r["quantization_table_count"]>=1
    assert "SOF0" in r["marker_names"] and "DHT" in r["marker_names"] and "SOS" in r["marker_names"] and r["eoi_found"]

def test_png_structure():
    p=Path(__file__).parent/"fixtures"/"sample.png"; r=ContainerService().analyze(p)
    assert r["format"]=="PNG" and r["supported"] and r["width"]==16 and r["height"]==16
