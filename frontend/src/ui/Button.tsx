import React from "react";
import { lightTheme, darkTheme } from "./Theme";

interface Props {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  variant?: "primary" | "secondary";
  theme?: "light" | "dark";
}

export function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  theme = "light"
}: Props) {
  const th = theme === "light" ? lightTheme : darkTheme;

  const styles: React.CSSProperties = {
    background:
      variant === "primary" ? th.primary : th.surface,
    color: variant === "primary" ? "#FFF" : th.text,
    padding: "12px 20px",
    borderRadius: "10px",
    border: "none",
    fontSize: "16px",
    fontWeight: 600,
    cursor: "pointer",
    boxShadow: "0 4px 12px rgba(0,0,0,0.10)",
    transition: "0.2s",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      style={styles}
    >
      {children}
    </button>
  );
}
