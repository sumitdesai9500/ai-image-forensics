import struct
from pathlib import Path

JPEG_MARKERS={0xC0:"SOF0",0xC1:"SOF1",0xC2:"SOF2",0xC3:"SOF3",0xC4:"DHT",0xC5:"SOF5",0xC6:"SOF6",0xC7:"SOF7",0xC9:"SOF9",0xCA:"SOF10",0xCB:"SOF11",0xCC:"DAC",0xCD:"SOF13",0xCE:"SOF14",0xCF:"SOF15",0xDA:"SOS",0xDB:"DQT",0xDD:"DRI",0xFE:"COM",**{0xE0+i:f"APP{i}" for i in range(16)}}

class ContainerService:
    def analyze(self,path):
        data=Path(path).read_bytes()
        if data.startswith(b"\xff\xd8\xff"): return self._jpeg(data)
        if data.startswith(b"\x89PNG\r\n\x1a\n"): return self._png(data)
        if data.startswith(b"RIFF") and len(data)>=12 and data[8:12]==b"WEBP": return self._webp(data)
        return {"format":"UNKNOWN","supported":False}

    def _jpeg(self,data):
        if not data.startswith(b"\xff\xd8"): return {"format":"JPEG","supported":False,"error":"Missing SOI"}
        pos=2; seg=[]; qtables=[]; sof=[]; dht=sos=0; eoi=False; progressive=False
        while pos<len(data):
            while pos<len(data) and data[pos]!=0xFF: pos+=1
            if pos>=len(data): break
            while pos<len(data) and data[pos]==0xFF: pos+=1
            if pos>=len(data): break
            m=data[pos]; pos+=1
            if m==0x00: continue
            if m==0xD9: eoi=True; seg.append({"marker":"EOI"}); break
            if m in (0xD8,*range(0xD0,0xD8)):
                seg.append({"marker":JPEG_MARKERS.get(m,f"0xFF{m:02X}"),"length":0}); continue
            if pos+2>len(data): break
            n=struct.unpack(">H",data[pos:pos+2])[0]
            if n<2 or pos+n>len(data): break
            payload=data[pos+2:pos+n]; name=JPEG_MARKERS.get(m,f"0xFF{m:02X}")
            seg.append({"marker":name,"code":f"FF{m:02X}","length":n})
            if m==0xDB:
                q=0
                while q<len(payload):
                    info=payload[q]; q+=1; precision=info>>4; tid=info&15; size=128 if precision else 64
                    if q+size>len(payload): break
                    vals=[int.from_bytes(payload[q+i:q+i+(2 if precision else 1)],"big") for i in range(0,size,2 if precision else 1)]
                    qtables.append({"id":tid,"precision_bits":16 if precision else 8,"values":vals}); q+=size
            elif m==0xC4: dht+=1
            elif m==0xDA: sos+=1
            elif m in (0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF) and len(payload)>=6:
                sof.append({"marker":name,"precision_bits":payload[0],"height":int.from_bytes(payload[1:3],"big"),"width":int.from_bytes(payload[3:5],"big"),"components":payload[5]}); progressive=m in (0xC2,0xCA,0xC6,0xCE)
            pos+=n
        return {"format":"JPEG","supported":True,"encoding":"Progressive" if progressive else "Baseline","progressive":progressive,"segment_count":len(seg),"marker_names":[x["marker"] for x in seg],"segments":seg,"quantization_tables":qtables,"quantization_table_count":len(qtables),"sof":sof,"dht_count":dht,"sos_count":sos,"eoi_found":eoi}

    def _png(self,data):
        pos=8; chunks=[]; text=[]; icc=exif=False; width=height=bit_depth=color_type=None
        while pos+12<=len(data):
            n=int.from_bytes(data[pos:pos+4],"big"); kind=data[pos+4:pos+8].decode("latin1",errors="replace"); end=pos+12+n
            if end>len(data): break
            chunks.append(kind); payload=data[pos+8:pos+8+n]
            if kind=="IHDR" and len(payload)>=13: width=int.from_bytes(payload[:4],"big"); height=int.from_bytes(payload[4:8],"big"); bit_depth=payload[8]; color_type=payload[9]
            if kind in ("tEXt","zTXt","iTXt"): text.append(kind)
            if kind=="iCCP": icc=True
            if kind=="eXIf": exif=True
            pos=end
            if kind=="IEND": break
        return {"format":"PNG","supported":bool(chunks and chunks[0]=="IHDR" and chunks[-1]=="IEND"),"width":width,"height":height,"bit_depth":bit_depth,"color_type":color_type,"chunk_count":len(chunks),"chunks":chunks,"text_chunks":text,"has_text_chunks":bool(text),"has_icc_profile":icc,"has_exif_chunk":exif}

    def _webp(self,data):
        chunks=[]; pos=12; exif=xmp=icc=False
        while pos+8<=len(data):
            k=data[pos:pos+4].decode("latin1"); n=int.from_bytes(data[pos+4:pos+8],"little"); chunks.append(k); exif|=k=="EXIF"; xmp|=k=="XMP "; icc|=k=="ICCP"; pos+=8+n+(n&1)
        return {"format":"WEBP","supported":True,"chunk_count":len(chunks),"chunks":chunks,"has_exif":exif,"has_xmp":xmp,"has_icc":icc}
