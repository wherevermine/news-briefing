import feedparser
import requests
import logging
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from config import SECTIONS, FETCH_HOURS, MAX_ARTICLES_PER_SECTION, NEWSAPI_KEY

logger = logging.getLogger(__name__)

CUTOFF_TIME = timedelta(hours=FETCH_HOURS)
REQUEST_TIMEOUT = 10
SIMILARITY_THRESHOLD = 0.7


def _parse_entry_time(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _is_recent(entry) -> bool:
    pub = _parse_entry_time(entry)
    if pub is None:
        return True  # 날짜 없으면 포함
    return datetime.now(timezone.utc) - pub <= CUTOFF_TIME


def _is_duplicate(title: str, seen: list[str]) -> bool:
    title_lower = title.lower().strip()
    for s in seen:
        ratio = SequenceMatcher(None, title_lower, s.lower().strip()).ratio()
        if ratio >= SIMILARITY_THRESHOLD:
            return True
    return False


def _entry_to_article(entry) -> dict:
    title = getattr(entry, "title", "").strip()
    link = getattr(entry, "link", "").strip()
    summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
    # HTML 태그 기본 제거
    import re
    summary = re.sub(r"<[^>]+>", " ", summary).strip()
    summary = re.sub(r"\s+", " ", summary)[:500]
    pub = _parse_entry_time(entry)
    return {
        "title": title,
        "link": link,
        "summary": summary,
        "published": pub.isoformat() if pub else "",
    }


def fetch_rss_section(section_name: str, config: dict) -> list[dict]:
    articles = []
    seen_titles: list[str] = []

    for feed_url in config.get("feeds", []):
        try:
            resp = requests.get(feed_url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                logger.warning("피드 응답 오류 %s: HTTP %d", feed_url, resp.status_code)
                continue
            feed = feedparser.parse(resp.content)
        except Exception as exc:
            logger.warning("피드 파싱 실패 %s: %s", feed_url, exc)
            continue

        keywords = [k.lower() for k in config.get("keywords", [])]

        for entry in feed.entries:
            title = getattr(entry, "title", "").strip()
            if not title:
                continue
            if not _is_recent(entry):
                continue
            if _is_duplicate(title, seen_titles):
                continue

            article = _entry_to_article(entry)

            # 키워드 있으면 관련성 점수 부여
            text = (article["title"] + " " + article["summary"]).lower()
            article["relevance"] = sum(1 for kw in keywords if kw in text)

            seen_titles.append(title)
            articles.append(article)

    # 관련성 높은 순 → 최신 순 정렬
    articles.sort(key=lambda a: (-a["relevance"], a.get("published", "") or ""), reverse=False)
    articles.sort(key=lambda a: -a["relevance"])
    return articles[:MAX_ARTICLES_PER_SECTION]


def fetch_newsapi_section(section_name: str, keywords: list[str]) -> list[dict]:
    if not NEWSAPI_KEY or not keywords:
        return []
    try:
        query = " OR ".join(keywords[:5])
        from_dt = (datetime.now(timezone.utc) - CUTOFF_TIME).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_dt,
            "sortBy": "relevancy",
            "language": "en",
            "pageSize": MAX_ARTICLES_PER_SECTION,
            "apiKey": NEWSAPI_KEY,
        }
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        data = resp.json()
        articles = []
        for a in data.get("articles", []):
            if a.get("title") == "[Removed]":
                continue
            articles.append({
                "title": a.get("title", ""),
                "link": a.get("url", ""),
                "summary": (a.get("description") or "")[:500],
                "published": a.get("publishedAt", ""),
                "relevance": 0,
            })
        return articles
    except Exception as exc:
        logger.warning("NewsAPI 요청 실패 (%s): %s", section_name, exc)
        return []


def collect_all_news() -> dict[str, list[dict]]:
    result = {}
    for section_name, cfg in SECTIONS.items():
        logger.info("수집 중: %s", section_name)
        articles = fetch_rss_section(section_name, cfg)

        # RSS 결과가 부족하면 NewsAPI로 보완
        if len(articles) < 5 and NEWSAPI_KEY:
            api_articles = fetch_newsapi_section(section_name, cfg.get("keywords", []))
            seen = [a["title"] for a in articles]
            for a in api_articles:
                if not _is_duplicate(a["title"], seen):
                    articles.append(a)
                    seen.append(a["title"])
            articles = articles[:MAX_ARTICLES_PER_SECTION]

        result[section_name] = articles
        logger.info("  -> %d개 수집", len(articles))

    return result
