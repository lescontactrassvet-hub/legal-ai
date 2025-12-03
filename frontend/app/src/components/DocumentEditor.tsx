import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";

type DocumentEditorProps = {
  /** HTML-содержимое документа */
  value: string;
  /** Колбэк на изменение документа (HTML) */
  onChange: (html: string) => void;
};

/**
 * DocumentEditor — независимый мини-Word на TipTap.
 * Здесь Татьяна выдаёт результат, а пользователь правит документ вручную.
 */
export function DocumentEditor({ value, onChange }: DocumentEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Placeholder.configure({
        placeholder:
          "Пока это демонстрационный режим. Здесь будет текст документа, который подготовит ИИ Татьяна по результатам диалога.",
      }),
    ],
    content: value || "",
    onUpdate({ editor }) {
      onChange(editor.getHTML());
    },
  });

  if (!editor) {
    return null;
  }

  return (
    <div className="doc-editor-root">
      {/* Верхняя панель – мини-Word */}
      <div className="doc-editor-toolbar">
        {/* Заголовки */}
        <button
          type="button"
          className={editor.isActive("heading", { level: 1 }) ? "active" : ""}
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        >
          H1
        </button>
        <button
          type="button"
          className={editor.isActive("heading", { level: 2 }) ? "active" : ""}
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        >
          H2
        </button>
        <button
          type="button"
          className={editor.isActive("heading", { level: 3 }) ? "active" : ""}
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        >
          H3
        </button>

        <span className="doc-editor-toolbar-sep" />

        {/* Шрифт: базовые стили */}
        <button
          type="button"
          className={editor.isActive("bold") ? "active" : ""}
          onClick={() => editor.chain().focus().toggleBold().run()}
        >
          Ж
        </button>
        <button
          type="button"
          className={editor.isActive("italic") ? "active" : ""}
          onClick={() => editor.chain().focus().toggleItalic().run()}
        >
          К
        </button>
        <button
          type="button"
          className={editor.isActive("strike") ? "active" : ""}
          onClick={() => editor.chain().focus().toggleStrike().run()}
        >
          S
        </button>

        <span className="doc-editor-toolbar-sep" />

        {/* Списки */}
        <button
          type="button"
          className={editor.isActive("bulletList") ? "active" : ""}
          onClick={() => editor.chain().focus().toggleBulletList().run()}
        >
          • Список
        </button>
        <button
          type="button"
          className={editor.isActive("orderedList") ? "active" : ""}
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
        >
          1. Список
        </button>

        <span className="doc-editor-toolbar-sep" />

        {/* Undo / Redo */}
        <button
          type="button"
          onClick={() => editor.chain().focus().undo().run()}
        >
          ↶
        </button>
        <button
          type="button"
          onClick={() => editor.chain().focus().redo().run()}
        >
          ↷
        </button>
      </div>

      {/* Сам "лист" A4 с прокруткой внутри */}
      <div className="doc-editor-page-wrapper">
        <div className="doc-editor-page">
          <EditorContent editor={editor} />
        </div>
      </div>
    </div>
  );
}

