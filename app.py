import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="Global Art Travel Dashboard",
    page_icon="🏛️",
    layout="wide"
)

# 깃허브 Raw 데이터 기본 URL (사령관님의 계정과 저장소)
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/nifi2025yes-gh/Art-newsletter/main/"

# 대상 미술관 파일 목록 및 정보
MUSEUM_FILES = {
    "The Metropolitan Museum of Art": {"file": "met.html", "city": "뉴욕 (USA)", "badge": "🗽"},
    "The Louvre": {"file": "louvre.html", "city": "파리 (France)", "badge": "🗼"},
    "LACMA": {"file": "lacma.html", "city": "로스앤젤레스 (USA)", "badge": "🌴"},
    "Art Institute of Chicago": {"file": "chicago.html", "city": "시카고 (USA)", "badge": "🏙️"},
    "Guggenheim Bilbao": {"file": "bilbao.html", "city": "빌바오 (Spain)", "badge": "🖼️"},
    "MMCA (국립현대미술관)": {"file": "mmca.html", "city": "서울 (Korea)", "badge": "🇰🇷"},
}

@st.cache_data(ttl=600)  # 10분간 캐시 유지
def fetch_and_parse_exhibitions():
    """깃허브의 HTML 파일들을 파싱하여 데이터프레임으로 변환하는 함수"""
    all_exhibitions = []
    
    for museum_name, info in MUSEUM_FILES.items():
        url = GITHUB_RAW_BASE + info["file"]
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # exhibition-card 구조 파싱
                cards = soup.find_all(class_='exhibition-card')
                
                for card in cards:
                    title_elem = card.find(class_='exhibition-title')
                    date_elem = card.find(class_='exhibition-date')
                    link_elem = card.find('a', class_='exhibition-link')
                    img_elem = card.find(class_='exhibition-img')
                    
                    title = title_elem.text.strip() if title_elem else "제목 없음"
                    date_text = date_elem.text.replace('✦', '').strip() if date_elem else "일정 정보 없음"
                    link = link_elem['href'] if link_elem and link_elem.has_attr('href') else "#"
                    
                    all_exhibitions.append({
                        "도시/권역": f"{info['badge']} {info['city']}",
                        "미술관": museum_name,
                        "전시 제목": title,
                        "전시 기간": date_text,
                        "상세 링크": link
                    })
        except Exception as e:
            continue
            
    return pd.DataFrame(all_exhibitions)

# --- Header ---
st.title("🌐 GLOBAL ART TRAVEL DASHBOARD")
st.caption("사령관님의 GitHub 'Art-newsletter' 저장소와 실시간 연동된 미술관 관제판입니다.")
st.markdown("---")

# 데이터 로딩
with st.spinner("깃허브에서 최신 전시 데이터를 동기화하는 중..."):
    df = fetch_and_parse_exhibitions()

if not df.empty:
    # 2. Top Metric Cards (핵심 요약)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("연동된 주요 미술관", f"{df['미술관'].nunique()} 개소")
    col2.metric("총 수집된 전시 수", f"{len(df)} 건")
    col3.metric("커버리지 도시", f"{df['도시/권역'].nunique()} 개 도시")
    col4.metric("데이터 상태", "🟢 GitHub Live 연동")

    st.markdown("---")

    # 3. 도시 및 미술관 필터링 (Sidebar)
    st.sidebar.header("🔍 전시 검색 및 필터")
    selected_cities = st.sidebar.multiselect(
        "도시 선택", 
        options=df["도시/권역"].unique(),
        default=df["도시/권역"].unique()
    )
    
    search_keyword = st.sidebar.text_input("작가 또는 전시 키워드 검색", "")

    # 데이터 필터링 적용
    filtered_df = df[df["도시/권역"].isin(selected_cities)]
    if search_keyword:
        filtered_df = filtered_df[
            filtered_df["전시 제목"].str.contains(search_keyword, case=False) |
            filtered_df["미술관"].str.contains(search_keyword, case=False)
        ]

    # 4. 메인 데이터 테이블 시각화
    st.subheader("🏛️ 도시별 전시 현황 목록")
    
    # 링크를 클릭 가능한 버튼/표 형태로 제공
    st.dataframe(
        filtered_df,
        column_config={
            "상세 링크": st.column_config.LinkColumn("공식 페이지 바로가기"),
        },
        use_container_width=True,
        hide_index=True
    )

    # 5. 하단 2026 하반기 동선 제안
    st.markdown("---")
    st.subheader("🎯 보좌관 추천: 2026 하반기 여행 동선")
    
    tab1, tab2, tab3 = st.tabs(["🇺🇸 미주 코스 (뉴욕/시카고)", "🇪🇺 유럽 코스 (파리/빌바오)", "🇰🇷 아시아 코스 (서울)"])
    
    with tab1:
        st.write("**추천 일정:** 2026년 8월 ~ 10월")
        st.info("The Metropolitan Museum of Art ➔ Whitney Museum ➔ Art Institute of Chicago")
    with tab2:
        st.write("**추천 일정:** 2026년 9월 ~ 11월")
        st.info("The Louvre (파리) ➔ Guggenheim Bilbao (스페인)")
    with tab3:
        st.write("**추천 일정:** 상시")
        st.info("국립현대미술관(MMCA) 및 국립중앙박물관 기획전 연계")

else:
    st.warning("깃허브에서 데이터를 불러올 수 없습니다. URL 및 파일명을 확인해 주세요.")
