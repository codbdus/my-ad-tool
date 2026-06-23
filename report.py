import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="통합 매체 광고 보고서 자동화", layout="wide")

st.title("📊 통합 매체 광고 보고서 생성기")
st.caption("바이브코딩(Vibe Coding)으로 구축한 다중 매체 리포트 마스터")

with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    media_type = st.selectbox(
        "업로드할 광고 매체를 선택하세요", 
        ["네이버 SA", "네이버 GFA", "구글", "메타(페이스북)", "카카오"]
    )
    uploaded_file = st.file_uploader(
        f"[{media_type}] 광고시스템에서 추출한 RAW 파일(CSV)을 올려주세요", 
        type=["csv", "xlsx"]
    )

if uploaded_file is not None:
    try:
        df = None
        file_name = uploaded_file.name
        
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("지원하는 파일 인코딩을 찾을 수 없습니다.")

        st.subheader(f"📝 {media_type} RAW 데이터 확인")
        
        # 깃허브 복사 오류 방지를 위해 딕셔너리 구조를 한 줄 단위로 명확하게 간소화했습니다.
        column_mappings = {}
        column_mappings["네이버 SA"] = {"impressions": ['노출수', '노출 수'], "clicks": ['클릭수', '클릭 수'], "cost": ['총비용', '광고비', '비용', '총비용(VAT포함)', '광고비(VAT포함)']}
        column_mappings["네이버 GFA"] = {"impressions": ['노출수', '노출 수'], "clicks": ['클릭수', '클릭 수'], "cost": ['소진액', '소진 금액', '광고비', '총비용']}
        column_mappings["구글"] = {"impressions": ['노출수', '노출 수', 'Impressions', '노출'], "clicks": ['클릭수', '클릭 수', 'Clicks', '클릭'], "cost": ['비용', 'Cost', '광고비', '소진금액']}
        column_mappings["메타(페이스북)"] = {"impressions": ['노출', 'Impressions', '노출수'], "clicks": ['링크 클릭', 'Clicks', '클릭수', '클릭'], "cost": ['지출 금액', 'Amount Spent', '광고비', '비용']}
        column_mappings["카카오"] = {"impressions": ['노출수', '노출', 'Impressions'], "clicks": ['클릭수', '클릭', 'Clicks'], "cost": ['소진금액', '캐시소진액', '광고비', '비용']}
        
        current_mapping = column_mappings[media_type]
        
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

        found_camp_col = None
        for col in df.columns:
            if '캠페인' in str(col) or 'Campaign' in str(col):
                found_camp_col = col
                break
        if not found_camp_col:
