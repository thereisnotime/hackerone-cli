# HackerOne CLI Utility

## Description

An unofficial CLI client for the [HackerOne](https://hackerone.com/) platform. Manage and view your profile, reports, programs, payments, and more — straight from the terminal.

Uses the official [HackerOne API](https://api.hackerone.com/) under the hood.

## Installation

### Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip
- A HackerOne API key — grab one [here](https://hackerone.com/settings/api_token/edit)

### Install with uv

```sh
git clone git@github.com:thereisnotime/hackerone-cli.git
cd hackerone-cli
uv sync
```

### Install with pip

```sh
git clone git@github.com:thereisnotime/hackerone-cli.git
cd hackerone-cli
pip install -e .
```

### Configuration

Create a `.env` file in the project directory:

```sh
HACKERONE_USERNAME="<your-username>"
HACKERONE_API_KEY="<your-api-key>"
```

Or export the variables in your shell:

```sh
export HACKERONE_USERNAME="<your-username>"
export HACKERONE_API_KEY="<your-api-key>"
```

## Usage

With uv:

```sh
uv run hackerone <module> [args]
```

Or if installed via pip:

```sh
hackerone <module> [args]
```

### JSON Output

Pass `--json` or `-j` to any command to get machine-readable JSON output instead of formatted text. Handy for scripting and piping into other tools.

```sh
uv run hackerone programs 5 --json
uv run hackerone program security -j
```

## Modules

```txt
balance                         Check your balance
burp <handle>                   Download the burp configuration file (only from public programs)
csv <handle>                    Download CSV scope file (only from public programs)
earnings                        Check your earnings
help                            Help page
payouts                         Get a list of your payouts
profile                         Your profile on HackerOne
program <handle>                Get information from a program
programs [<max>]                Get a list of current programs (optional: <max> = maximum number of results)
report <id>                     Get a specific report
reports                         Get a list of your reports
scope <csv> [<outfile>]         Extract in-scope targets from a CSV scope file into a text file
```

### balance

Check your money balance. The value is in the currency set on your profile.

```txt
hackerone balance

Balance: 1337.0
```

### burp

Downloads the Burp Suite project configuration file from a public program. Not done through the API (no such endpoint), so it only works with public programs.

Find the program handle via `programs` or from the URL: `https://hackerone.com/<handle>/policy_scopes`.

```txt
hackerone burp security

Filename: security-(...).json
```

### csv

Downloads the CSV scope file from a public program. Same caveat as `burp` — public programs only.

```txt
hackerone csv security

Filename: scopes_for_security_(...).csv
```

### earnings

List your bounty earnings.

```txt
hackerone earnings

Earnings
----------------------------------------
Amount: 1337
Date: 2016-02-02T04:05:06.000Z
Program: HackerOne
Report: RXSS at example.hackerone.com
----------------------------------------
```

### help

Shows all available modules and their arguments.

### payouts

List your payouts.

```txt
hackerone payouts

Payouts
----------------------------------------
Amount: 1337
Status: sent
Date: 2016-02-02T04:05:06.000Z
Provider: Paypal
----------------------------------------
```

### profile

Shows your profile info. Only works if you have at least one report (it pulls your profile from the reporter field).

```txt
hackerone profile

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

### program

Get details about a specific program — scope, policy, bounty info, etc.

```txt
hackerone program security

Program
----------------------------------------
Name: HackerOne
Handle: security
State: open
Availability: Public
Creation date: 2013-11-06T00:00:00.000Z
Bounty: yes
Bounty Splitting: yes
Bookmarked: no

Scope
--------------------
Asset: hackerone.com
Type: URL
State: In-Scope
Bounty: yes
Max Severity: critical
--------------------
```

### programs

List recently updated programs you have access to (including private ones). Defaults to 10 results.

```txt
hackerone programs 2

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

### report

Get full details on a specific report — severity, comments, bounties, content, CVE/CWE, etc.

```txt
hackerone report 1234567

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

Hi!
Thanks for the report, @hacker. We're looking into it.

--------------------
@example awarded a bounty (1337.00 + 0.00)!

----------------------------------------
```

### reports

List your submitted reports with key info.

```txt
hackerone reports

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

### scope

Extract in-scope domains, URLs, IPs, CIDRs, and wildcards from a CSV scope file into a text file. Download the CSV first with the `csv` module, then pass it here.

```txt
hackerone scope scopes_for_example.csv out.txt

In-Scope
----------------------------------------
*.example.com
127.0.0.0/24
test.example.com
----------------------------------------
File 'out.txt' saved!
```

## Development

```sh
uv sync
uv run ruff check .
uv run ruff format .
```

## License

[MIT](./LICENSE)
