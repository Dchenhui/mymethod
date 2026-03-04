# mymethod

Personal library of reusable code patterns and techniques.

Each file documents a self-contained pattern — the logic and approach, not the project-specific implementation. Patterns are extracted from working projects after they've been tested and proven.

## Index

### LaTeX

| File | Pattern | Origin |
|------|---------|--------|
| `latex/dynamic-multirow-table.md` | Dynamic N-column table with two-row groups (label + blank), built at runtime via macro accumulation | oakwoodquestions MCQ answersheet |
| `latex/global-macro-accumulation.md` | Safe global row-building with `\g@addto@macro` and triple-expandafter — avoiding expansion pitfalls | oakwoodquestions scoresheet |
| `latex/recursive-environment-closing.md` | Recursively closing nested environments without `\loop..\repeat` (which breaks across `\end{}` group boundaries) | oakwoodquestions nested questions |
| `latex/auto-sizing-cell-height.md` | Measuring invisible text to auto-size table cell heights | oakwoodquestions FRQ answersheet |
