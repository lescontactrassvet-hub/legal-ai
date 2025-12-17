# backend/ai/nlp/rubert_intent.py
"""
RuBERT intent layer.
Безопасный слой: если модель недоступна — fallback.
"""

import logging
from functools import lru_cache
from typing import Dict

logger = logging.getLogger(__name__)

USE_RUBERT = True  # можно потом вынести в env

# Простые целевые intent'ы (C1)
INTENTS = {
    "consultation": [
        "что делать", "как поступить", "консультация", "помогите",
    ],
    "law_search": [
        "статья", "закон", "кодекс", "норма", "гк", "ук", "коап",
    ],
    "document_draft": [
        "договор", "заявление", "исковое", "жалоба", "претензия",
    ],
}

@lru_cache(maxsize=1)
def _load_model():
    try:
        from transformers import AutoTokenizer, AutoModel
        tokenizer = AutoTokenizer.from_pretrained(
            "DeepPavlov/rubert-base-cased"
        )
        model = AutoModel.from_pretrained(
            "DeepPavlov/rubert-base-cased"
        )
        model.eval()
        return tokenizer, model
    except Exception as exc:
        logger.warning("RuBERT not available: %s", exc)
        return None, None


def classify_intent(text: str) -> Dict[str, object]:
    """
    Возвращает:
    {
        "intent": str,
        "confidence": float,
        "engine": "rubert" | "fallback"
    }
    """
    text_l = text.lower()

    # Fallback-эвристика (работает всегда)
    for intent, keywords in INTENTS.items():
        for kw in keywords:
            if kw in text_l:
                return {
                    "intent": intent,
                    "confidence": 0.3,
                    "engine": "fallback",
                }

    # Попытка RuBERT (пока без fine-tune, future-ready)
    if USE_RUBERT:
        tokenizer, model = _load_model()
        if tokenizer and model:
            # Пока без классификатора — просто факт, что модель жива
            return {
                "intent": "consultation",
                "confidence": 0.5,
                "engine": "rubert",
            }

    return {
        "intent": "consultation",
        "confidence": 0.0,
        "engine": "fallback",
    }

