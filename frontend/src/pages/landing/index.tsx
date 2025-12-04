import React from "react";

export type LandingPageProps = {
  onGoToLogin: () => void;
  onGoToRegister: () => void;
};

export function LandingPage({ onGoToLogin, onGoToRegister }: LandingPageProps) {
  const currentYear = new Date().getFullYear();

  return (
    <div className="landing-root">
      {/* HEADER */}
      <header className="landing-header">
        <div className="landing-header-left">
          <img src="/logo.png" alt="logo" className="landing-logo" />
          <div className="landing-title-block">
            <h1 className="landing-title">LEGALAI</h1>
            <p className="landing-subtitle">Юридический ИИ — Татьяна</p>
          </div>
        </div>

        <div className="landing-header-right">
          <button className="landing-btn-secondary" onClick={onGoToLogin}>
            Войти
          </button>
          <button className="landing-btn-primary" onClick={onGoToRegister}>
            Регистрация
          </button>
        </div>
      </header>

      {/* HERO */}
      <section className="landing-hero">
        <div className="landing-hero-text">
          <h2 className="landing-hero-title">Юридический ИИ-ассистент «Татьяна»</h2>
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
            <button className="landing-btn-primary" onClick={onGoToLogin}>
              Попробовать бесплатно
            </button>
            <a href="#how" className="landing-btn-link">
              Узнать подробнее
            </a>
          </div>
        </div>

        <div className="landing-hero-image">
          <div className="landing-hero-mockup">
            <div className="landing-hero-mockup-chat">Окно чата Татьяны</div>
            <div className="landing-hero-mockup-doc">Фрагмент документа</div>
          </div>
        </div>
      </section>

      {/* FOR WHO */}
      <section className="landing-section">
        <h2 className="landing-section-title">Для кого создан LEGALAI</h2>

        <div className="landing-grid">
          <div className="landing-card">
            <h3>Физические лица</h3>
            <p>Бытовые ситуации, споры, заявления, обращения, консультации.</p>
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
            <p>Быстрые проекты документов и структурированный анализ.</p>
          </div>
        </div>
      </section>

      {/* WHAT TATIANA DOES */}
      <section className="landing-section">
        <h2 className="landing-section-title">Что умеет ИИ-юрист «Татьяна»</h2>

        <div className="landing-grid-3">
          <div className="landing-card">
            <h3>Проекты документов</h3>
            <p>
              Иски, заявления, жалобы, договоры — структурированные проекты для
              дальнейшей доработки.
            </p>
          </div>

          <div className="landing-card">
            <h3>Объяснение закона</h3>
            <p>Понятные объяснения норм права без лишней терминологии.</p>
          </div>

          <div className="landing-card">
            <h3>Подсказки по структуре</h3>
            <p>Татьяна подсказывает, что важно указать и в какой части документа.</p>
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
            <p>Сформируйте проект документа в редакторе и сохраните его.</p>
          </div>
        </div>
      </section>

      {/* IMPORTANT */}
      <section className="landing-section-important">
        <h2 className="landing-section-title">Важно знать</h2>
        <p className="landing-important-text">
          LEGALAI и ИИ-ассистент «Татьяна» не заменяют адвоката или юриста. Сервис
          помогает создать <strong>проект документа</strong> и лучше понимать вашу
          ситуацию. Перед отправкой документов рекомендуется внимательно
          перепроверить текст и при необходимости обратиться к специалисту.
        </p>
      </section>

      {/* CTA */}
      <section className="landing-section-cta">
        <h2>Попробуйте LEGALAI бесплатно</h2>
        <p>Создайте личный кабинет и подготовьте свой первый проект документа.</p>
        <button className="landing-btn-primary" onClick={onGoToLogin}>
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
      </footer>
    </div>
  );
}

export default LandingPage;

