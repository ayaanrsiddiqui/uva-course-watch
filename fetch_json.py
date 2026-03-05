import copy
from typing import Any

import requests


BASE_URL = "https://raw.githubusercontent.com/UVA-Course-Explorer/course-data/main"
PREVIOUS_SEMESTERS_URL = f"{BASE_URL}/previousSemesters.json"


def get_current_strm() -> str:
    """
    Fetch the current (latest) semester STRM code from previousSemesters.json.
    """
    resp = requests.get(PREVIOUS_SEMESTERS_URL, timeout=10)
    resp.raise_for_status()
    semesters = resp.json()
    latest = semesters[-1]  # last item is the most recent
    return latest["strm"]


def fetch_cs_json() -> dict:
    """
    Fetch the current CS.json for the latest semester from UVA Course Explorer GitHub.
    """
    strm = get_current_strm()
    cs_url = f"{BASE_URL}/data/{strm}/CS.json"
    resp = requests.get(cs_url, timeout=20)
    resp.raise_for_status()
    return resp.json()


def diff_json(old: Any, new: Any) -> dict[str, Any] | None:
    """
    Compare two JSON-serializable objects and return a single object containing
    only the fields that are different.

    - For dicts: keys that differ (or appear only in one side) are included;
      values are the recursive diff or {"old": v, "new": v}.
    - For lists: differing indices are reported under string keys "0", "1", ...
    - For primitives / type mismatches: returns {"old": old, "new": new}.
    - Returns None when there are no differences.
    """
    if old == new:
        return None

    if type(old) is not type(new):
        return {"old": old, "new": new}

    if isinstance(old, dict):
        result: dict[str, Any] = {}
        all_keys = set(old) | set(new)
        for k in sorted(all_keys):
            v_old = old.get(k)
            v_new = new.get(k)
            if k not in old:
                result[k] = {"old": None, "new": v_new}
                continue
            if k not in new:
                result[k] = {"old": v_old, "new": None}
                continue
            d = diff_json(v_old, v_new)
            if d is not None:
                result[k] = d
        return result if result else None

    if isinstance(old, list):
        result = {}
        for i in range(max(len(old), len(new))):
            a = old[i] if i < len(old) else None
            b = new[i] if i < len(new) else None
            d = diff_json(a, b)
            if d is not None:
                result[str(i)] = d
        return result if result else None

    return {"old": old, "new": new}


def report_changes(
    diff: dict[str, Any] | None,
    context: dict[str, Any],
    old_obj: dict[str, Any] | None = None,
    new_obj: dict[str, Any] | None = None,
) -> None:
    """
    Print user-facing messages for a diff object. Focuses on enrollment/seats:
    if enrollment_total or class_capacity changed and seats available dropped, prints Seat Alert.
    old_obj/new_obj are the two objects that were diffed (used to resolve capacity when only enrollment changed).
    """
    if diff is None:
        return
    if old_obj is None:
        old_obj = {}
    if new_obj is None:
        new_obj = {}

    # Resolve old/new enrollment_total and class_capacity from diff or full objects
    def _val(d: dict, key: str, side: str) -> int | None:
        if key in d and isinstance(d[key], dict) and side in d[key]:
            return d[key][side]
        return (old_obj if side == "old" else new_obj).get(key)

    old_cap = _val(diff, "class_capacity", "old")
    new_cap = _val(diff, "class_capacity", "new")
    old_enrolled = _val(diff, "enrollment_total", "old")
    new_enrolled = _val(diff, "enrollment_total", "new")

    if old_cap is None:
        old_cap = new_cap
    if new_cap is None:
        new_cap = old_cap
    if old_enrolled is None:
        old_enrolled = 0
    if new_enrolled is None:
        new_enrolled = 0

    old_available = (old_cap or 0) - old_enrolled
    new_available = (new_cap or 0) - new_enrolled
    if new_available < old_available:
        print(
            f"Seat Alert! {context.get('subject', 'CS')} "
            f"{context.get('catalog_number')} "
            f"section {context.get('class_section')} "
            f"seats dropped from {old_available} to {new_available}."
        )


def simulate_seat_change(courses: dict) -> None:
    """
    Take one course, decrease its 'enrollment_available' by 1 (simulated),
    and print a 'Seat Alert!' message if the number of seats dropped.
    """
    # CS.json has the structure: {"Computer Science": [ { "catalog_number": ..., "sessions": [...] }, ... ]}
    cs_course_list = courses.get("Computer Science", [])
    if not cs_course_list:
        print("No Computer Science courses found.")
        return

    # Just take the first course and its first session for this simulation
    course = cs_course_list[0]
    sessions = course.get("sessions", [])
    if not sessions:
        print("Course has no sessions.")
        return

    session = sessions[0]

    class_capacity = session.get("class_capacity")
    enrollment_total = session.get("enrollment_total")

    if class_capacity is None or enrollment_total is None:
        print("Session is missing capacity/enrollment data.")
        return

    if class_capacity - enrollment_total <= 0:
        print("No seats available to decrease.")
        return

    # Keep old state for diff, then simulate one seat being taken
    old_session = copy.deepcopy(session)
    session["enrollment_total"] = enrollment_total + 1

    diff = diff_json(old_session, session)
    context = {
        "subject": course.get("subject", "CS"),
        "catalog_number": course.get("catalog_number"),
        "class_section": session.get("class_section"),
    }
    report_changes(diff, context, old_session, session)


if __name__ == "__main__":
    cs_data = fetch_cs_json()
    simulate_seat_change(cs_data)