// frontend/src/pages/documents/index.tsx

import React from "react";

export default function DocumentsPage() {
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
      <h1 style={{ fontSize: "28px", marginBottom: "16px" }}>Документы</h1>
      <p style={{ fontSize: "16px", lineHeight: "1.6", maxWidth: "640px" }}>
        Здесь будет отдельная страница «Документы»: список сохранённых проектов
        документов, поиск, фильтры и переход к редактированию в Workspace.
      </p>

      <div
        style={{
          marginTop: "32px",
          padding: "16px",
          borderRadius: "12px",
          border: "1px solid rgba(255,255,255,0.08)",
          background:
            "linear-gradient(135deg, rgba(111, 66, 193, 0.25), rgba(0, 0, 0, 0.4))",
        }}
      >
        <p style={{ margin: 0, opacity: 0.9 }}>
          Пока страница работает как заглушка — главное, что приложение
          корректно собирается и не падает. Функционал подгрузим позже.
        </p>
      </div>
    </div>
  );
}


