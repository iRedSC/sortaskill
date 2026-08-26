# TypeScript TDD options

Inspect the package manager, test runner, TypeScript configuration, source and test paths, and CI before recommending changes. Extend the existing harness when it supports the contract.

Explain relevant options to the user before installing or configuring tooling:

| Need | Options | Recommend when |
|---|---|---|
| Runtime behavior | Existing runner; Vitest when none exists | A deterministic public behavior can run locally |
| Public type behavior | Existing convention; Vitest type tests; `tsd` | Exported inference or accepted and rejected inputs are the contract |
| Invariants over many inputs | `fast-check` | Examples would miss meaningful combinations or shrinking helps diagnosis |
| Coverage | Runner coverage; changed-line coverage | The project wants a gap signal, not a proxy for correctness |
| Mutation testing | StrykerJS | Assertion strength justifies the runtime and maintenance cost |
| Replayable red | Separate red and green commits; CI replay | The project wants proof that tests fail without the implementation |

Recommend the smallest set that proves the requested contract. State setup cost, CI cost, and what each option catches. Do not install tools, add thresholds, or change CI until the user chooses or project instructions require them.

When selected, preserve failing property-test seeds, cover positive and negative type behavior, and explain mutation exclusions rather than lowering a threshold silently.
