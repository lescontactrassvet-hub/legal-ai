#!/usr/bin/env python3
import os
import datetime
from collections import defaultdict

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ANALYSIS_FILE = os.path.join(ROOT, "Repo_LegalAI_Analysis.txt")

EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "deploy_logs",
    "backups",
}

# Попытаемся использовать функцию из update_readme.py, чтобы обновлять структуру
try:
    from update_readme import write_structure
except ImportError:
    write_structure = None


LANG_MAP = {
    ".py": "Python",
    ".js": "JavaScript/TypeScript",
    ".jsx": "JavaScript/TypeScript",
    ".ts": "JavaScript/TypeScript",
    ".tsx": "JavaScript/TypeScript",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "CSS",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
    ".md": "Markdown",
}


def classify_lang(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return LANG_MAP.get(ext, "Other")


def walk_files():
    """Итерируемся по всем файлам репозитория с учётом исключений."""
    for root, dirs, files in os.walk(ROOT):
        rel = os.path.relpath(root, ROOT)
        dirname = os.path.basename(root)

        if dirname in EXCLUDE_DIRS:
            dirs[:] = []
            continue

        # фильтруем подкаталоги
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for f in files:
            if f.startswith("."):
                continue
            full_path = os.path.join(root, f)
            yield rel, full_path, f


def collect_stats():
    per_top_dir = defaultdict(lambda: {"files": 0, "code_files": 0, "lines": 0})
    per_lang = defaultdict(lambda: {"files": 0, "lines": 0})

    for rel, full_path, filename in walk_files():
        # top-level каталог
        if rel == ".":
            top = "."
        else:
            top = rel.split(os.sep, 1)[0]

        lang = classify_lang(filename)
        per_top_dir[top]["files"] += 1
        per_lang[lang]["files"] += 1

        # только для "кодовых" файлов считаем строки
        if lang != "Other":
            per_top_dir[top]["code_files"] += 1
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    line_count = sum(1 for _ in f)
            except Exception:
                line_count = 0

            per_top_dir[top]["lines"] += line_count
            per_lang[lang]["lines"] += line_count

    return per_top_dir, per_lang


def list_workflows():
    workflows_dir = os.path.join(ROOT, ".github", "workflows")
    result = []
    if not os.path.isdir(workflows_dir):
        return result

    for name in sorted(os.listdir(workflows_dir)):
        if not (name.endswith(".yml") or name.endswith(".yaml")):
            continue
        path = os.path.join(workflows_dir, name)
        wf_name = ""
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("name:"):
                        wf_name = line.split(":", 1)[1].strip()
                        break
        except Exception:
            wf_name = ""

        result.append((name, wf_name))
    return result


def generate_analysis():
    per_top_dir, per_lang = collect_stats()
    workflows = list_workflows()

    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = []
    lines.append("LEGALAI REPOSITORY ANALYSIS")
    lines.append("=" * 32)
    lines.append(f"Generated (UTC): {now}")
    lines.append(f"Root path: {ROOT}")
    lines.append("")

    # --- Сводка по top-level каталогам ---
    lines.append("1) Top-level directories summary")
    lines.append("--------------------------------")
    lines.append("{:<20} {:>8} {:>12} {:>12}".format("Directory", "Files", "Code files", "Code lines"))
    lines.append("-" * 60)
    for top in sorted(per_top_dir.keys()):
        data = per_top_dir[top]
        lines.append(
            "{:<20} {:>8} {:>12} {:>12}".format(
                top,
                data["files"],
                data["code_files"],
                data["lines"],
            )
        )
    lines.append("")
    lines.append("")

    # --- Статистика по языкам ---
    lines.append("2) Language statistics")
    lines.append("----------------------")
    lines.append("{:<20} {:>8} {:>12}".format("Language", "Files", "Lines"))
    lines.append("-" * 50)
    for lang in sorted(per_lang.keys()):
        data = per_lang[lang]
        lines.append("{:<20} {:>8} {:>12}".format(lang, data["files"], data["lines"]))
    lines.append("")
    lines.append("")

    # --- Список workflows ---
    lines.append("3) GitHub Actions workflows")
    lines.append("---------------------------")
    if not workflows:
        lines.append("No workflows found in .github/workflows")
    else:
        for filename, wf_name in workflows:
            if wf_name:
                lines.append(f"- {filename}: {wf_name}")
            else:
                lines.append(f"- {filename}")
    lines.append("")
    lines.append("")

    # --- Примечание ---
    lines.append("4) Notes")
    lines.append("--------")
    lines.append("- Repo_LegalAI_Structure.txt содержит детальную структуру репозитория.")
    lines.append("- Данный отчёт генерируется автоматически ботом Repo Analyzer v2.")
    lines.append("")

    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[OK] Analysis saved to: {ANALYSIS_FILE}")


if __name__ == "__main__":
    # 1) Обновляем структуру репозитория (если функция доступна)
    if write_structure is not None:
        print("[INFO] Updating Repo_LegalAI_Structure.txt via update_readme.write_structure()")
        write_structure()
    else:
        print("[WARN] Cannot import write_structure from update_readme.py, skipping structure update")

    # 2) Генерируем расширенный отчёт
    generate_analysis()
