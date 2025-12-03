#!/data/data/com.termux/files/usr/bin/bash
set -e

cd ~/legal-ai/frontend/app

TSX="src/pages/workspace/index.tsx"

if [ ! -f "$TSX" ]; then
  echo "❌ Файл $TSX не найден."
  exit 1
fi

BACKUP="${TSX}.bak-$(date +%Y%m%d-%H%M%S)"
cp "$TSX" "$BACKUP"
echo "✔ Бэкап создан: $BACKUP"

python3 - << 'PY'
from pathlib import Path

path = Path("src/pages/workspace/index.tsx")
text = path.read_text(encoding="utf-8")

# --- 1. Удаляем мёртвый editorText state ---
old_editor_state = '''  /** текст текущего редактируемого документа */
  const [editorText, setEditorText] = useState<string>("");

'''
if old_editor_state in text:
    text = text.replace(old_editor_state, "", 1)
    print("✔ Удалён editorText state")
else:
    print("ℹ️ editorText state не найден (возможно, уже удалён)")


# --- 2. Удаляем старый handleInsertDraftTemplate (строчный текст) ---
old_insert = '''  /** демо-кнопка: заполнить редактор черновым шаблоном */
  function handleInsertDraftTemplate() {
    if (editorText.trim()) return;

    const template =
      "Черновой проект документа.\\n\\n" +
      "1. Вводная часть: краткое описание вашей ситуации.\\n" +
      "2. Основные обстоятельства: ключевые факты по делу.\\n" +
      "3. Правовое обоснование: ссылки на нормы права (будут добавлены Татьяной).\\n" +
      "4. Просьба / требование: чего вы хотите добиться.\\n\\n" +
      "Дальше вы можете редактировать текст сами или попросить ИИ Татьяну в чате скорректировать формулировки.";
    setEditorText(template);
  }

'''
if old_insert in text:
    text = text.replace(old_insert, "", 1)
    print("✔ Удалён старый handleInsertDraftTemplate (текстовая версия)")
else:
    print("ℹ️ Старый handleInsertDraftTemplate не найден")


# --- 3. Удаляем старый handleSaveDraft (editorText) ---
old_save = '''  function handleSaveDraft() {
    // В будущем здесь будет сохранение документа в личный кабинет.
    console.log("Сохранён черновик документа (демо):", editorText.length, "символов");
    alert("В демо-версии черновик сохраняется только локально. В рабочей версии он появится в разделе «Документы».");
  }

'''
if old_save in text:
    text = text.replace(old_save, "", 1)
    print("✔ Удалён старый handleSaveDraft (editorText)")
else:
    print("ℹ️ Старый handleSaveDraft не найден")


# --- 4. Удаляем старый handleDownloadStub (editorText-версия) ---
old_download = '''  function handleDownloadStub(format: "pdf" | "docx") {
    // Заглушка под будущую выгрузку файла
    alert(
      `Загрузка в формате ${format.toUpperCase()} появится, когда подключим модуль генерации файлов.`
    );
  }

'''
if old_download in text:
    text = text.replace(old_download, "", 1)
    print("✔ Удалён старый handleDownloadStub (текстовая версия)")
else:
    print("ℹ️ Старый handleDownloadStub не найден")


# --- 5. Добавляем useRef и useEffect в импорт React ---
import_old = 'import React, { useState } from "react";'
import_new = 'import React, { useState, useRef, useEffect } from "react";'
if import_old in text:
    text = text.replace(import_old, import_new, 1)
    print("✔ Импорт React дополнен useRef и useEffect")
else:
    print("ℹ️ Импорт React уже был изменён или отличается")


# --- 6. Добавляем messagesEndRef после documentHtml state ---
state_old = '  const [documentHtml, setDocumentHtml] = useState<string>("");\n\n'
state_new = '  const [documentHtml, setDocumentHtml] = useState<string>("");\n  const messagesEndRef = useRef<HTMLDivElement | null>(null);\n\n'
if state_old in text:
    text = text.replace(state_old, state_new, 1)
    print("✔ Добавлен messagesEndRef после documentHtml")
else:
    print("ℹ️ Не удалось найти место для messagesEndRef (state блок отличается)")


# --- 7. Меняем тип handleInputKeyDown под textarea ---
old_keydown = '  function handleInputKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {\n'
new_keydown = '  function handleInputKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {\n'
if old_keydown in text:
    text = text.replace(old_keydown, new_keydown, 1)
    print("✔ Исправлен тип события в handleInputKeyDown (HTMLTextAreaElement)")
else:
    print("ℹ️ handleInputKeyDown с типом HTMLInputElement не найден")


# --- 8. Добавляем useEffect с автоскроллом после handleDocumentChange ---
doc_change_old = '''  /** Обновление HTML-документа из редактора */
  function handleDocumentChange(value: string) {
    setDocumentHtml(value);
  }

'''
doc_change_new = '''  /** Обновление HTML-документа из редактора */
  function handleDocumentChange(value: string) {
    setDocumentHtml(value);
  }

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

'''
if doc_change_old in text:
    text = text.replace(doc_change_old, doc_change_new, 1)
    print("✔ Добавлен useEffect с автоскроллом чата")
else:
    print("ℹ️ Блок handleDocumentChange не найден или уже изменён")


# --- 9. Добавляем ref к концу списка сообщений ---
end_block_old = '                ))}\n              </div>\n'
end_block_new = '                ))}\n                <div ref={messagesEndRef} />\n              </div>\n'
if end_block_old in text:
    text = text.replace(end_block_old, end_block_new, 1)
    print("✔ Добавлен div с ref={messagesEndRef} в конец списка сообщений")
else:
    print("ℹ️ Не удалось вставить ref в конец списка сообщений")


# --- 10. Заменяем input на textarea в поле ввода чата ---
chat_input_old = '''              <input
                className="workspace-chat-input"
                placeholder="Опишите вашу ситуацию или задайте вопрос"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleInputKeyDown}
              />
'''
chat_input_new = '''              <textarea
                className="workspace-chat-input"
                placeholder="Опишите вашу ситуацию или задайте вопрос"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleInputKeyDown}
                rows={2}
              ></textarea>
'''
if chat_input_old in text:
    text = text.replace(chat_input_old, chat_input_new, 1)
    print("✔ Поле ввода чата заменено на textarea (многострочный ввод)")
else:
    print("ℹ️ Шаблон input поля чата не найден — возможно, уже заменён")


path.write_text(text, encoding="utf-8")
print("✅ Все изменения к файлу index.tsx применены.")
PY

echo "🎉 patch_full_fix.sh завершён."
