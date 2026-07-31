from datetime import datetime, timedelta, timezone
import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="Global Art Travel Dashboard", page_icon="🏛️", layout="wide"
)

# 대상 미술관 정보
MUSEUM_FILES = {
    "The Metropolitan Museum of Art": {
        "file": "met.html",
        "city": "뉴욕 (USA)",
        "badge": "🗽",
        "domain": "https://www.metmuseum.org",
        "utc_offset": -4,
        "map": "https://maps.google.com/?q=The+Metropolitan+Museum+of+Art",
    },
    "The Louvre": {
        "file": "louvre.html",
        "city": "파리 (France)",
        "badge": "🗼",
        "domain": "https://www.louvre.fr",
        "utc_offset": 2,
        "map": "https://maps.google.com/?q=Louvre+Museum",
    },
    "LACMA": {
        "file": "lacma.html",
        "city": "로스앤젤레스 (USA)",
        "badge": "🌴",
        "domain": "https://www.lacma.org",
        "utc_offset": -7,
        "map": "https://maps.google.com/?q=LACMA",
    },
    "Art Institute of Chicago": {
        "file": "chicago.html",
        "city": "시카고 (USA)",
        "badge": "🏙️",
        "domain": "https://www.artic.edu",
        "utc_offset": -5,
        "map": "https://maps.google.com/?q=Art+Institute+of+Chicago",
    },
    "Guggenheim Bilbao": {
        "file": "bilbao.html",
        "city": "빌바오 (Spain)",
        "badge": "🖼️",
        "domain": "https://www.guggenheim-bilbao.eus",
        "utc_offset": 2,
        "map": "https://maps.google.com/?q=Guggenheim+Museum+Bilbao",
    },
    "MMCA (국립현대미술관)": {
        "file": "mmca.html",
        "city": "서울 (Korea)",
        "badge": "🇰🇷",
        "domain": "https://www.mmca.go.kr",
        "utc_offset": 9,
        "map": "https://maps.google.com/?q=MMCA+Seoul",
    },
}


# 환율 정보 조회
@st.cache_data(ttl=3600)
def get_exchange_rates():
  try:
    res = requests.get(
        "https://open.er-api.com/v6/latest/USD", timeout=3
    ).json()
    krw = res["rates"]["KRW"]
    eur = krw / res["rates"]["EUR"]
    return {"USD": round(krw, 1), "EUR": round(eur, 1)}
  except:
    return {"USD": 1380.0, "EUR": 1500.0}


@st.cache_data(ttl=300)
def fetch_and_parse_exhibitions():
  all_exhibitions = []
  seen_titles = set()

  IGNORE_WORDS = [
      "looking for the met cloisters?",
      "current exhibitions",
      "featured",
      "recently opened",
      "closing soon",
      "all exhibitions are free with museum admission",
      "exhibitions and events - news and programming",
      "exhibitions",
  ]

  for museum_name, info in MUSEUM_FILES.items():
    urls = [
        f"https://raw.githubusercontent.com/nifi2025yes-gh/Art-newsletter/main/{info['file']}",
        f"https://raw.githubusercontent.com/nifi2025yes-gh/Art-newsletter/master/{info['file']}",
    ]

    res = None
    for url in urls:
      try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
          res = r
          break
      except:
        continue

    if res and res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")
      cards = soup.find_all(class_="exhibition-card")
      if not cards:
        cards = soup.find_all(["article", "div"])

      for card in cards:
        title_elem = card.find(class_="exhibition-title") or card.find(
            ["h2", "h3", "h4"]
        )
        date_elem = card.find(class_="exhibition-date") or card.find(
            ["p", "span"]
        )
        link_elem = card.find("a", class_="exhibition-link") or card.find("a")

        if title_elem and title_elem.text.strip():
          title = title_elem.text.strip()
          clean_title_check = title.lower()

          if (
              clean_title_check in IGNORE_WORDS
              or clean_title_check in seen_titles
          ):
            continue

          seen_titles.add(clean_title_check)

          date_text = (
              date_elem.text.replace("✦", "").strip()
              if date_elem
              else "일정 확인 필요"
          )

          link = info["domain"]
          if link_elem and link_elem.has_attr("href"):
            raw_href = link_elem["href"].strip()
            if raw_href.startswith("http"):
              link = raw_href
            elif raw_href.startswith("/"):
              link = info["domain"] + raw_href

          all_exhibitions.append({
              "도시/권역": f"{info['badge']} {info['city']}",
              "미술관": museum_name,
              "전시 제목": title,
              "전시 기간": date_text[:60],
              "공식 사이트": link,
              "구글 지도": info["map"],
          })

  return pd.DataFrame(all_exhibitions)


# --- 1. 대시보드 헤더 & 환율 위젯 ---
st.title("🏛️ GLOBAL ART TRAVEL COMMAND CENTER")
st.caption(
    "사령관 전용 글로벌 미술관 실시간 관제 및 여행 통합 모니터링 시스템"
)

rates = get_exchange_rates()
c1, c2, c3, c4 = st.columns(4)
c1.metric("💵 원/달러 (USD)", f"{rates['USD']} 원")
c2.metric("💶 원/유로 (EUR)", f"{rates['EUR']} 원")
c3.metric("✈️ 등록 미술관", "6개 주요 도시")
c4.metric("시스템 상태", "🟢 GitHub Live 정제 완료")

st.markdown("---")

# --- 2. 현지 시간 모니터링 위젯 ---
st.subheader("🌍 주요 미술관 도시 현지 시간")
time_cols = st.columns(4)

cities_info = [
    ("🇫🇷 파리 (루브르)", 2),
    ("🇺🇸 뉴욕 (Met)", -4),
    ("🇺🇸 시카고 (AIC)", -5),
    ("🇰🇷 서울 (국립현대)", 9),
]

now_utc = datetime.now(timezone.utc)

for idx, (city_name, offset) in enumerate(cities_info):
  city_time = now_utc + timedelta(hours=offset)
  time_cols[idx].metric(city_name, city_time.strftime("%m/%d %H:%M"))

st.markdown("---")

# --- 3. 데이터 파싱 & 표 시각화 ---
df = fetch_and_parse_exhibitions()

if not df.empty:
  st.sidebar.header("🔍 작전 필터")
  selected_cities = st.sidebar.multiselect(
      "도시 선택", options=df["도시/권역"].unique(), default=df["도시/권역"].unique()
  )
  search_keyword = st.sidebar.text_input("작가/전시 키워드 검색", "")

  filtered_df = df[df["도시/권역"].isin(selected_cities)]
  if search_keyword:
    filtered_df = filtered_df[
        filtered_df["전시 제목"].str.contains(search_keyword, case=False)
        | filtered_df["미술관"].str.contains(search_keyword, case=False)
    ]

  st.subheader(f"📌 중복 정제된 핵심 전시 리스트 (총 {len(filtered_df)}건)")

  st.dataframe(
      filtered_df,
      column_config={
          "공식 사이트": st.column_config.LinkColumn(
              "티켓/공식페이지", display_text="🎫 티켓/전시 안내"
          ),
          "구글 지도": st.column_config.LinkColumn(
              "위치 확인", display_text="📍 구글 지도 길찾기"
          ),
      },
      use_container_width=True,
      hide_index=True,
  )

  # --- 4. 여행 추천 동선 & 고급 블로그 원고 자동 생성기 ---
  st.markdown("---")
  st.subheader("🎯 대시보드 연동 스마트 작전 창")

  tab1, tab2, tab3 = st.tabs([
      "📝 고급 네이버 블로그 원고 자동 생성기",
      "🎯 2026 하반기 권역별 추천 동선",
      "📊 네이버 데이터랩 키워드 가이드",
  ])

  # [UPGRADED TAB] 고품질 네이버 블로그 원고 생성기
  with tab1:
    st.markdown("#### 🎨 고품격 미술 가이드형 블로그 원고 자동 생성")
    st.caption(
        "실시간 대시보드 데이터를 바탕으로, 네이버 검색 노출(SEO)과 인문학적"
        " 깊이를 갖춘 완성형 원고를 즉시 생성합니다."
    )

    exhibition_list = filtered_df["전시 제목"].tolist()
    selected_exhibition = st.selectbox("포스팅할 전시 선택", exhibition_list)

    if selected_exhibition:
      selected_row = filtered_df[
          filtered_df["전시 제목"] == selected_exhibition
      ].iloc[0]

      if st.button("✨ 고품격 블로그 원고 즉시 생성하기"):
        city_clean = (
            selected_row["도시/권역"]
            .split()[-1]
            .replace("(", "")
            .replace(")", "")
        )

        blog_content = f"""[2026 {city_clean} 여행] 예술과 삶이 만나는 순간 — {selected_row['미술관']} <{selected_row['전시 제목']}> 완벽 관람 가이드

안녕하세요, 예술과 클래식 여행을 사랑하는 블로그 이웃 여러분! 🎨

2026년 해외 여행을 준비하시며 '이번 여행에서는 어떤 예술적 영감을 얻을 수 있을까?' 설레는 마음으로 계획을 세우고 계시지 않나요?

오늘은 제가 실시간으로 운영하는 **글로벌 미술관 관제 대시보드**에서 포착한 가장 주목해야 할 2026년 필수 전시, 바로 **{selected_row['도시/권역']}의 {selected_row['미술관']}에서 열리는 <{selected_row['전시 제목']}>** 소식을 정성껏 정리해 드립니다.

---

🏛️ **[전시 핵심 요약 및 레이아웃]**

• **전시명:** {selected_row['전시 제목']}
• **개최 장소:** {selected_row['미술관']} ({selected_row['도시/권역']})
• **전시 일정:** {selected_row['전시 기간']}
• **공식 안내 및 예매:** {selected_row['공식 사이트']}

---

🖼️ **[왜 이 전시를 꼭 봐야 할까요? — 큐레이팅 포인트]**

세계적인 거장들의 숨결이 담긴 미술관은 언제나 우리에게 깊은 울림을 줍니다. 

이번 <{selected_row['전시 제목']}> 전시는 단순한 작품 감상을 넘어, 그 시대의 철학과 인간에 대한 따뜻한 시선을 관조할 수 있는 귀한 기회입니다. 

특히 {city_clean} 현지에서도 주목받고 있는 주요 기획전인 만큼, 미술에 관심이 깊으신 분들은 물론 처음 여행을 떠나시는 분들에게도 잊지 못할 삶의 정서적 풍요로움을 선사할 것입니다.

---

💡 **[실용적인 현지 관람 & 동선 꿀팁]**

1. **사전 예매 필수:** 세계 유명 미술관 특성상 현장 대기 줄이 길어질 수 있습니다. 아래 공식 사이트를 통해 미리 슬롯을 확보하세요.
   👉 [티켓 예매 및 공식 안내 페이지]({selected_row['공식 사이트']})

2. **스마트한 동선 계획:** 미술관 방문 후 주변 역사적 거리나 공원을 둘러보는 일정을 추천합니다. 아래 지도 링크를 활용해 동선을 구상해 보세요.
   👉 [구글 지도로 위치 및 동선 확인하기]({selected_row['구글 지도']})

---

이번 여행, 거장들의 일상이 녹아있는 작품들을 만나며 마음의 여유와 새로움을 채워보시는 것은 어떨까요? 

글로벌 미술관의 실시간 최신 소식은 계속해서 대시보드로 업데이트해 드리겠습니다. 도움이 되셨다면 **공감과 댓글, 이웃 추가** 부탁드립니다! ✨

#2026여행 #{city_clean}여행 #{selected_row['미술관'].replace(' ', '')} #{selected_row['전시 제목'].replace(' ', '')} #미술관여행 #클래식명화 #해외전시추천 #글로벌아트컴패스 #예술여행
"""
        st.success(
            "🎉 고품격 블로그 포스팅 원고 작성이 완료되었습니다! 아래 상자에서"
            " 복사하여 사용하세요."
        )
        st.text_area(
            "📋 생성된 원고 (클릭 후 Ctrl+A ➔ Ctrl+C 복사)",
            blog_content,
            height=450,
        )

  # [TAB 2] 추천 동선
  with tab2:
    st.info(
        "**[유럽 코스]** 파리 루브르 (미켈란젤로/로댕전) ➔ 스페인 구겐하임"
        " 빌바오\n\n**[미주 코스]** 뉴욕 Met/휘트니 ➔ 시카고 미술관 ➔ LA"
        " LACMA\n\n**[아시아 코스]** 서울 국립현대미술관 ➔ 도쿄 모리미술관"
    )

  # [TAB 3] 데이터랩 안내
  with tab3:
    st.write(
        "• **트렌드 키워드:** '2026 유럽여행', '미술관 추천', '파리 루브르"
        " 예약'\n• **활용법:** 대시보드의 실시간 데이터를 바탕으로 블로그를"
        " 작성하면, 검색 노출(SEO) 성능과 유저 신뢰도가 대폭 상승합니다."
    )

else:
  st.warning("데이터를 불러올 수 없습니다.")