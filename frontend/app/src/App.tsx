import { useState } from "react";
import "./App.css";

import { LoginPage } from "./pages/login";
import { RegisterPage } from "./pages/register";
import { ForgotPasswordPage } from "./pages/forgot";
import { ResetPasswordPage } from "./pages/reset";
import { WorkspacePage } from "./pages/workspace";
import { ProfilePage } from "./pages/profile";

type Page =
  | "login"
  | "register"
  | "forgot"
  | "reset"
  | "workspace"
  | "profile";

function App() {
  const [page, setPage] = useState<Page>("login");

  return (
    <>
      {/* --- ЛОГИН --- */}
      {page === "login" && (
        <LoginPage
          onGoRegister={() => setPage("register")}
          onGoToForgot={() => setPage("forgot")}
          onSuccessLogin={() => setPage("workspace")}
        />
      )}

      {/* --- РЕГИСТРАЦИЯ --- */}
      {page === "register" && (
        <RegisterPage onGoToLogin={() => setPage("login")} />
      )}

      {/* --- ЗАБЫЛ ПАРОЛЬ --- */}
      {page === "forgot" && (
        <ForgotPasswordPage
          onGoToLogin={() => setPage("login")}
          onGoToReset={() => setPage("reset")}
        />
      )}

      {/* --- НОВЫЙ ПАРОЛЬ --- */}
      {page === "reset" && (
        <ResetPasswordPage onGoToLogin={() => setPage("login")} />
      )}

      {/* --- РАБОЧИЙ КАБИНЕТ --- */}
      {page === "workspace" && (
        <WorkspacePage
          onGoToProfile={() => setPage("profile")}
          onLogout={() => setPage("login")}
        />
      )}

      {/* --- ПРОФИЛЬ --- */}
      {page === "profile" && (
        <ProfilePage
          onGoBack={() => setPage("workspace")}
          onGoToChangePassword={() => setPage("reset")}
        />
      )}
    </>
  );
}

export default App;

