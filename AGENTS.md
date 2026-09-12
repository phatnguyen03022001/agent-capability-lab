# AGENTS.md

## Authority

This repository measures practical agent capability and session endurance through independently verifiable, append-only evidence.

- Canonical branch: `main`.
- Canonical local root: `/Users/tienphat/Developer/agent-capability-lab`.
- Use Agent Runtime only for local execution in this repository.
- Agent Runtime, its tunnel, and its transport endpoint are infrastructure outside repository authority and must remain unchanged by project work.
- Keep the project zero-cost: no paid APIs, model API calls, cloud resources, hosted CI or GitHub Actions, hosted databases, metered services, Docker, daemons, background services, or queues.
- Prefer Python standard library only. Add a dependency only when repository evidence proves it is required.

## Benchmark invariants

- Benchmark checkpoints are append-only. Never overwrite or delete committed checkpoint evidence.
- A run may span at most 3 independent chats. Never report aggregate multi-chat progress as single-session endurance.
- A step is remote-proven alive only after `probe -> verify -> checkpoint -> commit -> push -> verify remote` succeeds on `main`.
- `last_proven_alive` is the latest checkpoint whose commit is verified on remote `main`.
- A dead session cannot authoritatively declare itself dead; a later independent session or auditor may classify what happened after `last_proven_alive`.
- Status vocabulary is exactly: `HEALTHY`, `DEGRADED`, `UNRELIABLE`, `POLICY_BLOCKED`, `TOOL_FAILED`, `BLOCKED`, `DEAD_OR_UNKNOWN`.
- Keep policy/tool failures distinct from model/session degradation. One failure is not proof of a hard platform limit.

## Verification and publication

Before commit/push, run:

```sh
python3 -B -m unittest discover -s tests -v
python3 -B scripts/verify.py
git diff --check
```

Work directly on `main`. Commit coherent repository changes and push to `origin main`; when publication matters, verify remote `main` equals local `HEAD`.

## Scope

Maintain the benchmark protocol, checkpoint integrity, verifier, schema, docs, baselines, and run evidence. Do not add frameworks, services, dashboards, telemetry systems, orchestration, or new benchmark machinery without an explicit task. Bootstrap/refactor work must not start the endurance-to-death benchmark.
