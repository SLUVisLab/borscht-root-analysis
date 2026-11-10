"""Compare local vs Lambda 2024 raw images on a normalized key (tube, depth int, date, TP)."""
import os, re, sys, json, collections as C

S = sys.argv[1]
PAT = re.compile(r'^kura_(\d+)_(\d+)_(\d{4}-\d\d-\d\d)_TP(\d+)\.png$', re.I)


def load(p):
    d = {}
    for l in open(p):
        h, f = l.rstrip('\n').split(None, 1)
        d[f.strip()] = h
    return d


def key(fname):
    m = PAT.match(os.path.basename(fname))
    return (int(m[1]), int(m[2]), m[3], int(m[4])) if m else None


L = load(f'{S}/local_raw.sha256')
R = load(f'{S}/remote_2024_raw.sha256')
Rmain = {f: h for f, h in R.items() if '/removes/' not in f}
Rrem = {f: h for f, h in R.items() if '/removes/' in f}

bad = [f for f in list(L) + list(R) if key(f) is None]
print('unparseable names:', bad)

def bykey(d):
    out = C.defaultdict(list)
    for f, h in d.items():
        out[key(f)].append((f, h))
    return out

LK, RK, RRK = bykey(L), bykey(Rmain), bykey(Rrem)
print(f'keys: local {len(LK)}  remote main {len(RK)}  remote removes {len(RRK)}')
for name, K in [('local', LK), ('remote main', RK), ('remote removes', RRK)]:
    multi = {k: v for k, v in K.items() if len(v) > 1}
    print(f'  {name}: keys with >1 file: {len(multi)}', [[f for f, _ in v] for v in list(multi.values())[:5]])

both = set(LK) & set(RK)
lonly = set(LK) - set(RK)
ronly = set(RK) - set(LK)
same_bytes = {k for k in both if {h for _, h in LK[k]} == {h for _, h in RK[k]}}
print(f'\nkey in both: {len(both)}  identical bytes: {len(same_bytes)}  differing bytes: {len(both - same_bytes)}')
print(f'local-only keys: {len(lonly)}  (of which in remote removes/: {len(lonly & set(RRK))})')
print(f'remote-only keys: {len(ronly)}')

rh = C.defaultdict(list)
for f, h in R.items():
    rh[h].append(f)
lh = C.defaultdict(list)
for f, h in L.items():
    lh[h].append(f)

print('\nLOCAL-ONLY keys not in removes:')
for k in sorted(lonly - set(RRK)):
    for f, h in LK[k]:
        print('  ', f, '| same bytes remote:', rh.get(h, []))
print('\nREMOTE-ONLY keys:')
for k in sorted(ronly):
    for f, h in RK[k]:
        print('  ', f, '| same bytes local:', lh.get(h, []))

diff_tp = C.Counter(k[3] for k in both - same_bytes)
diff_tube = C.Counter(k[0] for k in both - same_bytes)
print('\ndiffering-bytes by TP:', sorted(diff_tp.items()))
print('differing-bytes by tube:', sorted(diff_tube.items()))

# pairs to pixel-compare: same key, differing bytes; plus local-only that sit in removes w/ diff bytes
pairs = []
for k in sorted(both - same_bytes):
    pairs.append({'key': k, 'local': [f for f, _ in LK[k]], 'remote': [f for f, _ in RK[k]]})
for k in sorted(lonly & set(RRK)):
    if {h for _, h in LK[k]} != {h for _, h in RRK[k]}:
        pairs.append({'key': k, 'local': [f for f, _ in LK[k]], 'remote': [f for f, _ in RRK[k]]})
json.dump(pairs, open(f'{S}/pairs_to_pixel_compare.json', 'w'))
need = sorted({r for p in pairs for r in p['remote']} | {f for k in ronly for f, _ in RK[k]})
open(f'{S}/remote_fetch_list.txt', 'w').write('\n'.join(need) + '\n')
print(f'\npairs to pixel-compare: {len(pairs)}; remote files to fetch: {len(need)}')
