#!/data/data/com.termux/files/usr/bin/bash
set -e

cd ~/legal-ai/frontend/app

TSX="src/pages/workspace/index.tsx"
CSS="src/App.css"

echo "=== PATCH START ==="

# --- Проверка файла Workspace ---
if [ ! -f "$TSX" ]; then
  echo "❌ Файл $TSX не найден! Исправление чата невозможно."
else
  # Бэкап TSX
  TSX_BACKUP="${TSX}.bak-$(date +%Y%m%d-%H%M%S)"
  cp "$TSX" "$TSX_BACKUP"
  echo "✔ Бэкап создан: $TSX_BACKUP"

  # Замена input → textarea
  sed -i '
    s/<input\([^>]*workspace-chat-input[^>]*\)\/>/<textarea\1 rows={2}><\/textarea>/g
  ' "$TSX"

  echo "✔ Поле ввода чата заменено на многострочный textarea"
fi


# --- Работа с CSS ---
if [ ! -f "$CSS" ]; then
  echo "❌ Файл $CSS не найден — CSS-патчи пропущены."
  exit 0
fi

# Бэкап CSS
CSS_BACKUP="${CSS}.bak-$(date +%Y%m%d-%H%M%S)"
cp "$CSS" "$CSS_BACKUP"
echo "✔ Бэкап CSS создан: $CSS_BACKUP"

# Удаляем нижний дубль DocEditor
sed -i '/\/\* === Дополнительная полировка DocEditor/,${d;}' "$CSS"

echo "✔ Дубликат блока DocEditor удалён (если существовал)."

# Добавляем патч, если его ещё нет
if ! grep -q "AUTO PATCH: фиксированная высота чата" "$CSS"; then
cat << 'CSS_EOF' >> "$CSS"

/* === AUTO PATCH: фиксированная высота чата и многострочный ввод === */

.workspace-chat-box {
  height: 520px;
}

.workspace-chat-messages {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}

.workspace-chat-input {
  min-height: 2.8em;
  padding-top: 8px;
  padding-bottom: 8px;
  line-height: 1.3;
}

@media (max-width: 640px) {
  .workspace-chat-box {
    height: 420px;
  }
}

CSS_EOF

echo "✔ CSS-патч добавлен."
else
echo "ℹ️ CSS-патч уже существует, пропускаю."
fi

echo "=== PATCH COMPLETE ==="
