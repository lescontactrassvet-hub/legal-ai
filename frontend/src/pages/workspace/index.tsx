import React, {
  useState,
  useEffect,
  useRef,
  ChangeEvent,
  KeyboardEvent,
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

function getTatianaDemoReply(mode: WorkspaceMode, userText: string): string {
  const trimmed = userText.trim();

  if (!trimmed) {
    return "Я не увидела текста вопроса. Пожалуйста, опишите ситуацию или задайте вопрос — и я подскажу, как действовать с юридической точки зрения.";
  }

  if (mode === "simple") {
    return [
      "Спасибо, что описали ситуацию.",
      "",
      "Сейчас я в демонстрационном режиме и не обращаюсь к настоящей базе законов, но могу показать, как будет выглядеть ответ:",
      "",
      "1) Я уточню ключевые факты: даты, стороны, документы и ваши цели.",
      "2) Объясню простыми словами, какие у вас есть права и риски.",
      "3) Предложу конкретный план действий: что собрать, куда обращаться, какие шаги делать по порядку.",
      "",
      "В рабочей версии «Татьяна» будет использовать вашу историю обращений, шаблоны документов и актуальное законодательство для более точного ответа.",
    ].join("\n");
  }

  // pro-режим
  return [
    "Переключаемся в профессиональный режим.",
    "",
    "В полной версии здесь будет структурированный юридический анализ с ссылками на нормы права, судебную практику и готовыми фрагментами документов.",
    "",
    "Обычно ответ будет включать:",
    "— вводную часть (кто, когда и при каких обстоятельствах);",
    "— правовую квалификацию ситуации с указанием статей законов;",
    "— оценку рисков и вероятных исходов;",
    "— рекомендации по дальнейшим действиям и перечень необходимых документов.",
    "",
    "Сейчас это демонстрационный ответ. В будущем «Татьяна» сформирует черновик документа и предложит сразу отредактировать его в редакторе ниже.",
  ].join("\n");
}

async function requestTatianaReply(
  mode: WorkspaceMode,
  userText: string
): Promise<string> {
  // TODO: здесь позже будет реальный HTTP-запрос к backend Татьяны.
  // Пока возвращаем демо-ответ.
  return Promise.resolve(getTatianaDemoReply(mode, userText));
}

const WorkspacePage: React.FC<WorkspacePageProps> = ({
  onGoToProfile,
  onLogout,
  onGoToDocuments,
}) => {
  const [mode, setMode] = useState<WorkspaceMode>("simple");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [activeSidePanel, setActiveSidePanel] = useState<SidePanel>("cases");
  const [documentHtml, setDocumentHtml] = useState<string>("");

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

  const handleInputKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      void handleSend();
    }
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    console.log("Выбрано файлов для Татьяны:", files.length);
    alert(
      "В демо-версии файлы пока не отправляются на сервер.\nВ рабочей версии «Татьяна» сможет анализировать вложенные документы и использовать их в ответах."
    );
  };

  const handleDocumentChange = (html: string) => {
    setDocumentHtml(html);
  };

  const handleInsertDraftTemplate = () => {
    if (documentHtml.trim()) return;

    const template = [
      "<h2>Черновой проект документа</h2>",
      "<p>Ниже — базовая структура юридического документа. Отредактируйте её с учётом вашей ситуации или попросите «Татьяну» доработать текст.</p>",
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
    alert(
      "В демо-версии черновик сохраняется только в текущей сессии.\nВ полноценной версии он появится в разделе «Документы» как отдельный проект."
    );
  };

  const handleDownloadStub = (format: "pdf" | "docx") => {
    const label = format === "pdf" ? "PDF" : "Word (DOCX)";
    alert(
      `Экспорт в ${label} будет доступен после подключения модуля генерации файлов на backend.\nПока вы можете скопировать текст и вставить его в привычный редактор.`
    );
  };

  const handleGoToDocumentsClick = () => {
    if (onGoToDocuments) {
      onGoToDocuments();
    } else {
      alert(
        "Раздел «Документы» будет доступен через отдельную страницу.\nСейчас эта кнопка работает как заглушка."
      );
    }
  };

  return (
    <div className="workspace-root">
      <header className="workspace-header">
        <div className="workspace-header-inner">
          <div className="workspace-logo-block">
            <img
              src="/logo.png"
              alt="LEGALAI"
              className="workspace-logo"
            />
            <div className="workspace-logo-text">
              <div className="workspace-logo-title">LEGALAI</div>
              <div className="workspace-logo-subtitle">
                Юридический ИИ — «Татьяна»
              </div>
            </div>
          </div>

          <nav className="workspace-nav">
            <button
              type="button"
              className="workspace-nav-button workspace-nav-button-primary"
            >
              Чат ИИ «Татьяна»
            </button>
            <button
              type="button"
              className="workspace-nav-button"
              onClick={handleGoToDocumentsClick}
            >
              Документы
            </button>
            <button
              type="button"
              className="workspace-nav-button"
              onClick={onGoToProfile}
            >
              Профиль
            </button>
            <button
              type="button"
              className="workspace-nav-button workspace-nav-button-danger"
              onClick={onLogout}
            >
              Выйти
            </button>
          </nav>
        </div>
      </header>

      <main className="workspace-main">
        <section className="workspace-main-left">
          <div className="workspace-chat-header">
            <h1 className="workspace-chat-title">Чат ИИ «Татьяна»</h1>
            <p className="workspace-chat-subtitle">
              Опишите вашу ситуацию — «Татьяна» поможет понять, как действовать,
              и подготовит основу для юридического документа.
            </p>
          </div>

          <div className="workspace-mode-toggle">
            <button
              type="button"
              className={
                "workspace-mode-button" +
                (mode === "simple" ? " workspace-mode-button-active" : "")
              }
              onClick={() => setMode("simple")}
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
            >
              Профессиональный режим
            </button>
          </div>

          <p className="workspace-placeholder">
            В простом режиме «Татьяна» объясняет всё человеческим языком, без
            сложных терминов. В профессиональном — отвечает структурированно,
            с правовым анализом.
          </p>

          <p className="workspace-chat-tip">
            Чем подробнее вы опишете ситуацию (с датами, суммами и ссылками на
            документы), тем точнее «Татьяна» сможет подготовить план действий и
            структуру документов.
          </p>

          <div className="workspace-chat-box">
            <div className="workspace-chat-messages">
              {messages.length === 0 ? (
                <div className="workspace-chat-empty">
                  <p>
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
                      "workspace-chat-message workspace-chat-message-" +
                      msg.from
                    }
                  >
                    <div className="workspace-chat-message-author">
                      {msg.from === "user" ? "Вы" : "Татьяна"}
                    </div>
                    <div className="workspace-chat-message-text">
                      {msg.text.split("\n").map((line, i) => (
                        <p key={i}>{line}</p>
                      ))}
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="workspace-chat-input-row">
              <label className="workspace-chat-attach">
                📎
                <input
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  style={{ display: "none" }}
                />
              </label>
              <textarea
                className="workspace-chat-input"
                placeholder="Опишите проблему: кто, с кем, что произошло, какие документы есть и чего вы хотите добиться..."
                rows={4}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleInputKeyDown}
              />
              <button
                type="button"
                className="workspace-chat-send-button"
                onClick={handleSend}
              >
                ➤
              </button>
            </div>
          </div>
        </section>

        <aside className="workspace-main-right">
          <div className="workspace-sidepanel">
            <div className="workspace-sidepanel-header">
              <div className="workspace-sidepanel-title">Мои дела</div>
              <button
                type="button"
                className="workspace-sidepanel-toggle"
                onClick={() =>
                  setActiveSidePanel((prev) =>
                    prev === "cases" ? "docs" : "cases"
                  )
                }
              >
                {activeSidePanel === "cases" ? "К документам" : "К делам"}
              </button>
            </div>
            {activeSidePanel === "cases" && (
              <div className="workspace-sidepanel-body">
                <p>
                  Здесь появится список ваших дел с кратким статусом: «на
                  подготовке», «отправлено», «ожидание ответа», «завершено».
                </p>
                <p>
                  В полной версии вы сможете быстро переходить к делу, открывать
                  чат и связанные документы в один клик.
                </p>
              </div>
            )}
          </div>

          <div className="workspace-sidepanel">
            <div className="workspace-sidepanel-header">
              <div className="workspace-sidepanel-title">Документы</div>
              <button
                type="button"
                className="workspace-sidepanel-toggle"
                onClick={handleGoToDocumentsClick}
              >
                Открыть
              </button>
            </div>
            {activeSidePanel === "docs" && (
              <div className="workspace-sidepanel-body">
                <p>
                  Здесь будет список документов: черновики, финальные версии,
                  приложения и связанные файлы.
                </p>
                <p>
                  Черновики, созданные в редакторе ниже, позже будут сохраняться
                  сюда автоматически.
                </p>
              </div>
            )}
          </div>
        </aside>
      </main>

      <section className="workspace-editor">
        <div className="workspace-editor-header">
          <h2 className="workspace-editor-title">Редактор документа</h2>
          <p className="workspace-editor-subtitle">
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
          >
            Вставить черновой шаблон
          </button>
          <button
            type="button"
            className="workspace-editor-button workspace-editor-button-primary"
            onClick={handleSaveDraft}
          >
            Сохранить черновик
          </button>
          <button
            type="button"
            className="workspace-editor-button"
            onClick={() => handleDownloadStub("docx")}
          >
            Скачать в Word (скоро)
          </button>
          <button
            type="button"
            className="workspace-editor-button"
            onClick={() => handleDownloadStub("pdf")}
          >
            Скачать PDF (скоро)
          </button>
        </div>
      </section>
    </div>
  );
};

export default WorkspacePage;

