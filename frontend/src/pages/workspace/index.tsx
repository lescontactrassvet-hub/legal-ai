import React, {
  useState,
  useEffect,
  useRef,
  ChangeEvent,
} from "react";
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

function getTatianaDemoReply(mode: WorkspaceMode, userText: string): string {
  const trimmed = userText.trim();

  if (!trimmed) {
    return "Я не увидела текста вопроса. Пожалуйста, опишите ситуацию или задайте \nвопрос — и я подскажу, как действовать с юридической точки зрения.";
  }

  if (mode === "simple") {
    return [
      "Спасибо, что описали ситуацию.",
      "",
      "Сейчас я в демонстрационном режиме и не обращаюсь к настоящей базе законов, \nно могу показать, как будет выглядеть ответ:",
      "",
      "1) Я уточню ключевые факты: даты, стороны, документы и ваши цели.",
      "2) Объясню простыми словами, какие у вас есть права и риски.",
      "3) Предложу конкретный план действий: что собрать, куда обращаться, какие \nшаги делать по порядку.",
      "",
      "В рабочей версии «Татьяна» будет использовать вашу историю обращений, \nшаблоны документов и актуальное законодательство для более точного ответа.",
    ].join("\n");
  }

  // pro-режим
  return [
    "Переключаемся в профессиональный режим.",
    "",
    "В полной версии здесь будет структурированный юридический анализ с ссылками \nна нормы права, судебной практики и готовыми фрагментами документов.",
    "",
    "Обычно ответ будет включать:",
    "— вводную часть (кто, когда и при каких обстоятельствах);",
    "— правовую квалификацию ситуации с указанием статей законов;",
    "— оценку рисков и вероятных исходов;",
    "— рекомендации по дальнейшим действиям и перечень необходимых документов.",
    "",
    "Сейчас это демонстрационный ответ. В будущем «Татьяна» сформирует черновик \nдокумента и предложит сразу отредактировать его в редакторе ниже.",
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
  userText: string
): Promise<string> {
  const base =
    (import.meta as any)?.env?.VITE_API_BASE?.toString?.() ||
    "/api";

  const url = `${base.replace(/\/$/, "")}/ai/ask`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userText,
        intent: mode, // используем режим как "намерение" (simple/pro)
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
        (data && (data.error || data.message)) ||
        `HTTP ${res.status}`;
      throw new Error(msg);
    }

    const answer =
      (data && typeof data.answer === "string" && data.answer.trim()) ||
      (data && typeof data.message === "string" && data.message.trim()) ||
      "";

    const cites = data?.citations ? formatCitations(data.citations) : "";

    if (!answer) {
      // странный ответ, но не падаем
      return `Ответ получен, но поле "answer" пустое.${cites}`;
    }

    return `${answer}${cites}`;
  } catch {
    // fallback на демо, чтобы UX не ломался
    return getTatianaDemoReply(mode, userText);
  }
}

const WorkspacePage: React.FC<WorkspacePageProps> = ({
  onGoToProfile,
  onLogout,
  onGoToDocuments,
}) => {
  const [mode, setMode] = useState<WorkspaceMode>("simple");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [documentHtml, setDocumentHtml] = useState<string>("");
  const [activeSidePanel, setActiveSidePanel] = useState<SidePanel>("cases");

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;

    const userMessage: ChatMessage = { from: "user", text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const replyText = await requestTatianaReply(mode, text);
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
    alert(
      "В демо-версии файлы пока не отправляются на сервер.\nВ рабочей версии \n«Татьяна» сможет анализировать вложенные документы и использовать их в ответах."
    );
  };

  const handleDocumentChange = (html: string) => {
    setDocumentHtml(html);
  };

  const handleInsertDraftTemplate = () => {
    if (documentHtml.trim()) return;

    const template = [
      "<h2>Черновой проект документа</h2>",
      "<p>Ниже — базовая структура юридического документа. Отредактируйте её с \nучетом вашей ситуации или попросите «Татьяну» доработать текст.</p>",
      "<ol>",
      "<li><strong>Вводная часть.</strong> Кто, когда, где, на основании чего \nдействует.</li>",
      "<li><strong>Обстоятельства.</strong> Краткое и последовательное описание \nфактов.</li>",
      "<li><strong>Правовое обоснование.</strong> Указание норм права, ссылок на \nдоговоры, практику.</li>",
      "<li><strong>Просьба / Требование.</strong> Чёткая формулировка того, чего вы \nхотите добиться.</li>",
      "</ol>",
      "<p>После редактирования вы сможете сохранить этот черновик как отдельный \nдокумент и вернуться к нему в разделе «Документы».</p>",
    ].join("");
    setDocumentHtml(template);
  };

  const handleSaveDraft = () => {
    console.log("Сохранение черновика документа. Длина HTML:", documentHtml.length);
    alert(
      "В демо-версии черновик сохраняется только в текущей сессии.\nВ полноценной \nверсии он появится в разделе «Документы» как отдельный проект."
    );
  };

  const handleDownloadStub = (format: "pdf" | "docx") => {
    const label = format === "pdf" ? "PDF" : "Word (DOCX)";
    alert(
      `Экспорт в ${label} будет доступен после подключения модуля генерации файлов \nна backend.\nПока вы можете скопировать текст и вставить его в привычный \nредактор.`
    );
  };

  const handleGoToDocumentsClick = () => {
    if (onGoToDocuments) {
      onGoToDocuments();
    } else {
      alert(
        "Раздел «Документы» будет доступен через отдельную страницу.\nСейчас эта \nкнопка работает как заглушка."
      );
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setInput("");
  };

  const handleShowGuide = () => {
    alert(
      [
        "Как пользоваться рабочей страницей LEGALAI:",
        "",
        "1. Вверху страницы выберите режим: простой или профессиональный.",
        "2. В большом поле чата опишите вашу ситуацию и, при необходимости, \nприкрепите файлы.",
        "3. «Татьяна» в демо-режиме покажет пример того, как будет выглядеть разбор.",
        "4. Ниже в редакторе документа вы можете доработать черновик, сохранить его \nили подготовить к экспорту.",
        "",
        "Важно: сейчас это демонстрационная версия без реальных юридических \nконсультаций и сохранения данных на сервере.",
      ].join("\n")
    );
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
              marginLeft: "auto", // уводим блок кнопок вправо от логотипа
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

          {/* ВСЕ ЧЕТЫРЕ КНОПКИ В ОДНОЙ ЛИНИИ */}
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
                    Пока здесь нет сообщений. Напишите кратко, в чём ваша
                    ситуация, и «Татьяна» покажет, как будет выглядеть
                    юридический разбор в демо-режиме.
                  </p>
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
                  justifyContent: "space-between", // разъезжаемся по краям
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

        {/* ПРАВЫЕ БЛОКИ — АККОРДЕОН */}
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
                <p style={{ fontSize: "10px" }}>
                  Здесь появится список ваших дел с кратким статусом: «на
                  подготовке», «отправлено», «ожидание ответа», «завершено».
                </p>
                <p style={{ fontSize: "10px" }}>
                  В полной версии вы сможете быстро переходить к делу, открывать
                  чат и связанные документы в один клик.
                </p>
              </div>
            )}
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
                <p style={{ fontSize: "10px" }}>
                  Здесь будет список документов: черновики, финальные версии,
                  приложения и связанные файлы.
                </p>
                <p style={{ fontSize: "10px" }}>
                  Черновики, созданные в редакторе ниже, позже будут
                  сохраняться сюда автоматически.
                </p>
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
          <DocumentEditor value={documentHtml} onChange={handleDocumentChange} />
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

