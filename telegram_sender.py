import re
import asyncio
import logging
from datetime import datetime
import pytz
import telegram
from telegram.constants import ParseMode
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SECTIONS

logger = logging.getLogger(__name__)

TELEGRAM_MAX_LEN = 4000  # 안전 마진 포함 (실제 한도 4096)
KST = pytz.timezone("Asia/Seoul")


# MarkdownV2 이스케이프 - URL과 일반 텍스트를 구분해야 함
def _esc(text: str) -> str:
    """MarkdownV2 특수문자 이스케이프 (URL 제외)"""
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", str(text))


def _build_section_message(section_name: str, articles: list[dict], emoji: str) -> list[str]:
    """섹션 메시지를 4000자 이내 청크 리스트로 반환"""
    now_kst = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    header = f"{emoji} *{_esc(section_name)}*  \\|  {_esc(now_kst)}\n{'─' * 28}\n\n"

    chunks: list[str] = []
    current = header

    for i, article in enumerate(articles, 1):
        title = article.get("ko_title") or article.get("title", "")
        summary = article.get("ko_summary") or article.get("summary", "")
        link = article.get("link", "")
        highlighted = article.get("highlighted", False)

        # 제목 포맷
        title_prefix = "⭐ " if highlighted else ""
        title_line = f"*{title_prefix}{_esc(title)}*\n"

        # 요약 포맷
        summary_line = f"{_esc(summary)}\n" if summary else ""

        # 링크 포맷
        link_line = f"[🔗 원문]({link})\n\n" if link else "\n"

        block = f"📌 {i}\\. {title_line}{summary_line}{link_line}"

        # 청크 크기 초과 시 새 청크 시작
        if len(current) + len(block) > TELEGRAM_MAX_LEN:
            chunks.append(current)
            current = f"{emoji} *{_esc(section_name)}* \\(계속\\)\n\n{block}"
        else:
            current += block

    if current.strip():
        chunks.append(current)

    return chunks


def _build_intro_message(total_articles: int) -> str:
    now_kst = datetime.now(KST).strftime("%Y년 %m월 %d일 %H:%M")
    return (
        f"📰 *{_esc(now_kst)} 뉴스 브리핑*\n\n"
        f"총 *{total_articles}개* 기사를 요약했습니다\\.\n"
        f"각 섹션별 주요 뉴스를 확인하세요\\! 🔔"
    )


async def _send_message_async(bot: telegram.Bot, text: str):
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True,
        )
    except telegram.error.BadRequest as exc:
        logger.warning("Markdown 전송 실패, plaintext 재시도: %s", exc)
        # MarkdownV2 실패 시 텍스트로 폴백
        plain = re.sub(r"[\\*_`\[\]()]", "", text)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=plain[:4096],
            disable_web_page_preview=True,
        )


async def send_briefing_async(summarized: dict[str, list[dict]]):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return

    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    total = sum(len(v) for v in summarized.values())

    # 인트로 메시지
    await _send_message_async(bot, _build_intro_message(total))
    await asyncio.sleep(1)

    # 섹션별 메시지 전송
    for section_name, articles in summarized.items():
        if not articles:
            continue
        emoji = SECTIONS.get(section_name, {}).get("emoji", "📋")
        chunks = _build_section_message(section_name, articles, emoji)
        for chunk in chunks:
            await _send_message_async(bot, chunk)
            await asyncio.sleep(0.5)  # 텔레그램 rate limit 방지

    # 완료 메시지
    done_msg = "✅ *브리핑 전송 완료\\!*\n다음 브리핑은 내일 오전 6시입니다\\. 좋은 하루 되세요 ☀️"
    await _send_message_async(bot, done_msg)
    logger.info("텔레그램 전송 완료 (총 %d개 기사)", total)


def send_briefing(summarized: dict[str, list[dict]]):
    asyncio.run(send_briefing_async(summarized))


async def send_error_alert_async(error_msg: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    text = f"⚠️ *뉴스 브리핑 오류*\n\n{_esc(error_msg[:500])}"
    await _send_message_async(bot, text)


def send_error_alert(error_msg: str):
    try:
        asyncio.run(send_error_alert_async(error_msg))
    except Exception:
        pass
