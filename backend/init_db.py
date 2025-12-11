from app.db.database import Base, engine
import app.laws.models  # ⚠️ импорт нужен, чтобы модели подгрузились

print("Создаю таблицы...")
Base.metadata.create_all(bind=engine)
print("Готово!")

