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
    # 인코딩 문제를 방지하기 위해 예외 처리하며 데이터 로드
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(uploaded_file)
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='cp949')

    # 모든 컬럼명의 양끝 공백 제거
    df.columns = [str(col).strip() for col in df.columns]
    
    # [수정된 부분] 안전하게 리스트 형태로 컬럼 포함 여부 체크
    required_keywords = ['총비용', '캠페인', '비용', '광고비']
    has_keyword = any(k in df.columns for k in required_keywords)
    
    if not has_keyword:
        for i in range(min(10, len(df))):  # 상위 10개 행 안에서 검색
            row_str = df.iloc[i].astype(str).str.strip()
            if row_str.str.contains('총비용|캠페인|비용|광고비').any():
                df.columns = [str(c).strip() for c in df.iloc[i]]
                df = df.iloc[i+1:].reset_index(drop=True)
                break

    # 매체 보고서 양식에 따른 다각도 컬럼명 표준화 (동의어 매칭)
    column_mapping = {
        '비용': '총비용',
        '광고비': '총비용',
        '소진금액': '총비용',
        '소진액': '총비용',
        '클릭': '클릭수',
        '노출': '노출수',
        '전환수': '총전환수',
        '전환': '총전환수',
        '전환매출액': '총전환매출액'
    }
    df.rename(columns=column_mapping, inplace=True)

    # 데이터 내 '캠페인' 열이 존재하지 않는 경우 첫 번째 열을 캠페인으로 간주
    if '캠페인' not in df.columns and len(df.columns) > 0:
        df.rename(columns={df.columns[0]: '캠페인'}, inplace=True)

    # 문자열 데이터('123,456원')를 숫자로 변환
    num_cols = ['노출수', '클릭수', '총비용', '총전환수', '총전환매출액']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 필수 통계 지표 계산
    if '총비용' in df.columns:
        total_spend = int(df['총비용'].sum())
        total_impressions = int(df['노출수'].sum()) if '노출수' in df.columns else 0
        total_clicks = int(df['클릭수'].sum()) if '클릭수' in df.columns else 0
        total_conversions = int(df['총전환수'].sum()) if '총전환수' in df.columns else 0
        
        # 4. 상단 대시보드 메트릭 디자인 생성
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-box"><div class="metric-label">💵 총 소진 금액</div><div class="metric-value">{total_spend:,} 원</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><div class="metric-label">👁️ 총 노출수</div><div class="metric-value">{total_impressions:,} 회</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><div class="metric-label">🖱️ 총 클릭수</div><div class="metric-value">{total_clicks:,} 회</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-box"><div class="metric-label">🎯 총 전환수</div><div class="metric-value">{total_conversions:,} 건</div></div>', unsafe_allow_html=True)

        st.write("")
        st.write("")

        # 5. 데이터 시각화 그래프 섹션 (Plotly 적용)
        st.subheader("📈 캠페인별 주요 성과 시각화")
        graph_col1, graph_col2 = st.columns(2)
        
        if '캠페인' in df.columns and len(df) > 0:
            with graph_col1:
                fig_spend = px.bar(df, x='캠페인', y='총비용', title='캠페인별 소진 금액 (원)', 
                                   text_auto=',.0f', color='총비용', color_continuous_scale='Blues')
                fig_spend.update_layout(xaxis_tickangle=-45, showlegend=False)
                st.plotly_chart(fig_spend, use_container_width=True)
