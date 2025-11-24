#!/usr/bin/env python3
import os

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
OUTPUT_FILE = os.path.join(ROOT, "Repo_LegalAI_Structure.txt")

EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "deploy_logs",
    "backups"
}

def build_tree():
    lines = []
    for root, dirs, files in os.walk(ROOT):
        rel = os.path.relpath(root, ROOT)
        if rel == ".":
            level = 0
        else:
            level = rel.count(os.sep)

        dirname = os.path.basename(root)
        if dirname in EXCLUDE_DIRS:
            dirs[:] = []
            continue

        indent = "  " * level
        lines.append(f"{indent}{dirname}/")

        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for f in files:
            if f.startswith("."):
                continue
            lines.append(f"{indent}  {f}")

    return "\n".join(lines)


def write_structure():
    tree = build_tree()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(tree)
    print(f"[OK] Repo structure saved to: {OUTPUT_FILE}")


def update_readme():
    readme_path = os.path.join(ROOT, "README.md")
    if not os.path.isfile(readme_path):
        print("[WARN] README.md not found, skipping update.")
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!-- AUTO-STRUCTURE-START -->"
    end = "<!-- AUTO-STRUCTURE-END -->"

    if start not in content or end not in content:
        print("[INFO] README has no auto-structure block. Skipping.")
        return

    before = content.split(start)[0]
    after = content.split(end)[1]

    tree = build_tree()
    new_block = f"{start}\n```\n{tree}\n```\n{end}"

    new_content = before + new_block + after

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("[OK] README.md updated automatically")


if __name__ == "__main__":
    write_structure()
    if "--update-readme" in os.sys.argv:
        update_readme()

