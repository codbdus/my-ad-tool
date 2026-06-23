import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="네이버 SA 광고 보고서 자동화", layout="wide")

st.title("📊 통합 매체 광고 보고서 생성기")
st.caption("바이브코딩(Vibe Coding)으로 구축한 대행사 리포트 마스터")

# 1. 사이드바 - 파일 업로드
with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    media_type = st.selectbox("업로드할 광고 매체를 선택하세요", ["네이버 SA"])
    
    uploaded_file = st.file_uploader(
        f"[{media_type}] 광고시스템에서 추출한 RAW 파일(CSV)을 올려주세요", 
        type=["csv"]
    )

# 2. 메인 화면 로직
if uploaded_file is not None:
    try:
        # 네이버 SA 보고서는 보통 상단에 불필요한 행이 있거나 UTF-8/CP949 인코딩 문제가 있을 수 있음
        # 일반적인 네이버 보고서 형식에 맞춰 cp949로 읽어옵니다.
        df = pd.read_csv(uploaded_file, encoding="cp949")
        
        st.subheader(f"📝 {media_type} RAW 데이터 확인")
        
        # --- [광고비/비용 컬럼 자동 인식 및 전처리] ---
        # 네이버 SA에서 주로 쓰이는 비용 컬럼명 후보들
        cost_candidates = ['총비용', '광고비', '비용', '총비용(VAT포함)', '광고비(VAT포함)']
        found_cost_col = None
        
        for col in df.columns:
            if col.strip() in cost_candidates:
                found_cost_col = col
                break
        
        # 전처리: 숫자 형태가 아닌 것들을 숫자로 변경 (쉼표 제거 등)
        for col in ['노출수', '클릭수']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        if found_cost_col:
            # 금액 데이터에 포함된 쉼표(,) 제거 후 숫자로 변환
            df[found_cost_col] = df[found_cost_col].astype(str).str.replace(',', '').str.strip()
            df[found_cost_col] = pd.to_numeric(df[found_cost_col], errors='coerce').fillna(0).astype(int)
            
            # 노출수, 클릭수, 발견된 광고비 컬럼만 메인으로 보여주기
            display_cols = ['캠페인', '노출수', '클릭수', found_cost_col]
            available_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available_cols], use_container_width=True)
            
            # --- [데이터 요약 및 분석] ---
            total_impressions = df['노출수'].sum()
            total_clicks = df['클릭수'].sum()
            total_cost = df[found_cost_col].sum()
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
            
            st.markdown("---")
            st.subheader("📈 분석된 네이버 SA 주요 지표 요약")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("총 노출수", f"{total_impressions:,} 회")
            col2.metric("총 클릭수", f"{total_clicks:,} 회")
            col3.metric("클릭률 (CTR)", f"{ctr:.2f} %")
            col4.metric("총 소진 금액", f"{total_cost:,} 원")
            
            # --- [엑셀 보고서 다운로드 기능] ---
            st
