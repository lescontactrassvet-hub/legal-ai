#!/usr/bin/env bash
# LegalAI Termux Doctor v2
# Диагностика окружения + точечная автоустановка ТОЛЬКО недостающего.
# Итоговый отчёт: TXT + JSON. Безопасен для повторных запусков (идемпотентен).

set -euo pipefail

# ─── Параметры ─────────────────────────────────────────────────────────────────
AUTO_FIX="${AUTO_FIX:-1}"   # 1 = исправлять недостающее; 0 = только проверять
PORT_DEFAULT="${PORT_DEFAULT:-8000}"
REPORT_TS="$(date +%Y%m%d_%H%M%S)"
REPORT_TXT="legalai_report_${REPORT_TS}.txt"
REPORT_JSON="legalai_report_${REPORT_TS}.json"

PY_REQS=("fastapi" "uvicorn[standard]" "pydantic>=2" "python-dotenv" "sqlalchemy" "aiosqlite" "passlib[bcrypt]" "python-jose[cryptography]" "pyotp" "httpx")
BIN_REQS=("git" "ssh" "curl" "openssl")
NODE_REQS=("node" "npm")
POSTGRES_BIN=("psql" "pg_ctl") # опционально
MONOREPO_DIRS=("backend" "frontend" "shared")

# ─── Утилиты ───────────────────────────────────────────────────────────────────
cecho(){ printf "%b\n" "$1"; }
ok(){ cecho "✅ $1"; echo "OK | $1" >>"$REPORT_TXT"; }
warn(){ cecho "⚠️  $1"; echo "WARN | $1" >>"$REPORT_TXT"; }
err(){ cecho "❌ $1"; echo "ERR | $1" >>"$REPORT_TXT"; }
step(){ cecho "\n——— $1 ———"; echo "----- $1" >>"$REPORT_TXT"; }
line(){ cecho "────────────────────────────────────────────────────"; echo "────────────────────────────────────────────────────" >>"$REPORT_TXT"; }
need_cmd(){ command -v "$1" >/dev/null 2>&1; }

declare -a FIXED_ACTIONS=()
declare -a STILL_MISSING=()
note_fix(){ FIXED_ACTIONS+=("$1"); }
note_missing(){ STILL_MISSING+=("$1"); }

pkg_install(){
  if [ "$AUTO_FIX" = "1" ]; then
    yes | pkg install -y "$@" >/dev/null 2>&1 && note_fix "pkg install: $*" || warn "Не удалось установить: $*"
  fi
}
pip_install(){
  if [ "$AUTO_FIX" = "1" ]; then
    python3 -m pip install -U pip >/dev/null 2>&1 || true
    python3 -m pip install "$@" >/dev/null 2>&1 \
      && note_fix "pip install: $*" \
      || warn "pip: установка не удалась: $*"
  fi
}

# ─── Заголовок отчёта ──────────────────────────────────────────────────────────
echo "LegalAI Termux Doctor v2 — $(date)" >"$REPORT_TXT"
line

# ─── Проверка Termux ───────────────────────────────────────────────────────────
step "Проверка среды Termux"
if [[ -z "${PREFIX:-}" || ! -d "$PREFIX" || ! -x "$(command -v pkg || true)" ]]; then
  err "Это не Termux (нет \$PREFIX/pkg). Скрипт рассчитан на Termux."
  exit 1
fi
ok "Обнаружен Termux в $PREFIX"

# ─── Репозитории Termux ────────────────────────────────────────────────────────
step "Проверка репозиториев pkg"
if pkg list 1>/dev/null 2>&1; then
  ok "pkg отвечает"
else
  warn "pkg отвечает нестабильно — может потребоваться termux-change-repo"
  note_missing "termux-change-repo"
fi

# ─── Базовые бинарники ─────────────────────────────────────────────────────────
step "Базовые утилиты"
for b in "${BIN_REQS[@]}"; do
  if need_cmd "$b"; then
    v="$($b --version 2>/dev/null | head -n1 || echo 'n/a')"
    ok "$b найден ($v)"
  else
    warn "$b не найден"
    pkg_install "$b" || true
    need_cmd "$b" && ok "$b установлен" || note_missing "$b"
  fi
done

# ─── Git/SSH: базовая настройка ────────────────────────────────────────────────
step "Git / SSH"
if need_cmd git; then
  git config --global user.name >/dev/null 2>&1 || warn "git user.name не настроен"
  git config --global user.email >/dev/null 2>&1 || warn "git user.email не настроен"
fi
if need_cmd ssh; then
  if [ -f "$HOME/.ssh/id_ed25519" ] || [ -f "$HOME/.ssh/id_rsa" ]; then
    ok "SSH-ключ найден"
  else
    warn "SSH-ключ отсутствует"
    if [ "$AUTO_FIX" = "1" ]; then
      mkdir -p "$HOME/.ssh"
      ssh-keygen -t ed25519 -N "" -f "$HOME/.ssh/id_ed25519" <<< y >/dev/null 2>&1 && {
        ok "Сгенерирован SSH-ключ (~/.ssh/id_ed25519)"
        cecho "— Публичный ключ:\n$(cat "$HOME/.ssh/id_ed25519.pub")"
        note_fix "ssh-keygen id_ed25519"
      }
    else
      note_missing "SSH key"
    fi
  fi
fi

# ─── Python / pip / venv ───────────────────────────────────────────────────────
step "Python / pip / venv"
if ! need_cmd python3; then
  warn "python3 не найден"
  pkg_install python
fi
if need_cmd python3; then
  log_pyver="$(python3 -V 2>/dev/null)"
  ok "Python: $log_pyver"
  if ! need_cmd pip; then
    pkg_install python-pip
  fi
  # venv
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv || python3 -m venv --without-pip .venv || true
    . .venv/bin/activate || source .venv/bin/activate || true
    python -m ensurepip --upgrade >/dev/null 2>&1 || true
    ok "Создано .venv"
    note_fix "python venv"
  else
    ok ".venv найден"
    . .venv/bin/activate || source .venv/bin/activate || true
  fi
  python -m pip -q install -U pip >/dev/null 2>&1 || true
else
  err "Python недоступен — дальнейшие проверки библиотек пропущены"
fi

# ─── Python-зависимости ────────────────────────────────────────────────────────
step "Python-зависимости проекта"
if need_cmd python3; then
  missing_py=()
  for p in "${PY_REQS[@]}"; do
    if python - <<PY >/dev/null 2>&1
import pkg_resources; pkg_resources.require("${p}")
PY
    then ok "Python: ${p} — ОК"
    else warn "Python: ${p} — отсутствует"; missing_py+=("$p")
    fi
  done
  if [ "${#missing_py[@]}" -gt 0 ]; then
    pip_install "${missing_py[@]}"
    # повторная проверка
    for p in "${missing_py[@]}"; do
      if python - <<PY >/dev/null 2>&1
import pkg_resources; pkg_resources.require("${p}")
PY
      then ok "Установлено: ${p}"
      else note_missing "pip:${p}"
      fi
    done
  fi
fi

# ─── FastAPI/OpenAPI smoke-test ────────────────────────────────────────────────
step "FastAPI/OpenAPI — быстрая проверка"
if need_cmd python3; then
  python - <<'PY' || true
import sys
print("Python:", sys.version.split()[0])
try:
    import fastapi, pydantic
    print("fastapi:", fastapi.__version__)
    print("pydantic:", pydantic.__version__)
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/health")
    def health(): return {"status":"ok"}
    schema = app.openapi()
    print("OpenAPI schema ok:", isinstance(schema, dict))
except Exception as e:
    print("FASTAPI TEST ERROR:", e)
PY
fi

# ─── Node.js / npm ─────────────────────────────────────────────────────────────
step "Node.js / npm"
for n in "${NODE_REQS[@]}"; do
  if need_cmd "$n"; then
    v="$($n -v 2>/dev/null || $n --version 2>/dev/null || echo 'n/a')"
    ok "$n найден ($v)"
  else
    warn "$n не найден"
    pkg_install nodejs
    need_cmd "$n" && ok "$n установлен" || note_missing "$n"
  fi
done

# ─── PostgreSQL (опционально) ──────────────────────────────────────────────────
step "PostgreSQL (опционально)"
for b in "${POSTGRES_BIN[@]}"; do
  if need_cmd "$b"; then ok "$b найден ($($b --version 2>/dev/null | head -n1))"
  else warn "$b не найден"; fi
done

# ─── Структура монорепозитория ────────────────────────────────────────────────
step "Структура монорепозитория"
monorepo_ok=1
for d in "${MONOREPO_DIRS[@]}"; do
  if [ -d "$d" ]; then ok "Папка $d найдена"
  else warn "Папка $d отсутствует"; monorepo_ok=0; fi
done
[ "$monorepo_ok" = "1" ] || warn "Скрипт лучше запускать из корня репо (где backend/frontend/shared)."

# ─── Тестовый Uvicorn (свободный порт) ─────────────────────────────────────────
step "Тестовый запуск Uvicorn и проверка /health"
# подбираем порт, если PORT_DEFAULT занят
pick_port="$PORT_DEFAULT"
for try_port in "$PORT_DEFAULT" 8001 8010 0; do
  if [ "$try_port" = "0" ]; then
    warn "Не удалось подобрать порт для теста — пропускаю запуск"
    pick_port=0; break
  fi
  if (ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null) | grep -q ":$try_port "; then
    warn "Порт $try_port занят, пробуем следующий"
  else
    pick_port="$try_port"; break
  fi
done

TMP_MAIN="backend/main_legalai_probe.py"
mkdir -p backend
cat > "$TMP_MAIN" <<'PY'
from fastapi import FastAPI
app = FastAPI()
@app.get("/health")
def health(): return {"status":"ok"}
PY

if need_cmd python3 && [ "$pick_port" != "0" ]; then
  . .venv/bin/activate || source .venv/bin/activate || true
  if python -c "import uvicorn" >/dev/null 2>&1; then
    uvicorn backend.main_legalai_probe:app --host 127.0.0.1 --port "$pick_port" --log-level warning &
    UV_PID=$!
    sleep 2
    if curl -sSf "http://127.0.0.1:${pick_port}/health" >/dev/null 2>&1; then
      ok "Uvicorn ответил на /health (порт ${pick_port})"
    else
      warn "Не удалось обратиться к /health на порту ${pick_port}"
    fi
    kill "$UV_PID" >/dev/null 2>&1 || true
  else
    warn "uvicorn не установлен в .venv"
  fi
fi

# ─── Финальный отчёт (JSON + TXT) ──────────────────────────────────────────────
step "ИТОГОВЫЙ ОТЧЁТ"
line
echo "Отчёт (txt):  $REPORT_TXT"
echo "Отчёт (json): $REPORT_JSON"
echo
# JSON
{
  printf '{\n'
  printf '  "timestamp": "%s",\n' "$(date -Iseconds)"
  printf '  "auto_fix": %s,\n' "$( [ "$AUTO_FIX" = "1" ] && echo true || echo false )"
  # Список исправлений
  printf '  "fixed_actions": [\n'
  for i in "${!FIXED_ACTIONS[@]}"; do
    printf '    "%s"%s\n' "${FIXED_ACTIONS[$i]}" $([ "$i" -lt $((${#FIXED_ACTIONS[@]}-1)) ] && echo "," || true)
  done
  printf '  ],\n'
  # Список проблем
  printf '  "still_missing": [\n'
  for i in "${!STILL_MISSING[@]}"; do
    printf '    "%s"%s\n' "${STILL_MISSING[$i]}" $([ "$i" -lt $((${#STILL_MISSING[@]}-1)) ] && echo "," || true)
  done
  printf '  ]\n'
  printf '}\n'
} > "$REPORT_JSON"

cecho "📄 TXT сохранён: $REPORT_TXT"
cecho "🧾 JSON сохранён: $REPORT_JSON"
line
cecho "📌 Пришли эти файлы/скрины — по ним дам следующий шаг (реализацию /auth)."
