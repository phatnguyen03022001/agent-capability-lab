#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ALLOWED_STATUSES = {
    "HEALTHY",
    "DEGRADED",
    "UNRELIABLE",
    "POLICY_BLOCKED",
    "TOOL_FAILED",
    "BLOCKED",
    "DEAD_OR_UNKNOWN",
}

REQUIRED_FIELDS = (
    "run_id",
    "chat_ordinal",
    "step",
    "previous_step",
    "previous_checkpoint_hash",
    "checkpoint_hash",
    "canary_ok",
    "probe_result",
    "verification_status",
    "timestamp",
    "session_status",
)
_HEX64 = re.compile(r"^[0-9a-f]{64}$")

def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)

def compute_checkpoint_hash(checkpoint):
    payload = dict(checkpoint)
    payload.pop("checkpoint_hash", None)
    canonical = json.dumps(payload, sort_keys=True,
        separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()

def validate_checkpoint(checkpoint, predecessor=None):
    if not isinstance(checkpoint, dict):
        return ["checkpoint must be an object"]
    errors = []
    missing = [field for field in REQUIRED_FIELDS if field not in checkpoint]
    errors.extend(f"missing required field: {field}" for field in missing)
    unexpected = sorted(set(checkpoint) - set(REQUIRED_FIELDS))
    errors.extend(f"unexpected field: {field}" for field in unexpected)
    run_id = checkpoint.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("run_id must be a non-empty string")
    chat_ordinal = checkpoint.get("chat_ordinal")
    if not _is_int(chat_ordinal) or not 1 <= chat_ordinal <= 3:
        errors.append("chat_ordinal must be an integer from 1 to 3")
    step = checkpoint.get("step")
    if not _is_int(step) or step < 1:
        errors.append("step must be positive")
    previous_step = checkpoint.get("previous_step")
    if not _is_int(previous_step) or previous_step < 0:
        errors.append("previous_step is invalid")
    previous_hash = checkpoint.get("previous_checkpoint_hash")
    if previous_hash is not None and not _HEX64.fullmatch(str(previous_hash)):
        errors.append("previous_checkpoint_hash is invalid")
    checkpoint_hash = checkpoint.get("checkpoint_hash")
    if not isinstance(checkpoint_hash, str) or not _HEX64.fullmatch(checkpoint_hash):
        errors.append("checkpoint_hash is invalid")
    canary_ok = checkpoint.get("canary_ok")
    if canary_ok is not True:
        errors.append("canary_ok must be true")
    probe_result = checkpoint.get("probe_result")
    if not ((isinstance(probe_result, str) and probe_result.strip()) or (isinstance(probe_result, dict) and probe_result)):
        errors.append("probe_result is invalid")
    if checkpoint.get("verification_status") != "PASS":
        errors.append("verification_status must be PASS")
    timestamp = checkpoint.get("timestamp")
    if not isinstance(timestamp, str) or not timestamp.strip():
        errors.append("timestamp is invalid")
    status = checkpoint.get("session_status")
    if status not in ALLOWED_STATUSES:
        errors.append("session_status is invalid")
    if _is_int(step) and step >= 1:
        if step == 1:
            if previous_step != 0:
                errors.append("first checkpoint previous_step must be 0")
            if previous_hash is not None:
                errors.append("first checkpoint previous_checkpoint_hash must be null")
            if predecessor is not None:
                errors.append("first checkpoint must not have a predecessor")
        else:
            if previous_step != step - 1:
                errors.append("previous_step must equal step - 1")
            if predecessor is None:
                errors.append("predecessor is required for step > 1")
            elif isinstance(predecessor, dict):
                if predecessor.get("run_id") != run_id:
                    errors.append("predecessor run_id mismatch")
                if predecessor.get("step") != step - 1:
                    errors.append("predecessor step mismatch")
                pred_hash = predecessor.get("checkpoint_hash")
                if previous_hash != pred_hash:
                    errors.append("previous_checkpoint_hash does not match predecessor")
            else:
                errors.append("predecessor must be an object")
    if isinstance(checkpoint_hash, str) and _HEX64.fullmatch(checkpoint_hash):
        if checkpoint_hash != compute_checkpoint_hash(checkpoint):
            errors.append("checkpoint_hash does not match checkpoint content")
    return errors

def write_checkpoint(runs_root, checkpoint):
    runs_root = Path(runs_root)
    step = checkpoint.get("step")
    predecessor = None
    if _is_int(step) and step > 1:
        previous_path = runs_root / checkpoint["run_id"] / "checkpoints" / f"{step - 1:06d}.json"
        if not previous_path.is_file():
            raise ValueError("predecessor checkpoint file does not exist")
        text = previous_path.read_text(encoding="utf-8")
        predecessor = json.loads(text)
    errors = validate_checkpoint(checkpoint, predecessor)
    if errors:
        raise ValueError("; ".join(errors))
    target_dir = runs_root / checkpoint["run_id"] / "checkpoints"
    target_dir.mkdir(parents=True, exist_ok=True)
    name = "%06d.json" % checkpoint["step"]
    target = target_dir / name
    target.touch(exist_ok=False)
    payload = json.dumps(checkpoint, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    target.write_text(payload, encoding="utf-8")
    return target

def _load_json(path):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate",))
    parser.add_argument("checkpoint")
    parser.add_argument("--previous")
    args = parser.parse_args(argv)
    checkpoint = _load_json(args.checkpoint)
    predecessor = None
    if args.previous:
        predecessor = _load_json(args.previous)
    errors = validate_checkpoint(checkpoint, predecessor)
    if errors:
        return 1
    print("CHECKPOINT VALID")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
