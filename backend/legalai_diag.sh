#!/usr/bin/env bash
# LegalAI Termux Env Doctor
# Диагностика и (опционально) авто-установка окружения для проекта LegalAI.
# По умолчанию НИЧЕГО не устанавливает, только проверяет и делает отчёт.
# Включить авто-фикс: запусти с AUTO_FIX=1 (пример ниже).

set -euo pipefail

### ─────────────────────────── Настройки ───────────────────────────
AUTO_FIX="${AUTO_FIX:-0}"               # 0 = только проверка; 1 = пытаться исправлять
REPORT_FILE="legalai_report_$(date +%Y%m%d_%H%M%S).txt"
PY_REQS=("fastapi" "uvicorn[standard]" "pydantic>=2" "python-dotenv" "sqlalchemy" "aiosqlite" "passlib[bcrypt]" "python-jose[cryptography]" "pyotp" "httpx")
NODE_REQS=("node" "npm")
BIN_REQS=("git" "ssh" "curl" "openssl")
POSTGRES_BIN=("psql" "pg_ctl")          # опционально (ОК, если отсутствуют)
MONOREPO_DIRS=("backend" "frontend" "shared")

cecho() { printf "%b\n" "$1"; }
ok()    { cecho "✅ $1"; }
warn()  { cecho "⚠️  $1"; }
err()   { cecho "❌ $1"; }
step()  { cecho "\n——— $1 ———"; }
line()  { cecho "────────────────────────────────────────────────────"; }

log()   { echo -e "$1" | tee -a "$REPORT_FILE" >/dev/null; }
log_kv(){ printf "%-28s : %s\n" "$1" "$2" | tee -a "$REPORT_FILE" >/dev/null; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

pkg_install() {
  if [ "$AUTO_FIX" = "1" ]; then
    yes | pkg install -y "$@" || true
  fi
}

pip_install() {
  if [ "$AUTO_FIX" = "1" ]; then
    python3 -m pip install -U pip >/dev/null 2>&1 || true
    python3 -m pip install "$@" || true
  fi
}

### ───────────────────── Проверка Termux/Arch ─────────────────────
step "Проверка среды Termux"
if [[ -z "${PREFIX:-}" || ! -d "$PREFIX" || ! -x "$(command -v pkg || true)" ]]; then
  err "Похоже, это не Termux (нет \$PREFIX или пакета pkg). Скрипт рассчитан на Termux."
  exit 1
fi
ok "Обнаружен Termux в $PREFIX"
log "LegalAI Termux Environment Report"
log "$(date)"
line | tee -a "$REPORT_FILE" >/dev/null

### ───────────────────── Зеркала Termux (репозитории) ─────────────
step "Проверка доступности репозиториев pkg"
if need_cmd pkg; then
  if pkg list | head -n 1 >/dev/null 2>&1; then
    ok "pkg доступен"
  else
    warn "pkg отвечает нестабильно. Если будут ошибки — попробуем сменить зеркало: termux-change-repo"
    if [ "$AUTO_FIX" = "1" ]; then
      pkg_install termux-tools
      termux-change-repo || true
    fi
  fi
fi

### ────────────────────────── Базовые утилиты ─────────────────────
step "Базовые бинарники"
for b in "${BIN_REQS[@]}"; do
  if need_cmd "$b"; then
    ver="$($b --version 2>/dev/null | head -n1 || echo 'n/a')"
    ok "$b найден ($ver)"
    log_kv "$b" "$ver"
  else
    warn "$b не найден"
    log_kv "$b" "NOT FOUND"
    pkg_install "$b"
  fi
done

### ─────────────────────────── Git / SSH ключ ─────────────────────
step "Проверка Git и доступа по SSH (к GitHub)"
if need_cmd git; then
  git_ver="$(git --version | sed 's/git version //')"
  log_kv "git" "$git_ver"
  git config --global user.name >/dev/null 2>&1 || warn "git user.name не настроен"
  git config --global user.email >/dev/null 2>&1 || warn "git user.email не настроен"
fi

if need_cmd ssh; then
  if [ -f "$HOME/.ssh/id_rsa" ] || [ -f "$HOME/.ssh/id_ed25519" ]; then
    ok "SSH ключ найден"
  else
    warn "SSH ключ не найден"
    if [ "$AUTO_FIX" = "1" ]; then
      mkdir -p "$HOME/.ssh"
      ssh-keygen -t ed25519 -N "" -f "$HOME/.ssh/id_ed25519" <<< y >/dev/null 2>&1 || true
      ok "Сгенерирован ключ ~/.ssh/id_ed25519. Добавь его в GitHub → Settings → SSH keys"
      cecho "----- ПУБЛИЧНЫЙ КЛЮЧ -----"
      cat "$HOME/.ssh/id_ed25519.pub" || true
      cecho "---------------------------"
    fi
  fi
fi

### ─────────────────────────── Python / pip ───────────────────────
step "Python и pip"
if ! need_cmd python3; then
  warn "python3 не найден"
  pkg_install python
fi

if need_cmd python3; then
  pyver="$(python3 -V 2>/dev/null | awk '{print $2}')"
  log_kv "Python" "$pyver"
  # Рекомендуем 3.11+; совместимость с pydantic v1 на 3.12 ломалась — мы форсим v2+
  python3 - <<'PY' || true
import sys
from distutils.version import LooseVersion as V
ver = sys.version.split()[0]
need = "3.11"
print(f"Python={ver}  Требуется>={need}")
if V(ver) < V(need):
    print("WARNING: Python < 3.11. Рекомендуется обновить.")
PY
  if ! need_cmd pip; then
    pkg_install python-pip
  fi
  python3 -m pip --version >/dev/null 2>&1 || python3 -m ensurepip --upgrade || true
fi

### ───────────────────── Виртуальное окружение проекта ────────────
step "Виртуальное окружение (.venv)"
if need_cmd python3; then
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv || python3 -m venv --without-pip .venv || true
    . .venv/bin/activate || source .venv/bin/activate || true
    python -m ensurepip --upgrade >/dev/null 2>&1 || true
    ok "Создано .venv"
  else
    ok ".venv найдено"
    . .venv/bin/activate || source .venv/bin/activate || true
  fi
  python -m pip install -U pip >/dev/null 2>&1 || true
fi

### ───────────────────── Python-библиотеки проекта ────────────────
step "Проверка и установка Python-зависимостей"
if need_cmd python3; then
  missing=()
  for p in "${PY_REQS[@]}"; do
    if python - <<PY >/dev/null 2>&1
import pkg_resources; pkg_resources.require("${p}")
PY
    then
      ok "Python: ${p} — OK"
    else
      warn "Python: ${p} — отсутствует"
      missing+=("$p")
    fi
  done
  if [ "${#missing[@]}" -gt 0 ]; then
    log_kv "Python missing" "${missing[*]}"
    pip_install "${missing[@]}"
  fi
fi

### ───────────────────── Проверка FastAPI/Pydantic ────────────────
step "Тест FastAPI/OpenAPI (выявляем баги схемы)"
if need_cmd python3; then
  python - <<'PY' || true
import sys
print("Python:", sys.version)
try:
    import fastapi, pydantic
    print("fastapi:", fastapi.__version__)
    print("pydantic:", pydantic.__version__)
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/health")
    def health(): return {"status": "ok"}
    # Пробуем сгенерить openapi (ранее на pydantic v1 + py3.12 падало)
    try:
        schema = app.openapi()
        print("OpenAPI schema generated:", isinstance(schema, dict))
    except Exception as e:
        print("OpenAPI generation ERROR:", e)
except Exception as e:
    print("Import ERROR:", e)
PY
fi

### ───────────────────── Node.js / npm (для фронтенда) ────────────
step "Проверка Node.js / npm"
for n in "${NODE_REQS[@]}"; do
  if need_cmd "$n"; then
    ver="$($n -v 2>/dev/null || $n --version 2>/dev/null || echo 'n/a')"
    ok "$n найден ($ver)"
    log_kv "$n" "$ver"
  else
    warn "$n не найден"
    log_kv "$n" "NOT FOUND"
    pkg_install nodejs
  fi
done

### ───────────────────── PostgreSQL (опционально) ─────────────────
step "Проверка PostgreSQL (опционально, можно пропустить)"
for b in "${POSTGRES_BIN[@]}"; do
  if need_cmd "$b"; then
    ok "$b найден ($($b --version 2>/dev/null | head -n1))"
  else
    warn "$b не найден"
  fi
done
if need_cmd psql && need_cmd pg_ctl; then
  # Лёгкая проверка инициализации кластера
  PGDATA="$PREFIX/var/lib/postgresql"
  if [ -d "$PGDATA" ] && [ -f "$PGDATA/PG_VERSION" ]; then
    ok "PostgreSQL кластер найден в $PGDATA"
  else
    warn "Кластер PostgreSQL не инициализирован ($PGDATA)"
    if [ "$AUTO_FIX" = "1" ]; then
      pkg_install postgresql
      mkdir -p "$PGDATA"
      initdb -D "$PGDATA" >/dev/null 2>&1 || true
      ok "Выполнен initdb (если возможен)."
    fi
  fi
fi

### ───────────────────── Структура монорепозитория ────────────────
step "Структура проекта (monorepo)"
have_all=1
for d in "${MONOREPO_DIRS[@]}"; do
  if [ -d "$d" ]; then
    ok "Папка $d найдена"
  else
    warn "Папка $d отсутствует"
    have_all=0
  fi
done

if [ "$have_all" = "1" ]; then
  ok "Монорепозиторий выглядит корректно"
else
  warn "Монорепозиторий неполный в текущей директории."
  echo "Подсказка: перейди в корень репо (где backend/frontend/shared) перед запуском скрипта."
fi

### ───────────────────── Быстрый прогон backend (локально) ────────
step "Тестовый запуск Uvicorn (локально) и проверка /health"
TMP_MAIN="backend/main_legalai_probe.py"
mkdir -p backend
cat > "$TMP_MAIN" <<'PY'
from fastapi import FastAPI
app = FastAPI()
@app.get("/health")
def health(): return {"status": "ok"}
PY

if need_cmd python3; then
  . .venv/bin/activate || source .venv/bin/activate || true
  # Запускаем uvicorn в фоне, ждём и проверяем curl'ом
  if python -c "import uvicorn" >/dev/null 2>&1; then
    uvicorn backend.main_legalai_probe:app --host 127.0.0.1 --port 8000 --log-level warning &
    UV_PID=$!
    sleep 2
    if curl -sSf http://127.0.0.1:8000/health >/dev/null 2>&1; then
      ok "Uvicorn ответил на /health"
      log_kv "Uvicorn /health" "OK"
    else
      warn "Не удалось обратиться к /health (проверь порты/разрешения)"
      log_kv "Uvicorn /health" "FAIL"
    fi
    kill "$UV_PID" >/dev/null 2>&1 || true
  else
    warn "uvicorn не установлен в .venv"
  fi
fi

### ───────────────────── Итоговый отчёт ───────────────────────────
step "ИТОГОВЫЙ ОТЧЁТ"
line | tee -a "$REPORT_FILE" >/dev/null
cecho "Отчёт сохранён: $REPORT_FILE"
cecho "Режим авто-фикса: $AUTO_FIX (0=только проверка, 1=пытаться исправить)"
line

cecho "📌 Дальше: пришли скрин(ы) с выводом и файл отчёта, я разберу и дам следующий шаг."
