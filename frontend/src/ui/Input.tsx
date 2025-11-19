import React from "react";
import { lightTheme, darkTheme } from "./Theme";

export function Input({
  value,
  onChange,
  placeholder,
  theme = "light",
  type = "text"
}) {
  const th = theme === "light" ? lightTheme : darkTheme;

  return (
    <input
      type={type}
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      style={{
        width: "100%",
        padding: "12px 16px",
        borderRadius: "10px",
        border: `1px solid ${th.border}`,
        background: th.surface,
        color: th.text,
        fontSize: "16px",
        outline: "none",
      }}
    />
  );
}
