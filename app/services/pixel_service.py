import math
import numpy as np
from PIL import Image, ImageFile, ImageFilter, UnidentifiedImageError

ImageFile.LOAD_TRUNCATED_IMAGES = False
MAX_PIXELS = 40_000_000
MIN_DIMENSION = 2

class PixelService:
    def analyze(self, path):
        try:
            with Image.open(path) as im:
                original_mode = im.mode
                w, h = im.size
                if w < MIN_DIMENSION or h < MIN_DIMENSION:
                    raise ValueError(f"Image dimensions too small: {w}x{h}")
                if w * h > MAX_PIXELS:
                    raise ValueError(f"Image has {w*h:,} pixels; maximum is {MAX_PIXELS:,}")
                im.load()
                rgb = im.convert("RGB")
                arr = np.asarray(rgb, dtype=np.float64)
                gray = np.asarray(rgb.convert("L"), dtype=np.float64)
                corr, corr_status = {}, {}
                for name, a, b in (("rg",arr[...,0],arr[...,1]),("rb",arr[...,0],arr[...,2]),("gb",arr[...,1],arr[...,2])):
                    corr[name], corr_status[name] = self._safe_corr(a,b)
                noise = self._noise(gray)
                return {
                    "format": im.format, "mode": original_mode, "width": w, "height": h, "channels": 3,
                    "mean_rgb": [round(float(x),4) for x in arr.mean(axis=(0,1))],
                    "std_rgb": [round(float(x),4) for x in arr.std(axis=(0,1))],
                    "luminance_mean": round(float(gray.mean()),4),
                    "luminance_std": round(float(gray.std()),4),
                    "luminance_entropy": round(self._entropy(gray),6),
                    "gradient_energy": round(self._gradient(gray),6),
                    "edge_density": round(self._edges(gray),6),
                    "noise_variance": round(float(np.var(noise)),6),
                    "noise_entropy": round(self._entropy(noise + 128),6),
                    "channel_correlations": {k: None if v is None else round(v,6) for k,v in corr.items()},
                    "channel_correlation_status": corr_status,
                    "fft": self._fft(gray),
                    "patches": self._patches(gray),
                    "validation": {"status":"PASS", "pixel_count":w*h, "max_pixels":MAX_PIXELS},
                }
        except (UnidentifiedImageError, OSError) as e:
            return {"validation":{"status":"INVALID_IMAGE","error":f"{type(e).__name__}: {e}"}}
        except Exception as e:
            return {"validation":{"status":"REJECTED","error":f"{type(e).__name__}: {e}"}}

    @staticmethod
    def _safe_corr(a,b):
        a,b=np.asarray(a,dtype=np.float64).ravel(),np.asarray(b,dtype=np.float64).ravel()
        if a.size < 2: return None,"INSUFFICIENT_SAMPLES"
        if np.std(a)==0 or np.std(b)==0: return None,"UNDEFINED_ZERO_VARIANCE"
        v=float(np.corrcoef(a,b)[0,1])
        return (v,"DEFINED") if math.isfinite(v) else (None,"UNDEFINED_NONFINITE")

    @staticmethod
    def _entropy(a):
        if a.size==0: return 0.0
        lo,hi=float(np.min(a)),float(np.max(a))
        if hi<=lo: return 0.0
        h,_=np.histogram(a,bins=256,range=(lo,hi)); p=h[h>0].astype(float); p/=p.sum()
        return float(-(p*np.log2(p)).sum())

    @staticmethod
    def _gradient(g):
        return float((np.diff(g,axis=1)**2).mean()+(np.diff(g,axis=0)**2).mean())

    @staticmethod
    def _edges(g):
        gx=np.diff(g,axis=1); gy=np.diff(g,axis=0)
        if gx.size==0 or gy.size==0: return 0.0
        t=max(float(np.percentile(np.abs(np.concatenate((gx.ravel(),gy.ravel()))),90)),10.0)
        return float((np.abs(gx)>=t).mean()*0.5+(np.abs(gy)>=t).mean()*0.5)

    @staticmethod
    def _noise(g):
        low=np.asarray(Image.fromarray(np.clip(g,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1)),dtype=np.float64)
        return g-low

    @staticmethod
    def _fft(g):
        p=np.abs(np.fft.fftshift(np.fft.fft2(g-g.mean())))**2; total=float(p.sum())
        if total<=0: return {"low_frequency_energy_ratio":None,"high_frequency_energy_ratio":None,"spectral_entropy":0.0}
        h,w=p.shape; yy,xx=np.ogrid[:h,:w]; r=np.sqrt((yy-h/2)**2+(xx-w/2)**2); cut=max(min(h,w)*.1,1)
        q=p.ravel()/total; q=q[q>0]
        return {"low_frequency_energy_ratio":round(float(p[r<=cut].sum()/total),6),"high_frequency_energy_ratio":round(float(p[r>=cut*3].sum()/total),6),"spectral_entropy":round(float(-(q*np.log2(q)).sum()),6)}

    @staticmethod
    def _patches(g,grid=4):
        out=[]; h,w=g.shape
        for r in range(grid):
            for c in range(grid):
                a=g[r*h//grid:(r+1)*h//grid,c*w//grid:(c+1)*w//grid]
                if a.size: out.append({"row":r,"col":c,"mean":round(float(a.mean()),4),"std":round(float(a.std()),4),"entropy":round(PixelService._entropy(a),6)})
        return {"grid":f"{grid}x{grid}","count":len(out),"statistics":out}
