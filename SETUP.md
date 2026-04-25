# 뉴스 브리핑 봇 설치 및 실행 가이드

## 1단계: Python 설치 (아직 없는 경우)

```
winget install Python.Python.3.12
```
설치 후 **새 터미널(PowerShell/CMD)** 열기.

---

## 2단계: 의존성 설치

```powershell
cd C:\wbot\news_briefing
pip install -r requirements.txt
```

---

## 3단계: API 키 설정

`.env.example`을 복사해 `.env` 파일 생성:

```powershell
copy .env.example .env
notepad .env
```

`.env` 파일에 입력:

```
GEMINI_API_KEY=AIzaSy...              ← https://aistudio.google.com/apikey
TELEGRAM_BOT_TOKEN=1234567890:AAAA...  ← @BotFather에서 발급
TELEGRAM_CHAT_ID=123456789           ← 아래 확인 방법 참고
NEWSAPI_KEY=abc123...                 ← https://newsapi.org (없으면 생략 가능)
```

### Telegram Chat ID 확인 방법
1. Telegram에서 `@userinfobot` 에게 아무 메시지 전송
2. 응답에서 `Id:` 숫자 복사
3. 채널이라면 채널 정보 → 링크 복사 → `-100` 앞에 붙인 숫자 ID

---

## 4단계: 즉시 테스트 실행

```powershell
cd C:\wbot\news_briefing
python main.py --now
```

로그는 `logs\briefing.log` 에서 확인.

---

## 5단계: 자동 실행 설정 (3가지 방법)

### 방법 A — Python 스케줄러 (간단, 컴퓨터가 켜져 있어야 함)

```powershell
python main.py
```
프로그램이 켜져 있는 동안 매일 오전 6시에 자동 실행.

### 방법 B — Windows 작업 스케줄러 (안정적, PC가 켜져 있어야 함)

**관리자 권한 PowerShell**에서:

```powershell
cd C:\wbot\news_briefing
.\setup_windows_task.bat
```

또는 직접 등록:

```powershell
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\wbot\news_briefing\main.py --now" -WorkingDirectory "C:\wbot\news_briefing"
$trigger = New-ScheduledTaskTrigger -Daily -At "06:00AM"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName "NewsBriefingBot" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
```

등록 후 즉시 테스트:
```powershell
Start-ScheduledTask -TaskName "NewsBriefingBot"
```

### 방법 C — GitHub Actions (권장, PC 꺼져 있어도 동작)

GitHub 서버에서 매일 오전 6시 KST에 자동 실행됩니다. PC가 꺼져 있어도 됩니다.

**1) GitHub 저장소 생성 및 코드 업로드**

```powershell
cd C:\wbot\news_briefing
git init
git add .
git commit -m "초기 커밋"
```

GitHub에서 새 저장소(예: `news-briefing-bot`) 생성 후:

```powershell
git remote add origin https://github.com/사용자명/news-briefing-bot.git
git branch -M main
git push -u origin main
```

**2) GitHub Secrets 등록**

저장소 페이지 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| 이름 | 값 |
|------|-----|
| `GEMINI_API_KEY` | Google AI Studio에서 발급한 키 |
| `TELEGRAM_BOT_TOKEN` | BotFather에서 발급한 토큰 |
| `TELEGRAM_CHAT_ID` | 텔레그램 채팅 ID |
| `NEWSAPI_KEY` | newsapi.org 키 (없으면 빈 값으로 등록) |

**3) 수동 테스트 실행**

저장소 페이지 → **Actions** → **일일 뉴스 브리핑** → **Run workflow**

**스케줄:** `.github/workflows/daily_briefing.yml`의 cron `0 21 * * *` = UTC 21:00 = KST 06:00

---

## 섹션 커스터마이징

`config.py`의 `SECTIONS` 딕셔너리를 수정하여 섹션/RSS 피드/키워드 변경 가능.

### 관심 키워드 추가

`config.py`의 `HIGHLIGHT_KEYWORDS` 리스트에 추가:

```python
HIGHLIGHT_KEYWORDS = [
    "RNAi", "siRNA", "mRNA",
    "Alzheimer",
    "EUV", "ASML",
    "추가하고 싶은 키워드",  ← 여기에 추가
]
```

---

## 로그 확인

```powershell
Get-Content C:\wbot\news_briefing\logs\briefing.log -Tail 50
```
