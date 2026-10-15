---
name: tdd
description: Use when the user or project instructions require test-driven development. Project instructions override this default method.
---

# TDD

Follow the project's TDD policy when it exists. Otherwise use this method for observable behavior or public type changes with a cheap, deterministic test path.

If TDD would require disproportionate harness work, brittle mocks, or unreliable infrastructure, say so and use the cheapest verification that still proves the behavior. Documentation, formatting, generated output, and presentation-only styling usually need verification rather than TDD.

## Shape the contract

Inspect the affected code, contract, and nearest existing test harness. Choose the test cases yourself. Ask the user only when the intended behavior is ambiguous, and frame the question as behavior, not test mechanics.

Tests specify behavior, not implementation. Prefer the nearest harness and the smallest focused test. Avoid brittle mocks, timing, global state, broad fixture churn, and assertions added only for coverage. Make flaky regression signals deterministic where practical.

If the project lacks a suitable harness, ask before installing or configuring tooling. For TypeScript, read [typescript.md](typescript.md).

## Run red-green

1. Write the test before touching production code.
2. Run it. Red means the expected behavioral failure, not a syntax, import, timeout, or unrelated failure.
3. Implement the smallest coherent change that passes the test.
4. Refactor while green, then run the focused tests, relevant project checks, and the real path when practical.

Use separate red and green commits when the project requires them or the user wants replayable proof. If implementation exposes a flaw in the test, fix the test only when the original expectation was wrong, and say why. If the behavior itself must change, ask first.

## Hold the line

- Preserve existing contracts unless changing them is part of the requested outcome.
- Do not weaken assertions or add implementation-specific checks merely to reach green.
- Report the red and green evidence and any verification gap.

Coverage, mutation testing, property testing, type testing, commit structure, and CI replay are project-selected enforcement. Honor them when configured; otherwise propose them only when their value is proportional to the change.
