import time
import logging
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL, HIGHLIGHT_KEYWORDS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """당신은 전문 뉴스 번역 및 요약 어시스턴트입니다.
영문 뉴스 기사를 한국어로 번역하고, 각 기사를 3문장 이내로 핵심 내용을 요약합니다.
요약은 명확하고 간결하게, 투자자 관점에서 중요한 정보를 포함합니다."""


def _build_prompt(section_name: str, articles: list[dict]) -> str:
    highlight_str = ", ".join(HIGHLIGHT_KEYWORDS)
    lines = [
        f"아래는 [{section_name}] 섹션의 최근 뉴스 기사들입니다.",
        f"각 기사를 한국어로 번역하고 3문장 이내로 핵심 내용을 요약해주세요.",
        f"만약 기사 내용에 {highlight_str} 관련 내용이 있으면 제목 앞에 [★] 를 붙여주세요.",
        "",
        "출력 형식 (반드시 지켜주세요):",
        "---기사_1---",
        "제목: [한국어 제목]",
        "요약: [3문장 이내 한국어 요약]",
        "---기사_2---",
        "...",
        "",
        "기사 목록:",
    ]
    for i, a in enumerate(articles, 1):
        lines.append(f"\n[기사 {i}]")
        lines.append(f"제목: {a['title']}")
        if a.get("summary"):
            lines.append(f"본문 요약: {a['summary']}")
    return "\n".join(lines)


def summarize_section(section_name: str, articles: list[dict]) -> list[dict]:
    if not articles:
        return []
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY가 설정되지 않았습니다.")
        return articles

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = _build_prompt(section_name, articles)
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=2048,
            ),
        )
        return _parse_summaries(articles, response.text)
    except Exception as exc:
        logger.error("Gemini API 오류 (%s): %s", section_name, exc)
        return articles


def _parse_summaries(articles: list[dict], response: str) -> list[dict]:
    import re
    blocks = re.split(r"---ARTICLE_\d+---", response)
    blocks = [b.strip() for b in blocks if b.strip()]
    enriched = []

    for i, article in enumerate(articles):
        if i < len(blocks):
            block = blocks[i]
            title_match = re.search(r"제목:\s*(.+)", block)
            summary_match = re.search(r"요약:\s*([\s\S]+?)(?=\n제목:|\Z)", block)
            ko_title = title_match.group(1).strip() if title_match else article["title"]
            ko_summary = summary_match.group(1).strip() if summary_match else ""
            ko_summary = " ".join(ko_summary.split())
        else:
            ko_title = article["title"]
            ko_summary = article.get("summary", "")

        enriched.append({
            **article,
            "ko_title": ko_title,
            "ko_summary": ko_summary,
            "highlighted": ko_title.startswith("[★]"),
        })
    return enriched


def summarize_all(news_data: dict[str, list[dict]]) -> dict[str, list[dict]]:
    result = {}
    for i, (section_name, articles) in enumerate(news_data.items()):
        logger.info("요약 중: %s (%d개)", section_name, len(articles))
        result[section_name] = summarize_section(section_name, articles)
        if i < len(news_data) - 1:
            time.sleep(5)  # 무료 티어 분당 15회 제한 대응
    return result
