import React, { useState, FormEvent } from "react";

type LoginPageProps = {
  onLoginSuccess: () => void;
  onGoToRegister: () => void;
  onGoToForgot: () => void;
};

const LoginPage: React.FC<LoginPageProps> = ({
  onLoginSuccess,
  onGoToRegister,
  onGoToForgot,
}) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();

    // Простая демо-проверка: оба поля должны быть не пустыми.
    if (!email.trim() || !password.trim()) {
      setError("Пожалуйста, заполните e-mail и пароль.");
      return;
    }

    setError(null);

    // В реальной версии здесь будет запрос к backend.
    // Сейчас сразу считаем вход успешным и переводим в Workspace.
    onLoginSuccess();
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo-block">
          <img src="/logo.png" alt="LEGALAI" className="auth-logo" />
          <div className="auth-logo-text">
            <div className="auth-logo-title">LEGALAI</div>
            <div className="auth-logo-subtitle">
              Юридический ИИ — «Татьяна»
            </div>
          </div>
        </div>

        <h1 className="auth-title">Вход в личный кабинет</h1>
        <p className="auth-subtitle">
          Введите e-mail и пароль, чтобы продолжить работу с делами и
          документами.
        </p>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-field">
            <label htmlFor="login-email" className="auth-label">
              E-mail
            </label>
            <input
              id="login-email"
              type="email"
              className="auth-input"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="auth-field">
            <label htmlFor="login-password" className="auth-label">
              Пароль
            </label>
            <div className="auth-password-wrapper">
              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                className="auth-input auth-input-password"
                placeholder="Ваш пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((prev) => !prev)}
              >
                {showPassword ? "Скрыть" : "Показать"}
              </button>
            </div>
          </div>

          <div className="auth-row-between">
            <label className="auth-remember">
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

          <button type="submit" className="auth-primary-button">
            Войти
          </button>
        </form>

        <div className="auth-footer-text">
          Нет аккаунта?{" "}
          <button
            type="button"
            className="auth-link-button"
            onClick={onGoToRegister}
          >
            Зарегистрироваться
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

