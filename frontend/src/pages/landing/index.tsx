import React from "react";

export type LandingPageProps = {
  onGoLogin: () => void;
  onGoToRegister: () => void;
  onGoAdmin?: () => void;
};

export function LandingPage({
  onGoLogin,
  onGoToRegister,
  onGoAdmin,
}: LandingPageProps) {
  const currentYear = new Date().getFullYear();

  return (
    <div className="landing-root">
      {/* HEADER */}
      <header className="landing-header">
        <div className="landing-header-left">
          <img src="/logo.png" alt="logo" className="landing-logo" />
          <div className="landing-title-block">
            <h1 className="landing-title">LEGALAI</h1>
            <p className="landing-subtitle">
              Юридический ИИ – Татьяна, помощник по правовым вопросам
            </p>
          </div>
        </div>

        <div className="landing-header-right">
          <button
            className="landing-btn-secondary"
            onClick={onGoLogin}
          >
            Войти
          </button>
          <button
            className="landing-btn-primary"
            onClick={onGoToRegister}
          >
            Регистрация
          </button>
        </div>
      </header>

      {/* HERO */}
      <section className="landing-hero">
        <div className="landing-hero-text">
          <h2 className="landing-hero-title">
            Юридический ИИ-ассистент для повседневных задач
          </h2>
          <p className="landing-hero-desc">
            Помогает вам подготовить{" "}
            <strong>проекты юридических документов</strong> и разобраться в
            ситуации простым человеческим языком.
          </p>

          <ul className="landing-hero-list">
            <li>Проекты исков, заявлений, договоров</li>
            <li>Пошаговые объяснения без сложных терминов</li>
            <li>Связка чата и редактора документов</li>
            <li>Сохранение ваших проектов в личном кабинете</li>
          </ul>

          <div className="landing-hero-buttons">
            <button
              className="landing-btn-primary"
              onClick={onGoToRegister}
            >
              Попробовать бесплатно
            </button>
            <a href="#how" className="landing-btn-link">
              Узнать подробнее
            </a>
          </div>
        </div>

        <div className="landing-hero-image">
          <div className="landing-hero-mockup">
            <div className="landing-hero-mockup-chat">
              Окно чата ИИ-ассистента
            </div>
            <div className="landing-hero-mockup-doc">
              Фрагмент документа
            </div>
          </div>
        </div>
      </section>

      {/* FOR WHO */}
      <section className="landing-section">
        <h2 className="landing-section-title">Для кого создан LEGALAI</h2>

        <div className="landing-grid">
          <div className="landing-card">
            <h3>Физические лица</h3>
            <p>
              Бытовые ситуации, споры, заявления, обращения, жалобы.
            </p>
          </div>

          <div className="landing-card">
            <h3>Индивидуальные предприниматели</h3>
            <p>Договоры, претензии, работа с контрагентами.</p>
          </div>

          <div className="landing-card">
            <h3>Малый бизнес</h3>
            <p>Документы, переписка, юридическая подготовка.</p>
          </div>

          <div className="landing-card">
            <h3>Юристы и помощники</h3>
            <p>
              Быстрые проекты документов и структурированный черновик для
              доработки.
            </p>
          </div>
        </div>
      </section>

      {/* WHAT TATIANA DOES */}
      <section className="landing-section">
        <h2 className="landing-section-title">Что умеет ИИ-юрист Татьяна</h2>

        <div className="landing-grid-3">
          <div className="landing-card">
            <h3>Проекты документов</h3>
            <p>
              Иски, заявления, жалобы, договоры — структурированный текст для
              дальнейшей доработки.
            </p>
          </div>

          <div className="landing-card">
            <h3>Объяснение закона</h3>
            <p>
              Понятные объяснения норм права без лишней терминологии.
            </p>
          </div>

          <div className="landing-card">
            <h3>Подсказки по структуре</h3>
            <p>
              Татьяна подсказывает, что важно указать и в каком порядке.
            </p>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how" className="landing-section">
        <h2 className="landing-section-title">Как это работает</h2>

        <div className="landing-steps">
          <div className="landing-step">
            <span className="landing-step-num">1</span>
            <p>Опишите свою ситуацию в чате.</p>
          </div>

          <div className="landing-step">
            <span className="landing-step-num">2</span>
            <p>Получите разъяснения и структуру документа.</p>
          </div>

          <div className="landing-step">
            <span className="landing-step-num">3</span>
            <p>Сформируйте проект документа в редакторе и сохраните.</p>
          </div>
        </div>
      </section>

      {/* IMPORTANT */}
      <section className="landing-section-important">
        <h2 className="landing-section-title">Важно знать</h2>
        <p className="landing-important-text">
          LEGALAI и ИИ-ассистент «Татьяна» не заменяют адвоката и не дают
          юридических заключений. Сервис помогает создать{" "}
          <strong>проект документа</strong> и лучше понять ситуацию. Перед
          отправкой документов рекомендуется внимательно перепроверить текст и
          при необходимости обратиться к специалисту.
        </p>
      </section>

      {/* CTA */}
      <section className="landing-section-cta">
        <h2 className="landing-section-title">Попробуйте LEGALAI бесплатно</h2>
        <p>
          Создайте личный кабинет и подготовьте свой первый проект документа с
          помощью ИИ-ассистента.
        </p>
        <button
          className="landing-btn-primary"
          onClick={onGoToRegister}
        >
          Начать сейчас
        </button>
      </section>

      {/* FOOTER */}
      <footer className="landing-footer">
        <p>© {currentYear} LEGALAI</p>
        <div className="landing-footer-links">
          <a href="#">Политика конфиденциальности</a>
          <a href="#">Пользовательское соглашение</a>
          <a href="#">Контакты</a>
        </div>

        {/* Тихая ссылка для входа в админку */}
        <div className="landing-footer-admin">
          <button
            type="button"
            onClick={() => onGoAdmin && onGoAdmin()}
            style={{
              marginTop: "8px",
              background: "none",
              border: "none",
              padding: 0,
              fontSize: "10px",
              cursor: "pointer",
              color: "#888",
            }}
          >
            Админ
          </button>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
