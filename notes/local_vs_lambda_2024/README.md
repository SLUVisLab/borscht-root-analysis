# Local vs Lambda: 2024 raw minirhizotron images (2026-11-10)

**Local:** `growth-display/public/images/` (raw files only, pattern `kura_<tube>_<depth>_<date>_TP<n>.png`), 3,798 files.
**Lambda:** `abby-lambda:/data/datasets/BII-NRR_MinirhizotronData/2024/raw_images/` (3,778 files, plus 62 in `removes/`).

## Conclusion

Lambda 2024 is a **curated version of the local set**. It contains no 2024 images that aren't also local. Lambda also has 2023 and 2025 data and segmentation masks for all three years, which the local copy lacks.

## Reconciliation (all 3,798 local / 3,778 Lambda files accounted for)

| Category | Count |
|---|---|
| Same image, same name: byte-identical | 3,404 |
| Same image, same name: identical pixels, local re-saved with Adobe XMP metadata | 357 |
| Same image, depth relabelled on Lambda | 14 |
| Local only: dropped in curation | 19 |
| Local only: moved to Lambda `removes/` (`kura_206_002_2024-03-11_TP1`) | 1 |
| Same name, different content: Lambda file is a misfiled mask | 3 |

Names are compared after zero-padding the depth. Local TP4 uses `1`–`7` instead of `001`–`007`.

### Depth relabels (local name → Lambda name)
- Tube 216, TP6 (2024-05-21): `002`–`007` → `001`–`006`
- Tube 229, TP5 (2024-05-07): `001`–`006` → `002`–`007`
- Tube 235, TP1 (2024-03-11): `005` → `004`
- Tube 247, TP5 (2024-05-09): `002` → `001`

### Dropped in curation (local only)
- Tubes 238 and 239, TP5: local has two captures per depth (2024-05-07 and 2024-05-09); Lambda kept one per depth (14 files dropped).
- `kura_201_003_2024-03-26_TP2`: byte-identical duplicate of local `201_002` TP2.
- `kura_203_002_2024-10-08_TP11`
- `kura_216_001_2024-05-21_TP6`, `kura_235_004_2024-03-11_TP1`, `kura_247_001_2024-05-09_TP5`: the wrong images that the relabels above replaced.

### Error in the Lambda copy
In Lambda's `raw_images/`, `kura_226_001`, `kura_226_002` and `kura_235_006` (TP12, 2024-11-12) are 2-colour segmentation masks, not photos. They were written 2026-09-24 and also differ from the copies in `dataset_masks/` (dated 2024-12-05). The local versions are the real photos.

## Implications
- Treat Lambda filenames (the curated depth labels) as ground truth, especially when pairing images with masks.
- The local alignment outputs (`_sift`, `_correlate`, `_depths_all`) were built on the uncurated labels. Expect errors for tube 216 TP6, tube 229 TP5 and tubes 238/239 TP5.
- Lambda's 2023 and 2025 raw images use an uppercase `.PNG` extension.

## Files
- `local_2024_raw.sha256`, `lambda_2024_raw.sha256`: SHA-256 manifests of both sides.
- `compare_keys.out`, `pixel_compare.out`, `residual_match.out`: script outputs.
- Scripts: `scripts/dataset_comparison/`. They were run ad hoc, taking the working directory as `argv[1]`. `pixel_compare.py` and `residual_match.py` expect the needed Lambda files rsynced into `<dir>/remote_2024/` and `<dir>/remote_cand/`.
