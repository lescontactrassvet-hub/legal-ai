import React from "react";

type RegisterPageProps = {
  onGoToLogin: () => void;
};

export function RegisterPage({ onGoToLogin }: RegisterPageProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Здесь позже подключим реальный запрос к backend /auth/register
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

        <form className="auth-form" onSubmit={handleSubmit}>
          {/* Фамилия */}
          <div className="auth-field">
            <label htmlFor="lastName">Фамилия *</label>
            <input
              id="lastName"
              type="text"
              className="auth-input"
              placeholder="Введите фамилию"
              required
            />
          </div>

          {/* Имя */}
          <div className="auth-field">
            <label htmlFor="firstName">Имя *</label>
            <input
              id="firstName"
              type="text"
              className="auth-input"
              placeholder="Введите имя"
              required
            />
          </div>

          {/* Отчество (необязательно) */}
          <div className="auth-field">
            <label htmlFor="middleName">Отчество (при наличии)</label>
            <input
              id="middleName"
              type="text"
              className="auth-input"
              placeholder="Введите отчество (если есть)"
            />
          </div>

          {/* Год рождения */}
          <div className="auth-field">
            <label htmlFor="birthYear">Год рождения *</label>
            <input
              id="birthYear"
              type="number"
              className="auth-input"
              placeholder="Например: 1975"
              required
            />
          </div>

          {/* Email */}
          <div className="auth-field">
            <label htmlFor="email">Email *</label>
            <input
              id="email"
              type="email"
              className="auth-input"
              placeholder="Ваш email"
              required
            />
          </div>

          {/* Телефон */}
          <div className="auth-field">
            <label htmlFor="phone">Телефон *</label>
            <input
              id="phone"
              type="tel"
              className="auth-input"
              placeholder="+7 900 000 00 00"
              required
            />
          </div>

          {/* Подтверждение телефона */}
          <div className="auth-field">
            <label htmlFor="phoneConfirm">Подтвердите телефон *</label>
            <input
              id="phoneConfirm"
              type="tel"
              className="auth-input"
              placeholder="Повторите телефон"
              required
            />
          </div>

          {/* Страна */}
          <div className="auth-field">
            <label htmlFor="country">Страна *</label>
            <input
              id="country"
              type="text"
              className="auth-input"
              placeholder="Страна"
              required
            />
          </div>

          {/* Город / район */}
          <div className="auth-field">
            <label htmlFor="city">Город / район *</label>
            <input
              id="city"
              type="text"
              className="auth-input"
              placeholder="Город или район"
              required
            />
          </div>

          {/* Род деятельности */}
          <div className="auth-field">
            <label htmlFor="activity">Род деятельности *</label>
            <select id="activity" className="auth-input" required>
              <option value="">Выберите вариант</option>
              <option value="lawyer">Юрист / адвокат</option>
              <option value="business">Собственник бизнеса</option>
              <option value="private">Частное лицо</option>
              <option value="student">Студент</option>
              <option value="other">Другое</option>
            </select>
            <p className="auth-hint">
              Укажите, как вы планируете пользоваться сервисом.
            </p>
          </div>

          {/* Логин */}
          <div className="auth-field">
            <label htmlFor="login">Логин *</label>
            <input
              id="login"
              type="text"
              className="auth-input"
              placeholder="Латинские буквы, цифры, точка, подчёркивание"
              required
            />
            <p className="auth-hint">
              Логин от 3 до 30 символов. Разрешены латинские буквы, цифры,
              точка и подчёркивание. Первый символ — буква.
            </p>
          </div>

          {/* Пароль */}
          <div className="auth-field">
            <label htmlFor="password">Пароль *</label>
            <input
              id="password"
              type="password"
              className="auth-input"
              placeholder="Не менее 8 символов"
              required
            />
            <p className="auth-hint">
              Пароль от 8 до 64 символов, должен содержать: строчную букву,
              заглавную букву, цифру и спецсимвол (например: LegalAI_2024!).
            </p>
          </div>

          {/* Согласия */}
          <div className="auth-field">
            <label className="auth-remember">
              <input type="checkbox" className="auth-checkbox" required />
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

          {/* Кнопка Создать аккаунт */}
          <button type="submit" className="auth-primary-button">
            Создать аккаунт
          </button>
        </form>

        {/* Низ: ссылка на логин */}
        <p className="auth-footer-text">
          Уже есть аккаунт?{" "}
          <button type="button" className="auth-link-button" onClick={onGoToLogin}>
            Войти
          </button>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;

