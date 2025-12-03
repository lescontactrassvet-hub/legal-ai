#!/data/data/com.termux/files/usr/bin/bash
set -e

cd ~/legal-ai/frontend/app

TSX="src/pages/workspace/index.tsx"

if [ ! -f "$TSX" ]; then
  echo "❌ Файл $TSX не найден."
  exit 1
fi

# Бэкап
BACKUP="${TSX}.bak-$(date +%Y%m%d-%H%M%S)"
cp "$TSX" "$BACKUP"
echo "✔ Бэкап создан: $BACKUP"

python3 - << 'PY'
from pathlib import Path

path = Path("src/pages/workspace/index.tsx")
text = path.read_text(encoding="utf-8")

old = """  <input
    className="workspace-chat-input"
    placeholder="Опишите вашу ситуацию или задайте вопрос"
    value={input}
    onChange={(e) => setInput(e.target.value)}
    onKeyDown={handleInputKeyDown}
  />"""

new = """  <textarea
    className="workspace-chat-input"
    placeholder="Опишите вашу ситуацию или задайте вопрос"
    value={input}
    onChange={(e) => setInput(e.target.value)}
    onKeyDown={handleInputKeyDown}
    rows={2}
  ></textarea>"""

if old not in text:
    print("⚠️ Шаблон input для чата не найден, файл оставлен без изменений.")
else:
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print("✔ input заменён на textarea (многострочный чат).")
PY

echo "✅ patch_chat_v5 завершён."
