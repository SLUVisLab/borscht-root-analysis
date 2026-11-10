"""Pixel-level comparison of local raw images that have no byte-identical copy on Lambda
against the Lambda files that have no byte-identical copy locally."""
import sys, os, re, hashlib, collections as C
import numpy as np
from PIL import Image

S, LOCAL_DIR = sys.argv[1], sys.argv[2]
REMOTE_DIR = f'{S}/remote_2024'
load = lambda p: {f.strip(): h for h, f in (l.rstrip('\n').split(None, 1) for l in open(p))}
L = load(f'{S}/local_raw.sha256'); R = load(f'{S}/remote_2024_raw.sha256')
rhs, lhs = set(R.values()), set(L.values())
local_un = sorted(f for f, h in L.items() if h not in rhs)
remote_un = sorted(f for f, h in R.items() if h not in lhs)

PAT = re.compile(r'kura_(\d+)_(\d+)_(\d{4}-\d\d-\d\d)_TP(\d+)\.png$', re.I)
key = lambda f: (lambda m: (int(m[1]), int(m[2]), m[3], int(m[4])))(PAT.search(os.path.basename(f)))


def info(path):
    im = Image.open(path)
    mode, size = im.mode, im.size
    a = np.asarray(im.convert('RGB'))
    ph = hashlib.sha256(a.tobytes() + str(a.shape).encode()).hexdigest()
    small = np.asarray(im.convert('L').resize((106, 95), Image.BILINEAR), dtype=np.float32).ravel()
    small = (small - small.mean()) / (small.std() + 1e-6)
    return dict(mode=mode, size=size, ph=ph, arr=a, small=small, meta=sorted(im.info.keys()))


LI = {f: info(os.path.join(LOCAL_DIR, f)) for f in local_un}
RI = {f: info(os.path.join(REMOTE_DIR, f)) for f in remote_un}
print(f'local unmatched {len(LI)}, remote unmatched {len(RI)}')
print('local modes/sizes', C.Counter((v['mode'], v['size']) for v in LI.values()))
print('remote modes/sizes', C.Counter((v['mode'], v['size']) for v in RI.values()))
print('local png chunks', C.Counter(tuple(v['meta']) for v in LI.values()))
print('remote png chunks', C.Counter(tuple(v['meta']) for v in RI.values()))

rph = C.defaultdict(list)
for f, v in RI.items():
    rph[v['ph']].append(f)

cats, rows = C.Counter(), []
used_remote = set()
for f, v in LI.items():
    k = key(f)
    hits = rph.get(v['ph'], [])
    if hits:
        used_remote.update(hits)
        same = [h for h in hits if key(h) == k]
        if same:
            cat = 'pixel-identical, same key' + (' (in removes/)' if all('/removes/' in h for h in same) else '')
        else:
            cat = 'pixel-identical, DIFFERENT key'
        cats[cat] += 1; rows.append((cat, f, hits, 1.0, 0.0)); continue
    # no pixel match: best correlation against all remote unmatched
    best = max(RI, key=lambda r: float(v['small'] @ RI[r]['small']) / len(v['small']))
    corr = float(v['small'] @ RI[best]['small']) / len(v['small'])
    same_key = [r for r in RI if key(r) == k]
    mad = None
    if same_key and RI[same_key[0]]['arr'].shape == v['arr'].shape:
        mad = float(np.abs(RI[same_key[0]]['arr'].astype(int) - v['arr'].astype(int)).mean())
    cat = 'no pixel match'
    cats[cat] += 1; rows.append((cat, f, [best], corr, mad, same_key))

print('\n', cats)
for r in rows:
    if r[0] != 'pixel-identical, same key':
        print(r)
print('\nremote unmatched with no local pixel twin:', sorted(set(RI) - used_remote))
