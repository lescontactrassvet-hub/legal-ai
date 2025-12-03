#!/data/data/com.termux/files/usr/bin/bash
set -e

cd ~/legal-ai/frontend/app

TSX="src/pages/workspace/index.tsx"

if [ ! -f "$TSX" ]; then
  echo "❌ Файл $TSX не найден."
  exit 1
fi

BACKUP="${TSX}.bak-autogrow-$(date +%Y%m%d-%H%M%S)"
cp "$TSX" "$BACKUP"
echo "✔ Бэкап создан: $BACKUP"

python3 - << 'PY'
from pathlib import Path

path = Path("src/pages/workspace/index.tsx")
text = path.read_text(encoding="utf-8")

# --- 1. Добавляем chatInputRef после messagesEndRef ---
state_old = '''  const [mode, setMode] = useState<WorkspaceMode>("simple");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [activeSidePanel, setActiveSidePanel] = useState<SidePanel>("cases");
  const [documentHtml, setDocumentHtml] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

'''
state_new = '''  const [mode, setMode] = useState<WorkspaceMode>("simple");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [activeSidePanel, setActiveSidePanel] = useState<SidePanel>("cases");
  const [documentHtml, setDocumentHtml] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const chatInputRef = useRef<HTMLTextAreaElement | null>(null);

'''
if state_old in text:
    text = text.replace(state_old, state_new, 1)
    print("✔ Добавлен chatInputRef рядом с messagesEndRef")
else:
    print("ℹ️ Блок состояний не совпал — возможно, уже изменён")


# --- 2. Добавляем handleInputChange перед handleInputKeyDown ---
old_keydown = '''  function handleInputKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSend();
    }
  }

'''
new_block = '''  function handleInputChange(event: React.ChangeEvent<HTMLTextAreaElement>) {
    const el = event.target;
    setInput(el.value);

    if (chatInputRef.current) {
      const textarea = chatInputRef.current;
      textarea.style.height = "auto";
      const maxHeight = 4 * 24; // примерно 4 строки
      const newHeight = Math.min(textarea.scrollHeight, maxHeight);
      textarea.style.height = newHeight + "px";
    }
  }

  function handleInputKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSend();
    }
  }

'''
if old_keydown in text:
    text = text.replace(old_keydown, new_block, 1)
    print("✔ Добавлен handleInputChange с автоувеличением textarea")
else:
    print("ℹ️ handleInputKeyDown в ожидаемом виде не найден")


# --- 3. Обновляем textarea в JSX: добавляем ref и новый onChange ---
old_textarea = '''              <textarea
                className="workspace-chat-input"
                placeholder="Опишите вашу ситуацию или задайте вопрос"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleInputKeyDown}
                rows={2}
              ></textarea>
'''
new_textarea = '''              <textarea
                ref={chatInputRef}
                className="workspace-chat-input"
                placeholder="Опишите вашу ситуацию или задайте вопрос"
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleInputKeyDown}
                rows={2}
              ></textarea>
'''
if old_textarea in text:
    text = text.replace(old_textarea, new_textarea, 1)
    print("✔ textarea чата подключена к chatInputRef и handleInputChange")
else:
    print("ℹ️ Шаблон textarea не найден — возможно, уже изменён")

path.write_text(text, encoding="utf-8")
print("✅ Изменения для автоувеличения поля ввода применены.")
PY

echo "🎉 patch_chat_autogrow.sh завершён."
