type DocumentsPageProps = {
  // В будущем сюда можно будет пробросить навигацию:
  // onGoToWorkspace?: () => void;
  // onLogout?: () => void;
};

export function DocumentsPage(_props: DocumentsPageProps) {
  const currentYear = new Date().getFullYear();

  return (
    <div className="workspace-page">
      {/* ШАПКА такая же по стилю, как в Workspace */}
      <header className="workspace-header">
        <div className="workspace-header-inner">
          {/* ЛОГОТИП + НАЗВАНИЕ */}
          <div className="workspace-logo-block">
            <img src="/logo.png" alt="Logo" className="workspace-logo" />
            <div className="workspace-logo-text">
              <div className="workspace-title">LEGALAI</div>
              <div className="workspace-subtitle">
                Юридический ИИ — Татьяна
              </div>
            </div>
          </div>

          {/* МЕНЮ СПРАВА — пока без логики навигации */}
          <div className="workspace-menu">
            <button className="auth-primary-button">Чат ИИ “Татьяна”</button>
            <button className="auth-primary-button">Документы</button>
            <button className="auth-primary-button">Профиль</button>
            <button className="auth-primary-button">Выйти</button>
          </div>
        </div>
      </header>

      {/* ОСНОВНОЙ КОНТЕНТ СТРАНИЦЫ ДОКУМЕНТОВ */}
      <main className="workspace-main">
        <div className="workspace-main-left">
          <h2 className="workspace-section-title">Документы</h2>
          <p className="workspace-placeholder">
            Здесь будет раздел с вашими документами: черновики, финальные версии,
            вложения и экспорт в Word/PDF. Сейчас это демонстрационная страница
            без данных.
          </p>
          <p className="workspace-chat-tip">
            Позже здесь появится список документов, фильтры, поиск и быстрый
            переход к редактированию в рабочем кабинете.
          </p>
        </div>

        <div className="workspace-main-right">
          <section className="workspace-side-panel workspace-side-panel-active">
            <div className="workspace-side-panel-header">
              <h2 className="workspace-section-title">Фильтры</h2>
              <span className="workspace-side-panel-toggle">Свернуть</span>
            </div>
            <p className="workspace-placeholder">
              Здесь позже появятся фильтры по типу документа, статусу, дате
              создания и т.п.
            </p>
          </section>

          <section className="workspace-side-panel workspace-side-panel-collapsed">
            <div className="workspace-side-panel-header">
              <h2 className="workspace-section-title">Статистика</h2>
              <span className="workspace-side-panel-toggle">Открыть</span>
            </div>
            <p className="workspace-placeholder">
              Здесь будет короткая статистика: сколько дел, сколько документов,
              какие из них требуют внимания.
            </p>
          </section>
        </div>
      </main>

      {/* ФУТЕР */}
      <footer className="workspace-footer">
        <p className="workspace-footer-text">
          © {currentYear} Проект LegalAI. Все права на сервис и разработанные
          материалы принадлежат Береску Н. Защищено законодательством РФ и
          международным правом.
        </p>
      </footer>
    </div>
  );
}

