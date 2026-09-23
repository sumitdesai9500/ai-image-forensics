from app.services.c2pa_service import C2PAService

def test_manifest_missing_maps_to_not_present(monkeypatch):
    class FakeContext:
        def __enter__(self): return self
        def __exit__(self,*a): pass
    class FakeReader:
        def __init__(self,ctx,path): pass
        def json(self): raise RuntimeError("ManifestNotFound: no JUMBF data found")
    import sys, types
    fake = types.SimpleNamespace(Context=lambda: FakeContext(), Reader=FakeReader)
    monkeypatch.setitem(sys.modules, "c2pa", fake)
    service=C2PAService()
    result=service.analyze("dummy.jpg")
    assert result["validation_status"]=="NOT_PRESENT"
    assert result["manifest_detected"] is False
