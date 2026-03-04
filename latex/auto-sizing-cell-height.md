# Auto-Sizing Table Cell Height from Content

**Problem:** Create a table cell whose height adapts to the length of content that isn't actually displayed in that cell. For example: an answer sheet where the blank writing area is sized to match the hidden solution text.

**Origin:** oakwoodquestions FRQ answersheet — each answer cell is sized to fit the solution text, even though the cell is left blank for students.

## The Pattern

```latex
% 1. Typeset the content invisibly in a \vbox at the target column width
%    \linewidth minus other column widths gives the available space.
\setbox0=\vbox{%
    \hsize=\dimexpr\linewidth - 5em - 4\tabcolsep\relax  % target column width
    \noindent #1%   % the content to measure
}%

% 2. Get the total height (height + depth)
\@tempdima=\dimexpr \ht0 + \dp0 \relax

% 3. Convert to a line count (divide by \baselineskip)
\@tempcnta=0\relax
\@whiledim \@tempdima>0pt \do{%
    \advance\@tempcnta by 1\relax
    \advance\@tempdima by -\baselineskip\relax
}%

% 4. Add padding (extra comfort lines)
\advance\@tempcnta by 1\relax  % 1 extra line of padding

% 5. Enforce a minimum (e.g. 4 lines)
\ifnum\@tempcnta<4\relax
    \@tempcnta=4\relax
\fi

% 6. Create a vertical strut with the computed height
\edef\mystrut{\noexpand\rule{0pt}{\the\@tempcnta\noexpand\baselineskip}}

% 7. Place the strut in the table cell — it forces the row height
% In the table row:  & \mystrut \\
```

## Key Details

- **`\setbox0=\vbox{...}`** typesets in a vertical box without placing it on the page — purely for measurement.
- **`\hsize` inside `\vbox`** controls the paragraph width for line-breaking, so the measured height reflects how tall the content would be at that specific column width.
- **`\ht0 + \dp0`** gives the full vertical extent (ascenders + descenders).
- **`\rule{0pt}{height}`** is a zero-width vertical strut — invisible but forces the row to be at least that tall.
- **Store as `\edef`** with `\noexpand\rule` and `\noexpand\baselineskip` so the strut definition can be embedded in accumulated table data.

## When to Use This

- Answer sheets / exam papers where blank space must match hidden content
- Any table where one column's height should adapt to content that appears elsewhere
- Dynamic forms where writing areas need to be proportional to expected answer length
