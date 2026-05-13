import argparse
import csv
import json
import os
from pathlib import Path
from typing import Optional

import requests

REPORT_PATH = Path("report.json")
RESULTS_PATH = Path("results.json")
MAP_PATH = Path("github_moodle_map.csv")


def compute_score() -> dict:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    summary = report.get("summary", {})
    total = int(summary.get("total", 0))
    passed = int(summary.get("passed", 0))
    failed = int(summary.get("failed", 0))
    errors = int(summary.get("error", 0))
    max_score = 100
    score = round((passed / total) * max_score, 2) if total else 0.0

    result = {
        "github_username": resolve_github_username(),
        "assignment": os.getenv("ASSIGNMENT_NAME", "Unknown Assignment"),
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "total": total,
    }

    RESULTS_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def resolve_github_username() -> str:
    """
    Resolve the real student GitHub username.

    GitHub Classroom sometimes triggers workflows as github-classroom[bot].
    In that case, we extract the student username from the repository name.

    Example:
        fm3-python-programming-davmoha -> davmoha
    """

    invalid_users = {
        "github-classroom[bot]",
        "github-actions[bot]",
        "izen-academy",
    }

    github_username = os.getenv("GITHUB_USERNAME", "").strip()
    github_actor = os.getenv("GITHUB_ACTOR", "").strip()

    for candidate in [github_username, github_actor]:
        if candidate and candidate.lower() not in invalid_users:
            return candidate

    repo = os.getenv("GITHUB_REPOSITORY", "").strip()
    repo_name = repo.split("/", 1)[1] if "/" in repo else repo

    assignment_slug = os.getenv("ASSIGNMENT_SLUG", "").strip()
    if assignment_slug:
        prefix = f"{assignment_slug}-"
        if repo_name.startswith(prefix):
            return repo_name[len(prefix):]

    if "-" in repo_name:
        return repo_name.split("-")[-1]

    raise RuntimeError(
        f"Could not determine GitHub username. "
        f"GITHUB_ACTOR={github_actor}, GITHUB_REPOSITORY={repo}"
    )


def lookup_moodle_student_id(github_username: str, course_id: str) -> Optional[str]:
    if not MAP_PATH.exists():
        raise FileNotFoundError(f"Mapping file not found: {MAP_PATH}")

    with MAP_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_github = row.get("github_username", "").strip().lower()
            row_course = row.get("course_id", "").strip()

            if row_github == github_username.strip().lower() and row_course == str(course_id):
                return row.get("moodle_student_id", "").strip()

    return None


def sync_score() -> None:
    if not RESULTS_PATH.exists():
        raise FileNotFoundError("results.json not found. Run compute mode first.")

    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

    moodle_url = os.environ["MOODLE_URL"]
    moodle_token = os.environ["MOODLE_TOKEN"]
    course_id = os.environ["MOODLE_COURSE_ID"]
    activity_id = os.environ["MOODLE_ACTIVITY_ID"]

    github_username = resolve_github_username()
    print(f"Resolved GitHub username: {github_username}")

    student_id = lookup_moodle_student_id(github_username, course_id)
    if not student_id:
        raise RuntimeError(
            f"No Moodle student id found for GitHub user: {github_username} "
            f"in course {course_id}"
        )

    payload = {
        "wstoken": moodle_token,
        "wsfunction": "core_grades_update_grades",
        "moodlewsrestformat": "json",
        "source": "mod/assign",
        "courseid": course_id,
        "component": "mod_assign",
        "activityid": activity_id,
        "itemnumber": 0,
        "grades[0][studentid]": student_id,
        "grades[0][grade]": results["score"],
    }

    print("Sending Moodle payload:")
    for key, value in payload.items():
        if key == "wstoken":
            print(f"{key}: ***")
        else:
            print(f"{key}: {value}")

    response = requests.post(moodle_url, data=payload, timeout=30)
    print("Response status:", response.status_code)
    print("Response body:", response.text)
    response.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["compute", "sync"], required=True)
    args = parser.parse_args()

    if args.mode == "compute":
        compute_score()
    else:
        sync_score()


if __name__ == "__main__":
    main()
