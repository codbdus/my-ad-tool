import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 및 디자인 CSS 적용
st.set_page_config(page_title="통합 매체 광고 성과 자동화 보고서", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 30px; font-weight: bold; color: #1E293B; margin-bottom: 5px; }
    .sub-title { font-size: 14px; color: #64748B; margin-bottom: 30px; }
    .metric-box { background-color: #F8FAFC; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; text-align: center; }
    .metric-label { font-size: 13px; color: #64748B; font-weight: 500; }
    .metric-value { font-size: 22px; color: #0F172A; font-weight: bold; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# 2. 사이드바 - 파일 업로드 영역
with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    media_type = st.selectbox("업로드할 광고 매체를 선택하세요", ["네이버 SA", "기타 매체"])
    uploaded_file = st.file_uploader(f"[{media_type}] 광고시스템에서 추출한 RAW 파일", type=["csv", "xlsx"])

# 3. 메인 화면 타이틀
st.markdown('<div class="main-title">📊 통합 매체 광고 성과 자동화 보고서 시스템</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">바이브코딩(Vibe Coding)으로 구축하는 대행사 멀티매체 리포팅 툴</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    # [에러 방지] 인코딩 문제를 방지하기 위해 예외 처리하며 데이터 로드
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(uploaded_file)
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='cp949')

    # 모든 컬럼명의 양끝 공백 제거
    df.columns = [str(col).strip() for col in df.columns]
    
    # [에러 해결 ①] 네이버 SA 파일 상단에 빈 행이나 요약 정보 행이 끼어있을 경우 진짜 헤더행 찾기
    if '총비용' not in df.columns and '캠페인' not in df.columns and '비
