import React, { useState } from "react";

type RegisterPageProps = {
  onRegisterSuccess: () => void;
  onGoToLogin: () => void;
};

export default function RegisterPage({
  onRegisterSuccess,
  onGoToLogin,
}: RegisterPageProps) {
  const [lastName, setLastName] = useState("");
  const [firstName, setFirstName] = useState("");
  const [middleName, setMiddleName] = useState("");
  const [birthYear, setBirthYear] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [phoneConfirm, setPhoneConfirm] = useState("");
  const [country, setCountry] = useState("");
  const [city, setCity] = useState("");
  const [activity, setActivity] = useState("");
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedLastName = lastName.trim();
    const trimmedFirstName = firstName.trim();
    const trimmedBirthYear = birthYear.trim();
    const trimmedEmail = email.trim();
    const trimmedPhone = phone.trim();
    const trimmedPhoneConfirm = phoneConfirm.trim();
    const trimmedCountry = country.trim();
    const trimmedCity = city.trim();
    const trimmedActivity = activity.trim();
    const trimmedLogin = login.trim();
    const trimmedPassword = password.trim();

    if (
      !trimmedLastName ||
      !trimmedFirstName ||
      !trimmedBirthYear ||
      !trimmedEmail ||
      !trimmedPhone ||
      !trimmedPhoneConfirm ||
      !trimmedCountry ||
      !trimmedCity ||
      !trimmedActivity ||
      !trimmedLogin ||
      !trimmedPassword
    ) {
      alert("Пожалуйста, заполните все обязательные поля со звёздочкой.");
      return;
    }

    if (trimmedPhone !== trimmedPhoneConfirm) {
      alert("Номер телефона и его подтверждение не совпадают.");
      return;
    }

    if (!/^\d{4}$/.test(trimmedBirthYear)) {
      alert("Укажите год рождения в формате 4 цифр, например: 1975.");
      return;
    }

    if (trimmedLogin.length < 3 || trimmedLogin.length > 30) {
      alert("Логин должен содержать от 3 до 30 символов.");
      return;
    }

    if (!/^[A-Za-z][A-Za-z0-9._]*$/.test(trimmedLogin)) {
      alert(
        "Логин должен начинаться с латинской буквы и может содержать латинские буквы, цифры, точку и подчёркивание."
      );
      return;
    }

    if (trimmedPassword.length < 8) {
      alert("Пароль должен содержать минимум 8 символов.");
      return;
    }

    if (!acceptTerms) {
      alert(
        "Чтобы продолжить, необходимо подтвердить согласие с условиями сервиса и обработкой персональных данных."
      );
      return;
    }

    setIsSubmitting(true);

    // Демо-логика регистрации.
    // Здесь позже появится реальный запрос к backend.
    setTimeout(() => {
      setIsSubmitting(false);
      onRegisterSuccess();
    }, 700);
  };

  const handleTogglePassword = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Регистрация</h1>
        <p className="auth-subtitle">
          Заполните данные, чтобы создать аккаунт в LegalAI.
          <br />
          Поля со звёздочкой обязательны.
        </p>

        <form onSubmit={handleSubmit} className="auth-form">
          {/* Фамилия */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-last-name">
              Фамилия *
            </label>
            <input
              id="reg-last-name"
              type="text"
              className="auth-input"
              placeholder="Введите фамилию"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
            />
          </div>

          {/* Имя */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-first-name">
              Имя *
            </label>
            <input
              id="reg-first-name"
              type="text"
              className="auth-input"
              placeholder="Введите имя"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
            />
          </div>

          {/* Отчество */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-middle-name">
              Отчество (при наличии)
            </label>
            <input
              id="reg-middle-name"
              type="text"
              className="auth-input"
              placeholder="Введите отчество (если есть)"
              value={middleName}
              onChange={(e) => setMiddleName(e.target.value)}
            />
          </div>

          {/* Год рождения */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-birth-year">
              Год рождения *
            </label>
            <input
              id="reg-birth-year"
              type="text"
              className="auth-input"
              placeholder="Например: 1975"
              value={birthYear}
              onChange={(e) => setBirthYear(e.target.value)}
            />
          </div>

          {/* Email */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-email">
              Email *
            </label>
            <input
              id="reg-email"
              type="email"
              className="auth-input"
              placeholder="Ваш email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>

          {/* Телефон */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-phone">
              Телефон *
            </label>
            <input
              id="reg-phone"
              type="tel"
              className="auth-input"
              placeholder="+7 900 000 00 00"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </div>

          {/* Подтверждение телефона */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-phone-confirm">
              Подтвердите телефон *
            </label>
            <input
              id="reg-phone-confirm"
              type="tel"
              className="auth-input"
              placeholder="Повторите телефон"
              value={phoneConfirm}
              onChange={(e) => setPhoneConfirm(e.target.value)}
            />
          </div>

          {/* Страна */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-country">
              Страна *
            </label>
            <input
              id="reg-country"
              type="text"
              className="auth-input"
              placeholder="Страна"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
            />
          </div>

          {/* Город / район */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-city">
              Город / район *
            </label>
            <input
              id="reg-city"
              type="text"
              className="auth-input"
              placeholder="Город или район"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </div>

          {/* Род деятельности */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-activity">
              Род деятельности *
            </label>
            <select
              id="reg-activity"
              className="auth-input"
              value={activity}
              onChange={(e) => setActivity(e.target.value)}
            >
              <option value="">Выберите вариант</option>
              <option value="individual">Физическое лицо</option>
              <option value="self-employed">ИП / самозанятый</option>
              <option value="business">Малый бизнес</option>
              <option value="lawyer">Юрист / помощник</option>
              <option value="other">Другое</option>
            </select>
            <p className="auth-hint">
              Укажите, как вы планируете пользоваться сервисом.
            </p>
          </div>

          {/* Логин */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-login">
              Логин *
            </label>
            <input
              id="reg-login"
              type="text"
              className="auth-input"
              placeholder="Латинские буквы, цифры, точка, подчёркивание"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              autoComplete="username"
            />
            <p className="auth-hint">
              Логин от 3 до 30 символов. Разрешены латинские буквы, цифры,
              точка и подчёркивание. Первый символ — буква.
            </p>
          </div>

          {/* Пароль */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="reg-password">
              Пароль *
            </label>
            <div className="auth-password-wrapper">
              <input
                id="reg-password"
                type={showPassword ? "text" : "password"}
                className="auth-input"
                placeholder="Не менее 8 символов"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={handleTogglePassword}
              >
                {showPassword ? "Скрыть" : "Показать"}
              </button>
            </div>
            <p className="auth-hint">
              Пароль от 8 до 64 символов, рекомендуется использовать строчные и
              заглавные буквы, цифры и специальные символы.
            </p>
          </div>

          {/* Согласие с условиями */}
          <div className="auth-field">
            <label className="auth-checkbox">
              <input
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
              />
              <span>
                Я подтверждаю, что ознакомился(ась) и согласен(на) со всеми
                условиями и правилами сервиса LegalAI, а также с обработкой
                моих персональных данных.
              </span>
            </label>
            <p className="auth-hint">
              Правила и условия · Политика конфиденциальности
            </p>
          </div>

          {/* Кнопка регистрации */}
          <button
            type="submit"
            className="auth-primary-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Создаём аккаунт..." : "Создать аккаунт"}
          </button>
        </form>

        {/* Низ карточки — уже есть аккаунт */}
        <p className="auth-footer-text">
          Уже есть аккаунт?{" "}
          <button
            type="button"
            className="auth-link-button"
            onClick={onGoToLogin}
          >
            Войти
          </button>
        </p>

        {/* Рекламный блок для сторонних источников (как на логине) */}
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

