#!/data/data/com.termux/files/usr/bin/bash
set -e

TSX="src/pages/workspace/index.tsx"

if [ ! -f "$TSX" ]; then
  echo "❌ Файл не найден: $TSX"
  exit 1
fi

BACKUP="${TSX}.bak-textarea4-$(date +%Y%m%d-%H%M%S)"
cp "$TSX" "$BACKUP"
echo "✔ Бэкап создан: $BACKUP"

python3 - << 'PY'
from pathlib import Path
import re

path = Path("src/pages/workspace/index.tsx")
text = path.read_text(encoding="utf-8")

# Заменяем input → textarea (фиксированные 4 строки)
text = re.sub(
    r'<input([^>]+className="workspace-chat-input"[^>]*)>',
    (
        '<textarea className="workspace-chat-input"\n'
        '  rows="4"\n'
        '  style={{ resize: "none" }}\n'
        '  placeholder="Опишите вашу ситуацию или задайте вопрос"\n'
        '  value={input}\n'
        '  onChange={(e) => setInput(e.target.value)}\n'
        '  onKeyDown={handleInputKeyDown}\n'
        '></textarea>'
    ),
    text
)

path.write_text(text, encoding="utf-8")
print("✔ Многострочный textarea (4 строки) восстановлен.")
PY

echo "🎉 patch_chat_textarea_4rows.sh завершён."
