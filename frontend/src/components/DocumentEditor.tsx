import { useEffect } from "react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";

type DocumentEditorProps = {
  // HTML TipTap-документа (то, что хранится в версии)
  value: string;
  onChange: (html: string) => void;

  // Даём Workspace доступ к editor (чтобы выполнить replace selection)
  onEditorReady?: (editor: any) => void;

  // Сообщаем Workspace текущее выделение (позиции и текст)
  onSelectionChange?: (sel: { from: number; to: number; text: string }) => void;
};

/**
 * DocumentEditor — независимый мини-Word на TipTap.
 * Здесь Татьяна выдаёт результат, а пользователь правит документ вручную.
 */
export function DocumentEditor({ value, onChange, onEditorReady, onSelectionChange }: DocumentEditorProps) {
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

// Передаём editor наружу + отслеживаем выделение (TipTap selection)
useEffect(() => {
  if (!editor) return;

  // 1) отдаём editor в Workspace
  onEditorReady?.(editor);

  // 2) функция, которая отправляет выделение
  const pushSelection = () => {
    const { from, to } = editor.state.selection;
    const text = editor.state.doc.textBetween(from, to, "\n");
    onSelectionChange?.({ from, to, text });
  };

  // первый пуш сразу
  pushSelection();

  // и дальше на каждое изменение выделения
  editor.on("selectionUpdate", pushSelection);

  return () => {
    editor.off("selectionUpdate", pushSelection);
  };
}, [editor, onEditorReady, onSelectionChange]);

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

export default DocumentEditor;

