#!/data/data/com.termux/files/usr/bin/bash
set -e

cd ~/legal-ai/frontend/app

TSX="src/pages/workspace/index.tsx"

if [ ! -f "$TSX" ]; then
  echo "❌ Файл $TSX не найден."
  exit 1
fi

BACKUP="${TSX}.bak-api-$(date +%Y%m%d-%H%M%S)"
cp "$TSX" "$BACKUP"
echo "✔ Бэкап создан: $BACKUP"

python3 - << 'PY'
from pathlib import Path

path = Path("src/pages/workspace/index.tsx")
text = path.read_text(encoding="utf-8")

old_handle_send = '''  function handleSend() {
    const text = input.trim();
    if (!text) return;

    const userMsg: ChatMessage = { from: "user", text };

    const aiIntro =
      mode === "simple"
        ? "Спасибо, что описали ситуацию. В демо-версии я фиксирую только примеры запросов, чтобы лучше настроить будущую работу Татьяны."
        : "Приняла запрос. В дальнейшем ИИ Татьяна будет формировать юридический анализ, подбирать нормы права и предлагать структуру документов.";

    const aiMsg: ChatMessage = {
      from: "ai",
      text: aiIntro,
    };

    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setInput("");
  }
'''

new_block = '''  function getTatianaDemoReply(mode: WorkspaceMode, userText: string): string {
    return mode === "simple"
      ? "Спасибо, что описали ситуацию. В демо-версии я фиксирую только примеры запросов, чтобы лучше настроить будущую работу Татьяны."
      : "Приняла запрос. В дальнейшем ИИ Татьяна будет формировать юридический анализ, подбирать нормы права и предлагать структуру документов.";
  }

  async function requestTatianaReply(mode: WorkspaceMode, userText: string): Promise<string> {
    // TODO: заменить на реальный вызов API Татьяны (backend)
    return getTatianaDemoReply(mode, userText);
  }

  async function handleSend() {
    const text = input.trim();
    if (!text) return;

    const userMsg: ChatMessage = { from: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    const aiText = await requestTatianaReply(mode, text);

    const aiMsg: ChatMessage = {
      from: "ai",
      text: aiText,
    };

    setMessages((prev) => [...prev, aiMsg]);
  }
'''

if old_handle_send in text:
    text = text.replace(old_handle_send, new_block, 1)
    print("✔ handleSend вынесен через requestTatianaReply / getTatianaDemoReply")
else:
    print("ℹ️ Ожидаемый блок handleSend не найден — возможно, он уже изменён")

path.write_text(text, encoding="utf-8")
print("✅ Подготовка к API для WorkspacePage применена.")
PY

echo "🎉 patch_workspace_api_prep.sh завершён."
