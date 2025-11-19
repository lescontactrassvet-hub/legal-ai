import React from "react";
import { lightTheme, darkTheme } from "./Theme";

export function Card({ children, theme = "light" }) {
  const th = theme === "light" ? lightTheme : darkTheme;

  return (
    <div
      style={{
        background: th.surface,
        borderRadius: "16px",
        padding: "24px",
        boxShadow: "0 6px 18px rgba(0,0,0,0.12)",
      }}
    >
      {children}
    </div>
  );
}
