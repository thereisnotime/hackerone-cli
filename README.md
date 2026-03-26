# HackerOne CLI

An unofficial CLI client for the [HackerOne](https://hackerone.com/) platform. Manage your profile, reports, programs, payments, and more — straight from the terminal.

Built on the official [HackerOne API v1](https://api.hackerone.com/).

---

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Modules](#modules)
  - [Programs & Scope](#programs--scope) — `programs`, `program`, `scope`, `csv`, `burp`
  - [Reports](#reports) — `reports`, `report`
  - [Payments](#payments) — `balance`, `earnings`, `payouts`
  - [Account](#account) — `profile`, `help`
- [Development](#development)
- [License](#license)

---

## Quick Start

```sh
git clone git@github.com:thereisnotime/hackerone-cli.git
cd hackerone-cli
uv sync
echo 'HACKERONE_USERNAME="your-username"' > .env
echo 'HACKERONE_API_KEY="your-api-key"' >> .env
uv run hackerone programs 5
```

---

## Installation

**Requirements:** Python >= 3.10, a [HackerOne API key](https://hackerone.com/settings/api_token/edit)

### With uv (recommended)

```sh
git clone git@github.com:thereisnotime/hackerone-cli.git
cd hackerone-cli
uv sync
```

### With pip

```sh
git clone git@github.com:thereisnotime/hackerone-cli.git
cd hackerone-cli
pip install -e .
```

### With just

If you have [just](https://github.com/casey/just) installed:

```sh
just install
```

Run `just` to see all available recipes.

---

## Configuration

Create a `.env` file in the project root:

```sh
HACKERONE_USERNAME="your-username"
HACKERONE_API_KEY="your-api-key"
```

Or export them directly:

```sh
export HACKERONE_USERNAME="your-username"
export HACKERONE_API_KEY="your-api-key"
```

You can get your API key from [HackerOne Settings](https://hackerone.com/settings/api_token/edit).

---

## Usage

```sh
# With uv
uv run hackerone <command> [args]

# With pip install
hackerone <command> [args]

# With just
just run <command> [args]
```

### JSON Output

Any command supports `--json` (or `-j`) for machine-readable output. Great for scripting, piping into `jq`, or integrating with other tools.

```sh
uv run hackerone programs 5 --json
uv run hackerone program security -j | jq '.attributes.handle'
```

---

## Modules

| Command | Description |
|---|---|
| `programs [max]` | List programs you have access to (default: 10) |
| `program <handle>` | Details on a specific program (scope, policy, bounty info) |
| `scope <csv> [outfile]` | Extract in-scope targets from a CSV file |
| `csv <handle>` | Download CSV scope file (public programs only) |
| `burp <handle>` | Download Burp Suite config (public programs only) |
| `reports` | List your submitted reports |
| `report <id>` | Full details on a specific report |
| `balance` | Check your current balance |
| `earnings` | List your bounty earnings |
| `payouts` | List your payouts |
| `profile` | Your profile info |
| `help` | Show available commands |

### Programs & Scope

#### `programs [max]`

List recently updated programs you have access to, including private ones. Defaults to 10 results.

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

#### `program <handle>`

Get details about a specific program — scope, policy, bounty info. Works with both public and private programs (if you have access).

Find the handle via `programs` or from the URL: `https://hackerone.com/<handle>`.

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

#### `csv <handle>`

Download the CSV scope file from a public program. This uses a web endpoint, not the API.

```
$ hackerone csv security

Filename: scopes_for_security_(...).csv
```

#### `scope <csv> [outfile]`

Parse a downloaded CSV scope file and extract in-scope domains, URLs, IPs, CIDRs, and wildcards into a text file. Useful for feeding into other recon tools.

Output file defaults to `inscope.txt`.

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

#### `burp <handle>`

Download the Burp Suite project configuration file from a public program.

```
$ hackerone burp security

Filename: security-(...).json
```

### Reports

#### `reports`

List your submitted reports with key metadata.

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

#### `report <id>`

Get the full details on a specific report — severity, comments, bounties, content, CVE/CWE, and more.

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

### Payments

#### `balance`

Check your current balance (in the currency set on your profile).

```
$ hackerone balance

Balance: 1337.0
```

#### `earnings`

List your bounty earnings by program.

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

#### `payouts`

List your processed payouts.

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

### Account

#### `profile`

Show your profile info. Requires at least one submitted report (the API derives your profile from the reporter field).

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

#### `help`

Show all available commands and their arguments.

---

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

---

## License

[MIT](./LICENSE)
