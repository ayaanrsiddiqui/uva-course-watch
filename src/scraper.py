from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


BASE_URL = "https://raw.githubusercontent.com/UVA-Course-Explorer/course-data/main"
PREVIOUS_SEMESTERS_URL = f"{BASE_URL}/previousSemesters.json"


def get_current_strm(timeout: int = 10) -> str:
    """
    Fetch the current (latest) semester STRM code from previousSemesters.json.
    """
    resp = requests.get(PREVIOUS_SEMESTERS_URL, timeout=timeout)
    resp.raise_for_status()
    semesters = resp.json()
    latest = semesters[-1]  # last item is the most recent
    return latest["strm"]


def fetch_current_subject_catalog(
    subject: str = "CS", timeout: int = 20
) -> dict[str, Any]:
    """
    Fetch the current subject JSON (e.g. CS.json) for the latest semester.
    """
    strm = get_current_strm(timeout=timeout)
    url = f"{BASE_URL}/data/{strm}/{subject}.json"
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def _snapshot_path(subject: str = "CS") -> Path:
    """
    Location on disk where we store the latest snapshot for a subject.

    For CS, this is: data/CS/snapshot.json at the repo root.
    """
    root = Path(__file__).resolve().parents[1]
    return root / "data" / subject / "snapshot.json"


def load_previous_snapshot(subject: str = "CS") -> dict[str, Any] | None:
    """
    Return the previously stored full catalog for a subject, if it exists.
    """
    path = _snapshot_path(subject)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_snapshot(data: dict[str, Any], subject: str = "CS") -> None:
    """
    Persist the latest catalog snapshot for a subject to disk.
    """
    path = _snapshot_path(subject)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def get_snapshots(
    subject: str = "CS",
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """
    High-level helper for the engine:

    - Loads the previously stored snapshot (if any) for the given subject.
    - Fetches the current catalog from UVA Course Explorer.
    - Updates the on-disk snapshot to the current catalog.

    Returns (old_state, new_state), where:
      - old_state is the previous snapshot, or None if this is the first run
      - new_state is the freshly fetched catalog from GitHub
    """
    old_state = load_previous_snapshot(subject=subject)
    new_state = fetch_current_subject_catalog(subject=subject)
    save_snapshot(new_state, subject=subject)
    return old_state, new_state

