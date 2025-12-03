import React, { useState } from "react";

type LoginPageProps = {
  onGoRegister: () => void;
  onGoToForgot: () => void;
  onSuccessLogin: () => void;
};

export function LoginPage({ onGoRegister, onGoToForgot, onSuccessLogin }: LoginPageProps) {
  const [passwordVisible, setPasswordVisible] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Позже здесь появится реальный запрос к backend /auth/login
    onSuccessLogin(); // <<< ДОБАВИЛ ВЫЗОВ
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Вход в аккаунт</h1>
        <p className="auth-subtitle">Добро пожаловать в LegalAI</p>

        <form className="auth-form" onSubmit={handleSubmit}>

          {/* Email */}
          <div className="auth-field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className="auth-input"
              placeholder="Введите email"
              required
            />
          </div>

          {/* Пароль + Показать */}
          <div className="auth-field">
            <div className="auth-label-row">
              <label htmlFor="password">Пароль</label>
              <button
                type="button"
                className="password-toggle"
                onClick={() => setPasswordVisible((v) => !v)}
              >
                {passwordVisible ? "Скрыть" : "Показать"}
              </button>
            </div>

            <input
              id="password"
              type={passwordVisible ? "text" : "password"}
              className="auth-input"
              placeholder="Введите пароль"
              required
            />
          </div>

          {/* Запомнить меня */}
          <div className="auth-row-between">
            <label className="auth-remember">
              <input type="checkbox" className="auth-checkbox" />
              <span>Запомнить меня</span>
            </label>
          </div>

          {/* Забыли пароль */}
          <div className="auth-forgot">
            <button type="button" className="auth-link-button" onClick={onGoToForgot}>
              Забыли пароль?
            </button>
          </div>

          {/* Кнопка Войти */}
          <button type="submit" className="auth-primary-button">
            Войти
          </button>
        </form>

        {/* Низ: ссылка на регистрацию */}
        <p className="auth-footer-text">
          Нет аккаунта?{" "}
          <button
            type="button"
            className="auth-link-button"
            onClick={onGoRegister}
          >
            Зарегистрироваться
          </button>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;

