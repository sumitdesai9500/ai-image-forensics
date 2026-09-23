from pathlib import Path
from PIL import Image
from app.services.pixel_service import PixelService

def test_uniform_image_has_no_numpy_correlation_warning(tmp_path):
    p=tmp_path/"uniform.png"; Image.new("RGB",(32,32),(255,255,255)).save(p)
    r=PixelService().analyze(p)
    assert r["validation"]["status"]=="PASS"
    assert r["channel_correlations"]["rg"] is None
    assert r["channel_correlation_status"]["rg"]=="UNDEFINED_ZERO_VARIANCE"

def test_grayscale_image(tmp_path):
    p=tmp_path/"gray.png"; Image.new("L",(32,32),128).save(p)
    r=PixelService().analyze(p)
    assert r["validation"]["status"]=="PASS" and r["mode"]=="L" and r["channels"]==3

def test_invalid_image(tmp_path):
    p=tmp_path/"broken.jpg"; p.write_bytes(b"not an image")
    assert PixelService().analyze(p)["validation"]["status"]=="INVALID_IMAGE"
