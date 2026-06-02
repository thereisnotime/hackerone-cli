# Security Policy

## Reporting a vulnerability

If you find a security issue in this tool, please do not open a public GitHub issue.

Report it privately via [GitHub's private vulnerability reporting](https://github.com/thereisnotime/hackerone-cli/security/advisories/new) or email the maintainer directly.

Include:
- A description of the issue and its potential impact
- Steps to reproduce
- Any suggested fix if you have one

You'll get a response within a few days. If the issue is confirmed, a fix will be released as soon as possible.

## Scope

This tool is a CLI client for the HackerOne API. It handles API credentials locally — it does not transmit them anywhere except to `api.hackerone.com` and `hackerone.com`. Relevant areas:

- Credential handling (`.env` file, environment variables, CLI flags)
- API request construction
- Output parsing and display
