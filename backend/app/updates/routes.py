from typing import List, Dict

from fastapi import APIRouter

# Пытаемся использовать httpx + BeautifulSoup, но если их нет —
# возвращаем пустой список, чтобы не ломать всё приложение.
try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:  # зависимости ещё не установлены
    httpx = None
    BeautifulSoup = None

router = APIRouter(
    prefix="/laws",
    tags=["laws"],
)

# Источники publication.pravo.gov.ru
SOURCES: Dict[str, str] = {
    "president": "http://publication.pravo.gov.ru/documents/block/president",
    "council_1": "http://publication.pravo.gov.ru/documents/block/council_1",
    "council_2": "http://publication.pravo.gov.ru/documents/block/council_2",
    "government": "http://publication.pravo.gov.ru/documents/block/government",
    "court": "http://publication.pravo.gov.ru/documents/block/court",
}


async def _fetch_block(name: str, url: str) -> List[Dict]:
    """
    Загружает HTML-страницу блока и вытаскивает список документов.
    Формат элемента списка:
    {
        "title": "...",   # название акта
        "date": "...",    # строка даты (если найдём)
        "type": "...",    # тип/источник (president, government и т.п.)
        "link": "...",    # ссылка на документ (если есть)
    }
    """
    # Если зависимости не установлены — отдаём пустой список, но без падения сервера
    if httpx is None or BeautifulSoup is None:
        return []

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except Exception:
        # Любая ошибка сети / HTTP — просто считаем, что из этого блока ничего нет
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items: List[Dict] = []

    # Структура сайта может меняться, поэтому берём базовый вариант:
    # просто ищем ссылки внутри основного блока документов.
    # Если разметка поменяется, здесь понадобится корректировка.
    for a in soup.select("a"):
        title = a.get_text(strip=True)
        href = a.get("href")

        if not title or not href:
            continue

        # Пробуем найти рядом элемент с датой (span или div)
        parent = a.parent
        date_text = None
        if parent is not None:
            # ищем любой span/div с текстом, похожим на дату
            for el in parent.find_all(["span", "div"], recursive=False):
                t = el.get_text(strip=True)
                if any(ch.isdigit() for ch in t):
                    date_text = t
                    break

        items.append(
            {
                "title": title,
                "date": date_text,
                "type": name,
                "link": href,
            }
        )

        # Ограничимся первыми 10 документами из каждого блока,
        # чтобы не перегружать интерфейс.
        if len(items) >= 10:
            break

    return items


async def _gather_all_sources() -> List[Dict]:
    """
    Собирает документы со всех пяти источников.
    """
    all_items: List[Dict] = []

    for name, url in SOURCES.items():
        block_items = await _fetch_block(name, url)
        all_items.extend(block_items)

    return all_items


@router.get("/today")
async def get_laws_today() -> List[Dict]:
    """
    Документы, опубликованные сегодня.
    Пока что возвращаем объединённый список из всех блоков
    без жёсткой фильтрации по дате (HTML приходит без явного API).
    На фронтенде блок называется «Сегодня вступили в силу».
    """
    # На первой версии просто отдаём последние документы.
    # При необходимости позже усилим фильтрацию по дате.
    return await _gather_all_sources()


@router.get("/week")
async def get_laws_week() -> List[Dict]:
    """
    Документы за последнюю неделю.
    В текущей версии возвращает тот же список, что и /today.
    Логику фильтрации по дате можно доработать отдельно.
    """
    return await _gather_all_sources()


@router.get("/month")
async def get_laws_month() -> List[Dict]:
    """
    Документы за последний месяц.
    Сейчас аналогично /week — отдаёт общий список.
    """
    return await _gather_all_sources()
