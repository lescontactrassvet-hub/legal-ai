import { useEffect } from "react";

type LandingPageProps = {
  onTryFree: () => void;
  onLoginClick: () => void;
};

export function LandingPage({ onTryFree, onLoginClick }: LandingPageProps) {
  // SEO: заголовок и мета-теги для поисковиков
  useEffect(() => {
    const title = "LEGALAI — юридический ИИ-ассистент Татьяна | Проекты документов и подсказки";
    const description =
      "LEGALAI — виртуальный юридический ИИ-ассистент Татьяна. Помогает разобраться в вашей ситуации, предлагает план действий и готовит проекты юридических документов в удобном редакторе.";
    const keywords =
      "LEGALAI, юридический ИИ, ИИ юрист, Татьяна, юридический помощник, проект документа, юридический документ, жалоба, обращение, заявление, консультация, права, закон";

    document.title = title;

    // meta description
    let metaDescription = document.querySelector(
      'meta[name="description"]'
    ) as HTMLMetaElement | null;
    if (!metaDescription) {
      metaDescription = document.createElement("meta");
      metaDescription.name = "description";
      document.head.appendChild(metaDescription);
    }
    metaDescription.content = description;

    // meta keywords
    let metaKeywords = document.querySelector(
      'meta[name="keywords"]'
    ) as HTMLMetaElement | null;
    if (!metaKeywords) {
      metaKeywords = document.createElement("meta");
      metaKeywords.name = "keywords";
      document.head.appendChild(metaKeywords);
    }
    metaKeywords.content = keywords;
  }, []);

  return (
    <div className="landing-page">
      {/* Шапка */}
      <header className="landing-header">
        <div className="landing-header-left">
          <div className="landing-logo">
            <img src="/logo.png" alt="LEGALAI" className="landing-logo-image" />
            <div className="landing-logo-text">
              <div className="landing-logo-title">LEGALAI</div>
              <div className="landing-logo-subtitle">Юридический ИИ — Татьяна</div>
            </div>
          </div>
        </div>
        <div className="landing-header-right">
          <button
            type="button"
            className="landing-header-link"
            onClick={onLoginClick}
          >
            Войти
          </button>
        </div>
      </header>

      {/* Hero-блок */}
      <main className="landing-main">
        <section className="landing-hero">
          <div className="landing-hero-text">
            <h1 className="landing-hero-title">
              Юридический ИИ-ассистент, который объясняет закон простым языком
            </h1>
            <p className="landing-hero-subtitle">
              Татьяна помогает разобраться в вашей ситуации, предлагает возможные
              шаги и готовит проекты юридических документов — от обращений и
              заявлений до служебных записок.
            </p>
            <div className="landing-hero-actions">
              <button
                type="button"
                className="landing-hero-button"
                onClick={onTryFree}
              >
                Попробовать бесплатно
              </button>
              <p className="landing-hero-note">
                Демо-режим: знакомство с возможностями системы. Не заменяет
                консультацию адвоката или представителя.
              </p>
            </div>
          </div>

          <div className="landing-hero-preview">
            <div className="landing-preview-card">
              <div className="landing-preview-header">
                <span className="landing-preview-title">Чат ИИ “Татьяна”</span>
                <span className="landing-preview-status">онлайн</span>
              </div>
              <div className="landing-preview-chat">
                <div className="landing-preview-message landing-preview-message-user">
                  Мне нужна помощь с ситуацией на работе, не понимаю, нарушили
                  ли мои права.
                </div>
                <div className="landing-preview-message landing-preview-message-ai">
                  Опишите, пожалуйста, что именно произошло: какие действия
                  работодателя вас беспокоят, были ли письменные документы или
                  устные распоряжения.
                </div>
                <div className="landing-preview-message landing-preview-message-ai">
                  Я помогу выделить ключевые моменты, объясню, на какие нормы
                  права опираться, и подготовлю проект документа, если он
                  понадобится.
                </div>
              </div>
              <div className="landing-preview-document">
                <div className="landing-preview-document-header">
                  <span>Проект документа</span>
                </div>
                <div className="landing-preview-document-body">
                  <p>
                    1. Вводная часть: кто вы, какой у вас статус и к кому
                    обращаетесь.
                  </p>
                  <p>
                    2. Описание ситуации: факты, даты, участники и ключевые
                    обстоятельства.
                  </p>
                  <p>
                    3. Правовое обоснование: ссылки на нормы и ваши права.
                  </p>
                  <p>
                    4. Просьба: чего вы хотите добиться в результате обращения.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Блок возможностей */}
        <section className="landing-section">
          <h2 className="landing-section-title">Что умеет Татьяна</h2>
          <div className="landing-features">
            <div className="landing-feature-card">
              <h3>Понятные ответы на сложные вопросы</h3>
              <p>
                Опишите ситуацию своими словами — Татьяна задаст уточняющие
                вопросы и объяснит, что происходит с юридической точки зрения,
                без перегрузки терминами.
              </p>
            </div>
            <div className="landing-feature-card">
              <h3>Проекты юридических документов</h3>
              <p>
                Система помогает приготовить структурированный проект документа:
                обращения, заявления, жалобы или служебной записки, который вы
                сможете доработать в встроенном редакторе.
              </p>
            </div>
            <div className="landing-feature-card">
              <h3>Подготовка к диалогу и переговорам</h3>
              <p>
                Татьяна помогает сформулировать позицию, список вопросов и
                собрать факты перед обращением к юристу, в организацию или
                госорган.
              </p>
            </div>
          </div>
        </section>

        {/* Как это работает */}
        <section className="landing-section">
          <h2 className="landing-section-title">Как это работает</h2>
          <div className="landing-steps">
            <div className="landing-step-card">
              <div className="landing-step-number">1</div>
              <h3>Расскажите о своей ситуации</h3>
              <p>
                Опишите, что произошло, в свободной форме. При необходимости вы
                сможете приложить документы для анализа.
              </p>
            </div>
            <div className="landing-step-card">
              <div className="landing-step-number">2</div>
              <h3>Татьяна задаёт вопросы и анализирует</h3>
              <p>
                ИИ помогает не упустить важные детали, выделяет ключевые моменты
                и объясняет, какие права могут быть затронуты.
              </p>
            </div>
            <div className="landing-step-card">
              <div className="landing-step-number">3</div>
              <h3>Получаете план действий и проект документа</h3>
              <p>
                Система формирует понятный план возможных шагов и проект
                документа, который можно редактировать и использовать как основу.
              </p>
            </div>
          </div>
        </section>

        {/* Для кого */}
        <section className="landing-section">
          <h2 className="landing-section-title">Кому это может быть полезно</h2>
          <div className="landing-audience">
            <div className="landing-audience-card">
              <h3>Частным лицам</h3>
              <p>
                Бытовые ситуации, покупки и возврат товаров, услуги, аренда,
                трудовые вопросы и другие житейские истории, где важно понять,
                какие у вас есть возможности и права.
              </p>
            </div>
            <div className="landing-audience-card">
              <h3>ИП и малому бизнесу</h3>
              <p>
                Взаимодействие с клиентами и подрядчиками, базовые договорные
                вопросы, претензии и ответы, подготовка проектов документов для
                деловой переписки.
              </p>
            </div>
            <div className="landing-audience-card">
              <h3>Специалистам и командам</h3>
              <p>
                Юристам, HR и руководителям, которым важно быстро структурировать
                информацию и получить первичный проект документа для дальнейшей
                доработки.
              </p>
            </div>
          </div>
        </section>

        {/* Рекламный блок / оффер + место для внешней рекламы */}
        <section className="landing-section landing-promo-section">
          <div className="landing-promo-main">
            <h2 className="landing-section-title">Попробуйте LEGALAI бесплатно</h2>
            <p className="landing-promo-text">
              Оцените, как ИИ-ассистент Татьяна помогает разбираться в сложных
              ситуациях, готовить проекты документов и экономить ваше время.
            </p>
            <ul className="landing-promo-list">
              <li>Демо-режим без привязки карты.</li>
              <li>Можно протестировать работу на своих примерах.</li>
              <li>Конфиденциальное общение — только вы и виртуальный ассистент.</li>
            </ul>
            <button
              type="button"
              className="landing-hero-button"
              onClick={onTryFree}
            >
              Попробовать бесплатно
            </button>
          </div>

          {/* Рекламный блок для внешнего кода (из панели администратора) */}
          <aside className="landing-ads">
            <div
              className="landing-ad-slot"
              data-ad-slot="landing-sidebar-1"
            >
              {/* Рекламный блок.
                  Код баннера или виджета будет подставляться из панели администратора.
                  Здесь оставляем только контейнер. */}
              Рекламный блок (будет настроен администратором)
            </div>
          </aside>
        </section>

        {/* Безопасность и ограничения */}
        <section className="landing-section">
          <h2 className="landing-section-title">Важно знать</h2>
          <div className="landing-important">
            <p>
              Татьяна помогает ориентироваться в информации, формировать проекты
              документов и план действий, но не заменяет адвоката или официального
              представителя в суде или органах власти.
            </p>
            <p>
              Не указывайте лишние персональные данные, если это не требуется для
              описания ситуации. При необходимости получения профессиональной
              юридической помощи обращайтесь к практикующему специалисту.
            </p>
          </div>
        </section>
      </main>

      {/* Футер */}
      <footer className="landing-footer">
        <div className="landing-footer-main">
          <div className="landing-footer-brand">
            <span className="landing-footer-logo">LEGALAI</span>
            <span className="landing-footer-text">
              Юридический ИИ — Татьяна
            </span>
          </div>
          <div className="landing-footer-links">
            <button type="button" className="landing-footer-link">
              Политика конфиденциальности
            </button>
            <button type="button" className="landing-footer-link">
              Пользовательское соглашение
            </button>
            <button type="button" className="landing-footer-link">
              Контакты
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

