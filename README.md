# Agent Capability Lab

Zero-cost empirical lab for practical agent capability and session endurance. Progress counts only when it is independently verifiable.

## Protocol

`probe -> verify -> checkpoint -> commit -> push -> verify remote`

A step is remote-proven alive only after remote `main` is verified to contain its commit. The latest such checkpoint is `last_proven_alive`. A run may span at most three independent chats, which remain separate evidence units.

Canonical docs: [`docs/protocol.md`](docs/protocol.md) and [`docs/design.md`](docs/design.md). Preserved audit evidence lives in `docs/baselines/`.

## Boundaries

The repository stays intentionally zero-cost and uses Python standard library only. Agent Runtime is execution infrastructure outside benchmark authority and remains unchanged by project work. Bootstrap/refactor work does not start the endurance benchmark.

## Verify

```sh
python3 -B -m unittest discover -s tests -v
python3 -B scripts/verify.py
```

Validate one checkpoint with `python3 -B scripts/checkpoint.py validate <checkpoint>`; for step 2+, add `--previous <checkpoint>`.

## Layout

- `AGENTS.md` — agent working rules.
- `docs/protocol.md` — normative benchmark protocol.
- `docs/design.md` — repository design.
- `docs/baselines/` — preserved bounded audit evidence.
- `schemas/` — checkpoint contract.
- `scripts/` — checkpoint and repository verification logic.
- `tests/` — standard-library tests.
- `runs/` — append-only run evidence; empty during bootstrap.
