import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

GEMINI_MODEL = "gemini-2.5-flash"  # 무료 티어 지원
MAX_ARTICLES_PER_SECTION = 10
FETCH_HOURS = 24  # 지난 24시간

# 관심 키워드 - 발견 시 강조 표시
HIGHLIGHT_KEYWORDS = [
    "RNAi", "RNA interference", "siRNA", "mRNA",
    "Alzheimer", "알츠하이머",
    "EUV", "extreme ultraviolet", "ASML",
    "반도체", "semiconductor",
]

# 10개 뉴스 섹션 정의
SECTIONS = {
    "주요 뉴스": {
        "emoji": "🌍",
        "feeds": [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
            "https://feeds.reuters.com/reuters/topNews",
        ],
        "keywords": [],
    },
    "미국 주식": {
        "emoji": "📈",
        "feeds": [
            "https://feeds.marketwatch.com/marketwatch/topstories/",
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US",
        ],
        "keywords": ["stock", "market", "S&P", "nasdaq", "dow", "wall street", "fed", "rate", "earnings"],
    },
    "반도체": {
        "emoji": "💾",
        "feeds": [
            "https://semiengineering.com/feed/",
            "https://www.eetimes.com/feed/",
            "https://www.tomshardware.com/feeds/all",
        ],
        "keywords": ["semiconductor", "chip", "TSMC", "Intel", "NVIDIA", "AMD", "EUV", "ASML", "foundry", "fab"],
    },
    "바이오/제약": {
        "emoji": "🧬",
        "feeds": [
            "https://www.fiercebiotech.com/rss/xml",
            "https://www.statnews.com/feed/",
            "https://www.biopharmadive.com/feeds/news/",
        ],
        "keywords": ["biotech", "pharma", "drug", "trial", "FDA", "therapy", "RNAi", "siRNA", "Alzheimer", "cancer"],
    },
    "AI/기술": {
        "emoji": "🤖",
        "feeds": [
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "https://venturebeat.com/category/ai/feed/",
            "https://www.technologyreview.com/feed/",
        ],
        "keywords": ["AI", "artificial intelligence", "LLM", "GPT", "machine learning", "deep learning", "model", "AGI"],
    },
    "한국 경제": {
        "emoji": "🇰🇷",
        "feeds": [
            "https://koreajoongangdaily.joins.com/rss/feeds/finance.xml",
            "http://www.koreaherald.com/common/rss.php?cat=biz",
            "https://en.yna.co.kr/RSS/economy.xml",
        ],
        "keywords": ["Korea", "Korean", "Seoul", "Samsung", "Hyundai", "SK", "LG", "KOSPI"],
    },
    "글로벌 경제": {
        "emoji": "🌐",
        "feeds": [
            "https://feeds.reuters.com/reuters/businessNews",
            "https://feeds.reuters.com/reuters/companyNews",
            "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
        ],
        "keywords": ["economy", "GDP", "inflation", "interest rate", "central bank", "trade", "tariff", "recession"],
    },
    "에너지/환경": {
        "emoji": "⚡",
        "feeds": [
            "https://cleantechnica.com/feed/",
            "https://www.renewableenergyworld.com/feed/",
            "https://oilprice.com/rss/main",
        ],
        "keywords": ["energy", "solar", "wind", "battery", "EV", "oil", "gas", "climate", "carbon", "green"],
    },
    "헬스케어": {
        "emoji": "🏥",
        "feeds": [
            "https://medcitynews.com/feed/",
            "https://www.healthcarefinancenews.com/feed",
            "https://www.modernhealthcare.com/section/news/rss",
        ],
        "keywords": ["healthcare", "hospital", "patient", "treatment", "disease", "medical", "health"],
    },
    "스타트업/VC": {
        "emoji": "🚀",
        "feeds": [
            "https://techcrunch.com/category/startups/feed/",
            "https://feeds.feedburner.com/venturebeat/SZYF",
            "https://www.crunchbase.com/rss/feed",
        ],
        "keywords": ["startup", "funding", "IPO", "unicorn", "venture", "investment", "series A", "series B"],
    },
}
