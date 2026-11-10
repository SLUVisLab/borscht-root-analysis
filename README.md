# roots

Exploratory analysis of minirhizotron root images from the BII-NRR Kura clover project: 48 tubes, 7 depths, imaged across 2023–2025.

## Setup

```bash
uv sync                 # creates .venv from uv.lock (Python 3.12)
uv run python ...       # or select .venv as the Jupyter kernel
```

## Where things live

| What | Where |
|---|---|
| This project (code, notes) | here; shared via git |
| Full dataset (raw images + segmentation masks, 2023–2025) | `abby-lambda:/data/datasets/BII-NRR_MinirhizotronData/` |
| Local 2024 images + alignment outputs | `growth-display/public/images/` (separate repo, git-ignored here) |
| Alignment pipelines | `references/growth-alignment/` (separate repo, git-ignored here) |

### How code, environments and data move between machines

| What | Canonical home | How it reaches each machine |
|---|---|---|
| Code | the git remote | each machine has a clone; edit and commit on the Mac, push, `git pull` elsewhere |
| Python environment | `pyproject.toml` + `uv.lock` | each machine runs `uv sync` and builds its own; environments are never copied |
| Data, model weights, outputs | the machine's data disk (Lambda: `/data`) | copied explicitly (rsync/rclone) or pulled from the Hugging Face hub; copied to `/scratch/<user>` while a job uses them |
| Secrets, machine settings | each machine's own `.env` | never in git |

Lambda (4× RTX 2080 Ti) is a pull-only run checkout in `~/projects/roots`. Treat it as disposable: anything not pushed or copied back is lost with the instance. It uses a read-only deploy key, not personal git credentials.

## Notes

- [Local vs Lambda 2024 comparison](notes/local_vs_lambda_2024/README.md)
