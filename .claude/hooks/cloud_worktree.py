#!/usr/bin/env python3
"""SessionStart hook: give every Claude cloud session its own git worktree.

Runs only in Claude Code cloud sessions (CLAUDE_CODE_REMOTE=true); does
nothing on your own computer. For each session it creates a worktree at
.claude/worktrees/session-<id> on a new branch claude/session-<id>, based
on whatever commit the session started from, then tells Claude to do all
its work there. Safe to run repeatedly (resume / clear / compact reuse the
same worktree). It never blocks a session: on any error it just reports.
"""
import json
import os
import re
import subprocess
import sys


def git(*args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )


def emit(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": text,
        }
    }))
    sys.exit(0)


def main():
    if os.environ.get("CLAUDE_CODE_REMOTE") != "true":
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    project = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    top = git("rev-parse", "--show-toplevel", cwd=project)
    if top.returncode != 0:
        sys.exit(0)
    root = top.stdout.strip()

    # Already inside a linked worktree? Nothing to do.
    gd = git("rev-parse", "--absolute-git-dir", cwd=root).stdout.strip()
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=root).stdout.strip()
    if gd and common and os.path.realpath(gd) != os.path.realpath(common):
        sys.exit(0)

    sid = (os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID")
           or data.get("session_id") or "unknown")
    short = re.sub(r"[^A-Za-z0-9]", "", sid.replace("session_", ""))[:12] or "unknown"
    branch = f"claude/session-{short}"
    wt_rel = f".claude/worktrees/session-{short}"
    wt = os.path.join(root, wt_rel)

    # Keep worktrees out of git status without touching .gitignore.
    exclude = os.path.join(common or os.path.join(root, ".git"), "info", "exclude")
    try:
        os.makedirs(os.path.dirname(exclude), exist_ok=True)
        existing = open(exclude).read() if os.path.exists(exclude) else ""
        if ".claude/worktrees/" not in existing:
            with open(exclude, "a") as f:
                f.write("\n.claude/worktrees/\n")
    except OSError:
        pass

    base = git("rev-parse", "--abbrev-ref", "HEAD", cwd=root).stdout.strip() or "HEAD"

    if not os.path.isdir(wt):
        os.makedirs(os.path.dirname(wt), exist_ok=True)
        has_branch = git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", cwd=root).returncode == 0
        args = ["worktree", "add", wt, branch] if has_branch else ["worktree", "add", "-b", branch, wt, "HEAD"]
        r = git(*args, cwd=root)
        if r.returncode != 0:
            emit("Cloud worktree hook could not create a worktree "
                 f"({r.stderr.strip()[:300]}). Work in {root} as usual.")

    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if env_file:
        try:
            with open(env_file, "a") as f:
                f.write(f"export CLAUDE_SESSION_WORKTREE='{wt}'\n")
        except OSError:
            pass

    emit(
        f"This cloud session has its own git worktree: {wt} (branch {branch}, "
        f"created from {base}). Do ALL work there: run `cd {wt}` before any "
        f"command, and read, edit, create and commit files only under that path. "
        f"Do not edit files or commit in {root} itself, and never commit to "
        f"{base} directly. Push with `git push -u origin {branch}`. If your "
        f"session instructions name a different branch to push to, push this "
        f"worktree's commits there instead (`git push origin HEAD:<that-branch>`)."
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # never break session start
        emit(f"Cloud worktree hook failed ({e}); work in the project directory as usual.")
