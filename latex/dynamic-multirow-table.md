# Dynamic Multi-Row Table with N Columns

**Problem:** Build a table where the number of columns is configurable at runtime (e.g. 5, 10, 20), and data arrives one item at a time during document processing — not all at once.

**Origin:** MCQ answersheet in oakwoodquestions — each `\mcq` call adds one question number, and the table must wrap into rows of N columns with a two-row layout (label row + blank answer row).

## Core Idea

1. **Accumulate cells into a buffer macro** as data arrives, one `\item` call at a time.
2. **Track position** with a counter. When it reaches N, **flush** the buffer as a complete row pair.
3. At render time, **pad** any incomplete final row with empty cells before flushing.
4. **Build the column spec dynamically** with a recursive macro so any N works.

## Implementation Skeleton

```latex
% --- Configuration ---
\newcommand{\mycols}{10}           % number of columns per row

% --- State ---
\newcount\mypos                     % current position within the row (0-based)
\global\mypos=0\relax
\newcommand{\myheaderbuf}{}         % accumulates label cells for current row
\let\myheaderbuf\empty
\newcommand{\mytabledata}{}         % accumulates completed row pairs
\let\mytabledata\empty

% --- Called once per data item ---
\newcommand{\additem}[1]{%
    % Append cell to header buffer (with & separator if not first)
    \ifnum\mypos>0\relax
        \edef\@temprow{& #1}%
    \else
        \edef\@temprow{#1}%
    \fi
    \expandafter\g@addto@macro\expandafter\myheaderbuf\expandafter{\@temprow}%
    % Advance position
    \global\advance\mypos by 1\relax
    % If row is full, flush it
    \ifnum\mypos=\mycols\relax
        \flushrows
        \global\mypos=0\relax
    \fi
}

% --- Flush: append header row + blank row to table data ---
\newcommand{\flushrows}{%
    % Row 1: labels
    \expandafter\g@addto@macro\expandafter\mytabledata\expandafter{\myheaderbuf}%
    \g@addto@macro\mytabledata{\\\hline}%
    % Row 2: blank cells (N-1 ampersands)
    \buildblankrow
    \g@addto@macro\mytabledata{\\\hline}%
    % Reset buffer
    \let\myheaderbuf\empty
}

% --- Build N-1 ampersands for the blank row ---
\newcount\blankcnt
\newcommand{\buildblankrow}{%
    \global\blankcnt=1\relax
    \blankrowloop
}
\newcommand{\blankrowloop}{%
    \ifnum\blankcnt<\mycols\relax
        \g@addto@macro\mytabledata{&}%
        \global\advance\blankcnt by 1\relax
        \blankrowloop
    \fi
}

% --- Pad incomplete final row before rendering ---
\newcommand{\padrow}{%
    \ifnum\mypos>0\relax
        \padrowloop
    \fi
}
\newcommand{\padrowloop}{%
    \ifnum\mypos<\mycols\relax
        \g@addto@macro\myheaderbuf{&}%
        \global\advance\mypos by 1\relax
        \padrowloop
    \else
        \flushrows
        \global\mypos=0\relax
    \fi
}

% --- Build column spec dynamically: |c|c|c|...|c| ---
\newcount\colcnt
\newcommand{\buildcolspec}{%
    \global\colcnt=0\relax
    \colspecloop
}
\newcommand{\colspecloop}{%
    \ifnum\colcnt<\mycols\relax
        |c%
        \global\advance\colcnt by 1\relax
        \colspecloop
    \else
        |%
    \fi
}

% --- Render the table ---
\newcommand{\rendertable}{%
    \padrow  % flush any incomplete row
    \begin{tabular}{\buildcolspec}
        \hline
        \mytabledata
    \end{tabular}
}
```

## Key Lessons

- **Use `\g@addto@macro` (global append)** — data accumulates across TeX group boundaries (environments open/close groups that revert local assignments).
- **Recursive macros, not `\loop..\repeat`** — `\loop` defines `\iterate` locally; if a group closes mid-loop (e.g. `\end{...}`), `\iterate` is destroyed. Recursive macros survive because they're defined in the outer scope.
- **Pad before rendering** — the last row is almost never exactly full. Pad with empty `&` cells so the column count matches.
- **`\edef` with `\unexpanded`** — when building rows containing user text, wrap it in `\unexpanded{...}` to prevent premature expansion of math, font commands, etc.
