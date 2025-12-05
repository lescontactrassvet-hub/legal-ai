// frontend/src/pages/workspace/index.tsx

import React from "react";

type WorkspacePageProps = {
  onGoToProfile: () => void;
  onLogout: () => void;
  onGoToDocuments?: () => void;
};

export default function WorkspacePage({
  onGoToProfile,
  onLogout,
  onGoToDocuments,
}: WorkspacePageProps) {
  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#050812",
        color: "#ffffff",
        padding: "24px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "24px",
        }}
      >
        <div style={{ fontSize: "22px", fontWeight: 600 }}>LEGALAI — Workspace</div>

        <div style={{ display: "flex", gap: "12px" }}>
          <button onClick={onGoToProfile}>Профиль</button>
          {onGoToDocuments && (
            <button onClick={onGoToDocuments}>Документы</button>
          )}
          <button onClick={onLogout}>Выйти</button>
        </div>
      </header>

      <main>
        <h1 style={{ fontSize: "26px", marginBottom: "12px" }}>
          Рабочее пространство
        </h1>
        <p style={{ maxWidth: "640px", lineHeight: 1.6 }}>
          Здесь будет чат с ИИ «Татьяна» и редактор юридических документов.
          Сейчас страница работает как упрощённая заглушка, чтобы всё
          приложение собиралось без ошибок.
        </p>
      </main>
    </div>
  );
}


