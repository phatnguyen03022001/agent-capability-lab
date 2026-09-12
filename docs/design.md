# Repository Design

The lab keeps benchmark evidence deterministic, auditable, and small. The normative procedure lives in `docs/protocol.md`.

## Checkpoint Model

Checkpoints are append-only JSON files under `runs/<run_id>/checkpoints/`. A valid checkpoint contains at least:

- `run_id`
- `chat_ordinal`
- `step`
- `previous_step`
- `previous_checkpoint_hash`
- `checkpoint_hash`
- `canary_ok`
- `probe_result`
- `verification_status`
- `timestamp`
- `session_status`

Integrity uses deterministic SHA-256 over a canonical JSON representation of the checkpoint payload excluding `checkpoint_hash`. The first checkpoint uses `previous_step = 0` and `previous_checkpoint_hash = null`. Step N > 1 requires `previous_step = N - 1` and the exact hash of checkpoint N - 1.

Validation rejects skipped predecessors, incorrect previous hashes, unknown statuses, malformed or missing required evidence, and a stored checkpoint hash that does not match canonical content.

## Repository Shape

- `AGENTS.md` — agent working rules and authority boundaries.
- `README.md` — purpose, quick start, and reporting semantics.
- `docs/protocol.md` — single canonical benchmark procedure.
- `docs/design.md` — repository design and invariants.
- `docs/baselines/` — preserved bounded audit evidence.
- `schemas/checkpoint.schema.json` — machine-readable checkpoint contract.
- `scripts/checkpoint.py` — checkpoint hashing, validation, and append-only writing.
- `scripts/verify.py` — repository/run verifier.
- `tests/` — standard-library `unittest` coverage.
- `runs/.gitkeep` — preserves the run root in a fresh clone without starting a run.

## Authority and Cost Boundaries

The repository intentionally uses only ChatGPT, Agent Runtime, local filesystem, Python/shell system facilities, Git, and ordinary GitHub commits/pushes. It must not enable paid APIs, paid model calls, paid cloud resources, paid CI/CD, hosted databases, third-party metered APIs, Docker, daemons, queues, or services.

All repository work is on `main`; no benchmark implementation requires branches or worktrees. Agent Runtime is execution infrastructure only and its lifecycle, tunnel, and listening port are outside benchmark authority.

## Failure Handling

The runner must fail closed. Invalid checkpoint data, missing predecessors, hash mismatches, missing evidence, repository verification failures, or push failures must not be converted into successful progress. Recovery may resume from the last valid state without duplicating already committed checkpoints.

The implementation must never infer a hard platform limit from one failed probe or one stopped chat.

## Testing Strategy

Use Python standard-library `unittest`. Tests cover canonical hashing, first-step creation, chained checkpoints, predecessor gaps, previous-hash mismatch, invalid status, missing evidence, tampering, duplicate step protection, and repository/run verification. Production logic is written only after a corresponding failing test is observed.

## Non-Goals

Bootstrap does not start the endurance-to-death benchmark. It does not implement a daemon, scheduler, cloud service, CI workflow, database, dashboard, paid integration, generalized agent framework, or hidden-limit discovery harness.
