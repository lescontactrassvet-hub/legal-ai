import React, { useState } from "react";

type ResetPasswordPageProps = {
  onGoToLogin: () => void;
};

export function ResetPasswordPage({ onGoToLogin }: ResetPasswordPageProps) {
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [password, setPassword] = useState("");
  const [passwordRepeat, setPasswordRepeat] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // позже подключим реальный запрос к backend /auth/reset-password
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Новый пароль</h1>
        <p className="auth-subtitle">
          Придумайте новый пароль для вашего аккаунта и повторите его.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          {/* Новый пароль */}
          <div className="auth-field">
            <div className="auth-label-row">
              <label htmlFor="password">Новый пароль</label>
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
              placeholder="Введите новый пароль"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {/* Повтор пароля */}
          <div className="auth-field">
            <label htmlFor="passwordRepeat">Повторите пароль</label>
            <input
              id="passwordRepeat"
              type={passwordVisible ? "text" : "password"}
              className="auth-input"
              placeholder="Введите пароль ещё раз"
              required
              value={passwordRepeat}
              onChange={(e) => setPasswordRepeat(e.target.value)}
            />
          </div>

          {/* Кнопка сохранить */}
          <button type="submit" className="auth-primary-button">
            Сохранить пароль
          </button>
        </form>

        {/* Низ: вернуться ко входу */}
        <p className="auth-footer-text">
          Вернуться на страницу{" "}
          <button
            type="button"
            className="auth-link-button"
            onClick={onGoToLogin}
          >
            входа
          </button>
        </p>
      </div>
    </div>
  );
}

export default ResetPasswordPage;

