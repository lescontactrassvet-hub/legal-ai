# backend/ai/router_rubert.py

"""
Простейший классификатор намерений на основе эвристик.
Используется как временная заглушка, пока не подключена настоящая RuBERT-модель.
"""

from __future__ import annotations


class RuBERTIntentClassifier:
    """
    Эвристический классификатор запросов пользователя.
    Используется для выбора режима:
      - template      → пользователь просит шаблон/документ
      - risk_check    → пользователь спрашивает о рисках
      - analysis      → обычная юридическая консультация
      - default       → fallback
    """

    def __init__(self):
        # Можно расширять словари ключевых слов
        self.template_keywords = [
            "договор",
            "шаблон",
            "иск",
            "заявление",
            "жалоба",
            "проект",
            "подготовь документ",
            "составь документ",
            "сделай документ",
        ]

        self.risk_keywords = [
            "риск",
            "риски",
            "опас",
            "последств",
            "будет ли ответственность",
            "уголов",
        ]

    def classify(self, text: str) -> str:
        """
        Простейшая логика:
        - если запрос содержит слова про документы → 'template'
        - если содержит слова про риски → 'risk_check'
        - иначе → 'analysis'
        """

        if not text:
            return "analysis"

        q = text.lower()

        for w in self.template_keywords:
            if w in q:
                return "template"

        for w in self.risk_keywords:
            if w in q:
                return "risk_check"

        return "analysis"
