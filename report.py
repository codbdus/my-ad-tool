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
        f"[{media_type}] 광고시스템에서 추출한 RAW 파일(CSV/XLSX)을 올려주세요", 
        type=["csv", "xlsx"]
    )

if uploaded_file is None:
    st.info("👈 왼쪽 사이드바에서 광고 매체를 선택하고 RAW 데이터 파일을 업로드해 주세요!")
    st.stop()

# 꼬임의 주범이었던 큰 try 블록을 없애고 파일을 안전하게 먼저 읽습니다.
df = None
file_name = uploaded_file.name

if file_name.endswith('.xlsx'):
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
else:
    for encoding in ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=encoding)
            break
        except:
            continue

if df is None:
    st.error("⚠️ 파일 인코딩을 인식할 수 없습니다. 올바른 CSV 또는 XLSX 파일인지 확인해주세요.")
    st.stop()

st.subheader(f"📝 {media_type} RAW 데이터 확인")

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
    if '캠페인' in str(col
