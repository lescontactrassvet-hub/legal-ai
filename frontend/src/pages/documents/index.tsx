// frontend/src/pages/documents/index.tsx
import React, {useEffect, useMemo, useState } from "react";

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
  const apiBaseRaw = (import.meta as any).env?.VITE_API_BASE || "";
  const apiBase = apiBaseRaw.endsWith("/") ? apiBaseRaw.slice(0, -1) : apiBaseRaw;
  const apiUrl = (path: string) => `${apiBase}${path}`;

  const [casesData, setCasesData] = useState<CaseRow[]>([]);
  const [docsData, setDocsData] = useState<DocRow[]>([]);

  useEffect(() => {
    let cancelled = false;

    async function fetchCases() {
      try {
        const r = await fetch(apiUrl("/cases"));
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = (await r.json()) as CaseRow[];
        if (cancelled) return;

        const arr = Array.isArray(data) ? data : [];
        setCasesData(arr);

        if (activeCaseId == null && arr.length > 0) {
          setActiveCaseId(arr[0].id);
        }
      } catch (e) {
        console.error("DocumentsPage: fetch /cases failed", e);
        if (!cancelled) setCasesData([]);
      }
    }

    fetchCases();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function fetchDocs(caseId: number) {
      try {
        const r = await fetch(apiUrl(`/cases/${caseId}/documents`));
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = (await r.json()) as DocRow[];
        if (cancelled) return;

        setDocsData(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error("DocumentsPage: fetch documents failed", e);
        if (!cancelled) setDocsData([]);
      }
    }

    if (activeCaseId == null) {
      setDocsData([]);
      return () => {
        cancelled = true;
      };
    }

    fetchDocs(activeCaseId);
    return () => {
      cancelled = true;
    };
  }, [activeCaseId]);



  const cases = useMemo(() => {
    const q = query.trim().toLowerCase();
    const base = casesData;
    if (!q) return base;
    return base.filter((c) => (c.title || "").toLowerCase().includes(q));
  }, [query, casesData]);

  const activeCase = useMemo(
    () => cases.find((c) => c.id === activeCaseId) || cases[0] || null,
    [cases, activeCaseId]
  );

  const documents = useMemo(() => {
    if (!activeCase) return [];
    return docsData;
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
              В следующем шаге подключим реальные API: /cases и /cases/:id/documents и сделаем “опрокидывание”
              выбранного документа обратно в Workspace.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

