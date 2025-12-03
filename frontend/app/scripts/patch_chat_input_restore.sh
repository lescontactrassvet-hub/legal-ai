#!/data/data/com.termux/files/usr/bin/bash
set -e

TSX="src/pages/workspace/index.tsx"

if [ ! -f "$TSX" ]; then
  echo "❌ Файл $TSX не найден."
  exit 1
fi

BACKUP="${TSX}.bak-restore-$(date +%Y%m%d-%H%M%S)"
cp "$TSX" "$BACKUP"
echo "✔ Бэкап создан: $BACKUP"

python3 - << 'PY'
from pathlib import Path
import re

path = Path("src/pages/workspace/index.tsx")
text = path.read_text(encoding="utf-8")

# 1) Удаляем textarea → восстанавливаем input
text = re.sub(
    r'<textarea([^>]*)className="workspace-chat-input"([^>]*)>(.*?)</textarea>',
    r'<input className="workspace-chat-input"\n      placeholder="Опишите вашу ситуацию или задайте вопрос"\n      value={input}\n      onChange={(e) => setInput(e.target.value)}\n      onKeyDown={handleInputKeyDown}\n    />',
    text,
    flags=re.DOTALL
)

# 2) Удаляем onInput={...} если остался
text = re.sub(r'onInput=\{[^\}]+\}', '', text)

# 3) Удаляем ref для textarea (messagesEndRef не трогаем!)
text = re.sub(r'ref=\{inputRef\}', '', text)

path.write_text(text, encoding="utf-8")
print("✔ Восстановлен фиксированный input для чата.")
PY

echo "🎉 patch_chat_input_restore.sh завершён."
