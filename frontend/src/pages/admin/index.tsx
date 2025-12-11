import React, { useState, useEffect } from "react";

type AdminSection =
  | "dashboard"
  | "laws-sources"
  | "laws-logs"
  | "laws-acts"
  | "ai"
  | "users"
  | "subscriptions"
  | "billing"
  | "marketing"
  | "support"
  | "system";

type LawSource = {
  id: number;
  name: string;
  type: string;
  base_url?: string | null;
  is_active: boolean;
  last_status?: string | null;
  last_started_at?: string | null;
  last_finished_at?: string | null;
  last_total_items?: number | null;
};

const sidebarStyle: React.CSSProperties = {
  width: "260px",
  backgroundColor: "#111827",
  color: "#e5e7eb",
  padding: "16px",
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const rootStyle: React.CSSProperties = {
  display: "flex",
  minHeight: "100vh",
  backgroundColor: "#020617",
  color: "#e5e7eb",
  fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
};

const contentStyle: React.CSSProperties = {
  flex: 1,
  padding: "24px",
  overflowY: "auto",
};

const groupTitleStyle: React.CSSProperties = {
  fontSize: "12px",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  color: "#9ca3af",
  marginBottom: "4px",
};

const logoStyle: React.CSSProperties = {
  fontSize: "18px",
  fontWeight: 700,
  marginBottom: "8px",
};

type MenuItemProps = {
  label: string;
  active?: boolean;
  onClick: () => void;
};

function MenuItem({ label, active, onClick }: MenuItemProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        textAlign: "left",
        border: "none",
        outline: "none",
        padding: "6px 10px",
        borderRadius: "6px",
        cursor: "pointer",
        fontSize: "14px",
        backgroundColor: active ? "#1f2937" : "transparent",
        color: active ? "#fff" : "#e5e7eb",
      }}
    >
      {label}
    </button>
  );
}

const AdminPage: React.FC = () => {
  const [section, setSection] = useState<AdminSection>("dashboard");

  const renderSection = () => {
    switch (section) {
      case "dashboard":
        return <DashboardSection />;
      case "laws-sources":
        return <LawSourcesSection />;
      case "laws-logs":
        return <LawUpdateLogSection />;
      case "laws-acts":
        return <LawActsSection />;
      case "ai":
        return <AiSection />;
      case "users":
        return <UsersSection />;
      case "subscriptions":
        return <SubscriptionsSection />;
      case "billing":
        return <BillingSection />;
      case "marketing":
        return <MarketingSection />;
      case "support":
        return <SupportSection />;
      case "system":
        return <SystemSection />;
      default:
        return <div>Раздел не найден.</div>;
    }
  };

  return (
    <div style={rootStyle}>
      {/* ЛЕВАЯ ПАНЕЛЬ */}
      <aside style={sidebarStyle}>
        <div>
          <div style={logoStyle}>LEGALAI · Admin</div>
          <div style={{ fontSize: "12px", color: "#9ca3af" }}>
            Панель управления проектом
          </div>
        </div>

        {/* ОБЗОР */}
        <div>
          <div style={groupTitleStyle}>Обзор</div>
          <MenuItem
            label="Dashboard"
            active={section === "dashboard"}
            onClick={() => setSection("dashboard")}
          />
        </div>

        {/* ЗАКОНЫ */}
        <div>
          <div style={groupTitleStyle}>Законы</div>
          <MenuItem
            label="Источники законов"
            active={section === "laws-sources"}
            onClick={() => setSection("laws-sources")}
          />
          <MenuItem
            label="Логи обновлений"
            active={section === "laws-logs"}
            onClick={() => setSection("laws-logs")}
          />
          <MenuItem
            label="Акты и документы"
            active={section === "laws-acts"}
            onClick={() => setSection("laws-acts")}
          />
        </div>

        {/* ИИ */}
        <div>
          <div style={groupTitleStyle}>ИИ</div>
          <MenuItem
            label="Татьяна и ответы"
            active={section === "ai"}
            onClick={() => setSection("ai")}
          />
        </div>

        {/* ПОЛЬЗОВАТЕЛИ */}
        <div>
          <div style={groupTitleStyle}>Пользователи</div>
          <MenuItem
            label="Список пользователей"
            active={section === "users"}
            onClick={() => setSection("users")}
          />
          <MenuItem
            label="Подписки и тарифы"
            active={section === "subscriptions"}
            onClick={() => setSection("subscriptions")}
          />
        </div>

        {/* ПЛАТЕЖИ */}
        <div>
          <div style={groupTitleStyle}>Платежи</div>
          <MenuItem
            label="Касса и платежи"
            active={section === "billing"}
            onClick={() => setSection("billing")}
          />
        </div>

        {/* МАРКЕТИНГ */}
        <div>
          <div style={groupTitleStyle}>Маркетинг</div>
          <MenuItem
            label="Акции и реклама"
            active={section === "marketing"}
            onClick={() => setSection("marketing")}
          />
        </div>

        {/* ПОДДЕРЖКА */}
        <div>
          <div style={groupTitleStyle}>Поддержка</div>
          <MenuItem
            label="Тикеты и диалоги"
            active={section === "support"}
            onClick={() => setSection("support")}
          />
        </div>

        {/* СИСТЕМА */}
        <div>
          <div style={groupTitleStyle}>Система</div>
          <MenuItem
            label="Настройки системы"
            active={section === "system"}
            onClick={() => setSection("system")}
          />
        </div>
      </aside>

      {/* ПРАВАЯ ОБЛАСТЬ */}
      <main style={contentStyle}>{renderSection()}</main>
    </div>
  );
};

/* ---------- ЗАГЛУШКИ / ЛЭЙАУТ РАЗДЕЛОВ ---------- */

function SectionLayout(props: { title: string; description: string }) {
  return (
    <div>
      <h1 style={{ fontSize: "24px", marginBottom: "8px" }}>{props.title}</h1>
      <p style={{ marginBottom: "24px", color: "#9ca3af" }}>
        {props.description}
      </p>
      <div
        style={{
          padding: "16px",
          borderRadius: "8px",
          border: "1px solid #1f2937",
          backgroundColor: "#020617",
        }}
      >
        <p style={{ color: "#6b7280", fontSize: "14px" }}>
          Здесь появится функционал этого раздела. Пока это заготовка, куда мы
          будем постепенно добавлять таблицы, формы и действия.
        </p>
      </div>
    </div>
  );
}

function DashboardSection() {
  return (
    <SectionLayout
      title="Dashboard"
      description="Краткий обзор состояния системы: количество законов, источников, статус обновлений, состояние ИИ и базы данных."
    />
  );
}

/* ---------- ИСТОЧНИКИ ЗАКОНОВ С РЕАЛЬНЫМИ ДАННЫМИ ---------- */

function LawSourcesSection() {
  const [sources, setSources] = useState<LawSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSources = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(
        (import.meta.env.VITE_API_BASE || "") + "/admin/laws/sources"
      );
      if (!resp.ok) {
        throw new Error("HTTP " + resp.status);
      }
      const data = await resp.json();
      setSources(data);
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Ошибка загрузки источников");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSources();
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: "24px", marginBottom: "8px" }}>
        Источники законов
      </h1>
      <p style={{ marginBottom: "16px", color: "#9ca3af" }}>
        Реальные данные из law_sources с последним статусом обновления.
      </p>

      <div style={{ marginBottom: "12px" }}>
        <button
          type="button"
          onClick={loadSources}
          style={{
            padding: "6px 12px",
            borderRadius: "6px",
            border: "1px solid #4b5563",
            backgroundColor: "#111827",
            color: "#e5e7eb",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          Обновить список
        </button>
      </div>

      {loading && (
        <p style={{ color: "#9ca3af", fontSize: "14px" }}>Загрузка...</p>
      )}

      {error && (
        <p style={{ color: "#f87171", fontSize: "14px" }}>Ошибка: {error}</p>
      )}

      {!loading && !error && (
        <div
          style={{
            borderRadius: "8px",
            border: "1px solid #1f2937",
            overflowX: "auto",
          }}
        >
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: "14px",
            }}
          >
            <thead style={{ backgroundColor: "#020617" }}>
              <tr>
                <th style={{ padding: "8px", textAlign: "left" }}>ID</th>
                <th style={{ padding: "8px", textAlign: "left" }}>Название</th>
                <th style={{ padding: "8px", textAlign: "left" }}>Тип</th>
                <th style={{ padding: "8px", textAlign: "left" }}>URL</th>
                <th style={{ padding: "8px", textAlign: "left" }}>Активен</th>
                <th style={{ padding: "8px", textAlign: "left" }}>
                  Последний статус
                </th>
              </tr>
            </thead>
            <tbody>
              {sources.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    style={{
                      padding: "12px",
                      textAlign: "center",
                      color: "#6b7280",
                    }}
                  >
                    Источники пока не найдены.
                  </td>
                </tr>
              ) : (
                sources.map((s) => (
                  <tr key={s.id} style={{ borderTop: "1px solid #111827" }}>
                    <td style={{ padding: "8px" }}>{s.id}</td>
                    <td style={{ padding: "8px" }}>{s.name}</td>
                    <td style={{ padding: "8px" }}>{s.type}</td>
                    <td style={{ padding: "8px" }}>
                      {s.base_url || (
                        <span style={{ color: "#6b7280" }}>—</span>
                      )}
                    </td>
                    <td style={{ padding: "8px" }}>
                      {s.is_active ? "Да" : "Нет"}
                    </td>
                    <td style={{ padding: "8px" }}>
                      {s.last_status || (
                        <span style={{ color: "#6b7280" }}>—</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ---------- ОСТАЛЬНЫЕ РАЗДЕЛЫ ПОКА КАК ЗАГЛУШКИ ---------- */

function LawUpdateLogSection() {
  return (
    <SectionLayout
      title="Логи обновлений законов"
      description="История обновлений правовой базы: даты запусков, источники, статус (успех/ошибка), статистика обработки документов."
    />
  );
}

function LawActsSection() {
  return (
    <SectionLayout
      title="Акты и документы"
      description="Просмотр и поиск загруженных нормативных актов, их версий и связанных документов."
    />
  );
}

function AiSection() {
  return (
    <SectionLayout
      title="ИИ и ответы (Татьяна)"
      description="Статус подключения ИИ, профиль Татьяны и тестовый стенд для проверки ответов на вопросы."
    />
  );
}

function UsersSection() {
  return (
    <SectionLayout
      title="Пользователи"
      description="Список пользователей, их статусы и базовое управление доступом."
    />
  );
}

function SubscriptionsSection() {
  return (
    <SectionLayout
      title="Подписки и тарифы"
      description="Настройка тарифных планов и управление подписками пользователей."
    />
  );
}

function BillingSection() {
  return (
    <SectionLayout
      title="Касса и платежи"
      description="Интеграция с платёжной системой, просмотр и диагностика платёжных операций."
    />
  );
}

function MarketingSection() {
  return (
    <SectionLayout
      title="Маркетинг, акции и реклама"
      description="Управление промо-акциями, промокодами и рекламными блоками на страницах сервиса."
    />
  );
}

function SupportSection() {
  return (
    <SectionLayout
      title="Поддержка и диалоги"
      description="Обработка запросов пользователей, тикеты и просмотр диалогов с ботом."
    />
  );
}

function SystemSection() {
  return (
    <SectionLayout
      title="Настройки системы"
      description="Технические настройки проекта, информация о версии, базе данных и сервисах."
    />
  );
}

export default AdminPage;
