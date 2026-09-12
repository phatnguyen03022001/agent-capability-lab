import json
import tempfile
import unittest
from pathlib import Path

from scripts.checkpoint import write_checkpoint
from scripts.verify import verify_repository
from tests.test_checkpoint import make_checkpoint

REQUIRED_STUBS = (
    "AGENTS.md",
    "README.md",
    "docs/protocol.md",
    "docs/design.md",
    "docs/baselines/capability.md",
    "docs/baselines/failure.md",
    "schemas/checkpoint.schema.json",
    "scripts/checkpoint.py",
    "scripts/verify.py",
    "runs/.gitkeep",
)


def make_repo(root):
    for relative in REQUIRED_STUBS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("stub\n", encoding="utf-8")
    (root / "tests").mkdir(exist_ok=True)


class VerifyTests(unittest.TestCase):
    def test_rejects_missing_required_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            (root / "README.md").unlink()
            errors = verify_repository(root)
            self.assertIn("missing required path: README.md", errors)

    def test_accepts_empty_runs_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            self.assertEqual(verify_repository(root), [])

    def test_rejects_missing_tracked_runs_placeholder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            (root / "runs" / ".gitkeep").unlink()
            errors = verify_repository(root)
            self.assertIn("missing required path: runs/.gitkeep", errors)

    def test_accepts_valid_checkpoint_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            first = make_checkpoint()
            second = make_checkpoint(step=2, previous=first)
            write_checkpoint(root / "runs", first)
            write_checkpoint(root / "runs", second)
            self.assertEqual(verify_repository(root), [])

    def test_rejects_tampered_checkpoint_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            first = make_checkpoint()
            write_checkpoint(root / "runs", first)
            path = root / "runs" / "run-001" / "checkpoints" / "000001.json"
            checkpoint = json.loads(path.read_text(encoding="utf-8"))
            checkpoint["probe_result"]["detail"] = "tampered"
            path.write_text(json.dumps(checkpoint), encoding="utf-8")
            errors = verify_repository(root)
            self.assertTrue(any("checkpoint_hash does not match checkpoint content" in error for error in errors))

    def test_rejects_non_contiguous_checkpoint_filenames(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            first = make_checkpoint()
            path = write_checkpoint(root / "runs", first)
            path.rename(path.with_name("000002.json"))
            errors = verify_repository(root)
            self.assertTrue(any("expected checkpoint filename 000001.json" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
