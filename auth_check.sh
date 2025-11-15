#!/usr/bin/env bash
# Шаг 1: проверка JWT и токенов для LegalAI
set -u

ACCESS_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzYxMTQ1MjgxfQ.4r8S5ydErfcleV-SXK2FXji0MNKtejxsgCUb2LcyQlE'
BASE_URL="http://127.0.0.1:8000"
REPORT=~/legal-ai/auth_check_report.txt

echo "=== LegalAI: Проверка JWT и токенов ===" | tee "$REPORT"

# 0) Утилиты (jq, base64, python3)
echo "[*] Проверка утилит..." | tee -a "$REPORT"
for pkg in jq; do
  if ! command -v "$pkg" >/dev/null 2>&1; then
    echo "    - Устанавливаю $pkg..." | tee -a "$REPORT"
    pkg install -y "$pkg" >/dev/null 2>&1 || true
  fi
done

# 1) Healthcheck
echo "[*] /health..." | tee -a "$REPORT"
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" || echo "000")
echo "    HTTP $HEALTH_CODE" | tee -a "$REPORT"

# 2) /auth/profile с валидным токеном
echo "[*] /auth/profile с валидным JWT..." | tee -a "$REPORT"
PROFILE_JSON=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE_URL/auth/profile")
PROFILE_CODE=$?
if [ $PROFILE_CODE -eq 0 ] && [ -n "$PROFILE_JSON" ]; then
  echo "    Ответ: $PROFILE_JSON" | tee -a "$REPORT"
else
  echo "    Ошибка запроса профиля (код=$PROFILE_CODE)" | tee -a "$REPORT"
fi

# 3) Разбор payload токена и проверка exp
echo "[*] Разбор JWT (payload/exp)..." | tee -a "$REPORT"
python3 - <<'PY' 2>>"$REPORT" | tee -a "$REPORT"
import os, sys, json, base64, time, datetime
token = os.environ.get("ACCESS_TOKEN", "")
try:
    header_b64, payload_b64, sig_b64 = token.split(".")
    def b64url_decode(s):
        s += "=" * (-len(s) % 4)
        return base64.urlsafe_b64decode(s)
    payload = json.loads(b64url_decode(payload_b64))
    print("    payload:", json.dumps(payload, ensure_ascii=False))
    exp = payload.get("exp")
    sub = payload.get("sub")
    now = int(time.time())
    print(f"    sub={sub}, now={now}, exp={exp}")
    if exp is not None:
        left = exp - now
        status = "OK (не просрочен)" if left > 0 else "EXPIRED (просрочен)"
        human_exp = datetime.datetime.utcfromtimestamp(exp).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"    exp_human={human_exp}, осталось_сек={left}, статус={status}")
    else:
        print("    В payload нет поля exp")
except Exception as e:
    print("    Ошибка разбора токена:", e)
PY

# 4) /auth/profile с невалидным токеном (ожидаем 401)
echo "[*] /auth/profile с НЕвалидным JWT (ожидаем 401)..." | tee -a "$REPORT"
INVALID_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer invalid.invalid.invalid" "$BASE_URL/auth/profile" || echo "000")
echo "    HTTP $INVALID_CODE" | tee -a "$REPORT"

echo "=== ИТОГО ===" | tee -a "$REPORT"
echo "health: $HEALTH_CODE" | tee -a "$REPORT"
echo "invalid_jwt_http: $INVALID_CODE" | tee -a "$REPORT"
echo "Смотри подробности в $REPORT" | tee -a "$REPORT"
