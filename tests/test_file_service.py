from app.services.file_service import FileService
def test_file(tmp_path):
    p=tmp_path/"x.png"; p.write_bytes(b"\x89PNG\r\n\x1a\n"+b"x"*20)
    r=FileService().analyze(str(p)); assert r["detected_format"]=="PNG"; assert len(r["sha256"])==64
