\
import json
import os
import subprocess
import sys
from pathlib import Path

import requests

def run_cmd(cmd, cwd=None, timeout=600):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, shell=True)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 1, "", f"Exception: {e}"

def md_section(title: str, body: str) -> str:
    return f"\n### {title}\n\n```\n{body.strip()}\n```\n" if body.strip() else ""

def get_changed_files(base_ref: str) -> list[str]:
    run_cmd(f"git fetch origin {base_ref}")
    code, out, err = run_cmd(f"git diff --name-only origin/{base_ref}...HEAD")
    if code != 0 or not out.strip():
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]

def post_pr_comment(repo: str, pr_number: int, token: str, body: str):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    resp = requests.post(url, headers=headers, json={"body": body})
    if resp.status_code >= 300:
        print(f"[WARN] Failed to post PR comment: {resp.status_code} {resp.text}")

def get_pr_number_from_event() -> int | None:
    event_path = os.getenv("GITHUB_EVENT_PATH", "")
    if not event_path or not Path(event_path).is_file():
        return None
    with open(event_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    pr = data.get("pull_request")
    if not pr:
        return None
    return pr.get("number")

def check_python(files):
    py_files = [f for f in files if f.endswith(".py")]
    if not py_files:
        return "", 0
    sections = []
    failures = 0

    code, out, err = run_cmd("flake8 " + " ".join(py_files))
    if code != 0:
        sections.append(md_section("Python flake8", out or err))
        failures += 1
    else:
        sections.append("✅ flake8: no issues found.\n")

    code, out, err = run_cmd("black --check " + " ".join(py_files))
    if code != 0:
        sections.append(md_section("Python black --check", out or err))
        failures += 1
    else:
        sections.append("✅ black --check: formatted correctly.\n")

    if Path("tests").exists():
        code, out, err = run_cmd("pytest -q")
        if code != 0:
            sections.append(md_section("pytest", out or err))
            failures += 1
        else:
            sections.append("✅ pytest: all tests passed.\n")
    return "\n".join(sections), failures

def check_js(files):
    js_files = [f for f in files if f.endswith((".js", ".jsx", ".ts", ".tsx"))]
    if not js_files or not Path("package.json").exists():
        return "", 0
    sections = []
    failures = 0

    code, out, err = run_cmd("npx --yes eslint " + " ".join(js_files))
    if code != 0:
        sections.append(md_section("ESLint", out or err))
        failures += 1
    else:
        sections.append("✅ ESLint: no issues found.\n")

    code, out, err = run_cmd("npx --yes prettier -c " + " ".join(js_files))
    if code != 0:
        sections.append(md_section("Prettier --check", out or err))
        failures += 1
    else:
        sections.append("✅ Prettier: formatting OK.\n")
    return "\n".join(sections), failures

def check_cpp(files):
    cpp_files = [f for f in files if f.endswith((".cpp", ".cc", ".cxx", ".h", ".hpp"))]
    if not cpp_files:
        return "", 0
    sections = []
    failures = 0

    code, out, err = run_cmd("cpplint " + " ".join(cpp_files))
    if code != 0:
        sections.append(md_section("cpplint", out or err))
        failures += 1
    else:
        sections.append("✅ cpplint: no issues found.\n")

    changed = []
    for f in cpp_files:
        c, o, e = run_cmd(f"clang-format --dry-run --Werror {f}")
        if c != 0:
            changed.append(f)
    if changed:
        sections.append(md_section("clang-format --dry-run --Werror", "\n".join(changed)))
        failures += 1
    else:
        sections.append("✅ clang-format: formatting OK.\n")
    return "\n".join(sections), failures

def main():
    repo = os.getenv("GITHUB_REPOSITORY")
    base_ref = os.getenv("GITHUB_BASE_REF", "main")
    token = os.getenv("GITHUB_TOKEN")
    pr_number = get_pr_number_from_event()

    files = get_changed_files(base_ref)
    if not files:
        summary = "No changed files detected or unable to compute diff. Skipping checks."
        print(summary)
        if repo and token and pr_number:
            post_pr_comment(repo, pr_number, token, summary)
        return

    python_md, py_fail = check_python(files)
    js_md, js_fail = check_js(files)
    cpp_md, cpp_fail = check_cpp(files)

    total_fail = py_fail + js_fail + cpp_fail
    header = f"## Automated Code Review Summary\n\nChanged files:\n- " + "\n- ".join(files[:50])
    body = header + "\n\n" + python_md + js_md + cpp_md

    if total_fail > 0:
        body += "\n\n❌ Some checks failed. Please address the issues above."
    else:
        body += "\n\n✅ All checks passed. Nice work!"

    if repo and token and pr_number:
        post_pr_comment(repo, pr_number, token, body)
    print(body)
    if total_fail > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
