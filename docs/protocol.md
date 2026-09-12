# Benchmark Protocol

## Purpose

`agent-capability-lab` is a small empirical laboratory for measuring whether a ChatGPT/agent session can keep producing independently verifiable progress under increasing session duration. The lab measures self-driving session endurance, not mere responsiveness and not hidden platform maxima.

## Core Protocol

A run repeatedly performs:

`probe -> verify -> checkpoint -> commit -> push -> verify remote`

A step is remote-proven alive only after all six stages succeed. A local checkpoint or local commit alone is insufficient.

A dead session cannot authoritatively declare itself dead. The latest checkpoint whose commit was verified on remote `main` is the run's `last_proven_alive`. A later independent session or auditor may classify what happened after that checkpoint.

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
6. The commit must be pushed to the expected remote `main`, and remote `main` must be verified to resolve to that commit before the step is considered remote-proven alive.

If push fails, the step may exist locally but is not remote-proven alive until push succeeds and remote `main` is verified.

## Failure Handling

The runner must fail closed. Invalid checkpoint data, missing predecessors, hash mismatches, missing evidence, repository verification failures, or push failures must not be converted into successful progress. Recovery may resume from the last valid state without duplicating already committed checkpoints.

The implementation must never infer a hard platform limit from one failed probe or one stopped chat.

## Non-Goals

Bootstrap does not start the endurance-to-death benchmark. It does not implement a daemon, scheduler, cloud service, CI workflow, database, dashboard, paid integration, generalized agent framework, or hidden-limit discovery harness.
