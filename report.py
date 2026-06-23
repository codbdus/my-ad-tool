import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="통합 매체 광고 보고서 자동화", layout="wide")

st.title("📊 통합 매체 광고 보고서 생성기")
st.caption("바이브코딩(Vibe Coding)으로 구축한 다중 매체 리포트 마스터")

# 1. 사이드바 - 파일 업로드 및 매체 선택
with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    media_type = st.selectbox(
        "업로드할 광고 매체를 선택하세요", 
        ["네이버 SA", "네이버 GFA", "구글", "메타(페이스북)", "카카오"]
    )
    
    uploaded_file = st.file_uploader(
        f"[{media_type}] 광고시스템에서 추출한 RAW 파일(CSV 또는 XLSX)을 올려주세요", 
        type=["csv", "xlsx"]
    )

# 2. 메인 화면 로직
if uploaded_file is not None:
    df = None
    file_name = uploaded_file.name
    
    # --- 인코딩 및 파일 확장자 예외 처리 (cp949 및 업로드 에러 방지) ---
    try:
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            # CSV 파일의 경우 여러 인코딩을 순서대로 시도하여 'cp949' 에러를 원천 차단합니다.
            encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']
            for encoding in encodings:
                try:
                    uploaded_file.seek(0) # 파일 포인터 리셋
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("지원하는 파일 인코жения(UTF-8, CP949 등)를 찾을 수 없습니다.")

        st.subheader(f"📝 {media_type} RAW 데이터 확인")
        
        # --- [매체별 핵심 지표 표준화 매핑 사전] ---
        column_mappings = {
            "네이버 SA": {
                "impressions": ['노출수', '노출 수'],
                "clicks": ['클릭수', '클릭 수'],
                "cost": ['총비용', '광고비', '비용', '총비용(VAT포함)', '광고비(VAT포함)']
            },
            "네이버 GFA": {
                "impressions": ['노출수', '노출 수'],
                "clicks": ['클릭수', '클릭 수'],
                "cost": ['소진액', '소진 금액', '광고비', '총비용']
            },
            "구글": {
                "impressions": ['노출수', '노출 수', 'Impressions', '노출'],
                "clicks": ['클릭수', '클릭 수', 'Clicks', '클릭'],
                "cost": ['비용', 'Cost', '광고비', '소진금액']
            },
            "메타(페이스북)": {
                "impressions": ['노출', 'Impressions', '노출수'],
                "clicks": ['링크 클릭', 'Clicks', '클릭수', '클릭'],
                "cost": ['지출 금액', 'Amount Spent', '광고비', '비용']
            },
            "카카오": {
                "impressions": ['노출수', '노출', 'Impressions'],
                "clicks": ['클릭수', '클릭', 'Clicks'],
                "cost": ['소진금액', '캐시소진액', '광고비', '비용']
            }
        }
        
        current_mapping = column_mappings[media_type]
        
        # 실제 데이터에서 매칭되는 컬럼 찾기
        found_imp_col = None
        found_clk_col = None
        found_cost_col = None
        
        for col in df.columns:
            cleaned_col = str(col).strip()
            if not found_imp_col and cleaned_col in current_mapping["impressions"]:
                found_imp_col = col
            if not found_clk_col and cleaned_col in current_mapping["clicks"]:
                found_clk_col = col
            if not found_cost_col and cleaned_col in current_mapping["cost"]:
                found_cost_col = col

        # 기준이 될 캠페인 컬럼 탐색
        found_camp_col = None
        for col in df.columns:
            if '캠페인' in str(col) or 'Campaign' in str(col):
                found_camp_col = col
                break
        if not found_camp_col:
            found_camp_col = df.columns[0]

        # --- 수치형 데이터 정제 함수 (쉼표 제거 및 문자를 숫자로 변경) ---
        def clean_numeric(series):
            return pd.to_numeric(series.astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

        if found_imp_col: df[found_imp_col] = clean_numeric(df[found_imp_col]).astype(int)
        if found_clk_col: df[found_clk_col] = clean_numeric(df[found_clk_col]).astype(int)
        if found_cost_col: df[found_cost_col] = clean_numeric(df[found_cost_col]).astype(int)

        # 필요한 컬럼만 추려 대시보드에 노출
        display_cols = [found_camp_col]
        if found_imp_col: display_cols.append(found_imp_col)
        if found_clk_col: display_cols.append(found_clk_col)
        if found_cost_col: display_cols.append(found_cost_col)
        
        st.dataframe(df[display_cols], use_container_width=True)
        
        # --- [종합 지표 계산] ---
        total_impressions = df[found_imp_col].sum() if found_imp_col else 0
        total_clicks = df[found_clk_col].sum() if found_clk_col else 0
        total_cost = df[found_cost_col].sum() if found_cost_col else 0
        
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
        
        st.markdown("---")
        st.subheader(f"📈 분석된 {media_type} 주요 지표 요약")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 노출수", f"{total_impressions:,} 회")
        col2.metric("총 클릭수", f"{total_clicks:,} 회")
        col3.metric("클릭률 (CTR)", f"{ctr:.2f} %")
        col4.metric("총 소진 금액", f"{total_cost:,} 원")
        
        # --- [엑셀 보고서 다운로드 기능] ---
        st.markdown("---")
        st.subheader("📥 정제된 분석 보고서 다운로드")
