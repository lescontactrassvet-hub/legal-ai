import { useState } from "react";

import { LandingPage } from "./pages/landing";
import { WorkspacePage } from "./pages/workspace";
import { ProfilePage } from "./pages/profile";
import { DocumentsPage } from "./pages/documents";
import { LoginPage } from "./pages/login";
import { RegisterPage } from "./pages/register";
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

export function App() {
  const [page, setPage] = useState<AppPage>("landing");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // ——— Авторизация ———

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    setPage("workspace");
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setPage("login");
  };

  // ——— Навигация из лендинга ———

  const goToLogin = () => setPage("login");

  // ——— Навигация из шапки Workspace ———

  const handleGoToProfile = () => {
    if (!isAuthenticated) {
      setPage("login");
      return;
    }
    setPage("profile");
  };

  const handleGoToDocuments = () => {
    if (!isAuthenticated) {
      setPage("login");
      return;
    }
    setPage("documents");
  };

  // ——— Навигация из профиля ———

  const handleProfileBack = () => {
    if (!isAuthenticated) {
      setPage("login");
      return;
    }
    setPage("workspace");
  };

  const handleGoToChangePassword = () => {
    setPage("reset");
  };

  // ——— Навигация логин / регистрация / восстановление ———

  const goToRegister = () => setPage("register");
  const goToForgot = () => setPage("forgot");

  // ——— Рендер страниц ———

  switch (page) {
    case "landing":
      return (
        <LandingPage
          onTryFree={goToLogin}
          onLoginClick={goToLogin}
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
          // при необходимости можно добавить onGoBack, пока оставим как самостоятельную страницу
        />
      );

    case "workspace":
    default:
      return (
        <WorkspacePage
          onGoToProfile={handleGoToProfile}
          onLogout={handleLogout}
          // если в WorkspacePage позже появится проп onGoToDocuments,
          // можно будет пробросить handleGoToDocuments
        />
      );
  }
}

