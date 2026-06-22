import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 및 디자인 CSS 가미
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
    uploaded_file = st.file_saver = st.file_uploader(f"[{media_type}] 광고시스템에서 추출한 RAW 파일", type=["csv", "xlsx"])

# 3. 메인 화면 타이틀
st.markdown('<div class="main-title">📊 통합 매체 광고 성과 자동화 보고서 시스템</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">바이브코딩(Vibe Coding)으로 구축하는 대행사 멀티매체 리포팅 툴</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    # 파일 확장자에 따라 데이터 로드
    try:
        if uploaded_file.name.endswith('.csv'):
            # 네이버 SA 보고서는 cp949 혹은 utf-8-sig 인코딩인 경우가 많습니다.
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(uploaded_file)
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='cp949')

    # 데이터 정제 (총 소진 금액 미인식 에러 해결)
    # 금액/수치 컬럼에서 콤마(,)나 '원' 글자를 제거하고 숫자형으로 변환
    num_cols = ['노출수', '클릭수', '총비용', '총전환수', '총전환매출액']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 데이터가 정상 로드되었을 때 계산 진행
    if '총비용' in df.columns:
        total_spend = int(df['총비용'].sum())
        total_impressions = int(df['노출수'].sum()) if '노출수' in df.columns else 0
        total_clicks = int(df['클릭수'].sum()) if '클릭수' in df.columns else 0
        total_conversions = int(df['총전환수'].sum()) if '총전환수' in df.columns else 0
        
        # 4. 상단 대시보드 메트릭 카드 시각화 디지인
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

        # 5. 데이터 시각화 그래프 섹션 추가
        st.subheader("📈 캠페인별 주요 성과 시각화")
        graph_col1, graph_col2 = st.columns(2)
        
        with graph_col1:
            # 캠페인별 소진 금액 차트
            fig_spend = px.bar(df, x='캠페인', y='총비용', title='캠페인별 소진 금액 (원)', 
                               text_auto=',.0f', color='총비용', color_continuous_scale='Blues')
            fig_spend.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig_spend, use_container_width=True)
            
        with graph_col2:
            # 캠페인별 클릭수 및 전환수 비교 차트
            fig_perf = px.bar(df, x='캠페인', y=['클릭수', '총전환수'], title='캠페인별 클릭 및 전환 성과 비교',
                              barmode='group', color_discrete_sequence=['#38BDF8', '#34D399'])
            fig_perf.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_perf, use_container_width=True)

        # 6. 하단 데이터 테이블 및 AI 리포트 코멘트
        st.write("")
        st.subheader("📋 네이버 SA RAW 데이터 원본 (상위 5개 행)")
        st.dataframe(df.head(5), use_container_width=True)

        st.write("")
        st.subheader("💬 자동 생성된 AI 리포트 코멘트")
        
        # 간단한 데이터 기반 자동 코멘트 예시 생성
        top_campaign = df.loc[df['총비용'].idxmax()]['캠페인'] if not df.empty else "N/A"
        ai_comment = f"""매체에 기입될 코멘트 내용 수정:

- 금일 가장 많은 예산이 소진된 캠페인은 [{top_campaign}]입니다.
- 하루 예산 조정으로 효율 방어 진행 후 예산 소진 확인 완료되었습니다.
- 네이버 SA 당일 모니터링 및 소재 이상 무 확인되었습니다.
- 총 소진 금액 {total_spend:,}원 대비 총 {total_conversions:,}건의 전환이 기록되었습니다."""
        
        st.text_area(label="AI 분석 내용", value=ai_comment, height=150, label_visibility="collapsed")

    else:
        st.warning("업로드된 파일에서 '총비용' 컬럼을 찾을 수 없습니다. 파일 양식을 확인해주세요.")

else:
    # 파일이 아직 업로드되지 않았을 때 대기 화면 디자인
    st.info("💡 왼쪽 사이드바에서 광고 보고서 RAW 파일(CSV/Excel)을 업로드하시면 자동으로 대시보드가 생성됩니다.")
