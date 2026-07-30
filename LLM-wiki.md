# 세계 10대 미술관 뉴스레터 수집·발송 시스템 — LLM Wiki

> 프로젝트명: **Hermes (museum_newsletter)**  
> 매주 월요일 아침 전 세계 10대 미술관의 전시 동향 정보를자동 수집하고 HTML 이메일로 발행하는 파이썬 기반 크롤링·자동화 파이프라인

---

## 1. 개요 (Overview)

`museum_newsletter` (프로젝트 Hermes)는 전 세계 유수의 미술관(메트로폴리탄, 루브르, 테이트, 국립중앙박물관 등) 공식 웹사이트에서 현재 진행 중이거나 예정된 전시(Exhibitions) 정보를 정기적으로 수집(Scraping)하고, Jinja2 기반의 세련된 HTML 이메일 템플릿으로 시각화하여 지정된 구독자들에게 자동 발송하는 **Python 뉴스레터 자동화 파이프라인**입니다.

비개발자도 쉽게 다른 PC로 마이그레이션하거나 배치 스케줄러를 등록할 수 있도록 배포 가이드와 윈도우 실행 파일(`run_newsletter.bat`)을 함께 포함하고 있습니다.

---

## 2. 핵심 목표 & 주요 특징

- **10대 글로벌 미술관 동시 수집**: Met, Tate, Louvre, National Gallery, V&A, LACMA, Whitney, Mori, 국립중앙박물관, Chicago 등 세계 주요 미술관 정보 크롤링.
- **객체지향 스크래퍼 추상화 (`BaseScraper`)**: 템플릿 메서드 패턴을 적용하여 새로운 미술관 크롤러를 쉽게 추가할 수 있는 확장성 보장.
- **안전망(Fail-safe) 메커니즘**:
  - 특정 미술관 사이트 구조 변경/네트워크 오류 발생 시 개별 실패 처리 후 나머지 미술관 정상 수집 진행.
  - SMTP 이메일 설정(`.env`) 미비 시 프로그램이 중단되지 않고 로컬 콘솔 미리보기 및 `preview.html` 디버깅 파일 자동 생성.
- **템플릿 분리 (Jinja2)**: 수집 로직과 시각적 이메일 HTML 디자인을 완벽히 분리하여 유지보수성 확보.
- **무중단 이사 및 자동화 지원**: `venv` 가상환경 독립성 제공 및 윈도우 작업 스케줄러(Task Scheduler) 연동용 배치 파일 제공.

---

## 3. 전체 시스템 아키텍처 & 데이터 흐름

```
[ 10대 미술관 웹사이트 ]
       │
       ▼ (HTTP GET / Requests & BeautifulSoup)
[ BaseScraper 서브클래스들 (scrapers/*.py) ]
       │
       ▼ Dict 반환: {"title", "date", "image_url", "link"}
[ main.py 파이프라인 수집기 ]
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
[ Jinja2 HTML 렌더러 ]           [ 디버깅 파일 저장 ]
(templates/template.py)          (preview.html 생성)
       │
       ▼ HTML 문자열 반환
[ NewsletterMailer (mailer.py) ]
       │
       ▼ (Gmail SMTP / TLS 587)
[ 구독자 이메일 수신함 ]
```

---

## 4. 폴더 & 주요 파일 구성

```
museum_newsletter/
├─ scrapers/                         # 미술관별 크롤링 모듈 디렉터리
│  ├─ __init__.py                    # 스크래퍼 클래스 패키지 익스포트
│  ├─ base.py                        # BaseScraper 추상 기반 클래스
│  ├─ met.py                         # 메트로폴리탄 미술관 스크래퍼
│  ├─ tate.py                        # 테이트 미술관 스크래퍼
│  ├─ louvre.py                      # 루브르 박물관 스크래퍼
│  ├─ national_gallery.py            # 내셔널 갤러리(런던) 스크래퍼
│  ├─ vam.py                         # 빅토리아 앨버트 박물관(V&A) 스크래퍼
│  ├─ lacma.py                       # LACMA 스크래퍼
│  ├─ whitney.py                     # 휘트니 미술관 스크래퍼
│  ├─ mori.py                        # 모리 미술관 스크래퍼
│  ├─ nmk.py                         # 국립중앙박물관 스크래퍼
│  ├─ chicago.py                     # 시카고 미술관 스크래퍼
│  └─ moma.py                        # MoMA 스크래퍼
├─ templates/                        # 이메일 HTML 템플릿 모듈
│  ├─ __init__.py                    # render_newsletter 노출
│  ├─ template.py                    # Jinja2 템플릿 렌더링 함수
│  └─ newsletter.html                # 뉴스레터 HTML 템플릿 (반응형/카드 디자인)
├─ tests/                            # Pytest 단위 테스트
│  └─ test_scrapers.py               # 스크래퍼 및 렌더러 테스트
├─ main.py                           # 전체 오케스트레이션 실행 메인 스크립트
├─ mailer.py                         # SMTP 기반 이메일 발송 클래스
├─ requirements.txt                  # Python 패키지 의존성 목록
├─ run_newsletter.bat                # 윈도우 작업 스케줄러용 배치 파일
├─ .env                              # 이메일 계정 및 수신자 환경변수 설정 파일
├─ MIGRATION_GUIDE.md                # 새 PC 마이그레이션 매뉴얼 (마크다운)
└─ 다른 PC로 이사 가는 방법 (매뉴얼).txt # 새 PC 마이그레이션 매뉴얼 (텍스트)
```

---

## 5. 주요 모듈 및 클래스 사양

### 5.1 스크래퍼 모듈 (`scrapers/`)

#### `BaseScraper` (`scrapers/base.py`)
모든 미술관 크롤러의 부모 클래스입니다.

```python
class BaseScraper(ABC):
    def __init__(self):
        self.museum_name = "Unknown"
        self.base_url = ""

    @abstractmethod
    def fetch_data(self) -> str:
        """웹페이지의 HTML 내용을 가져옵니다."""
        pass

    @abstractmethod
    def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
        """HTML에서 전시 정보 딕셔너리 리스트를 추출합니다."""
        pass

    def get_exhibitions(self) -> List[Dict[str, Any]]:
        """fetch_data 후 parse_data를 실행하는 템플릿 메서드"""
        html = self.fetch_data()
        return self.parse_data(html) if html else []
```

#### 표준 반환 데이터 규격 (Exhibition Data Structure)
`parse_data` 메소드는 반드시 아래 키를 갖는 딕셔너리 리스트를 반환합니다.
```python
[
    {
        "title": "전시 제목",
        "date": "전시 기간 (예: 2026.01.01 - 2026.06.30)",
        "image_url": "https://.../exhibition_thumb.jpg",
        "link": "https://.../exhibition_detail_page"
    },
    ...
]
```

---

### 5.2 메인 오케스트레이터 (`main.py`)

1. **환경변수 로드**: `python-dotenv`를 활용해 `.env` 수신자/발신자 정보 로딩.
2. **파이프라인 순회**: 10개 미술관 스크래퍼 객체를 순차 생성하고 `get_exhibitions()` 실행.
3. **오류 격리**: 하나의 미술관 수집 중 `Exception`이 발생하더라도 `try-except` 구문으로 차단하여 다른 미술관 정보 수집에 영향을 주지 않음.
4. **미리보기 파일 생성**: 수집 데이터로 `render_newsletter(data)` 호출 후 결과를 `preview.html`로 저장하여 검증 지원.
5. **발송 실행**: `NewsletterMailer.send_email()`을 호출하여 수신자 목록(`RECEIVER_EMAIL`)으로 메일 송신.

---

### 5.3 이메일 발송 모듈 (`mailer.py`)

- **클래스**: `NewsletterMailer`
- **프로토콜**: Gmail SMTP (`smtp.gmail.com`, Port 587, TLS)
- **환경 변수 목록**:
  - `SENDER_EMAIL`: 발신 Gmail 주소
  - `SENDER_PASSWORD`: Gmail 앱 비밀번호 (16자리)
  - `RECEIVER_EMAIL`: 수신자 이메일 목록 (쉼표로 구분하여 다중 지정 가능)
- **안전 fallback**: `SENDER_EMAIL` 미설정 시 발송을 취소하고 로컬 콘솔에 미리보기 텍스트를 출력하여 에러 방지.

---

## 6. 이메일 템플릿 (`templates/`)

- **엔진**: `Jinja2` (`Environment`, `FileSystemLoader`)
- **디자인 구조**:
  - 미술관 이름별 카테고리 헤더.
  - 전시별 대표 이미지 카드, 제목 링크, 전시 일정 표기.
  - 모바일 및 주요 이메일 클라이언트(Gmail, Outlook 등) 호환 모던 뷰티 스타일 반응형 CSS 적용.

---

## 7. 마이그레이션 & 실행 방법

### 7.1 환경 구축 및 실행
```powershell
# 1. venv 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
.\venv\Scripts\activate

# 3. 의존성 패키지 설치
pip install -r requirements.txt

# 4. 수동 실행 테스트
python main.py
```

### 7.2 `.env` 설정 예시
```env
SENDER_EMAIL=your_gmail_account@gmail.com
SENDER_PASSWORD=your_16_digit_app_password
RECEIVER_EMAIL=subscriber1@example.com,subscriber2@example.com
```

### 7.3 윈도우 작업 스케줄러 (자동화)
- `run_newsletter.bat` 파일은 스크립트 실행 경로로 자동 이동(`cd /d "%~dp0"`)한 후 가상환경을 켜고 `python main.py`를 실행하도록 작성되어 있습니다.
- 윈도우 **작업 스케줄러(Task Scheduler)**에 등록하여 `매주 월요일 오전 8:00`에 `run_newsletter.bat`가 실행되도록 설정하면 무인 자동 수집 파이프라인이 완성됩니다.

---

## 8. 테스트 및 확장 가이드

### 8.1 pytest 단위 테스트
```powershell
pytest
```
- `tests/test_scrapers.py`는 MoMA 스크래퍼 및 Jinja2 HTML 렌더러가 올바른 딕셔너리 구조와 HTML 노드를 출력하는지 검증합니다.

### 8.2 신규 미술관 스크래퍼 추가 방법 (3-Step)

1. `scrapers/`에 신규 파이썬 파일 생성 (예: `scrapers/guggenheim.py`)
2. `BaseScraper`를 상속받아 `fetch_data()` 및 `parse_data()` 구현
   ```python
   from .base import BaseScraper

   class GuggenheimScraper(BaseScraper):
       def __init__(self):
           super().__init__()
           self.museum_name = "Solomon R. Guggenheim Museum"
           self.base_url = "https://www.guggenheim.org/exhibitions"

       def fetch_data(self) -> str:
           # requests 혹은 fetch 로직
           ...

       def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
           # BeautifulSoup 파싱 로직
           ...
   ```
3. `scrapers/__init__.py` 등록 및 `main.py`의 `scraper_classes` 목록에 추가.

---

## 9. 재사용 가능한 패턴 (LLM & Developer Insights)

1. **템플릿 메서드 패턴 (Template Method Pattern)**:
   데이터 수집(`fetch_data`)과 파싱(`parse_data`)을 분리하고 상위 `BaseScraper`에서 템플릿 흐름(`get_exhibitions`)을 제어함으로써, 파싱 방식이 각기 다른 외부 미술관 사이트를 통일된 인터페이스로 다룰 수 있습니다.
2. **Fail-safe 파이프라인**:
   웹 크롤링 특성상 타겟 사이트의 DOM 구조 변경이나 일시적 다운이 자주 발생합니다. 모듈별 독립적 예외 처리와 로컬 HTML 미리보기 저장(`preview.html`) 기능은 파이프라인 전체가 마비되는 것을 막아줍니다.
3. **환경 의존성 격리 (Portable Batch Runner)**:
   배치 스크립트(`run_newsletter.bat`)에 `%~dp0` 스위치를 사용하여 상대 경로 기준으로 가상환경을 활성화하므로, 폴더 위치가 이동하더라도 작업 스케줄러 수정 없이 즉시 재배치 가능합니다.
