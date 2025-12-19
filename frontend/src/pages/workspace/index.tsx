 import React, { useState, useEffect, useRef, ChangeEvent } from "react";
import DocumentEditor from "../../components/DocumentEditor";

type WorkspacePageProps = {
  onGoToProfile: () => void;
  onLogout: () => void;
  onGoToDocuments?: () => void;
};

type WorkspaceMode = "simple" | "pro";

type ChatMessage = {
  from: "user" | "ai";
  text: string;
};

type SidePanel = "cases" | "docs";

type TatianaAskResponse = {
  answer?: string;
  citations?: unknown;
  error?: string;
  message?: string;
};

// Демо-режим включается ТОЛЬКО явным флагом.
// По умолчанию: боевой режим (backend).
const DEMO_MODE = false;

function getTatianaDemoReply(mode: WorkspaceMode, userText: string): string {
  const trimmed = userText.trim();

  if (!trimmed) {
    return (
      "Я не увидела текста вопроса. Пожалуйста, опишите ситуацию или задайте \n" +
      "вопрос — и я подскажу, как действовать с юридической точки зрения."
    );
  }

  if (mode === "simple") {
    return [
      "Спасибо, что описали ситуацию.",
      "",
      "Сейчас включён демонстрационный режим (VITE_DEMO_MODE=true).",
      "Я не обращаюсь к базе законов, но показываю пример структуры ответа:",
      "",
      "1) Уточню ключевые факты: даты, стороны, документы и ваши цели.",
      "2) Объясню простыми словами, какие у вас есть права и риски.",
      "3) Предложу конкретный план действий: что собрать, куда обращаться, какие",
      "   шаги делать по порядку.",
      "",
      "В рабочей версии «Татьяна» использует актуальное законодательство и данные",
      "с сервера для точного ответа.",
    ].join("\n");
  }

  // pro-режим
  return [
    "Переключаемся в профессиональный режим.",
    "",
    "Сейчас включён демонстрационный режим (VITE_DEMO_MODE=true).",
    "В полной версии здесь будет структурированный юридический анализ со ссылками",
    "на нормы права, судебную практику и фрагменты документов.",
    "",
    "Обычно ответ включает:",
    "— вводную часть (кто, когда и при каких обстоятельствах);",
    "— правовую квалификацию ситуации с указанием статей законов;",
    "— оценку рисков и вероятных исходов;",
    "— рекомендации по дальнейшим действиям и перечень необходимых документов.",
    "",
    "В будущем «Татьяна» сформирует черновик документа и предложит отредактировать",
    "его в редакторе ниже.",
  ].join("\n");
}

function formatCitations(citations: unknown): string {
  if (!citations) return "";
  try {
    if (Array.isArray(citations)) {
      const items = citations
        .map((c, idx) => {
          if (typeof c === "string") return `${idx + 1}. ${c}`;
          if (c && typeof c === "object") {
            const asAny = c as Record<string, unknown>;
            const title = typeof asAny.title === "string" ? asAny.title : "";
            const ref = typeof asAny.ref === "string" ? asAny.ref : "";
            const url = typeof asAny.url === "string" ? asAny.url : "";
            const parts = [title, ref, url].filter(Boolean);
            return `${idx + 1}. ${parts.join(" — ") || JSON.stringify(c)}`;
          }
          return `${idx + 1}. ${String(c)}`;
        })
        .filter(Boolean);

      if (items.length === 0) return "";
      return ["", "Источники:", ...items].join("\n");
    }

    if (typeof citations === "string") {
      return ["", "Источники:", citations].join("\n");
    }

    if (citations && typeof citations === "object") {
      return ["", "Источники:", JSON.stringify(citations, null, 2)].join("\n");
    }

    return ["", "Источники:", String(citations)].join("\n");
  } catch {
    return "";
  }
}
async function requestTatianaReply(
  mode: WorkspaceMode,
  userText: string,
  context?: any
): Promise<string> {

  const finalMessage =
    context?.mode === "edit_fragment"
      ? `Ты юридический редактор. Твоя задача — переписать ТОЛЬКО выделенный фрагмент текста.\n\n
СТРОГИЕ ПРАВИЛА:\n
- Верни ТОЛЬКО новую версию фрагмента\n
- БЕЗ комментариев, объяснений, списков\n
- БЕЗ всего документа\n
- Формат ответа СТРОГО:\n
<<<DRAFT>>>\n
<новая версия фрагмента>\n
<<<END>>>\n\n
ВЫДЕЛЕННЫЙ ФРАГМЕНТ:\n${context?.selection_text}\n\n
КОНТЕКСТ ДОКУМЕНТА (для стиля и смысла):\n${context?.document_html}`
      : userText;


  const base =
    (import.meta as any)?.env?.VITE_API_BASE?.toString?.() || "/api";

  const url = `${base.replace(/\/$/, "")}/ai/ask`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: finalMessage,
        intent: mode, // используем режим как "намерение" (simple/pro)
        context: context || undefined,
      }),
    });
    // Если backend отдаёт HTML/ошибку — поймаем и покажем нормально
    const rawText = await res.text();
    let data: TatianaAskResponse | null = null;

    try {
      data = JSON.parse(rawText) as TatianaAskResponse;
    } catch {
      // не JSON (например, HTML)
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${rawText.slice(0, 200)}`);
      }
      // если ok, но не JSON — возвращаем как текст
      return rawText;
    }

    if (!res.ok) {
      const msg =
        (data && (data.error || data.message)) || `HTTP ${res.status}`;
      throw new Error(msg);
    }

    const answer =
      (data && typeof data.answer === "string" && data.answer.trim()) ||
      (data && typeof data.message === "string" && data.message.trim()) ||
      "";

    const cites = data?.citations ? formatCitations(data.citations) : "";

  if (data && typeof (data as any).document_draft === "string" && (data as any).document_draft.trim()) {
    setDocumentHtml((data as any).document_draft);
    setAiDraft((data as any).document_draft);

  }


    if (!answer) {
      // странный ответ, но не падаем
      return `Ответ получен, но поле "answer" пустое.${cites}`;
    }

    return `${answer}${cites}`;
  } catch (e) {
    // В БОЕВОМ режиме НЕ подменяем ответ демо-ответом — показываем честную ошибку.
    if (DEMO_MODE) {
      return getTatianaDemoReply(mode, userText);
    }

    const msg =
      e instanceof Error
        ? e.message
        : "Неизвестная ошибка при обращении к серверу ИИ.";

    return [
      "Ошибка при обращении к серверу ИИ.",
      "",
      "Что можно сделать:",
      "1) Проверьте, что сервис доступен и интернет-соединение работает.",
      "2) Попробуйте повторить запрос через несколько секунд.",
      "3) Если проблема повторяется — проверьте настройки VITE_API_BASE и прокси /api.",
      "",
      `Техническая информация: ${msg}`,
    ].join("\n");
  }
}

type CaseItem = {
  id: number;
  title: string;
  status?: string | null;
  description?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

type DocumentItem = {
  id: number;
  case_id: number;
  title: string;
  type?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

const WorkspacePage: React.FC<WorkspacePageProps> = ({
  onGoToProfile,
  onLogout,
  onGoToDocuments,
}) => {
  const [mode, setMode] = useState<WorkspaceMode>("simple");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [documentHtml, setDocumentHtml] = useState<string>("");
  const [documentLoading, setDocumentLoading] = useState<boolean>(false);
  const [documentError, setDocumentError] = useState<string>("");
  const [activeSidePanel, setActiveSidePanel] = useState<SidePanel>("cases");
  const [saving, setSaving] = useState(false);
const [saveError, setSaveError] = useState<string | null>(null);
const [saveOk, setSaveOk] = useState<string | null>(null);
const [draftOk, setDraftOk] = useState<string | null>(null);

// чтобы не плодить одинаковые версии
const lastSavedHashRef = useRef<string>("");
// TipTap editor instance (нужен, чтобы заменить выделенный текст)
const editorRef = useRef<any>(null);

// текущее выделение в редакторе (позиции TipTap)
const [selection, setSelection] = useState<{ from: number; to: number; text: string } | null>(null);

// черновик от ИИ (фрагмент для применения)
const [aiDraft, setAiDraft] = useState<string | null>(null);

  // 2.8: показываем применение только когда draft валиден и есть выделение
  const canApplyAiDraft = Boolean(
    aiDraft &&
    aiDraft.trim().length >= 10 &&
    selection &&
    selection.from !== selection.to &&
    aiDraft.trim() !== selection.text.trim()
  );


// для автосохранения: таймер

  const [cases, setCases] = useState<CaseItem[]>([]);
  const [activeCaseId, setActiveCaseId] = useState<number | null>(null);
  const [casesLoading, setCasesLoading] = useState<boolean>(false);
  const [casesError, setCasesError] = useState<string>("");

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [activeDocumentId, setActiveDocumentId] = useState<number | null>(null);
  const [documentsLoading, setDocumentsLoading] = useState<boolean>(false);
  const [documentsError, setDocumentsError] = useState<string>("");

const API_BASE = import.meta.env.VITE_API_BASE || "/api";
  
function hashText(s: string): string {
  // простой стабильный хеш (не крипто), нам только для сравнения
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return String(h);
}

async function saveVersion(mode: "manual" | "auto") {
  if (!activeDocumentId) return;

  const content = documentHtml || "";
  const contentHash = hashText(content);

  if (mode === "auto") {
    if (!content.trim()) return;
    if (contentHash === lastSavedHashRef.current) return;
  }

  if (mode === "manual") {
    setSaving(true);
    setSaveError(null);
    setSaveOk(null);
  }

try {
  const res = await fetch(`${API_BASE}/documents/${activeDocumentId}/versions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      content,
      source: "user",
    }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || "save failed"}`);
  }

  lastSavedHashRef.current = contentHash;

  if (mode === "manual") {
    setSaveOk("Версия сохранена");
    window.setTimeout(() => setSaveOk(null), 2000);
  } else {
    setDraftOk("Черновик сохранён");
    window.setTimeout(() => setDraftOk(null), 1500);
  }
} catch (e: any) {
  if (mode === "manual") {
    setSaveError(e?.message || "Ошибка сохранения версии документа");
  }
} finally {
  if (mode === "manual") setSaving(false);
}

}

  useEffect(() => {
    let cancelled = false;

    const loadCases = async () => {
      const base =
        (import.meta as any)?.env?.VITE_API_BASE?.toString?.() || "/api";
      const url = `${base.replace(/\/$/, "")}/cases`;

      setCasesLoading(true);
      setCasesError("");

      try {
        const res = await fetch(url);
        const raw = await res.text();

        let data: unknown;
        try {
          data = JSON.parse(raw);
        } catch {
          throw new Error(`Не JSON: ${raw.slice(0, 140)}`);
        }

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        if (!Array.isArray(data)) {
          throw new Error("Ожидался массив дел");
        }

        const list = data as CaseItem[];

        if (!cancelled) {
          setCases(list);
          if (list.length > 0) {
            setActiveCaseId(prev => (prev === null ? list[0].id : prev));
          } } } catch (e: any) {
  if (!cancelled) setCasesError(e?.message || String(e));
} finally {
  if (!cancelled) setCasesLoading(false);
}
};

    loadCases();
    return () => { cancelled = true; };
  }, []);

useEffect(() => {
  if (!activeCaseId) {
    setDocuments([]);
    setActiveDocumentId(null);
    return;
  }

  let cancelled = false;

  const loadDocuments = async () => {
    const base =
      (import.meta as any)?.env?.VITE_API_BASE?.toString?.() || "/api";
    const url = `${base.replace(/\/$/, "")}/cases/${activeCaseId}/documents`;

    setDocumentsLoading(true);
    setDocumentsError("");
    setActiveDocumentId(null);

    try {
      const res = await fetch(url);
      const raw = await res.text();

      let data: unknown;
      try {
        data = JSON.parse(raw);
      } catch {
        throw new Error(`Не JSON: ${raw.slice(0, 140)}`);
      }

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      if (!Array.isArray(data)) {
        throw new Error("Ожидался массив документов");
      }

      if (!cancelled) {
        setDocuments(data as DocumentItem[]);
    // AUTOSELECT: выбираем первый документ, чтобы редактор сразу загрузился
    if (!activeDocumentId && (data as DocumentItem[]).length > 0) {
      setActiveDocumentId((data as DocumentItem[])[0].id);
    }
      }
    } catch (e) {
      if (!cancelled) {
        const msg =
          e instanceof Error
            ? e.message
            : "Ошибка загрузки документов";
        setDocumentsError(msg);
        setDocuments([]);
      }
    } finally {
      if (!cancelled) {
        setDocumentsLoading(false);
      }
    }
  };

  loadDocuments();
  return () => {
    cancelled = true;
  };
}, [activeCaseId]);

useEffect(() => {
  if (!activeDocumentId) {
    setDocumentError("");
    return;
  }

  let cancelled = false;

  const loadLatestDocumentVersion = async () => {
    const base =
      (import.meta as any)?.env?.VITE_API_BASE?.toString?.() || "/api";
    const url = `${base.replace(/\/$/, "")}/documents/${activeDocumentId}/versions`;

    setDocumentLoading(true);
    setDocumentError("");

    try {
      const res = await fetch(url);
      const raw = await res.text();

      let data: unknown;
      try {
        data = JSON.parse(raw);
      } catch {
        throw new Error(`Не JSON: ${raw.slice(0, 140)}`);
      }

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      if (!Array.isArray(data)) {
        throw new Error("Ожидался массив версий документа");
      }

      const versions = data as Array<Record<string, unknown>>;
      const latest = versions[0];

      const content =
        latest && typeof latest.content === "string" ? latest.content : "";

      if (!cancelled) {
        setDocumentHtml(content);
      }
    } catch (e) {
      if (!cancelled) {
        const msg =
          e instanceof Error
            ? e.message
            : "Ошибка загрузки версии документа";
        setDocumentError(msg);
      }
    } finally {
      if (!cancelled) {
        setDocumentLoading(false);
      }
    }
  };

  loadLatestDocumentVersion();
  return () => {
    cancelled = true;
  };
}, [activeDocumentId]);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
// автосохранение: таймер и защита от дублей
const autoSaveTimerRef = useRef<number | null>(null);
const lastAutoSavedRef = useRef<string>("");

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

useEffect(() => {
  if (DEMO_MODE) return;
  if (!activeDocumentId) return;

  // сбрасываем предыдущий таймер
  if (autoSaveTimerRef.current) {
    window.clearTimeout(autoSaveTimerRef.current);
    autoSaveTimerRef.current = null;
  }

  // ставим новый таймер на автосохранение
  autoSaveTimerRef.current = window.setTimeout(() => {
    // saveVersion сама:
    // - проверяет пустой текст
    // - не плодит дубли по hash
    saveVersion("auto");
  }, 3000);

  return () => {
    if (autoSaveTimerRef.current) {
      window.clearTimeout(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }
  };
}, [documentHtml, activeDocumentId]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;

    const userMessage: ChatMessage = { from: "user", text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

  // 2.8: сбрасываем предыдущий draft при новом запросе
  setAiDraft(null);
  const ctx =
    selection && selection.from !== selection.to
      ? {
          mode: "edit_fragment",
          selection_text: selection.text,
          document_html: (documentHtml || "").slice(0, 4000),
        }
      : undefined;



  const replyText = await requestTatianaReply(mode, text, ctx);
const draftMatch = replyText.match(/<<<DRAFT>>>([\s\S]*?)<<<END>>>/);
if (draftMatch) {
    const draftText = (draftMatch[1] || "").trim();
    if (draftText.length >= 10) {
      setAiDraft(draftText);

      // AI_CREATE: Татьяна создаёт документ и сразу показывает в редакторе
      if (!activeDocumentId && activeCaseId) {
        
        const base = (import.meta as any)?.env?.VITE_API_BASE?.toString?.() || "/api";
        const title = "Документ от Татьяны";
        const res = await fetch(`${base.replace(/\/$/, "")}/cases/${activeCaseId}/documents`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title }),
        });
        const doc = await res.json();
        const docId = doc?.id;
        if (docId) {
          await fetch(`${base.replace(/\/$/, "")}/documents/${docId}/versions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: draftText, source: "ai" }),
          });
          setDocuments(prev => [{ id: docId, title }, ...prev]);
          setActiveDocumentId(docId);
          setDocumentHtml(draftText);
      }
        }

    // AI_APPLY: всегда показываем черновик в редакторе
    setDocumentHtml(draftText);
setAiDraft(null);

      }
    }
    const aiMessage: ChatMessage = { from: "ai", text: replyText };
    setMessages((prev) => [...prev, aiMessage]);
  };

  const handleInputChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    console.log("Выбрано файлов для Татьяны:", files.length);

    if (DEMO_MODE) {
      alert(
        "В демо-режиме файлы не отправляются на сервер.\n" +
          "В рабочем режиме (после подключения) «Татьяна» сможет анализировать вложения."
      );
      return;
    }

    alert(
      "Прикрепление файлов пока не подключено на сервере.\n" +
        "Следующий шаг проекта: загрузка вложений и анализ документов «Татьяной»."
    );
  };

  const handleDocumentChange = (html: string) => {
    setDocumentHtml(html);
  };

  const handleInsertDraftTemplate = () => {
    if (documentHtml.trim()) return;

    const template = [
      "<h2>Черновой проект документа</h2>",
      "<p>Ниже — базовая структура юридического документа. Отредактируйте её с учетом вашей ситуации или попросите «Татьяну» доработать текст.</p>",
      "<ol>",
      "<li><strong>Вводная часть.</strong> Кто, когда, где, на основании чего действует.</li>",
      "<li><strong>Обстоятельства.</strong> Краткое и последовательное описание фактов.</li>",
      "<li><strong>Правовое обоснование.</strong> Указание норм права, ссылок на договоры, практику.</li>",
      "<li><strong>Просьба / Требование.</strong> Чёткая формулировка того, чего вы хотите добиться.</li>",
      "</ol>",
      "<p>После редактирования вы сможете сохранить этот черновик как отдельный документ и вернуться к нему в разделе «Документы».</p>",
    ].join("");
    setDocumentHtml(template);
  };

  const handleSaveDraft = () => {
    console.log("Сохранение черновика документа. Длина HTML:", documentHtml.length);

    if (DEMO_MODE) {
      alert(
        "В демо-режиме черновик сохраняется только в текущей сессии.\n" +
          "В полноценной версии он появится в разделе «Документы» как отдельный проект."
      );
      return;
    }

    alert(
      "Сохранение черновика на сервер пока не подключено.\n" +
        "Следующий этап: связка Workspace ↔ Документы ↔ Мои дела."
    );
  };

  const handleDownloadStub = (format: "pdf" | "docx") => {
    const label = format === "pdf" ? "PDF" : "Word (DOCX)";
    alert(
      `Экспорт в ${label} будет доступен после подключения модуля генерации файлов на backend.\n` +
        "Пока вы можете скопировать текст и вставить его в привычный редактор."
    );
  };

  const handleGoToDocumentsClick = () => {
    if (onGoToDocuments) {
      onGoToDocuments();
      }
  else {
      alert(
        "Раздел «Документы» будет доступен через отдельную страницу.\n" +
          "Сейчас эта кнопка работает как заглушка."
      );
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setInput("");
  };

  const handleShowGuide = () => {
    const lines: string[] = [
      "Как пользоваться рабочей страницей LEGALAI:",
      "",
      "1. Вверху страницы выберите режим: простой или профессиональный.",
      "2. В большом поле чата опишите вашу ситуацию и, при необходимости, прикрепите файлы.",
      "3. «Татьяна» ответит и поможет подготовить основу для документа.",
      "4. Ниже в редакторе документа вы можете доработать черновик, сохранить его или подготовить к экспорту.",
      "",
    ];

    if (DEMO_MODE) {
      lines.push(
        "Важно: сейчас включён демонстрационный режим (VITE_DEMO_MODE=true).",
        "Ответы могут быть примером и не обращаться к серверу."
      );
    } else {
      lines.push(
        "Важно: сейчас используется боевой режим (ответы приходят с сервера).",
        "Если вы видите ошибку — проверьте доступность API и настройки VITE_API_BASE."
      );
    }

    alert(lines.join("\n"));
  };

  return (
    <div
      className="workspace-root"
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left, rgba(96, 165, 250, 0.4), transparent \n55%), radial-gradient(circle at bottom right, rgba(129, 140, 248, 0.5), \ntransparent 60%), linear-gradient(to bottom, #020617, #02091f)",
        paddingBottom: "24px",
      }}
    >
      <header className="workspace-header">
        <div className="workspace-header-inner">
          <div className="workspace-logo-block">
            <img src="/logo.png" alt="LEGALAI" className="workspace-logo" />
            <div className="workspace-logo-text">
              <div
                className="workspace-logo-title"
                style={{
                  fontSize: "20px",
                  letterSpacing: "0.14em",
                  color: "#a855ff",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  lineHeight: 1.1,
                }}
              >
                LEGALAI
              </div>
              <div
                className="workspace-logo-subtitle"
                style={{
                  fontSize: "10px",
                  opacity: 0.9,
                }}
              >
                Юридический ИИ — «Татьяна»
              </div>
            </div>
          </div>

          <nav
            className="workspace-nav"
            style={{
              marginLeft: "auto",
              display: "flex",
              gap: "8px",
            }}
          >
            <button
              type="button"
              className="workspace-nav-button workspace-nav-button-primary"
              style={{
                borderRadius: 999,
                padding: "6px 16px",
                background: "linear-gradient(90deg, #ec4899, #a855f7)",
                color: "#ffffff",
                border: "none",
                fontSize: "11px",
              }}
            >
              Чат ИИ «Татьяна»
            </button>
            <button
              type="button"
              className="workspace-nav-button"
              onClick={handleGoToDocumentsClick}
              style={{
                borderRadius: 999,
                padding: "6px 16px",
                background: "linear-gradient(90deg, #1f2937, #111827)",
                color: "#e5e7eb",
                border: "none",
                fontSize: "11px",
              }}
            >
              Документы
            </button>
            <button
              type="button"
              className="workspace-nav-button"
              onClick={onGoToProfile}
              style={{
                borderRadius: 999,
                padding: "6px 16px",
                background: "linear-gradient(90deg, #1f2937, #111827)",
                color: "#e5e7eb",
                border: "none",
                fontSize: "11px",
              }}
            >
              Профиль
            </button>
            <button
              type="button"
              className="workspace-nav-button workspace-nav-button-danger"
              onClick={onLogout}
              style={{
                borderRadius: 999,
                padding: "6px 16px",
                background: "linear-gradient(90deg, #b91c1c, #7f1d1d)",
                color: "#fee2e2",
                border: "none",
                fontSize: "11px",
              }}
            >
              Выйти
            </button>
          </nav>
        </div>
      </header>

      <main className="workspace-main">
        <section className="workspace-main-left">
          <div className="workspace-chat-header">
            <h1 className="workspace-chat-title" style={{ fontSize: "17px" }}>
              Чат ИИ «Татьяна»
            </h1>
            <p className="workspace-chat-subtitle" style={{ fontSize: "11px" }}>
              Опишите вашу ситуацию — «Татьяна» поможет понять, как действовать,
              и подготовит основу для юридического документа.
            </p>
          </div>

          <div
            className="workspace-mode-toggle"
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "8px",
              marginTop: "8px",
              marginBottom: "8px",
            }}
          >
            <button
              type="button"
              className={
                "workspace-mode-button" +
                (mode === "simple" ? " workspace-mode-button-active" : "")
              }
              onClick={() => setMode("simple")}
              style={{ fontSize: "10px" }}
            >
              Простой режим
            </button>
            <button
              type="button"
              className={
                "workspace-mode-button" +
                (mode === "pro" ? " workspace-mode-button-active" : "")
              }
              onClick={() => setMode("pro")}
              style={{ fontSize: "10px" }}
            >
              Профессиональный режим
            </button>
            <button
              type="button"
              className="workspace-mode-button"
              onClick={handleNewChat}
              style={{ fontSize: "10px" }}
            >
              Новый чат
            </button>
            <button
              type="button"
              className="workspace-mode-button"
              onClick={handleShowGuide}
              style={{ fontSize: "10px" }}
            >
              Инструкция
            </button>
          </div>

          <p className="workspace-placeholder" style={{ fontSize: "10px" }}>
            В простом режиме «Татьяна» объясняет всё человеческим языком, без
            сложных терминов. В профессиональном — отвечает структурированно, с
            правовым анализом.
          </p>

          <p className="workspace-chat-tip" style={{ fontSize: "10px" }}>
            Чем подробнее вы опишете ситуацию (с датами, суммами и ссылками на
            документы), тем точнее «Татьяна» сможет подготовить план действий и
            структуру документов.
          </p>

          <div
            className="workspace-chat-box"
            style={{
              background:
                "radial-gradient(circle at top left, rgba(129, 140, 248, 0.35), rgba(24, 16, \n64, 0.98))",
              boxShadow:
                "0 0 25px rgba(147, 197, 253, 0.45), 0 0 0 1px rgba(168, 85, 247, 0.45)",
            }}
          >
            <div className="workspace-chat-messages">
              {messages.length === 0 ? (
                <div className="workspace-chat-empty">
                  <p style={{ fontSize: "11px" }}>
                    Пока здесь нет сообщений. Опишите кратко вашу ситуацию — и
                    «Татьяна» поможет с юридическим разбором и планом действий.
                  </p>
                  {DEMO_MODE && (
                    <p style={{ fontSize: "10px", opacity: 0.85, marginTop: 8 }}>
                      Сейчас включён демо-режим (VITE_DEMO_MODE=true).
                    </p>
                  )}
                </div>
              ) : (
                messages.map((msg, index) => (
                  <div
                    key={index}
                    className={
                      "workspace-chat-message workspace-chat-message-" + msg.from
                    }
                  >
                    <div
                      className="workspace-chat-message-author"
                      style={{ fontSize: "9px" }}
                    >
                      {msg.from === "user" ? "Вы" : "Татьяна"}
                    </div>
                    <div
                      className="workspace-chat-message-text"
                      style={{ fontSize: "11px" }}
                    >
                      {msg.text.split("\n").map((line, i) => (
                        <p key={i}>{line}</p>
                      ))}
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <div
              className="workspace-chat-input-row"
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px",
                marginTop: "12px",
              }}
            >
              <textarea
                className="workspace-chat-input"
                placeholder="Опишите проблему: кто, с кем, что произошло, какие документы \nесть и чего вы хотите добиться..."
                rows={4}
                value={input}
                onChange={handleInputChange}
                style={{
                  width: "100%",
                  fontSize: "10px",
                  borderRadius: "16px",
                  fontWeight: 400,
                  lineHeight: 1.4,
                }}
              />

              <div
                className="workspace-chat-input-actions"
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  width: "100%",
                  gap: "12px",
                }}
              >
                <label className="workspace-chat-attach" style={{ fontSize: "10px" }}>
                  📎 Прикрепить файл
                  <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    style={{ display: "none" }}
                  />
                </label>
                <button
                  type="button"
                  className="workspace-chat-send-button"
                  onClick={handleSend}
                >
                  ➤
                </button>
              </div>
            </div>
          </div>
        </section>

        <aside className="workspace-main-right">
          <div
            className="workspace-sidepanel"
            style={{
              background:
                "radial-gradient(circle at top left, rgba(129, 140, 248, 0.35), rgba(24, 16, \n64, 0.98))",
              boxShadow:
                "0 0 20px rgba(147, 197, 253, 0.45), 0 0 0 1px rgba(168, 85, 247, 0.45)",
            }}
          >
            <div className="workspace-sidepanel-header">
              <button
                type="button"
                onClick={() => setActiveSidePanel("cases")}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "#e5e7eb",
                  textAlign: "left",
                  width: "100%",
                  fontSize: "12px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Мои дела
              </button>
            </div>
            {activeSidePanel === "cases" && (
  <div className="workspace-sidepanel-body">
    {casesLoading && (
      <p style={{ fontSize: "10px" }}>Загрузка дел…</p>
    )}

    {casesError && (
      <p style={{ fontSize: "10px", color: "#fca5a5" }}>
        Ошибка загрузки дел: {casesError}
      </p>
    )}

    {!casesLoading && !casesError && cases.length === 0 && (
      <p style={{ fontSize: "10px" }}>Дел пока нет.</p>
    )}

    {!casesLoading && !casesError && cases.length > 0 && (
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {cases.map((c) => (
          <li key={c.id}>
            <button
              type="button"
              onClick={() => setActiveCaseId(c.id)}
              style={{
                width: "100%",
                textAlign: "left",
                background:
                  c.id === activeCaseId
                    ? "rgba(168, 85, 247, 0.25)"
                    : "transparent",
                border: "none",
                color: "#e5e7eb",
                padding: "6px 4px",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "11px",
                fontWeight: c.id === activeCaseId ? 600 : 400,
              }}
            >
              {c.title || `Дело #${c.id}`}
            </button>
          </li>
        ))}
      </ul>
    )}
  </div>
)}
          </div>
{/* История версий документа (2.5) */}
<div className="workspace-sidepanel" style={{ marginTop: "16px" }}>
  <div className="workspace-sidepanel-header">
    <div
      style={{
        background: "transparent",
        border: "none",
        color: "#e5e7eb",
        textAlign: "left",
        width: "100%",
        fontSize: "12px",
        fontWeight: 600,
      }}
    >
      История версий
    </div>
  </div>

  <div className="workspace-sidepanel-body">
    {!activeDocumentId ? (
      <p style={{ fontSize: "10px", opacity: 0.85 }}>
        Выберите документ, чтобы увидеть историю версий.
      </p>
    ) : versionsLoading ? (
      <p style={{ fontSize: "10px" }}>Загрузка истории версий…</p>
    ) : versionsError ? (
      <p style={{ fontSize: "10px", color: "#fca5a5" }}>
        Ошибка загрузки версий: {versionsError}
      </p>
    ) : versions.length === 0 ? (
      <p style={{ fontSize: "10px", opacity: 0.85 }}>Версий пока нет.</p>
    ) : (
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {versions.map((v: any) => (
            <button
              key={v.id}
              type="button"
              onClick={() => {
                setSelectedVersionId(v.id);
                setSelectedVersionContent(typeof v.content === "string" ? v.content : "");
              }}
              style={{
                textAlign: "left",
                padding: "8px 10px",
                borderRadius: 10,
                border: "1px solid rgba(255,255,255,0.12)",
                background:
                  v.id === selectedVersionId
                    ? "rgba(255,255,255,0.08)"
                    : "rgba(255,255,255,0.03)",
                cursor: "pointer",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontSize: 12, fontWeight: 700 }}>
                  v{v.id} · {v.source}
                </span>
                <span style={{ fontSize: 11, opacity: 0.8 }}>
                  {typeof v.created_at === "string"
                    ? v.created_at.replace("T", " ").slice(0, 19)
                    : ""}
                </span>
              </div>
            </button>
          ))}
        </div>

        <div
          style={{
            marginTop: 6,
            padding: 10,
            borderRadius: 12,
            border: "1px solid rgba(255,255,255,0.12)",
            background: "rgba(255,255,255,0.03)",
          }}
        >
          <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 6 }}>
            Предпросмотр (read-only)
          </div>
          <div style={{ fontSize: 13, whiteSpace: "pre-wrap" }}>
            {selectedVersionContent || ""}
          </div>
        </div>
      </div>
    )}
  </div>
</div>

          <div
            className="workspace-sidepanel"
            style={{
              marginTop: "16px",
              background:
                "radial-gradient(circle at top left, rgba(129, 140, 248, 0.35), rgba(24, 16, \n64, 0.98))",
              boxShadow:
                "0 0 20px rgba(147, 197, 253, 0.45), 0 0 0 1px rgba(168, 85, 247, 0.45)",
            }}
          >
            <div className="workspace-sidepanel-header">
              <button
                type="button"
                onClick={() => setActiveSidePanel("docs")}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "#e5e7eb",
                  textAlign: "left",
                  width: "100%",
                  fontSize: "12px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Документы
              </button>
            </div>
            {activeSidePanel === "docs" && (
              <div className="workspace-sidepanel-body">
                {documentsLoading && (
  <p style={{ fontSize: "10px" }}>Загрузка документов…</p>
)}

{documentsError && (
  <p style={{ fontSize: "10px", color: "#fca5a5" }}>
    Ошибка загрузки документов: {documentsError}
  </p>
)}

{!documentsLoading && !documentsError && !activeCaseId && (
  <p style={{ fontSize: "10px" }}>
    Сначала выберите дело.
  </p>
)}

{!documentsLoading &&
  !documentsError &&
  activeCaseId &&
  documents.length === 0 && (
    <p style={{ fontSize: "10px" }}>
      В этом деле пока нет документов.
    </p>
  )}

{!documentsLoading &&
  !documentsError &&
  activeCaseId &&
  documents.length > 0 && (
    <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {documents.map((d) => (
        <li key={d.id}>
          <button
            type="button"
            onClick={() => setActiveDocumentId(d.id)}
            style={{
              width: "100%",
              textAlign: "left",
              background:
                d.id === activeDocumentId
                  ? "rgba(56, 189, 248, 0.25)"
                  : "transparent",
              border: "none",
              color: "#e5e7eb",
              padding: "6px 4px",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "11px",
              fontWeight: d.id === activeDocumentId ? 600 : 400,
            }}
          >
            {d.title || `Документ #${d.id}`}
          </button>
        </li>
      ))}
    </ul>
  )}
              </div>
            )}
          </div>
{/* История версий документа */}
<div style={{ marginTop: 12 }}>
  <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
    История версий
  </div>

  {!activeDocumentId ? (
    <div style={{ opacity: 0.8, fontSize: 13 }}>
      Выберите документ, чтобы увидеть историю версий.
    </div>
  ) : versionsLoading ? (
    <div style={{ opacity: 0.8, fontSize: 13 }}>
      Загрузка истории версий…
    </div>
  ) : versionsError ? (
    <div style={{ color: "#fca5a5", fontSize: 13 }}>
      Ошибка загрузки версий: {versionsError}
    </div>
  ) : versions.length === 0 ? (
    <div style={{ opacity: 0.8, fontSize: 13 }}>
      Версий пока нет.
    </div>
  ) : (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {versions.map((v) => (
        <button
          key={v.id}
          type="button"
          onClick={() => {
            setSelectedVersionId(v.id);
            setSelectedVersionContent(v.content || "");
          }}
          style={{
            textAlign: "left",
            padding: "8px 10px",
            borderRadius: 10,
            border: "1px solid rgba(255,255,255,0.12)",
            background:
              v.id === selectedVersionId
                ? "rgba(255,255,255,0.08)"
                : "rgba(255,255,255,0.03)",
            cursor: "pointer",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontSize: 12, fontWeight: 700 }}>
              v{v.id} · {v.source}
            </span>
            <span style={{ fontSize: 11, opacity: 0.8 }}>
              {v.created_at?.replace("T", " ").slice(0, 19)}
            </span>
          </div>
        </button>
      ))}

      <div
        style={{
          marginTop: 6,
          padding: 10,
          borderRadius: 12,
          border: "1px solid rgba(255,255,255,0.12)",
          background: "rgba(255,255,255,0.03)",
        }}
      >
        <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 6 }}>
          Предпросмотр (read-only)
        </div>
        <div style={{ fontSize: 13, whiteSpace: "pre-wrap" }}>
          {selectedVersionContent || ""}
        </div>
      </div>
    </div>
  )}
</div>
        </aside>
      </main>

      <section
        className="workspace-editor"
        style={{
          background:
            "radial-gradient(circle at top left, rgba(129, 140, 248, 0.3), rgba(15, 23, \n42, 0.98))",
          boxShadow:
            "0 0 25px rgba(147, 197, 253, 0.4), 0 0 0 1px rgba(168, 85, 247, 0.4)",
        }}
      >
        <div className="workspace-editor-header">
          <h2 className="workspace-editor-title" style={{ fontSize: "17px" }}>
            Редактор документа
          </h2>
          <p className="workspace-editor-subtitle" style={{ fontSize: "11px" }}>
            Здесь формируется результат работы «Татьяны» — черновик договора,
            претензии, заявления или иного юридического документа. Вы можете
            править текст вручную или через подсказки в чате.
          </p>
        </div>

        <div className="workspace-editor-body">
         {documentLoading && (
  <p style={{ fontSize: "11px", marginBottom: "6px" }}>
    Загрузка текста документа…
  </p>
)}

{documentError && (
  <p style={{ fontSize: "11px", color: "#fca5a5", marginBottom: "6px" }}>
    Ошибка загрузки текста документа: {documentError}
  </p>
)} 

{saveOk && (
  <p style={{ fontSize: "11px", color: "#86efac", marginBottom: "6px" }}>
    {saveOk}
  </p>
)}
{saveError && (
  <p style={{ fontSize: "11px", color: "#fca5a5", marginBottom: "6px" }}>
    {saveError}
  </p>
)}

{canApplyAiDraft && (

  <div style={{ margin: "8px 0" }}>
    <button
      type="button"
      onClick={async () => {
        if (!activeDocumentId) {
          alert("Сначала выберите документ");
          return;
        }
        if (!editorRef.current) {
          alert("Редактор ещё не готов");
          return;
        }
        if (!selection || selection.from === selection.to) {
          alert("Выделите текст, который нужно заменить");
          return;
        }

        // 1) заменяем выделение в TipTap
        editorRef.current
          .chain()
          .focus()
          .insertContentAt(
            { from: selection.from, to: selection.to },
            aiDraft
          )
          .run();

        // 2) получаем новый HTML документа
        const newHtml = editorRef.current.getHTML();

        // 3) сохраняем новую версию от ИИ
        const res = await fetch(
          `${API_BASE}/documents/${activeDocumentId}/versions`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              content: newHtml,
              source: "ai",
            }),
          }
        );

        if (!res.ok) {
          const t = await res.text();
          alert(
            `Не удалось сохранить AI-версию: ${res.status} ${t.slice(0, 200)}`
          );
          return;
        }

        // 4) обновляем состояние и защищаемся от лишнего автосейва
        setDocumentHtml(newHtml);
        lastSavedHashRef.current = hashText(newHtml);

        // 5) сбрасываем draft
        setAiDraft(null);
      }
}>
      Применить (заменить выделенное)
    </button>
  <p style={{ fontSize: "10px", opacity: 0.85, marginTop: 6 }}>
    Будет заменён только выделенный фрагмент документа.
  </p>

  </div>
)}

         <DocumentEditor
  value={documentHtml}
  onChange={handleDocumentChange}
  onEditorReady={(ed) => {
    editorRef.current = ed;
  }}
  onSelectionChange={(sel) => {
    setSelection(sel);
  }}
/>
        </div>

        <div className="workspace-editor-actions">
          <button
            type="button"
            className="workspace-editor-button"
            onClick={handleInsertDraftTemplate}
            style={{ fontSize: "10px" }}
          >
            Вставить черновой шаблон
          </button>
          <button
  type="button"
  className="workspace-editor-button workspace-editor-button-primary"
  onClick={() => saveVersion("manual")}
  disabled={!activeDocumentId || saving}
  style={{ fontSize: "10px" }}
>
  {saving ? "Сохранение..." : "Сохранить версию"}
</button>
          <button
            type="button"
            className="workspace-editor-button workspace-editor-button-primary"
            onClick={handleSaveDraft}
            style={{ fontSize: "10px" }}
          >
            Сохранить черновик
          </button>
          <button
            type="button"
            className="workspace-editor-button"
            onClick={() => handleDownloadStub("docx")}
            style={{ fontSize: "10px" }}
          >
            Скачать в Word (скоро)
          </button>
          <button
            type="button"
            className="workspace-editor-button"
            onClick={() => handleDownloadStub("pdf")}
            style={{ fontSize: "10px" }}
          >
            Скачать PDF (скоро)
          </button>
        </div>
      </section>

      <footer
        className="workspace-footer"
        style={{
          marginTop: "16px",
          padding: "16px 24px 0",
          fontSize: "10px",
          opacity: 0.85,
        }}
      >
        <div className="workspace-footer-links">
          <a href="#" className="workspace-footer-link">
            Пользовательское соглашение
          </a>
          {" · "}
          <a href="#" className="workspace-footer-link">
            Политика конфиденциальности
          </a>
          {" · "}
          <a href="#" className="workspace-footer-link">
            Контакты
          </a>
        </div>
        <p style={{ marginTop: "8px" }}>
          © {new Date().getFullYear()} LEGALAI. Все права защищены. Материалы,
          создаваемые с помощью сервиса, не являются официальной юридической
          консультацией. За окончательные решения и действия несёт
          ответственность пользователь.
        </p>
      </footer>
    </div>
  );
};

export default WorkspacePage;

