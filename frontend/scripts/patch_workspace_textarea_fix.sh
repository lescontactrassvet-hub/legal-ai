#!/data/data/com.termux/files/usr/bin/bash
set -e

TSX="src/pages/workspace/index.tsx"

if [ ! -f "$TSX" ]; then
  echo "❌ Файл не найден: $TSX"
  exit 1
fi

BACKUP="${TSX}.bak-textarea-fix-$(date +%Y%m%d-%H%M%S)"
cp "$TSX" "$BACKUP"
echo "✔ Бэкап создан: $BACKUP"

python3 - << 'PY'
from pathlib import Path
import re

path = Path("src/pages/workspace/index.tsx")
text = path.read_text(encoding="utf-8")

# 1) Убираем chatInputRef (оставляем только messagesEndRef)
text = text.replace(
    '  const [documentHtml, setDocumentHtml] = useState<string>("");\n'
    '  const messagesEndRef = useRef<HTMLDivElement | null>(null);\n'
    '  const chatInputRef = useRef<HTMLTextAreaElement | null>(null);\n',
    '  const [documentHtml, setDocumentHtml] = useState<string>("");\n'
    '  const messagesEndRef = useRef<HTMLDivElement | null>(null);\n'
)

# 2) Удаляем функцию handleInputChange (автоувеличение)
text = re.sub(
    r'\n\s*function handleInputChange\(event: React\.ChangeEvent<HTMLTextAreaElement>\) \{\s*'
    r'const el = event\.target;\s*'
    r'setInput\(el\.value\);\s*'
    r'if \(chatInputRef\.current\) \{\s*'
    r'const textarea = chatInputRef\.current;\s*'
    r'textarea\.style\.height = "auto";\s*'
    r'const maxHeight = 4 \* 24; // примерно 4 строки\s*'
    r'const newHeight = Math\.min\(textarea\.scrollHeight, maxHeight\);\s*'
    r'textarea\.style\.height = newHeight \+ "px";\s*'
    r'\}\s*'
    r'\}\s*',
    '\n',
    text
)

# 3) Чисто заменяем блок textarea + мусор на корректный textarea
pattern = r'''                <textarea className="workspace-chat-input"[\\s\\S]*?      />\n'''
replacement = '''              <textarea
                className="workspace-chat-input"
                rows={4}
                style={{ resize: "none" }}
                placeholder="Опишите вашу ситуацию или задайте вопрос"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleInputKeyDown}
              ></textarea>
'''
text, n = re.subn(pattern, replacement, text)
print(f"✔ Заменено textarea-блоков: {n}")

path.write_text(text, encoding="utf-8")
print("✅ Исправление textarea завершено.")
PY

echo "🎉 patch_workspace_textarea_fix.sh завершён."
