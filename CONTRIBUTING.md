# Contributing

## Setup

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```sh
git clone git@github.com:thereisnotime/hackerone-cli.git
cd hackerone-cli
just install
```

## Development workflow

```sh
just pytest       # run offline tests (no credentials needed)
just check        # lint + format check
just fix          # auto-fix lint and formatting issues
just test         # smoke test against the live API (requires credentials in .env)
just run <args>   # run the CLI locally
```

## Making changes

- Keep changes focused — one thing per PR.
- Run `just fix && just pytest` before pushing.
- If you add a new command, add corresponding tests in `tests/test_cli.py` for the offline cases (arg validation, error handling).

## Cutting a release

Releases are automated via GitHub Actions on version tags. To cut one:

```sh
just release 1.2.3
```

This bumps `__version__` in `hackerone.py`, commits, pushes, and tags — the release workflow handles the rest.

## Pull requests

- Target the `main` branch.
- Include a short description of what changed and why.
- If it fixes a bug, mention the reproduction steps.
