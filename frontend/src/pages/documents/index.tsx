cat > frontend/src/pages/documents/index.tsx <<'EOF'
// frontend/src/pages/documents/index.tsx
import React, { useMemo, useState } from "react";

type DocumentsPageProps = {
  onGoBack: () => void;
};

type CaseRow = {
  id: number;
  title: string;
  description?: string | null;
  created_at?: string | null;
};

type DocRow = {
  id: number;
  case_id: number;
  title: string;
  updated_at?: string | null;
  created_at?: string | null;
  status?: string | null; // под ТЗ
};

export default function DocumentsPage({ onGoBack }: DocumentsPageProps) {
  // Пока это “каркас”: UI готов, API подключим следующим шагом.
  const [query, setQuery] = useState<string>("");
  const [activeCaseId, setActiveCaseId] = useState<number | null>(null);

  // заглушечные данные (чтобы страница была НЕ пустая). На следующем шаге заменим на fetch.
  const mockCases: CaseRow[] = [
    { id: 1, title: "Пример дела", description: "После подключения API здесь будут реальные дела." },
  ];
  const mockDocs: DocRow[] = [
    {
      id: 101,
      case_id: 1,
      title: "Пример документа",
      status: "Черновик",
      updated_at: "",
      created_at: "",
    },
  ];

  const cases = useMemo(() => {
    const q = query.trim().toLowerCase();
    const base = mockCases;
    if (!q) return base;
    return base.filter((c) => (c.title || "").toLowerCase().includes(q));
  }, [query]);

  const activeCase = useMemo(
    () => cases.find((c) => c.id === activeCaseId) || cases[0] || null,
    [cases, activeCaseId]
  );

  const documents = useMemo(() => {
    if (!activeCase) return [];
    return mockDocs.filter((d) => d.case_id === activeCase.id);
  }, [activeCase]);

  return (
    <div
      className="workspace-root"
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left, rgba(96, 165, 250, 0.4), transparent 55%), radial-gradient(circle at bottom right, rgba(129, 140, 248, 0.5), transparent 60%), linear-gradient(to bottom, #020617, #02091f)",
        paddingBottom: "24px",
      }}
    >
      {/* Шапка как у Workspace */}
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
              <div className="workspace-logo-subtitle" style={{ fontSize: "10px", opacity: 0.9 }}>
                Юридический ии — «Татьяна»
              </div>
            </div>
          </div>

          <nav
            className="workspace-nav"
            style={{
              marginLeft: "auto",
              display: "flex",
              gap: "8px",
              alignItems: "center",
            }}
          >
            <button
              type="button"
              className="workspace-nav-button"
              onClick={onGoBack}
              style={{
                borderRadius: 999,
                padding: "6px 16px",
                background: "linear-gradient(90deg, #1f2937, #111827)",
                color: "#e5e7eb",
                border: "none",
                fontSize: "11px",
                cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              ← Назад в Workspace
            </button>

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
                cursor: "default",
                whiteSpace: "nowrap",
              }}
            >
              Документы
            </button>
          </nav>
        </div>
      </header>

      {/* Тело как у Workspace: две колонки внутри */}
      <main className="workspace-main">
        <div className="workspace-main-right" style={{ width: "100%" }}>
          <div style={{ width: "100%", maxWidth: 1200, margin: "0 auto" }}>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
              {/* Левая панель: дела */}
              <aside className="workspace-side-panel" style={{ flex: 1, minWidth: 320 }}>
                <div className="workspace-side-panel-header" style={{ marginBottom: 12 }}>
                  <div className="workspace-section-title">Мои дела</div>
                  <div className="workspace-side-panel-toggle" style={{ cursor: "default" }}>
                    Список дел
                  </div>
                </div>

                <input
                  className="auth-input"
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Поиск по делам..."
                  style={{ marginBottom: 12 }}
                />

                {cases.length === 0 ? (
                  <div className="workspace-placeholder">Дел пока нет.</div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {cases.map((c) => {
                      const active = (activeCase?.id ?? null) === c.id;
                      return (
                        <button
                          key={c.id}
                          type="button"
                          onClick={() => setActiveCaseId(c.id)}
                          style={{
                            textAlign: "left",
                            padding: "10px 12px",
                            borderRadius: 12,
                            border: "1px solid rgba(255,255,255,0.10)",
                            background: active ? "rgba(111, 66, 193, 0.28)" : "rgba(255,255,255,0.05)",
                            color: "#fff",
                            cursor: "pointer",
                          }}
                        >
                          <div style={{ fontWeight: 700, fontSize: 14 }}>{c.title}</div>
                          {c.description && (
                            <div style={{ opacity: 0.8, fontSize: 12, marginTop: 4 }}>{c.description}</div>
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}
              </aside>

              {/* Правая панель: документы */}
              <section className="workspace-side-panel" style={{ flex: 2, minWidth: 420 }}>
                <div className="workspace-side-panel-header" style={{ marginBottom: 12 }}>
                  <div className="workspace-section-title">Документы</div>
                  <div className="workspace-side-panel-toggle" style={{ cursor: "default" }}>
                    {activeCase ? `Дело: ${activeCase.title}` : "Выберите дело"}
                  </div>
                </div>

                {activeCase ? (
                  <>
                    {documents.length === 0 ? (
                      <div className="workspace-placeholder">Документов пока нет. Создайте документ в Workspace.</div>
                    ) : (
                      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                        {documents.map((d) => (
                          <div
                            key={d.id}
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: 12,
                              padding: "10px 12px",
                              borderRadius: 12,
                              border: "1px solid rgba(255,255,255,0.10)",
                              background: "rgba(0,0,0,0.22)",
                            }}
                          >
                            <div style={{ flex: 1 }}>
                              <div style={{ fontWeight: 700, fontSize: 14 }}>{d.title}</div>
                              <div style={{ opacity: 0.8, fontSize: 12, marginTop: 4 }}>
                                Статус: {d.status || "—"}
                              </div>
                            </div>

                            <button
                              type="button"
                              className="auth-primary-button"
                              style={{ width: "auto", padding: "10px 14px", fontSize: 12 }}
                              // Следующий шаг: реально “опрокидывать” в Workspace.
                              onClick={() => alert("Следующий шаг: открыть этот документ в Workspace")}
                            >
                              Открыть в Workspace
                            </button>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Блок под ТЗ Татьяны: экспорт/вложения */}
                    <div style={{ marginTop: 14 }}>
                      <div className="workspace-section-title" style={{ fontSize: 16, marginBottom: 10 }}>
                        Экспорт и вложения (по ТЗ)
                      </div>
                      <div className="workspace-placeholder">
                        Здесь будет: экспорт DOCX/PDF, ZIP с вложениями, список приложений (чеки, доказательства),
                        статусы “Готово/Черновик”, и управление версиями.
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="workspace-placeholder">Сначала выберите дело слева.</div>
                )}
              </section>
            </div>

            <p className="workspace-chat-tip" style={{ marginTop: 12 }}>
              В следующем шаге подключим реальные API: /cases и /cases/{id}/documents и сделаем “опрокидывание”
              выбранного документа обратно в Workspace.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
EOF

