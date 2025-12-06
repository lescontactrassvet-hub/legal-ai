import { useState } from "react";
import "./App.css";

import LandingPage from "./pages/landing";
import WorkspacePage from "./pages/workspace";
import ProfilePage from "./pages/profile";
import DocumentsPage from "./pages/documents";

import LoginPage from "./pages/login";
import RegisterPage from "./pages/register";
import ResetPage from "./pages/reset";
import ForgotPage from "./pages/forgot";

type AppPage =
  | "landing"
  | "login"
  | "register"
  | "workspace"
  | "documents"
  | "profile"
  | "reset"
  | "forgot";

export default function App() {
  const [page, setPage] = useState<AppPage>("landing");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // ---- Авторизация ----
  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    setPage("workspace");
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setPage("login");
  };

  // ---- Навигация из лендинга ----
  const goToLogin = () => setPage("login");

  // ---- Навигация из Workspace (шапка) ----
  const handleGoToProfile = () => {
    if (!isAuthenticated) return setPage("login");
    setPage("profile");
  };

  const handleGoToDocuments = () => {
    if (!isAuthenticated) return setPage("login");
    setPage("documents");
  };

  // ---- Навигация из профиля ----
  const handleProfileBack = () => {
    setPage(isAuthenticated ? "workspace" : "login");
  };

  // ---- Навигация логин → регистрация/восстановление ----
  const goToRegister = () => setPage("register");
  const goToForgot = () => setPage("forgot");

  const handleGoToChangePassword = () => setPage("reset");

  // ---- Рендер страниц ----
  switch (page) {
    case "landing":
      return (
        <LandingPage
          onGoToLogin={goToLogin}
          onGoToRegister={goToRegister}
        />
      );
    case "login":
      return (
        <LoginPage
          onLoginSuccess={handleLoginSuccess}
          onGoToRegister={goToRegister}
          onGoToForgot={goToForgot}
        />
      );

    case "register":
      return (
        <RegisterPage
          onRegisterSuccess={handleLoginSuccess}
          onGoToLogin={goToLogin}
        />
      );

    case "forgot":
      return <ForgotPage onBackToLogin={goToLogin} />;

    case "reset":
      return <ResetPage onBackToLogin={goToLogin} />;

    case "profile":
      return (
        <ProfilePage
          onGoBack={handleProfileBack}
          onGoToChangePassword={handleGoToChangePassword}
        />
      );

    case "documents":
      return (
        <DocumentsPage
          // позже добавим onGoBack
        />
      );

    case "workspace":
    default:
      return (
        <WorkspacePage
          onGoToProfile={handleGoToProfile}
          onLogout={handleLogout}
          onGoToDocuments={handleGoToDocuments}
        />
      );
  }
}

