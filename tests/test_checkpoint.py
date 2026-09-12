import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.checkpoint import compute_checkpoint_hash, validate_checkpoint, write_checkpoint


def make_checkpoint(step=1, previous=None, **overrides):
    checkpoint = {
        "run_id": "run-001",
        "chat_ordinal": 1,
        "step": step,
        "previous_step": 0 if step == 1 else step - 1,
        "previous_checkpoint_hash": None if step == 1 else previous["checkpoint_hash"],
        "canary_ok": True,
        "probe_result": {"status": "PASS", "detail": f"probe-{step}"},
        "verification_status": "PASS",
        "timestamp": f"2026-09-12T09:00:{step:02d}Z",
        "session_status": "HEALTHY",
    }
    checkpoint.update(overrides)
    checkpoint["checkpoint_hash"] = compute_checkpoint_hash(checkpoint)
    return checkpoint


class CheckpointTests(unittest.TestCase):
    def test_hash_is_deterministic_across_key_order(self):
        first = make_checkpoint()
        reordered = dict(reversed(list(first.items())))
        self.assertEqual(compute_checkpoint_hash(first), compute_checkpoint_hash(reordered))

    def test_valid_first_checkpoint(self):
        checkpoint = make_checkpoint()
        self.assertEqual(validate_checkpoint(checkpoint, None), [])

    def test_valid_chained_checkpoint(self):
        first = make_checkpoint()
        second = make_checkpoint(step=2, previous=first)
        self.assertEqual(validate_checkpoint(second, first), [])

    def test_rejects_skipped_predecessor(self):
        first = make_checkpoint()
        third = make_checkpoint(step=3, previous=first, previous_step=1)
        self.assertIn("previous_step must equal step - 1", validate_checkpoint(third, first))

    def test_rejects_incorrect_previous_hash(self):
        first = make_checkpoint()
        second = make_checkpoint(step=2, previous=first, previous_checkpoint_hash="0" * 64)
        self.assertIn("previous_checkpoint_hash does not match predecessor", validate_checkpoint(second, first))

    def test_rejects_invalid_status(self):
        checkpoint = make_checkpoint(session_status="DEAD")
        self.assertIn("session_status is invalid", validate_checkpoint(checkpoint, None))

    def test_rejects_missing_required_evidence(self):
        checkpoint = make_checkpoint()
        checkpoint.pop("probe_result")
        checkpoint["checkpoint_hash"] = compute_checkpoint_hash(checkpoint)
        self.assertIn("missing required field: probe_result", validate_checkpoint(checkpoint, None))

    def test_rejects_tampered_checkpoint(self):
        checkpoint = make_checkpoint()
        checkpoint["probe_result"]["detail"] = "tampered"
        self.assertIn("checkpoint_hash does not match checkpoint content", validate_checkpoint(checkpoint, None))

    def test_write_is_append_only(self):
        checkpoint = make_checkpoint()
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            path = write_checkpoint(runs_root, checkpoint)
            self.assertTrue(path.exists())
            with self.assertRaises(FileExistsError):
                write_checkpoint(runs_root, checkpoint)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved, checkpoint)


if __name__ == "__main__":
    unittest.main()
