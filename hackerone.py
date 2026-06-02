#!/usr/bin/env python3

import csv as csvmod
import json
import os
import re
import sys

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

__version__ = "1.0.2"

JSON_OUTPUT = False
VERBOSE = False
auth = None


def _render_markdown(text):
    """Try to render markdown with mdv, fall back to plain text."""
    try:
        if "COLUMNS" not in os.environ:
            try:
                os.environ["COLUMNS"] = str(os.get_terminal_size()[0])
            except OSError:
                os.environ["COLUMNS"] = "80"
        import mdv

        mdv.term_columns = _get_terminal_width()
        return mdv.main(text)
    except Exception:
        return text


def _get_terminal_width(default=80):
    try:
        return os.get_terminal_size()[0]
    except OSError:
        return default


def _log(msg):
    if VERBOSE and not JSON_OUTPUT:
        print(f"[*] {msg}", file=sys.stderr)


def _error(msg):
    if JSON_OUTPUT:
        print(json.dumps({"error": msg}))
    else:
        print(msg)


def _error_exit(msg):
    _error(msg)
    sys.exit(1)


def show_help():
    hacker_commands = {
        "balance": "Check your balance",
        "burp <handle>": "Download the burp configuration file (only from public programs)",
        "csv <handle>": "Download CSV scope file (only from public programs)",
        "earnings": "Check your earnings",
        "help": "Help page",
        "payouts": "Get a list of your payouts",
        "profile": "Your profile on HackerOne",
        "program <handle>": "Get information from a program",
        "programs [<max>]": "Get a list of current programs (optional: <max> = maximum number of results)",
        "report <id>": "Get a specific report",
        "reports": "Get a list of your reports",
        "scope <csv> [<outfile>]": "Extract in-scope domains/URLs/wildcards/IPs/CIDRs from a csv scope file and save it to a text file",
    }
    org_commands = {
        "org": "Show your organization info",
        "org-members <org_id>": "List organization members",
        "org-groups <org_id>": "List organization permission groups",
        "org-invitations <org_id>": "List pending organization invitations",
        "org-reports <handle> [<max>]": "List reports submitted to your program (default: 10)",
        "org-report <id>": "Get a report submitted to your program",
        "org-update-report <id> <state>": "Update report state (triaged, resolved, duplicate, spam, not-applicable)",
        "org-activities [<handle>]": "List recent activities (optionally filter by program)",
        "org-metrics <handle>": "Get program metrics and response efficiency",
        "org-scopes <handle>": "List structured scopes (assets) for a program",
        "org-invite-hacker <program_id> <username>": "Invite a hacker to a private program",
        "org-bounty <report_id> <amount>": "Award a bounty on a report",
        "org-swag <report_id>": "Award swag on a report",
    }
    all_commands = {**hacker_commands, **org_commands}
    if JSON_OUTPUT:
        print(json.dumps({"commands": all_commands}))
        return
    print("Hacker Modules:")
    for cmd, desc in hacker_commands.items():
        print(f"    {cmd:<44}{desc}")
    print("\nProgram Management Modules:")
    for cmd, desc in org_commands.items():
        print(f"    {cmd:<44}{desc}")
    print("\nOptions:")
    print("    --username, -u <username>        HackerOne API token identifier (overrides HACKERONE_USERNAME)")
    print("    --api-key, -k <key>             HackerOne API token value (overrides HACKERONE_API_KEY)")
    print("    --json, -j                      Output as JSON")
    print("    --env-file <path>               Path to .env file (default: .env in current directory)")
    print("    --verbose, -v                   Show progress and debug info")


def burp():
    if len(sys.argv) != 3:
        _error("Invalid arguments provided!")
        return

    handler = sys.argv[2]

    _log(f"Downloading Burp config for '{handler}'...")
    r = requests.get(f"https://hackerone.com/teams/{handler}/assets/download_burp_project_file.json")
    if r.status_code != 200 and r.status_code != 404:
        _error_exit(f"Request returned {r.status_code}!")
    if not r.headers["Content-Disposition"].startswith("attachment"):
        _error(f"Could not find program '{handler}'!")
        return

    filename = r.headers["Content-Disposition"].split('"')[1]
    with open(filename, "wb") as fp:
        fp.write(r.content)

    if JSON_OUTPUT:
        print(json.dumps({"filename": filename, "status": "downloaded"}))
    else:
        print("Filename: " + filename)


def csv():
    if len(sys.argv) != 3:
        _error("Invalid arguments provided!")
        return

    handler = sys.argv[2]

    _log(f"Downloading CSV scope for '{handler}'...")
    r = requests.get(f"https://hackerone.com/teams/{handler}/assets/download_csv.csv")
    if r.status_code != 200 and r.status_code != 404:
        _error_exit(f"Request returned {r.status_code}!")
    if not r.headers["Content-Disposition"].startswith("attachment"):
        _error(f"Could not find program '{handler}'!")
        return

    filename = r.headers["Content-Disposition"].split('"')[1]
    with open(filename, "wb") as fp:
        fp.write(r.content)

    if JSON_OUTPUT:
        print(json.dumps({"filename": filename, "status": "downloaded"}))
    else:
        print("Filename: " + filename)


def reports():
    _log("Fetching reports...")
    r = requests.get("https://api.hackerone.com/v1/hackers/me/reports", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print("You have no reports.")
        return

    print("Reports")
    print("----------------------------------------")
    for rep in data["data"]:
        print("ID: " + rep["id"])
        print("Title: " + rep["attributes"]["title"])
        print("State: " + rep["attributes"]["state"])
        print("Date: " + rep["attributes"]["created_at"])
        print("Program: " + rep["relationships"]["program"]["data"]["attributes"]["handle"])
        try:
            print("Severity: " + rep["relationships"]["severity"]["data"]["attributes"]["rating"])
        except:
            print("Severity: none")
        if "cve_ids" in rep["attributes"] and rep["attributes"]["cve_ids"] not in [None, "", []]:
            print("CVE: " + ", ".join(rep["attributes"]["cve_ids"]))
        try:
            print("CWE: " + str.upper(rep["relationships"]["weakness"]["data"]["attributes"]["external_id"]))
            print("Weakness: " + rep["relationships"]["weakness"]["data"]["attributes"]["name"])
        except:
            print("CWE: none")
            print("Weakness: none")
        try:
            print("CVSS: " + str(rep["relationships"]["severity"]["data"]["attributes"]["score"]))
        except:
            pass
        print("----------------------------------------")


def report():
    if len(sys.argv) != 3:
        _error("Invalid arguments provided!")
        return

    if not sys.argv[2].isdigit():
        _error(f"Invalid ID provided '{sys.argv[2]}'!")
        return

    id = sys.argv[2]

    _log(f"Fetching report {id}...")
    r = requests.get(f"https://api.hackerone.com/v1/hackers/reports/{id}", auth=auth)
    if r.status_code != 200 and r.status_code != 404:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if r.status_code == 404:
        _error("Report not found!")
        return

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print("You have no reports.")
        return

    rep = data["data"]

    print("Report")
    print("----------------------------------------")
    print("ID: " + rep["id"])
    print("Title: " + rep["attributes"]["title"])
    print("State: " + rep["attributes"]["state"])
    print("Date: " + rep["attributes"]["created_at"])
    print("Program: " + rep["relationships"]["program"]["data"]["attributes"]["handle"])
    try:
        print("Severity: " + rep["relationships"]["severity"]["data"]["attributes"]["rating"])
    except:
        print("Severity: none")
    if "cve_ids" in rep["attributes"] and rep["attributes"]["cve_ids"] not in [None, "", []]:
        print("CVE: " + ", ".join(rep["attributes"]["cve_ids"]))
    try:
        print("CWE: " + str.upper(rep["relationships"]["weakness"]["data"]["attributes"]["external_id"]))
        print("Weakness: " + rep["relationships"]["weakness"]["data"]["attributes"]["name"])
    except:
        print("CWE: none")
        print("Weakness: none")

    try:
        print("Asset: " + rep["relationships"]["structured_scope"]["data"]["attributes"]["asset_identifier"])
        print("Asset Type: " + rep["relationships"]["structured_scope"]["data"]["attributes"]["asset_type"])
    except:
        pass
    try:
        print("CVSS: " + str(rep["relationships"]["severity"]["data"]["attributes"]["score"]))
    except:
        pass

    if "vulnerability_information" in rep["attributes"]:
        print("\nContent")
        print("--------------------")
        print(_render_markdown(rep["attributes"]["vulnerability_information"]))

    print("\nComments")
    for comment in rep["relationships"]["activities"]["data"]:
        print("--------------------")
        if "username" in comment["relationships"]["actor"]["data"]["attributes"]:
            entity = comment["relationships"]["actor"]["data"]["attributes"]["username"]
        elif "handle" in comment["relationships"]["actor"]["data"]["attributes"]:
            entity = comment["relationships"]["actor"]["data"]["attributes"]["handle"]
        else:
            entity = "someone"
        try:
            match comment["type"]:
                case "activity-report-severity-updated":
                    print("\x1b[3m@" + entity + "\x1b[23m updated the severity of the report!")
                case "activity-bug-pending-program-review":
                    print(
                        "\x1b[3m@"
                        + entity
                        + "\x1b[23m"
                        + (
                            "\n\n" + comment["attributes"]["message"]
                            if "message" in comment["attributes"] and comment["attributes"]["message"] not in [None, ""]
                            else " changed the report status to 'Pending for review'!"
                        )
                    )
                case "activity-comment":
                    print(
                        "\x1b[3m@"
                        + entity
                        + "\x1b[23m"
                        + (
                            "\n\n" + comment["attributes"]["message"]
                            if "message" in comment["attributes"] and comment["attributes"]["message"] not in [None, ""]
                            else " posted a comment! (Not visible)"
                        )
                    )
                case "activity-bug-triaged":
                    print(
                        "\x1b[3m@"
                        + entity
                        + "\x1b[23m"
                        + (
                            "\n\n" + comment["attributes"]["message"]
                            if "message" in comment["attributes"] and comment["attributes"]["message"] not in [None, ""]
                            else " changed the report status to 'Triaged'!"
                        )
                    )
                case "activity-bug-resolved":
                    print(
                        "\x1b[3m@"
                        + entity
                        + "\x1b[23m"
                        + (
                            "\n\n" + comment["attributes"]["message"]
                            if "message" in comment["attributes"] and comment["attributes"]["message"] not in [None, ""]
                            else " changed the report status to 'Resolved'!"
                        )
                    )
                case "activity-bug-duplicate":
                    print(
                        "\x1b[3m@"
                        + entity
                        + "\x1b[23m"
                        + (
                            "\n\n" + comment["attributes"]["message"]
                            if "message" in comment["attributes"] and comment["attributes"]["message"] not in [None, ""]
                            else " changed the report status to 'Duplicate'!"
                        )
                    )
                case "activity-bounty-awarded":
                    print(
                        "\x1b[3m@"
                        + rep["relationships"]["program"]["data"]["attributes"]["handle"]
                        + "\x1b[23m"
                        + f" awarded a bounty ({comment['attributes']['bounty_amount']} + {comment['attributes']['bonus_amount']})!"
                        + (
                            "\n\n" + comment["attributes"]["message"]
                            if "message" in comment["attributes"] and comment["attributes"]["message"] not in [None, ""]
                            else ""
                        )
                    )
                case "activity-bug-retesting":
                    print("\x1b[3m@" + entity + "\x1b[23m changed the status of the report to 'Retesting'!")
                case "activity-hacker-requested-mediation":
                    print("\x1b[3m@" + entity + "\x1b[23m has requested mediation from HackerOne Support!")
                case "activity-user-completed-retest":
                    print(
                        "\x1b[3m@"
                        + entity
                        + "\x1b[23m"
                        + (
                            "\n\n" + comment["attributes"]["message"]
                            if "message" in comment["attributes"] and comment["attributes"]["message"] not in [None, ""]
                            else " completed retesting!"
                        )
                    )
                case "activity-report-retest-approved":
                    print("\x1b[3m@" + entity + "\x1b[23m approved the retesting!")
                case "activity-report-collaborator-invited":
                    print("\x1b[3m@" + entity + "\x1b[23m invited a collaborator!")
                case "activity-report-collaborator-joined":
                    print("\x1b[3m@" + entity + "\x1b[23m joined as a collaborator!")
                case "activity-agreed-on-going-public":
                    print(
                        "\x1b[3m@"
                        + entity
                        + "\x1b[23m"
                        + (
                            "\n\n" + comment["attributes"]["message"]
                            if "message" in comment["attributes"] and comment["attributes"]["message"] not in [None, ""]
                            else " agreed on the report going public!"
                        )
                    )
                case "activity-report-became-public":
                    print("\x1b[3m@" + entity + "\x1b[23m changed the report visibility to public!")
                case "activity-cancelled-disclosure-request":
                    print(
                        "\x1b[3m@"
                        + entity
                        + "\x1b[23m"
                        + (
                            "\n\n" + comment["attributes"]["message"]
                            if "message" in comment["attributes"] and comment["attributes"]["message"] not in [None, ""]
                            else " requested to cancel disclosure!"
                        )
                    )
                case "activity-report-title-updated":
                    print("\x1b[3m@" + entity + "\x1b[23m changed the report title!")
                case "activity-bug-needs-more-info":
                    print("\x1b[3m@" + entity + "\x1b[23m changed the report status to 'Needs more info'!")
                case "activity-bug-new":
                    print("\x1b[3m@" + entity + "\x1b[23m changed the report status to 'New'!")
                case "activity-cve-id-added":
                    print("\x1b[3m@" + entity + "\x1b[23m added a CVE id!")
                case "activity-external-user-joined":
                    print("\x1b[3m@" + entity + "\x1b[23m joined this report as a participant!")
                case "activity-manually-disclosed":
                    print("\x1b[3m@" + entity + "\x1b[23m disclosed this report!")
                case "activity-report-vulnerability-types-updated":
                    print("\x1b[3m@" + entity + "\x1b[23m updated the vulnerability type/weakness!")
                case _:
                    raise Exception()
        except:
            print(comment)
            print("\x1b[3m@" + entity + "\x1b[23m participated on the report! (Could not get more details)")
        print()
    print("----------------------------------------")


def balance():
    _log("Fetching balance...")
    r = requests.get("https://api.hackerone.com/v1/hackers/payments/balance", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    print("Balance: " + str(data["data"]["balance"]))


def earnings():
    _log("Fetching earnings...")
    r = requests.get("https://api.hackerone.com/v1/hackers/payments/earnings", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print("You have no earnings.")
        return

    print("Earnings")
    print("----------------------------------------")
    for earn in data["data"]:
        print(
            "Amount: "
            + earn["relationships"]["bounty"]["data"]["attributes"]["amount"]
            + " "
            + earn["relationships"]["bounty"]["data"]["attributes"]["awarded_currency"]
        )
        print("Date: " + earn["attributes"]["created_at"])
        print("Program: " + earn["relationships"]["program"]["data"]["attributes"]["name"])
        print(
            "Report: "
            + earn["relationships"]["bounty"]["data"]["relationships"]["report"]["data"]["attributes"]["title"]
        )
        print("----------------------------------------")


def payouts():
    _log("Fetching payouts...")
    r = requests.get("https://api.hackerone.com/v1/hackers/payments/payouts", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print("You have no payouts.")
        return

    print("Payouts")
    print("----------------------------------------")
    for payout in data["data"]:
        print("Amount: " + str(payout["amount"]))
        print("Status: " + payout["status"])
        print("Date: " + payout["paid_out_at"])
        print("Provider: " + payout["payout_provider"])


def programs():
    limit = 10
    if len(sys.argv) == 3:
        if sys.argv[2].isdigit() and int(sys.argv[2]) > 0:
            limit = sys.argv[2]
        else:
            _error(f"Invalid maximum value '{sys.argv[2]}'!")
            return

    limit = int(limit)
    c = 0

    results = []

    _log("Fetching programs...")
    while True:
        _log(f"  Fetching page {c + 1}...")
        r = requests.get(f"https://api.hackerone.com/v1/hackers/programs?page[size]=100&page[number]={c}", auth=auth)
        if r.status_code != 200 and r.status_code != 404:
            _error_exit(f"Request returned {r.status_code}!")
        data = json.loads(r.text)

        if r.status_code == 404:
            break

        if len(data["data"]) == 0:
            break

        for program in data["data"]:
            results.append(program)

        c += 1

    _log(f"Fetched {len(results)} programs total.")
    results = results[::-1]
    results = results[:limit]

    if JSON_OUTPUT:
        print(json.dumps({"data": results, "count": len(results)}))
        return

    count = 0

    print("Programs")

    for program in results:
        print("----------------------------------------")
        print("Program: " + program["attributes"]["name"])
        print("Handle: " + program["attributes"]["handle"])
        print("State: " + program["attributes"]["submission_state"])
        print("Availability: " + ("Public" if program["attributes"]["state"] == "public_mode" else "Private"))
        print("Available since: " + program["attributes"]["started_accepting_at"])
        print("Bounty Splitting: " + ("yes" if program["attributes"]["allows_bounty_splitting"] else "no"))
        print("Bookmarked: " + ("yes" if program["attributes"]["bookmarked"] else "no"))
        count += 1

    print("----------------------------------------\n")
    print(f"Got {count} results!")


def profile():
    _log("Fetching profile...")
    r = requests.get("https://api.hackerone.com/v1/hackers/me/reports", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if len(data["data"]) == 0:
        _error("Could not check your profile!")
        return

    user = data["data"][0]["relationships"]["reporter"]["data"]

    if JSON_OUTPUT:
        print(json.dumps(user))
        return

    print("Profile")
    print("----------------------------------------")
    print("ID: " + user["id"])
    print("Username: " + user["attributes"]["username"])
    print("Reputation: " + str(user["attributes"]["reputation"]))
    print("Name: " + user["attributes"]["name"])
    print("Creation Date: " + user["attributes"]["created_at"])
    print(
        "Bio: "
        + (
            user["attributes"]["bio"]
            if "bio" in user["attributes"] and user["attributes"]["bio"] not in [None, ""]
            else ""
        )
    )
    print(
        "Website: "
        + (
            user["attributes"]["website"]
            if "website" in user["attributes"] and user["attributes"]["website"] not in [None, ""]
            else ""
        )
    )
    print(
        "Location: "
        + (
            user["attributes"]["location"]
            if "location" in user["attributes"] and user["attributes"]["location"] not in [None, ""]
            else ""
        )
    )
    print("----------------------------------------")


def program():
    if len(sys.argv) < 3:
        _error("No handle provided!")
        return
    handle = sys.argv[2]

    _log(f"Fetching program '{handle}'...")
    r = requests.get(f"https://api.hackerone.com/v1/hackers/programs/{handle}", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    print("Program")
    print("----------------------------------------")
    print("Name: " + data["attributes"]["name"])
    print("Handle: " + data["attributes"]["handle"])
    print("State: " + data["attributes"]["submission_state"])
    print("Availability: " + ("Public" if data["attributes"]["state"] == "public_mode" else "Private"))
    print("Creation date: " + data["attributes"]["started_accepting_at"])
    print("Bounty: " + ("yes" if data["attributes"]["offers_bounties"] else "no"))
    print("Bounty Splitting: " + ("yes" if data["attributes"]["allows_bounty_splitting"] else "no"))
    print("Bookmarked: " + ("yes" if data["attributes"]["bookmarked"] else "no"))

    print("\nPolicy")
    print("--------------------")
    print(_render_markdown(data["attributes"]["policy"]))

    print("\nScope")
    for scope in data["relationships"]["structured_scopes"]["data"]:
        print("--------------------")
        print("Asset: " + scope["attributes"]["asset_identifier"])
        print("Type: " + scope["attributes"]["asset_type"])
        print("State: " + ("In-Scope" if scope["attributes"]["eligible_for_submission"] else "Out-of-Scope"))
        if "eligible_for_bounty" in scope["attributes"] and scope["attributes"]["eligible_for_bounty"]:
            print("Bounty: " + ("yes" if scope["attributes"]["eligible_for_bounty"] else "no"))
        if scope["attributes"]["instruction"]:
            print("Instruction: " + scope["attributes"]["instruction"])
        print(
            "Max Severity: " + scope["attributes"]["max_severity"]
            if scope["attributes"]["max_severity"] is not None
            else "None"
        )
    print("----------------------------------------")


def scope():
    if len(sys.argv) not in [3, 4]:
        _error("Invalid arguments provided!")
        return

    outfile = sys.argv[3] if len(sys.argv) == 4 else "inscope.txt"
    inscope = []
    try:
        with open(sys.argv[2]) as fp:
            reader = csvmod.reader(fp)
            try:
                next(reader)
            except:
                raise Exception()
            if not JSON_OUTPUT:
                print("In-Scope")
                print("----------------------------------------")
            for row in reader:
                if not row[4] or row[1] not in ["URL", "DOMAIN", "OTHER", "WILDCARD", "CIDR"]:
                    continue
                if re.match(
                    r"^(\*\.)?([a-zA-Z0-9\*]([a-zA-Z0-9\-\*]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,256}$", row[0]
                ) or re.match(
                    r"^(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}(\/[0-3]?[0-9])?$",
                    row[0],
                ):
                    inscope.append(row[0])
                    if not JSON_OUTPUT:
                        print(row[0])
            if not JSON_OUTPUT:
                print("----------------------------------------")
    except:
        _error(f"Failed to read file '{sys.argv[2]}'!")
        return

    if JSON_OUTPUT:
        print(json.dumps({"inscope": sorted(inscope), "outfile": outfile}))
        return

    try:
        with open(f"{outfile}", "a") as fp:
            fp.writelines(item + "\n" for item in sorted(inscope))
            print(f"File '{outfile}' saved!")
    except:
        print(f"Failed to write to file '{outfile}'!")
        return


# --- Program Management (Organization) Commands ---


def org():
    _log("Fetching organization info...")
    r = requests.get("https://api.hackerone.com/v1/me/organizations", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print("You don't belong to any organization.")
        return

    for o in data["data"]:
        print("Organization")
        print("----------------------------------------")
        print("ID: " + o["id"])
        print("Handle: " + o["attributes"]["handle"])
        print("Name: " + o["attributes"]["name"])
        print("Created: " + o["attributes"]["created_at"])
        if "permissions" in o["attributes"] and o["attributes"]["permissions"]:
            print("Permissions: " + ", ".join(o["attributes"]["permissions"]))
        print("----------------------------------------")


def org_reports():
    if len(sys.argv) < 3:
        _error("No program handle provided!")
        return

    handle = sys.argv[2]
    limit = 10
    if len(sys.argv) >= 4:
        if sys.argv[3].isdigit() and int(sys.argv[3]) > 0:
            limit = int(sys.argv[3])
        else:
            _error(f"Invalid maximum value '{sys.argv[3]}'!")
            return

    _log(f"Fetching reports for program '{handle}'...")
    params = {
        "filter[program][]": handle,
        "page[size]": min(limit, 100),
        "page[number]": 1,
    }
    r = requests.get("https://api.hackerone.com/v1/reports", params=params, auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print(f"No reports found for program '{handle}'.")
        return

    print(f"Reports for '{handle}'")
    print("----------------------------------------")
    count = 0
    for rep in data["data"]:
        if count >= limit:
            break
        print("ID: " + rep["id"])
        print("Title: " + rep["attributes"]["title"])
        print("State: " + rep["attributes"]["state"])
        print("Date: " + rep["attributes"]["created_at"])
        try:
            print("Reporter: " + rep["relationships"]["reporter"]["data"]["attributes"]["username"])
        except:
            print("Reporter: unknown")
        try:
            print("Severity: " + rep["relationships"]["severity"]["data"]["attributes"]["rating"])
        except:
            print("Severity: none")
        try:
            print("CWE: " + str.upper(rep["relationships"]["weakness"]["data"]["attributes"]["external_id"]))
        except:
            pass
        try:
            print("CVSS: " + str(rep["relationships"]["severity"]["data"]["attributes"]["score"]))
        except:
            pass
        print("----------------------------------------")
        count += 1
    print(f"\nShowing {count} of {len(data['data'])} results.")


def org_report():
    if len(sys.argv) != 3:
        _error("Invalid arguments provided!")
        return

    if not sys.argv[2].isdigit():
        _error(f"Invalid ID provided '{sys.argv[2]}'!")
        return

    id = sys.argv[2]

    _log(f"Fetching report {id}...")
    r = requests.get(f"https://api.hackerone.com/v1/reports/{id}", auth=auth)
    if r.status_code == 404:
        _error("Report not found!")
        return
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    rep = data["data"]

    print("Report")
    print("----------------------------------------")
    print("ID: " + rep["id"])
    print("Title: " + rep["attributes"]["title"])
    print("State: " + rep["attributes"]["state"])
    print("Date: " + rep["attributes"]["created_at"])
    try:
        print("Reporter: " + rep["relationships"]["reporter"]["data"]["attributes"]["username"])
    except:
        print("Reporter: unknown")
    try:
        print("Program: " + rep["relationships"]["program"]["data"]["attributes"]["handle"])
    except:
        pass
    try:
        print("Severity: " + rep["relationships"]["severity"]["data"]["attributes"]["rating"])
    except:
        print("Severity: none")
    if "cve_ids" in rep["attributes"] and rep["attributes"]["cve_ids"] not in [None, "", []]:
        print("CVE: " + ", ".join(rep["attributes"]["cve_ids"]))
    try:
        print("CWE: " + str.upper(rep["relationships"]["weakness"]["data"]["attributes"]["external_id"]))
        print("Weakness: " + rep["relationships"]["weakness"]["data"]["attributes"]["name"])
    except:
        pass
    try:
        print("Asset: " + rep["relationships"]["structured_scope"]["data"]["attributes"]["asset_identifier"])
    except:
        pass
    try:
        print("CVSS: " + str(rep["relationships"]["severity"]["data"]["attributes"]["score"]))
    except:
        pass

    if "vulnerability_information" in rep["attributes"] and rep["attributes"]["vulnerability_information"]:
        print("\nContent")
        print("--------------------")
        print(_render_markdown(rep["attributes"]["vulnerability_information"]))

    try:
        activities = rep["relationships"]["activities"]["data"]
        if activities:
            print("\nActivities")
            for act in activities:
                print("--------------------")
                try:
                    actor = act["relationships"]["actor"]["data"]["attributes"]
                    entity = actor.get("username") or actor.get("handle") or "someone"
                except:
                    entity = "someone"
                act_type = act["type"].replace("activity-", "").replace("-", " ").title()
                msg = ""
                if "message" in act.get("attributes", {}) and act["attributes"]["message"]:
                    msg = "\n" + act["attributes"]["message"]
                print(f"@{entity} — {act_type}{msg}")
            print("----------------------------------------")
    except:
        pass


def org_members():
    if len(sys.argv) < 3:
        _error("No organization ID provided! Use 'org' to find your org ID.")
        return

    org_id = sys.argv[2]
    _log(f"Fetching members for organization {org_id}...")
    r = requests.get(f"https://api.hackerone.com/v1/organizations/{org_id}/members", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print("No members found.")
        return

    print("Members")
    print("----------------------------------------")
    for member in data["data"]:
        try:
            user = member["relationships"]["user"]["data"]["attributes"]
            print("Username: " + user.get("username", "unknown"))
        except:
            print("ID: " + member["id"])
        try:
            groups = member["relationships"]["organization_member_groups"]["data"]
            group_names = [g["attributes"]["name"] for g in groups]
            if group_names:
                print("Groups: " + ", ".join(group_names))
        except:
            pass
        print("----------------------------------------")
    print(f"\n{len(data['data'])} members.")


def org_groups():
    if len(sys.argv) < 3:
        _error("No organization ID provided! Use 'org' to find your org ID.")
        return

    org_id = sys.argv[2]
    _log(f"Fetching groups for organization {org_id}...")
    r = requests.get(f"https://api.hackerone.com/v1/organizations/{org_id}/groups", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print("No groups found.")
        return

    print("Groups")
    print("----------------------------------------")
    for group in data["data"]:
        print("ID: " + group["id"])
        print("Name: " + group["attributes"]["name"])
        try:
            perms = group["attributes"]["permissions"]
            if perms:
                print("Permissions: " + ", ".join(perms))
        except:
            pass
        print("----------------------------------------")


def org_invitations():
    if len(sys.argv) < 3:
        _error("No organization ID provided! Use 'org' to find your org ID.")
        return

    org_id = sys.argv[2]
    _log(f"Fetching invitations for organization {org_id}...")
    r = requests.get(f"https://api.hackerone.com/v1/organizations/{org_id}/invitations", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print("No pending invitations.")
        return

    print("Pending Invitations")
    print("----------------------------------------")
    for inv in data["data"]:
        print("ID: " + inv["id"])
        try:
            print("Email: " + inv["attributes"]["email"])
        except:
            pass
        try:
            print("Created: " + inv["attributes"]["created_at"])
        except:
            pass
        print("----------------------------------------")


def org_update_report():
    if len(sys.argv) < 4:
        _error("Usage: org-update-report <id> <state>")
        _error("States: triaged, resolved, duplicate, spam, not-applicable")
        return

    if not sys.argv[2].isdigit():
        _error(f"Invalid report ID '{sys.argv[2]}'!")
        return

    report_id = sys.argv[2]
    state = sys.argv[3]

    state_map = {
        "triaged": "activity-bug-triaged",
        "resolved": "activity-bug-resolved",
        "duplicate": "activity-bug-duplicate",
        "spam": "activity-bug-spam",
        "not-applicable": "activity-bug-not-applicable",
        "informative": "activity-bug-informative",
        "needs-more-info": "activity-bug-needs-more-info",
        "new": "activity-bug-new",
    }

    if state not in state_map:
        _error(f"Invalid state '{state}'. Valid states: {', '.join(state_map.keys())}")
        return

    message = sys.argv[4] if len(sys.argv) >= 5 else ""

    _log(f"Updating report {report_id} to '{state}'...")
    payload = {
        "data": {
            "type": state_map[state],
            "attributes": {
                "message": message,
            },
        }
    }

    r = requests.post(
        f"https://api.hackerone.com/v1/reports/{report_id}/activities",
        json=payload,
        auth=auth,
    )
    if r.status_code not in (200, 201):
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    print(f"Report {report_id} updated to '{state}'.")


def org_activities():
    handle = sys.argv[2] if len(sys.argv) >= 3 else None

    _log("Fetching activities...")
    params = {"page[size]": 25}
    if handle:
        params["filter[program][]"] = handle

    r = requests.get("https://api.hackerone.com/v1/incremental/activities", params=params, auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print("No activities found.")
        return

    print("Activities" + (f" for '{handle}'" if handle else ""))
    print("----------------------------------------")
    for act in data["data"]:
        act_type = act["type"].replace("activity-", "").replace("-", " ").title()
        try:
            actor = act["relationships"]["actor"]["data"]["attributes"]
            entity = actor.get("username") or actor.get("handle") or "someone"
        except:
            entity = "someone"
        date = act.get("attributes", {}).get("created_at", "")
        msg = ""
        if "message" in act.get("attributes", {}) and act["attributes"]["message"]:
            msg = "\n  " + act["attributes"]["message"][:200]
        print(f"[{date}] @{entity} — {act_type}{msg}")
        print("--------------------")


def org_metrics():
    if len(sys.argv) < 3:
        _error("No program handle provided!")
        return

    handle = sys.argv[2]

    # First get program ID from handle
    _log(f"Fetching program '{handle}' to get ID...")
    r = requests.get(f"https://api.hackerone.com/v1/hackers/programs/{handle}", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Could not find program '{handle}' (status {r.status_code})!")
    program_data = json.loads(r.text)
    program_id = program_data.get("id", program_data.get("data", {}).get("id"))

    if not program_id:
        _error("Could not determine program ID!")
        return

    _log(f"Fetching metrics for program {program_id}...")
    r = requests.get(f"https://api.hackerone.com/v1/programs/{program_id}/metrics", auth=auth)
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    print(f"Metrics for '{handle}'")
    print("----------------------------------------")
    if "data" in data:
        for key, value in data["data"].get("attributes", data["data"]).items():
            if key not in ("type", "id"):
                print(f"{key.replace('_', ' ').title()}: {value}")
    else:
        for key, value in data.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    print("----------------------------------------")


def org_scopes():
    if len(sys.argv) < 3:
        _error("No program handle provided!")
        return

    handle = sys.argv[2]

    _log(f"Fetching scopes for program '{handle}'...")
    r = requests.get(
        f"https://api.hackerone.com/v1/hackers/programs/{handle}/structured_scopes",
        params={"page[size]": 100},
        auth=auth,
    )
    if r.status_code != 200:
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    if len(data["data"]) == 0:
        print(f"No scopes found for '{handle}'.")
        return

    in_scope = [s for s in data["data"] if s["attributes"].get("eligible_for_submission")]
    out_scope = [s for s in data["data"] if not s["attributes"].get("eligible_for_submission")]

    print(f"Scopes for '{handle}'")

    if in_scope:
        print("\nIn-Scope")
        print("----------------------------------------")
        for s in in_scope:
            attrs = s["attributes"]
            bounty = "yes" if attrs.get("eligible_for_bounty") else "no"
            print(f"  {attrs['asset_identifier']} ({attrs['asset_type']}) — bounty: {bounty}")
            if attrs.get("instruction"):
                print(f"    {attrs['instruction'][:120]}")
        print()

    if out_scope:
        print("Out-of-Scope")
        print("----------------------------------------")
        for s in out_scope:
            attrs = s["attributes"]
            print(f"  {attrs['asset_identifier']} ({attrs['asset_type']})")
        print()

    print(f"{len(in_scope)} in-scope, {len(out_scope)} out-of-scope.")


def org_invite_hacker():
    if len(sys.argv) < 4:
        _error("Usage: org-invite-hacker <program_id> <username>")
        return

    program_id = sys.argv[2]
    username = sys.argv[3]

    _log(f"Inviting '{username}' to program {program_id}...")
    payload = {
        "data": [
            {
                "type": "hacker-invitation",
                "attributes": {
                    "username": username,
                },
            }
        ]
    }

    r = requests.post(
        f"https://api.hackerone.com/v1/programs/{program_id}/hacker_invitations",
        json=payload,
        auth=auth,
    )
    if r.status_code not in (200, 201):
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    print(f"Invitation sent to '{username}' for program {program_id}.")


def org_bounty():
    if len(sys.argv) < 4:
        _error("Usage: org-bounty <report_id> <amount> [message]")
        return

    if not sys.argv[2].isdigit():
        _error(f"Invalid report ID '{sys.argv[2]}'!")
        return

    report_id = sys.argv[2]
    amount = sys.argv[3]
    message = sys.argv[4] if len(sys.argv) >= 5 else ""

    try:
        float(amount)
    except ValueError:
        _error(f"Invalid amount '{amount}'!")
        return

    _log(f"Awarding ${amount} bounty on report {report_id}...")
    payload = {
        "data": {
            "type": "bounty",
            "attributes": {
                "amount": float(amount),
                "message": message,
            },
        }
    }

    r = requests.post(
        f"https://api.hackerone.com/v1/reports/{report_id}/bounties",
        json=payload,
        auth=auth,
    )
    if r.status_code not in (200, 201):
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    print(f"Bounty of ${amount} awarded on report {report_id}.")


def org_swag():
    if len(sys.argv) < 3:
        _error("Usage: org-swag <report_id> [message]")
        return

    if not sys.argv[2].isdigit():
        _error(f"Invalid report ID '{sys.argv[2]}'!")
        return

    report_id = sys.argv[2]
    message = sys.argv[3] if len(sys.argv) >= 4 else ""

    _log(f"Awarding swag on report {report_id}...")
    payload = {
        "data": {
            "type": "swag",
            "attributes": {
                "message": message,
            },
        }
    }

    r = requests.post(
        f"https://api.hackerone.com/v1/reports/{report_id}/swag",
        json=payload,
        auth=auth,
    )
    if r.status_code not in (200, 201):
        _error_exit(f"Request returned {r.status_code}!")
    data = json.loads(r.text)

    if JSON_OUTPUT:
        print(json.dumps(data))
        return

    print(f"Swag awarded on report {report_id}.")


def _extract_flag(flag, *aliases):
    """Extract a --flag value from sys.argv, removing both the flag and its value."""
    for name in (flag, *aliases):
        if name in sys.argv:
            idx = sys.argv.index(name)
            if idx + 1 < len(sys.argv):
                value = sys.argv[idx + 1]
                sys.argv = sys.argv[:idx] + sys.argv[idx + 2 :]
                return value
            else:
                sys.argv = sys.argv[:idx] + sys.argv[idx + 1 :]
                return None
    return None


# Commands that don't need authentication
NO_AUTH_COMMANDS = {"help", "scope"}


def main():
    global JSON_OUTPUT, VERBOSE, auth
    if "--json" in sys.argv or "-j" in sys.argv:
        JSON_OUTPUT = True
        sys.argv = [a for a in sys.argv if a not in ("--json", "-j")]

    if "--verbose" in sys.argv or "-v" in sys.argv:
        VERBOSE = True
        sys.argv = [a for a in sys.argv if a not in ("--verbose", "-v")]

    env_file = _extract_flag("--env-file")
    load_dotenv(env_file if env_file else ".env")

    username = _extract_flag("--username", "-u") or os.getenv("HACKERONE_USERNAME") or None
    api_key = _extract_flag("--api-key", "-k") or os.getenv("HACKERONE_API_KEY") or None

    if not JSON_OUTPUT:
        print()

    if len(sys.argv) < 2:
        _error("No argument provided!")
        if not JSON_OUTPUT:
            print(f"Usage: {__file__} help")
        sys.exit(1)

    command = sys.argv[1]

    # Only require credentials for commands that hit the API
    if command not in NO_AUTH_COMMANDS:
        if username is None:
            _error_exit("No username provided! Use --username or set HACKERONE_USERNAME.")
        if api_key is None:
            _error_exit("No API key provided! Use --api-key or set HACKERONE_API_KEY.")
        auth = HTTPBasicAuth(username, api_key)
        _log(f"Authenticated as '{username}'.")

    match command:
        case "csv":
            csv()
        case "help":
            show_help()
        case "reports":
            reports()
        case "report":
            report()
        case "balance":
            balance()
        case "earnings":
            earnings()
        case "payouts":
            payouts()
        case "profile":
            profile()
        case "programs":
            programs()
        case "program":
            program()
        case "burp":
            burp()
        case "scope":
            scope()
        case "org":
            org()
        case "org-members":
            org_members()
        case "org-groups":
            org_groups()
        case "org-invitations":
            org_invitations()
        case "org-reports":
            org_reports()
        case "org-report":
            org_report()
        case "org-update-report":
            org_update_report()
        case "org-activities":
            org_activities()
        case "org-metrics":
            org_metrics()
        case "org-scopes":
            org_scopes()
        case "org-invite-hacker":
            org_invite_hacker()
        case "org-bounty":
            org_bounty()
        case "org-swag":
            org_swag()
        case _:
            _error(f"Invalid module '{command}'")
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
