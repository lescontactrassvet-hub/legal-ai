import React, { useState, FormEvent } from "react";

type RegisterPageProps = {
  onRegisterSuccess: () => void;
  onGoToLogin: () => void;
};

const RegisterPage: React.FC<RegisterPageProps> = ({
  onRegisterSuccess,
  onGoToLogin,
}) => {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [passwordRepeat, setPasswordRepeat] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();

    if (!fullName.trim() || !email.trim() || !password.trim()) {
      setError("Заполните имя, e-mail и пароль.");
      return;
    }

    if (password !== passwordRepeat) {
      setError("Пароли не совпадают.");
      return;
    }

    setError(null);

    // В реальной версии здесь будет запрос к backend и создание пользователя.
    // Сейчас сразу считаем регистрацию успешной и переводим в Workspace.
    onRegisterSuccess();
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

        <h1 className="auth-title">Регистрация</h1>
        <p className="auth-subtitle">
          Создайте аккаунт, чтобы сохранять дела и документы в личном кабинете.
        </p>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-field">
            <label htmlFor="register-name" className="auth-label">
              Как к вам обращаться
            </label>
            <input
              id="register-name"
              type="text"
              className="auth-input"
              placeholder="ФИО или имя"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>

          <div className="auth-field">
            <label htmlFor="register-email" className="auth-label">
              E-mail
            </label>
            <input
              id="register-email"
              type="email"
              className="auth-input"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="auth-field">
            <label htmlFor="register-password" className="auth-label">
              Пароль
            </label>
            <div className="auth-password-wrapper">
              <input
                id="register-password"
                type={showPassword ? "text" : "password"}
                className="auth-input auth-input-password"
                placeholder="Придумайте надёжный пароль"
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

          <div className="auth-field">
            <label htmlFor="register-password-repeat" className="auth-label">
              Повторите пароль
            </label>
            <input
              id="register-password-repeat"
              type={showPassword ? "text" : "password"}
              className="auth-input"
              placeholder="Повторите пароль"
              value={passwordRepeat}
              onChange={(e) => setPasswordRepeat(e.target.value)}
            />
          </div>

          <button type="submit" className="auth-primary-button">
            Зарегистрироваться
          </button>
        </form>

        <div className="auth-footer-text">
          Уже есть аккаунт?{" "}
          <button
            type="button"
            className="auth-link-button"
            onClick={onGoToLogin}
          >
            Войти
          </button>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;

