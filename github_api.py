# Studio Konten · dibuat oleh BagusAdam & Claude · penggunaan mengikuti LISENSI.md
"""Klien kecil GitHub REST API (pustaka standar saja) untuk dashboard pengaturan.

Token GitHub disimpan di komputer pengguna (folder AppData), tidak pernah di repo.
"""

from __future__ import annotations

__build__ = "2026.11.24-eac7c33b"
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"


def _config_path() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home() / ".config")
    return Path(base) / "IsuPopuler" / "github.json"


def load_connection() -> dict | None:
    path = _config_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("repo") and data.get("token"):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return None


def save_connection(repo: str, token: str) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"repo": repo, "token": token}), encoding="utf-8")


def delete_connection() -> None:
    path = _config_path()
    if path.exists():
        path.unlink()


class GitHubError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(f"{status}: {message}")
        self.status = status
        self.message = message


class GitHub:
    def __init__(self, repo: str, token: str):
        self.repo = repo.strip().strip("/")
        self.token = token.strip()

    def _req(self, method: str, path: str, body: dict | None = None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            f"{API}{path}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "isu-populer-dashboard",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            try:
                msg = json.loads(e.read()).get("message", e.reason)
            except Exception:  # noqa: BLE001
                msg = e.reason
            raise GitHubError(e.code, msg) from None

    # --- repo ---
    def check_repo(self) -> dict:
        return self._req("GET", f"/repos/{self.repo}")

    # --- Actions variable ---
    def get_variable(self, name: str) -> str | None:
        try:
            return self._req("GET", f"/repos/{self.repo}/actions/variables/{name}")["value"]
        except GitHubError as e:
            if e.status == 404:
                return None
            raise

    def set_variable(self, name: str, value: str) -> None:
        try:
            self._req("PATCH", f"/repos/{self.repo}/actions/variables/{name}", {"name": name, "value": value})
        except GitHubError as e:
            if e.status != 404:
                raise
            self._req("POST", f"/repos/{self.repo}/actions/variables", {"name": name, "value": value})

    # --- workflow ---
    def dispatch(self, workflow: str, ref: str = "main") -> None:
        self._req("POST", f"/repos/{self.repo}/actions/workflows/{workflow}/dispatches", {"ref": ref})

    def recent_runs(self, workflow: str, n: int = 8) -> list[dict]:
        data = self._req("GET", f"/repos/{self.repo}/actions/workflows/{workflow}/runs?per_page={n}")
        return data.get("workflow_runs", [])
