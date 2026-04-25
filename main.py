"""
뉴스 브리핑 봇 - 매일 오전 6시(KST) 자동 실행
실행: python main.py           (스케줄러 모드, 백그라운드 대기)
실행: python main.py --now     (즉시 1회 실행)
"""

import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from news_collector import collect_all_news
from ai_summarizer import summarize_all
from telegram_sender import send_briefing, send_error_alert

# ── 로그 설정 ────────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "briefing.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("main")

KST = pytz.timezone("Asia/Seoul")


def run_briefing():
    start = datetime.now(KST)
    logger.info("=" * 60)
    logger.info("브리핑 시작: %s", start.strftime("%Y-%m-%d %H:%M:%S KST"))

    try:
        logger.info("[1/3] 뉴스 수집 중...")
        news_data = collect_all_news()
        total_collected = sum(len(v) for v in news_data.values())
        logger.info("      수집 완료: 총 %d개", total_collected)

        logger.info("[2/3] AI 요약 중...")
        summarized = summarize_all(news_data)
        logger.info("      요약 완료")

        logger.info("[3/3] 텔레그램 전송 중...")
        send_briefing(summarized)

        elapsed = (datetime.now(KST) - start).total_seconds()
        logger.info("브리핑 완료: %.1f초 소요", elapsed)
        logger.info("=" * 60)

    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("브리핑 실패: %s\n%s", exc, tb)
        send_error_alert(f"브리핑 실패: {exc}\n\n{tb[:800]}")


def main():
    if "--now" in sys.argv or "-n" in sys.argv:
        logger.info("즉시 실행 모드")
        run_briefing()
        return

    # 매일 오전 6시 KST = UTC 21:00 전날
    scheduler = BlockingScheduler(timezone=KST)
    scheduler.add_job(
        run_briefing,
        trigger=CronTrigger(hour=6, minute=0, timezone=KST),
        id="daily_briefing",
        name="뉴스 브리핑",
        misfire_grace_time=300,  # 5분 내 실행 지연 허용
    )

    next_run = scheduler.get_jobs()[0].next_run_time
    logger.info("스케줄러 시작. 다음 실행: %s", next_run.strftime("%Y-%m-%d %H:%M:%S %Z"))
    logger.info("종료하려면 Ctrl+C 를 누르세요.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("스케줄러 종료됨.")


if __name__ == "__main__":
    main()
