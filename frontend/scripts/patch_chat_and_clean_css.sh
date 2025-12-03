#!/data/data/com.termux/files/usr/bin/bash
set -e

cd ~/legal-ai/frontend/app

CSS="src/App.css"
TSX="src/pages/WorkspacePage.tsx"

# --- Проверки наличия файлов ---
if [ ! -f "$CSS" ]; then
  echo "Файл $CSS не найден, скрипт остановлен."
  exit 1
fi

if [ ! -f "$TSX" ]; then
  echo "ВНИМАНИЕ: файл $TSX не найден. Пропускаю правку на многострочный чат."
else
  # --- Бэкап TSX ---
  TSX_BACKUP="${TSX}.bak-$(date +%Y%m%d-%H%M%S)"
  cp "$TSX" "$TSX_BACKUP"
  echo "Создан бэкап TSX: $TSX_BACKUP"

  # --- Заменяем input с className="workspace-chat-input" на textarea с rows={2} ---
  perl -0pi -e '
    s<
      <input([^>]*workspace-chat-input[^>]*?)\/>
    ><
      <textarea$1 rows={2}></textarea>
    >gsx
  ' "$TSX"

  echo "Поле чата с классом .workspace-chat-input заменено на <textarea> с rows={2} (если было найдено)."
fi

# --- Бэкап CSS ---
CSS_BACKUP="${CSS}.bak-$(date +%Y%m%d-%H%M%S)"
cp "$CSS" "$CSS_BACKUP"
echo "Создан бэкап CSS: $CSS_BACKUP"

# --- Чистка дубля: убираем старый блок моб.подстройки редактора (до 640px) ---
perl -0pi -e '
  s|
    /\* ===== Мобильная подстройка редактора \(до 640px\) ===== \*/\s*
    @media\s*\(max-width:\s*640px\)\s*\{
    .*?                             # содержимое первого @media
    \}\s*                           # закрывающая скобка этого блока
    @media\s*\(max-width:\s*640px\)\s*\{\s*\.workspace-header-inner
  |
    @media (max-width: 640px) {\n  .workspace-header-inner
  |gsx
' "$CSS"

echo "Старый дублирующий блок моб.подстройки редактора удалён (если он был)."

# --- Добавляем оверрайд для чата, если ещё не добавлен ---
if grep -q "AUTO PATCH: фиксированная высота чата и многострочный ввод" "$CSS"; then
  echo "CSS-патч для чата уже присутствует, повторно не добавляю."
else
  cat <<'CSS_EOF' >> "$CSS"

/* === AUTO PATCH: фиксированная высота чата и многострочный ввод === */

/* Чат Татьяна — фиксированная высота, прокрутка сообщений внутри */
.workspace-chat-box {
  height: 520px;            /* фиксированная высота на десктопе */
}

/* Область сообщений занимает всё доступное пространство и скроллится */
.workspace-chat-messages {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}

/* Поле ввода — реально многострочное (textarea) и высотой примерно в две строки */
.workspace-chat-input {
  min-height: 2.8em;        /* около двух строк текста */
  line-height: 1.3;
  padding-top: 8px;
  padding-bottom: 8px;
}

/* На мобильных — чат пониже по высоте, чтобы не съедал экран */
@media (max-width: 640px) {
  .workspace-chat-box {
    height: 420px;
  }
}
CSS_EOF

  echo "CSS-патч для чата добавлен."
fi

echo "Готово."
