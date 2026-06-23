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
        f"[{media_type}] 광고시스템에서 추출한 RAW 파일(CSV)을 올려주세요", 
        type=["csv", "xlsx"]
    )

# 2. 메인 화면 로직
if uploaded_file is not None:
    try:
        df = None
        file_name = uploaded_file.name
        
        # 파일 확장자 및 인코딩 처리
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
        
        # 매체별 컬럼 매핑 사전
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
        
        # 컬
