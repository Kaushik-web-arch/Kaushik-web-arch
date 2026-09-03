from __future__ import annotations

import html
import os
import re
from pathlib import Path

import requests

from profile_config import USERNAME

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
START = "<!-- PROJECTS_AUTO_START -->"
END = "<!-- PROJECTS_AUTO_END -->"

EXCLUDE = {
    USERNAME,
    "event-program",
}

FEATURED = {
    "ai-research-agent",
    "finsight-personal-finance-intelligence",
    "student-placement-porta",
    "ai-digital-twin",
}

SUMMARY_START = "<!-- PROFILE_SUMMARY_START -->"
SUMMARY_END = "<!-- PROFILE_SUMMARY_END -->"
API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": f"{USERNAME}-profile-index/1.0",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def clean_markdown(text: str) -> str:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`>#~]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def readme_title(markdown: str, fallback: str) -> str:
    for raw in markdown.splitlines():
        line = raw.strip()
        if line.startswith("# "):
            title = clean_markdown(line[2:])
            if title:
                return title
    return fallback.replace("-", " ").replace("_", " ").title()


def summary_from_readme(markdown: str) -> str | None:
    if SUMMARY_START in markdown and SUMMARY_END in markdown:
        marked = markdown.split(SUMMARY_START, 1)[1].split(SUMMARY_END, 1)[0]
        cleaned = clean_markdown(marked)
        if cleaned:
            return cleaned

    in_code = False
    paragraphs: list[str] = []
    current: list[str] = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if (
            line.startswith("#")
            or line.startswith("!")
            or line.startswith("[")
            or line.startswith("|")
            or line.startswith("-")
            or line.startswith("*")
            or line.startswith(">")
            or line.startswith("<")
        ):
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))

    for paragraph in paragraphs:
        cleaned = clean_markdown(paragraph)
        if len(cleaned) >= 45:
            return cleaned
    return None


def trim(text: str, limit: int = 190) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    shortened = text[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,.;:")
    return shortened + "…"


def get_json(url: str):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def get_readme(repo_name: str) -> str | None:
    headers = dict(HEADERS)
    headers["Accept"] = "application/vnd.github.raw+json"
    response = requests.get(
        f"{API}/repos/{USERNAME}/{repo_name}/readme",
        headers=headers,
        timeout=30,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.text


def repo_summary(repo: dict, readme: str) -> str:
    from_readme = summary_from_readme(readme)
    description = clean_markdown(repo.get("description") or "")
    return trim(from_readme or description or "README available — open the repository for project details.")


def render_repo(repo: dict, readme: str, summary: str) -> str:
    name = repo["name"]
    display_name = readme_title(readme, name)
    url = repo["html_url"]
    language = repo.get("language") or ""
    tag = f" · `{html.escape(language)}`" if language else ""
    featured = " · **Featured**" if name in FEATURED else ""
    return (
        f"#### [{html.escape(display_name)}]({url}){featured}\n"
        f"{html.escape(summary)}\n\n"
        f"`Public repository`{tag} · [View repository]({url})"
    )


def fetch_projects() -> list[tuple[dict, str, str]]:
    repos = get_json(
        f"{API}/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated&direction=desc"
    )
    projects: list[tuple[dict, str, str]] = []
    for repo in repos:
        name = repo.get("name", "")
        if name in EXCLUDE or repo.get("fork") or repo.get("archived") or repo.get("private"):
            continue
        readme = get_readme(name)
        if not readme:
            continue
        projects.append((repo, readme, repo_summary(repo, readme)))
    return projects


def build_section(projects: list[tuple[dict, str, str]]) -> str:
    if not projects:
        body = "_No eligible public project repositories with a README were found._"
    else:
        cards = [render_repo(repo, readme, summary) for repo, readme, summary in projects]
        body = "\n\n---\n\n".join(cards)

    return (
        f"{START}\n"
        f"### `kaushik@github:~$ ls ./all-projects`\n\n"
        f"This index is generated automatically from my public GitHub repositories that contain a README. "
        f"Featured projects stay pinned above; newly published projects appear here automatically.\n\n"
        f"{body}\n"
        f"{END}"
    )


def update_readme() -> None:
    projects = fetch_projects()
    text = README.read_text(encoding="utf-8")
    section = build_section(projects)

    if START in text and END in text:
        before = text.split(START, 1)[0].rstrip()
        after = text.split(END, 1)[1].lstrip()
        updated = before + "\n\n" + section + "\n\n" + after
    else:
        anchor = "### `kaushik@github:~$ cat ./in-progress/zen-sports.txt`"
        if anchor in text:
            updated = text.replace(anchor, section + "\n\n" + anchor, 1)
        else:
            updated = text.rstrip() + "\n\n" + section + "\n"

    README.write_text(updated, encoding="utf-8")
    print(f"Updated project index with {len(projects)} public repositories.")


if __name__ == "__main__":
    update_readme()
