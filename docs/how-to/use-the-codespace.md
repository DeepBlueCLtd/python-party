# How to use the Codespace

> **How-to** — a focused recipe. For the guided first run, see the
> [Start here tutorial](../tutorials/01-start-here.md).

## Open a Codespace

1. On the repository page: **Code → Codespaces → Create codespace on
   `claude/zealous-davinci-n4ssvn`** (or your branch).
2. Wait for provisioning. The devcontainer pins **Python 3.9.4** to match the target system
   (ADR 0007) and runs `make bootstrap` automatically.

## Everyday commands

| Command | What it does |
|---|---|
| `make` or `make help` | List available targets |
| `make bootstrap` | Install/refresh the toolchain (deps + dev + docs) |
| `make verify` | Lint + run the test suite (the "is it good?" check) |
| `make docs-serve` | Live-preview the HTML docs at <http://localhost:8000> |
| `make docs` | Build the static HTML site (strict) into `site/` |

The not-yet-implemented pipeline targets (`generate`, `gen-schema-docs`, `pipeline`,
`compare`, `bundle`) print a pointer to `specs/001-codespace-xml-scaffold/tasks.md` and exit
non-zero — they become real as the implementation tasks land.

## Confirm the Python version

```bash
python --version    # expected: Python 3.9.4
```

If this is not 3.9.4 inside the Codespace, the devcontainer didn't apply — rebuild the
container (**Cmd/Ctrl-Shift-P → Codespaces: Rebuild Container**).

## Rerun provisioning

If `bootstrap` didn't finish (e.g. a transient network issue), just run it again:

```bash
make bootstrap
```

## Local fallback

Everything above works locally too — you only need Python 3.9.x and `make`. Run
`make bootstrap` once, then the same targets. See
ADR 0006 for why we keep both paths.
