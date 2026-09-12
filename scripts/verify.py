#!/usr/bin/env python3
import json
import sys
from pathlib import Path

try:
    from scripts.checkpoint import validate_checkpoint
except ModuleNotFoundError:
    from checkpoint import validate_checkpoint

REQUIRED_PATHS = (
    "README.md",
    "protocols/self-driving-v1.md",
    "schemas/checkpoint.schema.json",
    "scripts/checkpoint.py",
    "scripts/verify.py",
    "tests",
    "runs",
    "baselines/sol-capability-audit.md",
    "baselines/sol-failure-audit.md",
)


def verify_repository(root):
    root = Path(root)
    errors = []
    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            errors.append(f"missing required path: {relative}")

    runs_root = root / "runs"
    if not runs_root.is_dir():
        return errors

    run_dirs = sorted(path for path in runs_root.iterdir() if path.is_dir())
    for run_dir in run_dirs:
        checkpoints_dir = run_dir / "checkpoints"
        if not checkpoints_dir.is_dir():
            errors.append(f"run {run_dir.name} is missing checkpoints directory")
            continue

        checkpoint_files = sorted(checkpoints_dir.glob("*.json"))
        predecessor = None
        for index, path in enumerate(checkpoint_files, start=1):
            expected = f"{index:06d}.json"
            if path.name != expected:
                errors.append(
                    f"{path.relative_to(root)}: expected checkpoint filename {expected}"
                )
            try:
                checkpoint = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{path.relative_to(root)}: cannot read checkpoint: {exc}")
                continue

            if checkpoint.get("run_id") != run_dir.name:
                errors.append(f"{path.relative_to(root)}: run_id does not match directory")

            for error in validate_checkpoint(checkpoint, predecessor):
                errors.append(f"{path.relative_to(root)}: {error}")
            predecessor = checkpoint

    return errors


def main():
    root = Path(__file__).resolve().parents[1]
    errors = verify_repository(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("VERIFY PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
