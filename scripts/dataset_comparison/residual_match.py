"""For local files with no pixel twin, compare against every remote image in the same tube/TP groups."""
import sys, os, re, ast, hashlib, glob
import numpy as np
from PIL import Image

S, LOCAL_DIR = sys.argv[1], sys.argv[2]
local = [ast.literal_eval(l)[1] for l in open(f'{S}/pixel_compare.out') if l.startswith("('no pixel match'")]
remote = sorted(glob.glob(f'{S}/remote_cand/raw_images/**/*.png', recursive=True))


def load(p):
    im = Image.open(p)
    a = np.asarray(im.convert('RGB'))
    g = np.asarray(im.convert('L').resize((212, 189), Image.BILINEAR), dtype=np.float32).ravel()
    return a, hashlib.sha256(a.tobytes()).hexdigest(), (g - g.mean()) / (g.std() + 1e-6)

R = {os.path.relpath(p, f'{S}/remote_cand'): load(p) for p in remote}
for f in local:
    a, ph, g = load(os.path.join(LOCAL_DIR, f))
    tube, tp = re.search(r'kura_(\d+)_', f)[1], re.search(r'_TP(\d+)', f)[1]
    cands = {r: v for r, v in R.items() if f'kura_{tube}_' in r and f'_TP{tp}.' in r}
    scored = sorted(((float(g @ v[2]) / len(g), r, v[1] == ph) for r, v in cands.items()), reverse=True)
    top = ', '.join(f"{os.path.basename(r)}{' [removes]' if 'removes' in r else ''} r={c:.3f}{' PIXEL-IDENTICAL' if same else ''}" for c, r, same in scored[:2])
    print(f'{f:36s} -> {top}')
