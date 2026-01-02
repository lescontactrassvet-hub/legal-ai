import React, { useState } from "react";

type LoginPageProps = {
  onLoginSuccess: () => void;
  onGoToRegister: () => void;
  onGoToForgot: () => void;
};

export default function LoginPage({
  onLoginSuccess,
  onGoToRegister,
  onGoToForgot,
}: LoginPageProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();

    if (!trimmedEmail || !trimmedPassword) {
      // В демо-версии просто alert, позже заменим на нормальные ошибки
      alert("Пожалуйста, введите логин и пароль.");
      return;
    }

    setIsSubmitting(true);

    // Реальный логин: POST /auth/login
    const storage = rememberMe ? localStorage : sessionStorage;
    fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: trimmedEmail, password: trimmedPassword }).toString(),
    })
      .then(async (res) => {

        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          const msg = (data && (data.detail || data.error || data.message)) || `HTTP ${res.status}`;
          throw new Error(msg);
        }
        const token = data.access_token || data.token;
        if (!token) throw new Error("Не получен access_token");
        storage.setItem("access_token", token);
        return token;
      })
      .then(() => {
        setIsSubmitting(false);
        onLoginSuccess();
      })
      .catch((e) => {
        setIsSubmitting(false);
        alert(e?.message || "Ошибка входа");
      });
  };

  const handleTogglePassword = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Вход в LEGALAI</h1>
        <p className="auth-subtitle">Юридический ИИ-ассистент «Татьяна»</p>

        <form onSubmit={handleSubmit} className="auth-form">
          {/* E-mail / Логин */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="login-email">
              E-mail
            </label>
            <input
              id="login-email"
              type="text"
              className="auth-input"
              placeholder="example@domain.ru"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>

          {/* Пароль + кнопка «Показать» */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="login-password">
              Пароль
            </label>
            <div className="auth-password-wrapper">
              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                className="auth-input"
                placeholder="Введите пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={handleTogglePassword}
              >
                {showPassword ? "Скрыть" : "Показать"}
              </button>
            </div>
          </div>

          {/* Запомнить меня / Забыли пароль? */}
          <div className="auth-row-between">
            <label className="auth-checkbox">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <span>Запомнить меня</span>
            </label>

            <button
              type="button"
              className="auth-forgot"
              onClick={onGoToForgot}
            >
              Забыли пароль?
            </button>
          </div>

          {/* Кнопка Войти */}
          <button
            type="submit"
            className="auth-primary-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Входим..." : "Войти"}
          </button>
        </form>

        {/* Низ карточки — регистрация */}
        <p className="auth-footer-text">
          Нет аккаунта?{" "}
          <button
            type="button"
            className="auth-link-button"
            onClick={onGoToRegister}
          >
            Зарегистрироваться
          </button>
        </p>

        {/* Рекламный блок для сторонних источников */}
        <div
          className="auth-footer-text"
          style={{ marginTop: "16px", fontSize: "12px", opacity: 0.85 }}
        >
          <div style={{ marginBottom: "4px" }}>
            Рекламный блок сторонних сервисов:
          </div>
          <ul style={{ listStyle: "disc", paddingLeft: "18px", margin: 0 }}>
            <li>
              Здесь будет размещаться информация о партнёрских сервисах
              LEGALAI.
            </li>
            <li>
              Позже сюда можно добавить ссылки на сторонние источники и их
              логотипы.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

