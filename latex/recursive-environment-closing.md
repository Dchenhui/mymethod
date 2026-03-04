# Recursive Environment Closing (Not \loop..\repeat)

**Problem:** Close a variable number of nested LaTeX environments in a loop. `\loop..\repeat` breaks because `\end{environment}` closes a TeX group, destroying the loop's internal `\iterate` token.

**Origin:** oakwoodquestions — questions can nest 4 levels deep. When a new top-level question starts, all open sub-levels must close.

## Why \loop..\repeat Fails

```latex
% THIS BREAKS after the first iteration:
\loop
    \ifnum\value{nestdepth}>0
    \end{mylist}\addtocounter{nestdepth}{-1}%
\repeat
```

`\loop` defines `\iterate` locally. `\end{mylist}` closes a TeX group, which reverts `\iterate` to its outer-scope value (undefined). The loop stops after one iteration with no error — a silent bug.

## The Fix: Recursive Macro

```latex
\newcounter{nestdepth}

% Close nested environments down to a target depth.
% #1 = target (stop when nestdepth <= #1)
\newcommand{\closeneststo}[1]{%
    \ifnum\value{nestdepth}>#1
        \end{mylist}%
        \addtocounter{nestdepth}{-1}%
        \closeneststo{#1}%   % recursive call — survives the group close
    \fi
}

% Convenience: close everything
\newcommand{\closenests}{\closeneststo{0}}
```

The recursive macro works because it's defined in the **outer scope** — `\end{mylist}` closes an inner group, but the macro name `\closeneststo` still exists in the outer scope and can be called again.

## When to Use This

- Any time you need to loop over `\end{environment}` calls
- Cleaning up nested lists/environments at end-of-document (`\AtEndDocument`)
- Auto-closing environments when transitioning between sections or levels

## General Rule

**Never use `\loop..\repeat` if the loop body closes a TeX group** (`\end{...}`, `\endgroup`, `}`). Use recursion instead.
