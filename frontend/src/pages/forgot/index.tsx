import React, { useState } from "react";

type ForgotPasswordPageProps = {
  onGoToLogin: () => void;
  onGoToReset: () => void;
};

export function ForgotPasswordPage({
  onGoToLogin,
  onGoToReset,
}: ForgotPasswordPageProps) {
  const [email, setEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // позже подключим запрос к backend /auth/forgot
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Восстановление пароля</h1>
        <p className="auth-subtitle">
          Введите ваш Email. Мы отправим ссылку для восстановления пароля.
        </p>

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
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {/* Кнопка отправки */}
          <button type="submit" className="auth-primary-button">
            Отправить ссылку
          </button>
        </form>

        {/* Низ: вернуться к входу */}
        <p className="auth-footer-text">
          Вспомнили пароль?{" "}
          <button
            type="button"
            className="auth-link-button"
            onClick={onGoToLogin}
          >
            Войти
          </button>
        </p>

        {/* Низ: переход к смене пароля */}
        <p className="auth-footer-text">
          Уже есть код для восстановления?{" "}
          <button
            type="button"
            className="auth-link-button"
            onClick={onGoToReset}
          >
            Сменить пароль
          </button>
        </p>
      </div>
    </div>
  );
}

export default ForgotPasswordPage;

