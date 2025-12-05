import React, { useState } from "react";

function PageStub({ name }: { name: string }) {
  return (
    <div
      style={{
        backgroundColor: "#050812",
        minHeight: "100vh",
        color: "#ffffff",
        padding: "20px",
        fontSize: "26px",
        textAlign: "center",
      }}
    >
      Страница: {name}
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState<"landing" | "login" | "workspace">("landing");

  if (page === "landing") return <PageStub name="Landing" />;
  if (page === "login") return <PageStub name="Login" />;
  if (page === "workspace") return <PageStub name="Workspace" />;

  return null;
}

