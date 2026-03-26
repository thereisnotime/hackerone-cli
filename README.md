# HackerOne CLI

An unofficial CLI client for [HackerOne](https://hackerone.com/). Manage your profile, reports, programs, payments, and more from the terminal. Built on the official [HackerOne API v1](https://api.hackerone.com/).

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Update](#update) | [Uninstall](#uninstall)
- [Configuration](#configuration)
  - [Credentials](#credentials) | [Custom .env File](#custom-env-file)
- [Usage](#usage)
  - [Global Options](#global-options) | [JSON Output](#json-output)
- [Commands](#commands)
  - Hacker: [Programs & Scope](#programs--scope) | [Reports](#reports) | [Payments](#payments) | [Account](#account)
  - Program Manager: [Organization](#organization--program-management)
- [Development](#development)
- [License](#license)

## Quick Start

```sh
git clone git@github.com:thereisnotime/hackerone-cli.git
cd hackerone-cli
uv tool install -e .
echo 'HACKERONE_USERNAME="your-username"' > .env
echo 'HACKERONE_API_KEY="your-api-key"' >> .env
hackerone programs 5
```

## Installation

**Requirements:** Python >= 3.10, a [HackerOne API key](https://hackerone.com/settings/api_token/edit)

```sh
git clone git@github.com:thereisnotime/hackerone-cli.git
cd hackerone-cli
uv tool install -e .
```

For rendered markdown in `report` and `program` output, install with the optional `markdown` extra:

```sh
uv tool install -e ".[markdown]"
```

This installs `hackerone` globally so you can run it from anywhere.

### Update

```sh
cd hackerone-cli
git pull
uv tool install -e . --force
```

### Uninstall

```sh
uv tool uninstall hackerone-cli
```

### Other install methods

<details>
<summary>Click to expand</summary>

**With pip:**

```sh
pip install -e .
```

**With uv (project-local):**

```sh
uv sync                     # install in .venv
uv run hackerone programs    # run via uv
# or activate the venv directly:
source .venv/bin/activate
hackerone programs
```

**With just:**

```sh
just install
```

</details>

## Configuration

### Credentials

Credentials are resolved in this order (first match wins):

| Method | Example |
|---|---|
| CLI flags | `hackerone -u myuser -k mykey programs` |
| Environment variables | `export HACKERONE_USERNAME="..."` / `export HACKERONE_API_KEY="..."` |
| `.env` file | Auto-loaded from the current directory |

### Custom .env File

```sh
hackerone --env-file /path/to/.env programs
```

Get your API key from [HackerOne Settings](https://hackerone.com/settings/api_token/edit).

## Usage

```sh
hackerone <command> [args] [options]
```

### Global Options

| Flag | Short | Description |
|---|---|---|
| `--json` | `-j` | Machine-readable JSON output |
| `--username <user>` | `-u` | HackerOne username (overrides env) |
| `--api-key <key>` | `-k` | HackerOne API key (overrides env) |
| `--env-file <path>` | | Path to a custom `.env` file |
| `--verbose` | `-v` | Show progress and debug info |

### JSON Output

Any command supports `--json` / `-j` for machine-readable output. Useful for scripting, piping into `jq`, or integrating with other tools.

```sh
hackerone programs 5 --json
hackerone program security -j | jq '.attributes.handle'
```

## Commands

### Command Reference

| Command | Description |
|---|---|
| [`programs [max]`](#programs-max) | List programs you have access to (default: 10) |
| [`program <handle>`](#program-handle) | Program details — scope, policy, bounty info |
| [`csv <handle>`](#csv-handle) | Download CSV scope file (public only) |
| [`scope <csv> [outfile]`](#scope-csv-outfile) | Extract in-scope targets from CSV |
| [`burp <handle>`](#burp-handle) | Download Burp Suite config (public only) |
| [`reports`](#reports-1) | List your submitted reports |
| [`report <id>`](#report-id) | Full report details |
| [`balance`](#balance) | Current balance |
| [`earnings`](#earnings) | Bounty earnings |
| [`payouts`](#payouts) | Payout history |
| [`profile`](#profile) | Your profile info |
| [`help`](#help) | Show available commands |
| | **Program Management** (requires org API token) |
| [`org`](#org) | Show your organization info |
| [`org-reports <handle> [max]`](#org-reports-handle-max) | List reports submitted to your program |
| [`org-report <id>`](#org-report-id) | Get a report submitted to your program |

---

### Programs & Scope

#### `programs [max]`

List recently updated programs you have access to, including private ones. Defaults to 10 results.

<details>
<summary>Example output</summary>

```
$ hackerone programs 2

Programs
----------------------------------------
Program: Example 1
Handle: example_1
State: open
Availability: Public
Available since: 2027-07-10T17:10:05.936Z
Bounty Splitting: no
Bookmarked: yes
----------------------------------------
Program: Example 2
Handle: example_2
State: open
Availability: Public
Available since: 2027-05-16T16:00:37.600Z
Bounty Splitting: yes
Bookmarked: no
----------------------------------------

Got 2 results!
```

</details>

#### `program <handle>`

Get details about a specific program — scope, policy, bounty info. Works with both public and private programs you have access to.

Find the handle via `programs` or from the URL: `https://hackerone.com/<handle>`.

<details>
<summary>Example output</summary>

```
$ hackerone program security

Program
----------------------------------------
Name: HackerOne
Handle: security
State: open
Availability: Public
Creation date: 2013-11-06T00:00:00.000Z
Bounty: yes
Bounty Splitting: yes

Scope
--------------------
Asset: hackerone.com
Type: URL
State: In-Scope
Bounty: yes
Max Severity: critical
--------------------
```

</details>

#### `csv <handle>`

Download the CSV scope file from a public program. Uses a web endpoint (not the API), so only works with public programs.

```
$ hackerone csv security
Filename: scopes_for_security_(...).csv
```

#### `scope <csv> [outfile]`

Extract in-scope domains, URLs, IPs, CIDRs, and wildcards from a downloaded CSV scope file. Output defaults to `inscope.txt`. Useful for feeding into recon tools.

<details>
<summary>Example output</summary>

```
$ hackerone scope scopes_for_example.csv targets.txt

In-Scope
----------------------------------------
*.example.com
127.0.0.0/24
test.example.com
----------------------------------------
File 'targets.txt' saved!
```

</details>

#### `burp <handle>`

Download the Burp Suite project configuration file from a public program.

```
$ hackerone burp security
Filename: security-(...).json
```

---

### Reports

#### `reports`

List your submitted reports with key metadata.

<details>
<summary>Example output</summary>

```
$ hackerone reports

Reports
----------------------------------------
ID: 1234567
Title: Information Exposure through phpinfo() at example.com
State: triaged
Date: 2027-03-13T16:48:17.286Z
CWE: CWE-200
Program: example
Severity: low
CVSS: 3.7
----------------------------------------
```

</details>

#### `report <id>`

Full details on a specific report — severity, comments, bounties, content, CVE/CWE, and more.

<details>
<summary>Example output</summary>

```
$ hackerone report 1234567

Report
----------------------------------------
ID: 1234567
Title: Stored XSS on example.com
State: resolved
Date: 2027-06-01T00:54:43.308Z
Program: example
Severity: medium
CWE: CWE-79
Weakness: Cross-site Scripting (XSS) - Stored

Comments
--------------------
@triager

Thanks for the report. We're looking into it.

--------------------
@example awarded a bounty (1337.00 + 0.00)!

----------------------------------------
```

</details>

---

### Payments

#### `balance`

Check your current balance (in the currency set on your profile).

```
$ hackerone balance
Balance: 1337.0
```

#### `earnings`

List your bounty earnings by program.

<details>
<summary>Example output</summary>

```
$ hackerone earnings

Earnings
----------------------------------------
Amount: 1337 USD
Date: 2016-02-02T04:05:06.000Z
Program: HackerOne
Report: RXSS at example.hackerone.com
----------------------------------------
```

</details>

#### `payouts`

List your processed payouts.

<details>
<summary>Example output</summary>

```
$ hackerone payouts

Payouts
----------------------------------------
Amount: 1337
Status: sent
Date: 2016-02-02T04:05:06.000Z
Provider: Paypal
----------------------------------------
```

</details>

---

### Account

#### `profile`

Show your profile info. Requires at least one submitted report (the API derives your profile from the reporter field).

<details>
<summary>Example output</summary>

```
$ hackerone profile

Profile
----------------------------------------
ID: 1234567
Username: example
Reputation: 1337
Name: Hacker Man
Creation Date: 2020-11-24T16:20:24.066Z
Bio: My beautiful bio
Website: https://example.com/
Location: Right here
----------------------------------------
```

</details>

#### `help`

Show all available commands and their arguments.

---

### Organization / Program Management

These commands use the **program management API** and require an organization-level API token (created in Organization Settings > API Tokens on HackerOne), not a hacker profile token.

You can use both token types in the same `.env` by switching with `--username` / `--api-key` flags, or use separate `.env` files with `--env-file`.

#### `org`

Show your organization info — ID, handle, name, and permissions.

```
$ hackerone org

Organization
----------------------------------------
ID: 12345
Handle: mycompany
Name: My Company
Created: 2025-01-01T00:00:00.000Z
Permissions: report_management, reward
----------------------------------------
```

#### `org-reports <handle> [max]`

List reports submitted to your program. Defaults to 10 results. Shows reporter, severity, state, and more.

```
$ hackerone org-reports mycompany 5

Reports for 'mycompany'
----------------------------------------
ID: 1234567
Title: XSS on login page
State: triaged
Date: 2027-03-13T16:48:17.286Z
Reporter: hackerman
Severity: high
CVSS: 8.3
----------------------------------------

Showing 1 of 1 results.
```

#### `org-report <id>`

Full details on a report submitted to your program, including content, activities, and metadata.

```
$ hackerone org-report 1234567
```

## Development

```sh
just install      # Install dependencies
just check        # Run lint + format checks
just fix          # Auto-fix lint and formatting
just test         # Smoke test against the live API
just run <args>   # Run the CLI
```

Or without just:

```sh
uv sync
uv run ruff check .
uv run ruff format .
```

## License

[MIT](./LICENSE)
