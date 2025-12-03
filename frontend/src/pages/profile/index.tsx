type ProfilePageProps = {
  onGoBack: () => void;
  onGoToChangePassword: () => void;
};

export function ProfilePage({
  onGoBack,
  onGoToChangePassword,
}: ProfilePageProps) {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Профиль</h1>
        <p className="auth-subtitle">
          Здесь отображаются ваши регистрационные данные. Позже мы добавим
          возможность менять их и настраивать аккаунт.
        </p>

        <div className="auth-field">
          <p>Email: <strong>user@example.com</strong></p>
          <p>Статус: <strong>аккаунт активен</strong></p>
        </div>

        <div className="auth-field">
          <button
            type="button"
            className="auth-primary-button"
            onClick={onGoToChangePassword}
          >
            Сменить пароль
          </button>
        </div>

        <div className="auth-field">
          <button
            type="button"
            className="auth-primary-button"
            onClick={onGoBack}
          >
            Вернуться в кабинет
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;

