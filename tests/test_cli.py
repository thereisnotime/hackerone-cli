import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CLI = [sys.executable, str(ROOT / "hackerone.py")]
FAKE_CREDS = {"HACKERONE_USERNAME": "x", "HACKERONE_API_KEY": "x"}
NO_CREDS = {"HACKERONE_USERNAME": "", "HACKERONE_API_KEY": ""}


def run(*args, creds=NO_CREDS):
    env = {**os.environ, **creds}
    return subprocess.run(
        CLI + ["--env-file", "/dev/null"] + list(args),
        capture_output=True,
        text=True,
        env=env,
    )


class TestHelp:
    def test_shows_output(self):
        r = run("help")
        assert r.returncode == 0
        assert "Hacker Modules" in r.stdout

    def test_no_creds_needed(self):
        r = run("help")
        assert r.returncode == 0

    def test_json_valid(self):
        r = run("help", "--json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "commands" in data

    def test_json_hacker_commands(self):
        r = run("help", "--json")
        keys = " ".join(json.loads(r.stdout)["commands"])
        for cmd in [
            "balance",
            "reports",
            "programs",
            "profile",
            "earnings",
            "payouts",
            "report",
            "program",
            "burp",
            "csv",
            "scope",
        ]:
            assert cmd in keys

    def test_json_org_commands(self):
        r = run("help", "--json")
        keys = " ".join(json.loads(r.stdout)["commands"])
        for cmd in [
            "org",
            "org-members",
            "org-reports",
            "org-report",
            "org-update-report",
            "org-activities",
            "org-metrics",
            "org-scopes",
            "org-invite-hacker",
            "org-bounty",
            "org-swag",
        ]:
            assert cmd in keys


class TestErrors:
    def test_no_username(self):
        r = run("balance")
        assert r.returncode != 0
        assert "No username provided" in r.stdout + r.stderr

    def test_no_api_key(self):
        r = run("balance", creds={"HACKERONE_USERNAME": "x", "HACKERONE_API_KEY": ""})
        assert r.returncode != 0
        assert "No API key provided" in r.stdout + r.stderr

    def test_no_arguments(self):
        r = run(creds=FAKE_CREDS)
        assert r.returncode != 0
        assert "No argument provided" in r.stdout + r.stderr

    def test_invalid_module(self):
        r = run("notamodule", creds=FAKE_CREDS)
        assert r.returncode != 0
        assert "Invalid module" in r.stdout + r.stderr

    def test_no_creds_json_returns_error_object(self):
        r = run("--json", "balance")
        data = json.loads(r.stdout)
        assert "error" in data


class TestArgValidation:
    def test_report_non_numeric_id(self):
        r = run("report", "abc", creds=FAKE_CREDS)
        assert "Invalid ID" in r.stdout + r.stderr

    def test_org_report_non_numeric_id(self):
        r = run("org-report", "abc", creds=FAKE_CREDS)
        assert "Invalid ID" in r.stdout + r.stderr

    def test_org_update_report_invalid_state(self):
        r = run("org-update-report", "123", "badstate", creds=FAKE_CREDS)
        assert "Invalid state" in r.stdout + r.stderr

    def test_org_update_report_missing_args(self):
        r = run("org-update-report", creds=FAKE_CREDS)
        assert "Usage" in r.stdout + r.stderr

    def test_org_bounty_invalid_amount(self):
        r = run("org-bounty", "123", "notanumber", creds=FAKE_CREDS)
        assert "Invalid amount" in r.stdout + r.stderr

    def test_org_bounty_missing_args(self):
        r = run("org-bounty", creds=FAKE_CREDS)
        assert "Usage" in r.stdout + r.stderr

    def test_org_members_requires_org_id(self):
        r = run("org-members", creds=FAKE_CREDS)
        assert "No organization ID" in r.stdout + r.stderr

    def test_org_groups_requires_org_id(self):
        r = run("org-groups", creds=FAKE_CREDS)
        assert "No organization ID" in r.stdout + r.stderr

    def test_org_reports_requires_handle(self):
        r = run("org-reports", creds=FAKE_CREDS)
        assert "No program handle" in r.stdout + r.stderr

    def test_org_metrics_requires_handle(self):
        r = run("org-metrics", creds=FAKE_CREDS)
        assert "No program handle" in r.stdout + r.stderr

    def test_org_scopes_requires_handle(self):
        r = run("org-scopes", creds=FAKE_CREDS)
        assert "No program handle" in r.stdout + r.stderr

    def test_org_invite_hacker_requires_args(self):
        r = run("org-invite-hacker", creds=FAKE_CREDS)
        assert "Usage" in r.stdout + r.stderr

    def test_org_swag_requires_report_id(self):
        r = run("org-swag", creds=FAKE_CREDS)
        assert "Usage" in r.stdout + r.stderr

    def test_scope_invalid_args(self):
        r = run("scope")
        assert "Invalid arguments" in r.stdout + r.stderr
