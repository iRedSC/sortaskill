# TypeScript modeling patterns

Use these as choices, not defaults. Prefer the simplest type that keeps callers honest.

## Exclusive states

An optional-field bag is fine when fields vary independently. When states are exclusive, name them.

```ts
// Bad: contradictory combinations compile.
type DiffState = { loading: boolean; diff?: GitDiff; error?: string };

// Better when the states are exclusive.
type DiffState =
  | { kind: "loading" }
  | { kind: "ready"; diff: GitDiff }
  | { kind: "failed"; error: string };
```

Handle closed variants exhaustively:

```ts
function render(state: DiffState): string {
  switch (state.kind) {
    case "loading": return "Loading";
    case "ready": return state.diff.text;
    case "failed": return state.error;
    default: {
      const unreachable: never = state;
      return unreachable;
    }
  }
}
```

## Stronger collections

Keep `T[]` when empty is valid. Strengthen it only when empty would make the operation partial.

```ts
type NonEmpty<T> = [T, ...T[]];

// Bad: the signature lies about the empty case.
const newest = (items: Item[]): Item => items[0]!;

// Better when the caller guarantees at least one item.
const newest = (items: NonEmpty<Item>): Item => items[0];

// Also valid when empty is expected.
const maybeNewest = (items: Item[]): Item | undefined => items[0];
```

Represent structure directly when it matches the domain, such as `[Key, Value][]` for entries. Do not claim a representation enforces facts it does not, such as a positive number without validation.

## Domain primitives

Brand a primitive when mixing two valid values would be a real bug. Keep construction controlled.

```ts
declare const userIdBrand: unique symbol;
type UserId = string & { readonly [userIdBrand]: true };

function parseUserId(input: string): UserId {
  if (!isUuid(input)) throw new Error("Invalid user id");
  return input as UserId;
}
```

The assertion is contained at the boundary after validation. Do not brand every identifier by reflex.

## Untrusted boundaries

External data starts as `unknown`. Use the project's validation library rather than repeating property assertions.

```ts
const User = z.object({ id: z.string().uuid(), name: z.string() });
type User = z.infer<typeof User>;

const user = User.parse(input);
```

Once parsed, avoid revalidating the same value throughout the call chain.

## Assertions and narrowing

Prefer compiler-supported facts first: discriminants, `in`, `typeof`, `instanceof`, and control flow. A type guard must verify its entire claim. Use an assertion only when interop or a controlled boundary leaves the compiler unable to express an established fact.

```ts
// Bad: no evidence supports the claim.
const user = input as User;

// Better: validate at the boundary.
const user = User.parse(input);
```

Use `satisfies` to check a value without widening its literals:

```ts
const config = { theme: "dark", columns: 3 } satisfies Config;
```

## Ownership and derivation

Derive a type when another definition owns the same contract:

```ts
type RenderInput = Pick<GeneratedMessage, "count" | "items">;
type HandlerResult = Awaited<ReturnType<typeof handleRequest>>;
```

Create a new named type when the domain owns a distinct contract, even if its current fields resemble another type.

## Object parameters

Use an object when positional arguments are easy to swap or likely to evolve:

```ts
// Bad: valid values in the wrong order still compile.
moveSelection(uri, startLine, startColumn, endLine, endColumn);

// Better for a multi-part operation.
moveSelection({ uri, startLine, startColumn, endLine, endColumn });
```

Keep simple conventional functions simple, such as `clamp(value, min, max)`.
