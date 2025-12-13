 import React, { useState, useEffect, useRef, ChangeEvent } from "react";
import DocumentEditor from "../../components/DocumentEditor";
import { useCasesDocuments } from "../../hooks/useCasesDocuments";

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
const DEMO_MODE =
 ((import.meta as any)?.env?.VITE_DEMO_MODE?.toString?.() || "").toLowerCase() ===
 "true";

function getTatianaDemoReply(mode: WorkspaceMode, userText: string): string {
 const trimmed = userText.trim();

 if (!trimmed) {
  return (
   "Я не увидела текста вопроса. Пожалуйста, опишите ситуацию или задайте \n" +
   "вопрос — и я подскажу, как действовать с юридической точки зрения."
  );
 }

 const lower = trimmed.toLowerCase();

 // простая демонстрация "умности"
 if (lower.includes("договор") || lower.includes("расторг")) {
  if (mode === "simple") {
   return [
    "В демонстрационном режиме я могу дать общий ориентир.",
    "",
    "Если речь о расторжении договора в одностороннем порядке, чаще всего нужно:",
    "1) проверить, предусмотрено ли это самим договором;",
    "2) уточнить основания (существенное нарушение, срок, отказ по закону);",
    "3) направить уведомление второй стороне (обычно заказным письмом/электронно).",
    "",
    "В боевом режиме я бы уточнила тип договора и условия, затем сослалась на нормы (например, ст. 450 ГК РФ и др.) и предложила текст уведомления.",
   ].join("\n");
  }

  return [
   "Переключаемся в профессиональный режим.",
   "",
   "Сейчас включён демонстрационный режим (VITE_DEMO_MODE=true).",
   "В полной версии здесь будет структурированный юридический анализ со ссылками",
   "на нормы права, судебную практику и фрагменты документов.",
   "",
   "Обычно ответ включает:",
   "— вводную часть (кто, когда и при каких обстоятельствах);",
   "— правовую квалификацию ситуации с указанием статей;",
   "— перечень доказательств/документов;",
   "— пошаговый план действий;",
   "— черновики документов (уведомление/претензия/иск).",
  ].join("\n");
 }

 // универсальный демо-ответ
 if (mode === "simple") {
  return [
   "Сейчас включён демонорежим (VITE_DEMO_MODE=true).",
   "",
   "Опишите:",
   "— кто участники (физ/юр лица),",
   "— что произошло (когда, где, какие документы есть),",
   "— чего вы хотите добиться.",
   "",
   "И я дам ориентир по правовой позиции и действиям.",
  ].join("\n");
 }

 return [
  "Демонорежим: профессиональный ответ.",
  "",
  "В полной версии я бы:",
  "1) уточнила факты и цели;",
  "2) выделила юридически значимые обстоятельства;",
  "3) подобрала применимые нормы;",
  "4) предложила структуру документа/заявления;",
  "5) подготовила черновик текста.",
 ].join("\n");
}

async function requestTatianaReply(mode: WorkspaceMode, userText: string): Promise<string> {
 if (DEMO_MODE) {
  return getTatianaDemoReply(mode, userText);
 }

 const API_BASE =
  (import.meta as any)?.env?.VITE_API_BASE?.toString?.() || "/api";

 try {
  const res = await fetch(`${API_BASE}/ai/ask`, {
   method: "POST",
   headers: { "Content-Type": "application/json" },
   body: JSON.stringify({
    message: userText,
    mode,
   }),
  });

  const raw = await res.text();
  let data: TatianaAskResponse | null = null;

  try {
   data = raw ? (JSON.parse(raw) as TatianaAskResponse) : null;
  } catch {
   // если вдруг вернули HTML/текст — покажем кусок
   if (!res.ok) {
    return [
     "Сервер вернул неожиданный ответ (не JSON).",
     "Проверьте настройки VITE_API_BASE и прокси /api.",
     "",
     `HTTP ${res.status}: ${raw.slice(0, 200)}`,
    ].join("\n");
   }
   return raw;
  }

  if (!res.ok) {
   const msg = (data && (data.error || data.message)) || `HTTP ${res.status}`;
   return [
    "Не удалось получить ответ от сервера.",
    "Проверьте доступность backend и настройки VITE_API_BASE.",
    "",
    `Техническая информация: ${String(msg)}`,
   ].join("\n");
  }

  if (!data) {
   return "Сервер вернул пустой ответ. Попробуйте ещё раз.";
  }

  if (data.answer) return data.answer;

  return "Ответ не получен. Попробуйте переформулировать запрос.";
 } catch (e: any) {
  const msg = e?.message ? String(e.message) : String(e);
  return [
   "Ошибка соединения с backend.",
   "Проверьте, что сервер запущен и VITE_API_BASE настроен правильно.",
   "Для продакшена обычно: VITE_API_BASE=/api",
   "",
   `Техническая информация: ${msg}`,
  ].join("\n");
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

 const API_BASE =
  (import.meta as any)?.env?.VITE_API_BASE?.toString?.() || "/api";

 const {
  cases,
  documents,
  versions,
  loadingCases,
  loadingDocuments,
  loadingVersions,
  error: casesError,
  activeCaseId,
  activeDocumentId,
  selectCase,
  selectDocument,
  saveVersion,
 } = useCasesDocuments(API_BASE);

 const messagesEndRef = useRef<HTMLDivElement | null>(null);

 useEffect(() => {
  if (!activeDocumentId) return;

  // Берём последнюю версию (если есть) и подставляем в редактор.
  if (versions && versions.length > 0) {
   const last = versions[versions.length - 1] as any;
   const content =
    (last?.content ?? last?.text ?? "")?.toString?.() || "";
   setDocumentHtml(content);
  } else {
   // Если версий нет — оставляем текущий текст, но можно начать с пустого.
   // setDocumentHtml("");
  }
 }, [activeDocumentId, versions]);

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

  if (DEMO_MODE) {
   alert(
    "Демо-режим: файлы сохраняются только локально и не отправляются в backend.\n" +
     `Выбрано файлов: ${files.length}`
   );
   return;
  }

  alert(
   "Загрузка файлов на сервер пока не подключена.\n" +
    "Следующий этап: связка Workspace ↔ Документы ↔ Мои дела + загрузка вложений."
  );
 };

 const handleDocumentHtmlChange = (value: string) => {
  setDocumentHtml(value);
 };

 const handleInsertDraftTemplate = () => {
  const template = [
   "<h2>Черновик документа</h2>",
   "<p><b>1) Вводные данные</b></p>",
   "<ul>",
   "<li>ФИО / Название организации:</li>",
   "<li>Контакты:</li>",
   "<li>Адрес:</li>",
   "</ul>",
   "<p><b>2) Описание ситуации</b></p>",
   "<p>Кратко опишите обстоятельства, даты, участников, договоры/акты.</p>",
   "<p><b>3) Правовая позиция</b></p>",
   "<p>Здесь будет обоснование со ссылками на нормы права.</p>",
   "<p><b>4) Требования</b></p>",
   "<p>Что вы просите: расторгнуть, взыскать, признать, обязать и т.д.</p>",
   "<p><b>5) Приложения</b></p>",
   "<p>Перечень документов, которые нужно приложить.</p>",
   "<hr/>",
   "<p style='font-size: 12px; color: #6b7280;'>",
   "⚠️ Это черновик-шаблон. В полной версии Татьяна сможет автоматически заполнить ",
   "его по данным дела/документа и вернуть готовый проект.",
   "</p>",
   "<p style='font-size: 12px; color: #6b7280;'>",
   "Также можно будет сохранить документ и вернуться к нему в разделе «Документы».",
   "</p>",
  ].join("");
  setDocumentHtml(template);
 };

 const handleSaveDraft = async () => {
  console.log("Сохранение черновика документа. Длина HTML:", documentHtml.length);

  if (DEMO_MODE) {
   alert(
    "В демо-режиме черновик сохраняется только в текущей сессии.\n" +
     "В полноценной версии он появится в разделе «Документы» как отдельный проект."
   );
   return;
  }

  if (!activeDocumentId) {
   alert(
    "Документ не выбран.\n" +
     "Сначала выберите дело и документ в боковой панели, затем сохраните версию."
   );
   return;
  }

  try {
   await saveVersion(activeDocumentId, documentHtml, "user");
   alert("Версия документа сохранена ✅");
  } catch (e: any) {
   alert(
    "Не удалось сохранить версию документа на сервер.\n" +
     "Проверьте доступность backend и настройки VITE_API_BASE.\n\n" +
     `Техническая информация: ${e?.message ? String(e.message) : String(e)}`
   );
  }
 };

 const handleDownloadStub = (format: "pdf" | "docx") => {
  const label = format === "pdf" ? "PDF" : "Word (DOCX)";
  alert(
   `Экспорт в ${label} будет доступен после подключения модуля генерации файлов на backend.\n` +
    "Пока вы можете скопировать текст и вставить его в привычный редактор."
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
     <div className="workspace-logo">
      <div className="workspace-logo-badge">LA</div>
      <div>
       <div className="workspace-logo-title">LEGALAI</div>
       <div className="workspace-logo-subtitle">
        Рабочая зона · ИИ “Татьяна”
       </div>
      </div>
     </div>

     <div className="workspace-header-actions">
      <button
       type="button"
       className="workspace-header-button"
       onClick={() => setMode("simple")}
       style={{
        background: mode === "simple" ? "rgba(255,255,255,0.12)" : "transparent",
       }}
      >
       Simple
      </button>
      <button
       type="button"
       className="workspace-header-button"
       onClick={() => setMode("pro")}
       style={{
        background: mode === "pro" ? "rgba(255,255,255,0.12)" : "transparent",
       }}
      >
       Pro
      </button>

      <button
       type="button"
       className="workspace-header-button"
       onClick={onGoToProfile}
      >
       Профиль
      </button>
      {onGoToDocuments && (
       <button
        type="button"
        className="workspace-header-button"
        onClick={onGoToDocuments}
       >
        Документы
       </button>
      )}
      <button
       type="button"
       className="workspace-header-button workspace-header-button-danger"
       onClick={onLogout}
      >
       Выйти
      </button>
     </div>
    </div>
   </header>

   <main className="workspace-main">
    <div className="workspace-grid">
     <aside className="workspace-sidebar">
      <div className="workspace-sidebar-card">
       <h2 style={{ marginTop: 0 }}>Контекст работы</h2>
       <p style={{ fontSize: "11px" }}>
        Вы можете держать под рукой дело, документы и общий чат.
       </p>
       <p style={{ fontSize: "10px" }}>
        В демо-режиме (VITE_DEMO_MODE=true) ответы и сохранения не уходят
        на backend. В боевом режиме — работают реальный чат и интеграции.
       </p>

       <div
        className="workspace-sidebar-info"
        style={{
         display: "flex",
         flexDirection: "column",
         gap: "8px",
         marginTop: "10px",
        }}
       >
        <div className="workspace-pill">
         <b>Режим:</b> {mode === "simple" ? "Simple" : "Pro"}
        </div>
        <div className="workspace-pill">
         <b>Демо:</b> {DEMO_MODE ? "Включен" : "Выключен"}
        </div>
        <div className="workspace-pill">
         <b>API:</b> {API_BASE}
        </div>
        <div className="workspace-pill">
         <b>Активное дело:</b> {activeCaseId ? `#${activeCaseId}` : "не выбрано"}
        </div>
        <div className="workspace-pill">
         <b>Активный документ:</b>{" "}
         {activeDocumentId ? `#${activeDocumentId}` : "не выбран"}
        </div>
       </div>
      </div>

      <div className="workspace-sidebar-card" style={{ marginTop: "16px" }}>
       <h3 style={{ marginTop: 0 }}>Файлы и приложения</h3>
       <p style={{ fontSize: "10px" }}>
        Здесь будет загрузка документов, сканов и вложений для анализа.
       </p>

       <div
        className="workspace-chat-attach-wrapper"
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
         className="workspace-header-button"
         onClick={() => alert("Импорт файлов будет подключён позже.")}
         style={{ fontSize: "10px", padding: "6px 10px" }}
        >
         Импорт
        </button>
       </div>

       <div style={{ marginTop: "10px" }}>
        <p style={{ fontSize: "10px" }}>
         В полной версии вы сможете быстро переходить к делу, открывать чат и
         связанные документы в один клик.
        </p>
       </div>
      </div>

      <div
       className="workspace-sidepanel"
       style={{
        marginTop: "16px",
        background:
         "radial-gradient(circle at top left, rgba(129, 140, 248, 0\n.35), rgba(24, 16, \n64, 0.98))",
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
         <p style={{ fontSize: "10px", marginTop: 0 }}>
          Выберите дело, чтобы загрузить связанные документы и продолжить работу
          в контексте конкретного кейса.
         </p>

         {loadingCases && <div style={{ fontSize: "10px" }}>Загрузка дел…</div>}
         {casesError && (
          <div style={{ fontSize: "10px", color: "#fca5a5" }}>{casesError}</div>
         )}

         {!loadingCases && !casesError && cases.length === 0 && (
          <div style={{ fontSize: "10px", opacity: 0.85 }}>
           Дел пока нет. Создание дел будет добавлено отдельной кнопкой.
          </div>
         )}

         <div
          style={{
           display: "flex",
           flexDirection: "column",
           gap: "6px",
           marginTop: "10px",
          }}
         >
          {cases.map((c) => (
           <button
            key={c.id}
            type="button"
            onClick={() => selectCase(c.id)}
            style={{
             width: "100%",
             textAlign: "left",
             background:
              activeCaseId === c.id
               ? "rgba(255,255,255,0.08)"
               : "rgba(255,255,255,0.04)",
             border: "1px solid rgba(255,255,255,0.08)",
             color: "#e5e7eb",
             padding: "8px",
             borderRadius: "10px",
             cursor: "pointer",
             fontSize: "11px",
            }}
           >
            <div style={{ fontWeight: 700 }}>{c.title || `Дело #${c.id}`}</div>
            {c.description && (
             <div style={{ fontSize: "10px", opacity: 0.85, marginTop: "4px" }}>
              {c.description}
             </div>
            )}
           </button>
          ))}
         </div>
        </div>
       )}

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
         <p style={{ fontSize: "10px", marginTop: 0 }}>
          Список документов выбранного дела. Выберите документ, чтобы открыть
          его версии и продолжить работу в редакторе.
         </p>

         {!activeCaseId && (
          <div style={{ fontSize: "10px", opacity: 0.85 }}>
           Сначала выберите дело в разделе «Мои дела».
          </div>
         )}

         {activeCaseId && loadingDocuments && (
          <div style={{ fontSize: "10px" }}>Загрузка документов…</div>
         )}

         {activeCaseId && !loadingDocuments && documents.length === 0 && (
          <div style={{ fontSize: "10px", opacity: 0.85 }}>
           У этого дела пока нет документов. Создание документов будет добавлено
           отдельной кнопкой.
          </div>
         )}

         <div
          style={{
           display: "flex",
           flexDirection: "column",
           gap: "6px",
           marginTop: "10px",
          }}
         >
          {documents.map((d) => (
           <button
            key={d.id}
            type="button"
            onClick={() => selectDocument(d.id)}
            style={{
             width: "100%",
             textAlign: "left",
             background:
              activeDocumentId === d.id
               ? "rgba(255,255,255,0.08)"
               : "rgba(255,255,255,0.04)",
             border: "1px solid rgba(255,255,255,0.08)",
             color: "#e5e7eb",
             padding: "8px",
             borderRadius: "10px",
             cursor: "pointer",
             fontSize: "11px",
            }}
           >
            <div style={{ fontWeight: 700 }}>
             {d.title || `Документ #${d.id}`}
            </div>
            {d.type && (
             <div style={{ fontSize: "10px", opacity: 0.85, marginTop: "4px" }}>
              {d.type}
             </div>
            )}
           </button>
          ))}
         </div>

         {activeDocumentId && (
          <div style={{ marginTop: "12px" }}>
           <div style={{ fontSize: "10px", opacity: 0.85 }}>
            Версии документа: {loadingVersions ? "загрузка…" : versions.length}
           </div>
           {!loadingVersions && versions.length > 0 && (
            <div
             style={{
              marginTop: "6px",
              display: "flex",
              flexDirection: "column",
              gap: "6px",
             }}
            >
             {versions.slice(-5).map((v) => (
              <div
               key={v.id}
               style={{
                background: "rgba(0,0,0,0.22)",
                border: "1px solid rgba(255,255,255,0.08)",
                padding: "8px",
                borderRadius: "10px",
                fontSize: "10px",
               }}
              >
               <div style={{ fontWeight: 700 }}>
                Версия #{v.id} {v.source ? `· ${v.source}` : ""}
               </div>
               {v.created_at && (
                <div style={{ opacity: 0.85, marginTop: "4px" }}>
                 {v.created_at}
                </div>
               )}
              </div>
             ))}
            </div>
           )}
          </div>
         )}
        </div>
       )}
      </div>
     </aside>

     <section className="workspace-chat">
      <div className="workspace-chat-card">
       <div className="workspace-chat-header">
        <div>
         <div className="workspace-chat-title">Чат с Татьяной</div>
         <div className="workspace-chat-subtitle">
          Задайте вопрос или уточните задачу для документа
         </div>
        </div>

        <div style={{ fontSize: "10px", opacity: 0.85 }}>
         {DEMO_MODE ? "DEMO" : "LIVE"}
        </div>
       </div>

       <div className="workspace-chat-messages">
        {messages.length === 0 && (
         <div className="workspace-chat-empty">
          <div style={{ fontWeight: 700, marginBottom: "6px" }}>
           Начните диалог
          </div>
          <div style={{ fontSize: "11px", opacity: 0.9 }}>
           Например: «Составь претензию», «Проанализируй договор», «Какие риски в
           этом документе?»
          </div>
         </div>
        )}

        {messages.map((m, idx) => (
         <div
          key={idx}
          className={
           m.from === "user"
            ? "workspace-chat-bubble workspace-chat-bubble-user"
            : "workspace-chat-bubble workspace-chat-bubble-ai"
          }
         >
          {m.text}
         </div>
        ))}
        <div ref={messagesEndRef} />
       </div>

       <div className="workspace-chat-input">
        <textarea
         value={input}
         onChange={handleInputChange}
         placeholder="Введите сообщение…"
         rows={3}
        />
        <div className="workspace-chat-controls">
         <button
          type="button"
          className="workspace-header-button"
          onClick={handleSend}
         >
          Отправить
         </button>
         <button
          type="button"
          className="workspace-header-button"
          onClick={() => setMessages([])}
         >
          Очистить
         </button>
        </div>
       </div>
      </div>
     </section>

     <section className="workspace-editor">
      <div className="workspace-editor-card">
       <div className="workspace-editor-header">
        <div>
         <div className="workspace-editor-title">Редактор документа</div>
         <div className="workspace-editor-subtitle">
          Подготовьте черновик. Сохраняйте версии по ходу работы.
         </div>
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
        </div>
       </div>

       <div className="workspace-editor-body">
        <DocumentEditor value={documentHtml} onChange={handleDocumentHtmlChange} />
       </div>

       <div className="workspace-editor-footer">
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
         <button
          type="button"
          className="workspace-header-button"
          onClick={() => handleDownloadStub("pdf")}
         >
          Экспорт PDF
         </button>
         <button
          type="button"
          className="workspace-header-button"
          onClick={() => handleDownloadStub("docx")}
         >
          Экспорт DOCX
         </button>
        </div>

        <div style={{ fontSize: "10px", opacity: 0.85, marginTop: "10px" }}>
         Подсказка: в боевом режиме сохраняйте версии, чтобы отслеживать правки.
        </div>
       </div>
      </div>
     </section>
    </div>
   </main>

   <footer className="workspace-footer">
    <div className="workspace-footer-links">
     <a href="#" className="workspace-footer-link">
      Политика конфиденциальности
     </a>
     <a href="#" className="workspace-footer-link">
      Пользовательское соглашение
     </a>
     <a href="#" className="workspace-footer-link">
      Контакты
     </a>
    </div>
    <p style={{ marginTop: "8px" }}>
     © {new Date().getFullYear()} LEGALAI. Все права защищены. Материалы,
     создаваемые с помощью сервиса, не являются официальной юридической
     консультацией. За окончательные решения и действия несёт ответственность
     пользователь.
    </p>
   </footer>
  </div>
 );
};

export default WorkspacePage;

