# Agent Capability Lab V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the minimal zero-cost V1 repository that can create and independently validate append-only endurance checkpoints without starting an endurance-to-death run.

**Architecture:** Python standard-library code owns checkpoint canonicalization, SHA-256 integrity, continuity validation, and repository/run verification. JSON Schema documents the external checkpoint contract; `unittest` provides executable proof. Markdown documents the protocol, preserved baselines, safety boundaries, and reporting semantics.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, Markdown, Git.

**Spec:** `docs/superpowers/specs/2026-09-12-agent-capability-lab-v1-design.md`

## Global Constraints

- Work only in `/Users/tienphat/Developer/agent-capability-lab` on branch `main`.
- No worktree and no other branch.
- Use Agent Runtime only for local execution.
- Do not perform any Agent Runtime/tunnel/port lifecycle operation.
- Zero intentional monetary cost: no paid API, cloud, CI runner, hosted service, or metered third party.
- Python standard library only; no framework, database, daemon, service, queue, Docker, or new dependency.
- Do not start the actual endurance-to-death benchmark during bootstrap.
- A step becomes remote-proven alive only after successful verification, commit, push, and remote-main verification.

---

### Task 1: Checkpoint integrity core

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/checkpoint.py`
- Create: `tests/__init__.py`
- Create: `tests/test_checkpoint.py`

**Interfaces:**
- Produces: `compute_checkpoint_hash(checkpoint: dict) -> str`
- Produces: `validate_checkpoint(checkpoint: dict, predecessor: dict | None) -> list[str]`
- Produces: `write_checkpoint(run_root: Path, checkpoint: dict) -> Path`
- Produces CLI: `python3 scripts/checkpoint.py validate <checkpoint> [--previous <checkpoint>]`

- [ ] **Step 1: Write failing checkpoint tests**

Tests must cover deterministic hash independence from key order, valid first checkpoint, valid chained checkpoint, skipped predecessor rejection, incorrect previous hash rejection, invalid status rejection, missing evidence rejection, tamper/hash mismatch rejection, and duplicate checkpoint-file rejection.

- [ ] **Step 2: Run checkpoint tests and verify RED**

Run: `python3 -m unittest tests.test_checkpoint -v`

Expected: failure because `scripts.checkpoint` or required functions do not yet exist.

- [ ] **Step 3: Implement minimal checkpoint logic**

Use canonical JSON `json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` encoded as UTF-8, excluding `checkpoint_hash`. Hash with SHA-256. Required statuses are exactly `HEALTHY`, `DEGRADED`, `UNRELIABLE`, `POLICY_BLOCKED`, `TOOL_FAILED`, `BLOCKED`, `DEAD_OR_UNKNOWN`. Require non-empty `run_id`, integer `chat_ordinal` in 1..3, integer `step >= 1`, matching predecessor fields, boolean `canary_ok`, non-empty string/object `probe_result`, `verification_status == "PASS"`, non-empty timestamp, and matching stored hash. `write_checkpoint` writes `runs/<run_id>/checkpoints/<step six digits>.json` with exclusive creation and never overwrites.

- [ ] **Step 4: Run checkpoint tests and verify GREEN**

Run: `python3 -m unittest tests.test_checkpoint -v`

Expected: all checkpoint tests pass.

- [ ] **Step 5: Commit and push task**

Commands: `git add scripts tests`; `git commit -m "feat: add checkpoint integrity core"`; `git push origin main`.

### Task 2: Repository and run verifier

**Files:**
- Create: `scripts/verify.py`
- Create: `tests/test_verify.py`

**Interfaces:**
- Consumes: `validate_checkpoint` from Task 1.
- Produces: `verify_repository(root: Path) -> list[str]`
- Produces CLI: `python3 scripts/verify.py`

- [ ] **Step 1: Write failing verifier tests**

Tests must cover missing required repository path, empty `runs/` acceptance, valid checkpoint-chain acceptance, invalid/tampered chain rejection, and non-contiguous checkpoint filenames rejection.

- [ ] **Step 2: Run verifier tests and verify RED**

Run: `python3 -m unittest tests.test_verify -v`

Expected: failure because `scripts.verify` does not exist.

- [ ] **Step 3: Implement minimal verifier**

Required static paths are `README.md`, `protocols/self-driving-v1.md`, `schemas/checkpoint.schema.json`, `scripts/checkpoint.py`, `scripts/verify.py`, `tests`, `runs`, `baselines/sol-capability-audit.md`, and `baselines/sol-failure-audit.md`. For every run checkpoint directory, require filenames `000001.json` through `NNNNNN.json` without gaps and validate each document against its immediate predecessor. Return errors instead of mutating state. CLI exits 0 with `VERIFY PASS` or non-zero with each error on stderr.

- [ ] **Step 4: Run verifier tests and verify GREEN**

Run: `python3 -m unittest tests.test_verify -v`

Expected: all verifier tests pass once fixture repos include the required paths.

- [ ] **Step 5: Commit and push task**

Commands: `git add scripts/verify.py tests/test_verify.py`; `git commit -m "feat: add repository verifier"`; `git push origin main`.

### Task 3: Protocol, schema, baselines, and operator docs

**Files:**
- Create: `README.md`
- Create: `protocols/self-driving-v1.md`
- Create: `schemas/checkpoint.schema.json`
- Create: `baselines/sol-capability-audit.md`
- Create: `baselines/sol-failure-audit.md`
- Create: `runs/.gitkeep`

**Interfaces:**
- Documents the exact checkpoint fields/status enum and last-proven-alive semantics implemented by Tasks 1-2.

- [ ] **Step 1: Add the JSON Schema and documentation artifacts**

Schema requires the checkpoint fields from the spec, sets `additionalProperties` to false, constrains `chat_ordinal` to 1..3, `step` to >=1, `previous_step` to >=0, hash fields to 64 lowercase hex characters where non-null, and `session_status` to the exact seven-value enum.

- [ ] **Step 2: Preserve baseline evidence without strengthening claims**

Capability baseline records only the supplied capability bullets and explicitly labels hard limits unknown. Failure baseline records 18 probes, 22 tool calls, 10/10 dependent steps, one recovered injected failure, retained canary, no observed false-success, three safety/policy blocks, and keeps endurance beyond ten steps plus cross-tool handoff unknown.

- [ ] **Step 3: Run all tests and repository verifier**

Run: `python3 -m unittest discover -s tests -v`

Run: `python3 scripts/verify.py`

Expected: both exit 0.

- [ ] **Step 4: Commit and push task**

Commands: `git add README.md protocols schemas baselines runs/.gitkeep`; `git commit -m "docs: define self-driving v1 protocol"`; `git push origin main`.

### Task 4: Final integrity and publication proof

**Files:**
- Modify only if verification exposes a defect.

- [ ] **Step 1: Run fresh full test suite**

Run: `python3 -m unittest discover -s tests -v` and require zero failures/errors.

- [ ] **Step 2: Run fresh repository verifier**

Run: `python3 scripts/verify.py` and require `VERIFY PASS`.

- [ ] **Step 3: Verify repository hygiene**

Run: `git diff --check`; `git branch --show-current`; `git remote get-url origin`; `git status --short --branch`.

Require branch `main`, expected GitHub origin, no whitespace errors, and a clean tree after final commit.

- [ ] **Step 4: Verify remote main matches local HEAD**

Run: `git push origin main`; `git rev-parse HEAD`; `git ls-remote origin refs/heads/main`.

Require the remote hash to equal local `HEAD`.

- [ ] **Step 5: Do not start the endurance benchmark**

Bootstrap ends after implementation proof. No run checkpoint is created as part of this plan.
