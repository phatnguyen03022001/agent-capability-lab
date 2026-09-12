# Agent Capability Lab V1 Design

## Purpose

`agent-capability-lab` is a small empirical laboratory for measuring whether a ChatGPT/agent session can keep producing independently verifiable progress under increasing session duration. V1 measures self-driving session endurance, not mere responsiveness and not hidden platform maxima.

## Core Protocol

A run repeatedly performs:

`probe -> verify -> externalize checkpoint -> commit -> push main -> next step`

A step is remote-proven alive only after all six stages succeed. A local checkpoint or local commit alone is insufficient.

A dead session cannot authoritatively write its own `DEAD` checkpoint. The latest checkpoint that was verified, committed, and pushed to remote `main` is the run's `last_proven_alive`. A later independent session or auditor may classify what happened after that checkpoint.

## Status Model

Checkpoint/session statuses are limited to:

- `HEALTHY`
- `DEGRADED`
- `UNRELIABLE`
- `POLICY_BLOCKED`
- `TOOL_FAILED`
- `BLOCKED`
- `DEAD_OR_UNKNOWN`

Policy and tool failures remain distinct from model death. The primary runner normally records only states it can support with current evidence; `DEAD_OR_UNKNOWN` is intended for later independent classification when the prior session cannot authoritatively classify itself.

## Multi-Chat Semantics

A benchmark run may span at most three independent chats. Each chat records its own ordinal, first step, last proven step, and termination reason. Aggregate progress across chats must never be reported as endurance of one session.

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

## Run Invariants

At every successful step:

1. The run canary must exist and match the run metadata.
2. The probe must produce a small bounded result.
3. Checkpoint continuity and hash integrity must validate.
4. Repository verification must pass.
5. The checkpoint commit must be created on `main`.
6. The commit must be successfully pushed to the expected remote `main` before the step is considered remote-proven alive.

If push fails, the step may exist locally but is not remote-proven alive until push succeeds and remote `main` is verified.

## V1 Repository Shape

- `README.md` — purpose, safety boundaries, quick start, and reporting semantics.
- `protocols/self-driving-v1.md` — normative benchmark procedure.
- `schemas/checkpoint.schema.json` — machine-readable checkpoint shape and enums.
- `scripts/checkpoint.py` — checkpoint creation and validation using Python standard library only.
- `scripts/verify.py` — repository/run verifier.
- `tests/` — `unittest` coverage for checkpoint and verifier behavior.
- `runs/.gitkeep` — keeps run root in Git without starting a benchmark run.
- `baselines/sol-capability-audit.md` — supplied capability baseline.
- `baselines/sol-failure-audit.md` — supplied bounded-failure baseline.
- `docs/superpowers/specs/` — design documents.
- `docs/superpowers/plans/` — implementation plans.

## Baseline Evidence Preserved

Capability baseline:

- GPT-5.6 Sol identity was exposed in the audited session.
- Python/Linux sandbox was available.
- Local macOS Agent Runtime execution was available when developer MCP execution was enabled.
- Multiple storage/authority domains existed.
- Tool schema exposure did not guarantee execution.
- Tool calls were not transactional.
- Policy/safety layers could block calls before execution.
- Many hard limits remained unknown.

Bounded-failure baseline:

- 18 probes and 22 tool calls.
- 10/10 dependent steps completed.
- One injected failure recovered correctly.
- Canary retained.
- No false-success observed.
- The same content-sensitive safety/policy boundary blocked three probes, triggering the required stop condition.
- Endurance beyond the tested ten-step chain remained unknown.
- Cross-tool handoff remained unknown.

## Authority and Cost Boundaries

V1 intentionally uses only ChatGPT, Agent Runtime, local filesystem, Python/shell system facilities, Git, and ordinary GitHub commits/pushes. It must not enable paid APIs, paid model calls, paid cloud resources, paid CI/CD, hosted databases, third-party metered APIs, Docker, daemons, queues, or services.

All repository work is on `main`; no benchmark implementation requires branches or worktrees. Agent Runtime is execution infrastructure only and its lifecycle, tunnel, and listening port are outside benchmark authority.

## Failure Handling

The runner must fail closed. Invalid checkpoint data, missing predecessors, hash mismatches, missing evidence, repository verification failures, or push failures must not be converted into successful progress. Recovery may resume from the last valid state without duplicating already committed checkpoints.

The implementation must never infer a hard platform limit from one failed probe or one stopped chat.

## Testing Strategy

Use Python standard-library `unittest`. Tests cover canonical hashing, first-step creation, chained checkpoints, predecessor gaps, previous-hash mismatch, invalid status, missing evidence, tampering, duplicate step protection, and repository/run verification. Production logic is written only after a corresponding failing test is observed.

## Non-Goals

V1 does not start the endurance-to-death benchmark during bootstrap. It does not implement a daemon, scheduler, cloud service, CI workflow, database, dashboard, paid integration, generalized agent framework, or hidden-limit discovery harness.
