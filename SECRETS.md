# Keeping secrets out of git

A minimal, layered setup. Each layer is cheap; together they make leaks hard.

## The layers

1. **`.gitignore`** — keeps `.env`, keys, and cert files untracked. Free, no tooling.
2. **Gitleaks pre-commit hook** — scans every commit locally and blocks it if a
   secret is found. Fast (milliseconds). Lives in `.pre-commit-config.yaml`.
3. **GitHub push protection** — server-side net that catches anything the local
   hook missed (e.g. a teammate who skipped it). This is the real guarantee.

> Hooks are **per-clone** and bypassable (`git commit --no-verify`). They're a
> convenience layer. The server-side scan is what makes it team-proof.

## One-time setup (each person, after cloning)

```bash
# Install pre-commit (once per machine)
pipx install pre-commit        # or: pip install pre-commit / brew install pre-commit

# Activate the hooks in this repo (once per clone)
pre-commit install
```

That's it. From now on, `git commit` runs gitleaks automatically.

## Daily use

Nothing changes. If a commit contains a secret, gitleaks blocks it:

```
  Finding:     AWS_SECRET=AKIA...
  Rule:        aws-access-token
  Commit:      (staged)
```

Fix it (remove the secret, use an env var), then commit again.

To scan the whole repo on demand:

```bash
gitleaks detect --source .          # working tree + history
```

## If a secret slips through

1. **Rotate it immediately.** Assume it's compromised the moment it was pushed —
   public *or* private. Revoke the key and issue a new one. This is the priority.
2. Remove it from history if needed (`git filter-repo` or BFG), but rotation
   comes first — scrubbing history does not un-leak a key that was already pushed.

## Maintenance

- `pre-commit autoupdate` every month or so — pulls the latest detection rules.
- Keep hooks fast. If they get slow, people start using `--no-verify`.

## Adding a config (`.env.example`)

Commit a `.env.example` with **placeholder** values so teammates know which
variables exist, without exposing real ones. The real `.env` stays gitignored.
