import React from "react";
import { lightTheme, darkTheme } from "./Theme";

export function Container({ children, theme = "light" }) {
  const th = theme === "light" ? lightTheme : darkTheme;

  return (
    <div
      style={{
        background: th.background,
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "20px",
      }}
    >
      {children}
    </div>
  );
}
