# Safe Global Macro Accumulation for Table Rows

**Problem:** Build table rows incrementally — each call to a command appends one row to a macro that is rendered later. Must survive TeX group boundaries and handle user text (math, font commands) without breaking.

**Origin:** oakwoodquestions scoresheet — `\addtoscore` appends rows to `\oakwood@scoredata`, rendered later inside `\longtable`.

## The Pattern

```latex
% 1. Initialize the accumulator
\newcommand{\mytabledata}{}
\let\mytabledata\empty

% 2. Build one row in a temporary macro using \edef
%    - \unexpanded{...} protects user text from expansion
%    - \noexpand delays \\ and \hline (they must expand at render time, not now)
\edef\temprow{%
    \unexpanded{#1}        % user text (math, fonts, etc.)
    &                      % column separator
    \unexpanded{#2}        % more user text
    & #3                   % safe expandable content (e.g. a number)
    & \noexpand\\          % row terminator (delayed)
    \noexpand\hline        % rule (delayed)
}%

% 3. Append to accumulator using triple-expandafter
\expandafter\g@addto@macro\expandafter\mytabledata\expandafter{\temprow}
```

## Why Triple Expandafter

`\g@addto@macro` expects `\macro{tokens}`. We need:
1. First `\expandafter` jumps over `\g@addto@macro`
2. Second `\expandafter` jumps over `\mytabledata`
3. Third `\expandafter` expands `\temprow` into its replacement text

Without this, `\g@addto@macro` would store the token `\temprow` literally, not its contents.

## What NOT to Do

| Mistake | Why it fails |
|---------|-------------|
| Use `\xappto` (etoolbox) | Different expansion timing — stored macros like `\oakwood@scorepoints` may not expand correctly |
| Store font commands (`\bfseries`, `\sffamily`) in the accumulated macro | Font declarations leak across cells. Apply formatting in the column spec (`>{\bfseries}c`) or at render time only |
| Use `\xdef` instead of `\edef` + `\g@addto@macro` | `\xdef` fully expands everything — destroys `\\`, `\hline`, math commands. `\edef` + `\unexpanded` gives precise control |

## When to Use This

- Building any table (longtable, tabular, tabularx) row-by-row during document processing
- Accumulating data across multiple calls that will be rendered once at the end
- Any situation where content is collected inside groups but must persist globally
