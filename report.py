import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="통합 광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    media = st.selectbox("광고 매체 선택", ["네이버 SA", "네이버 GFA", "구글", "메타(페이스북)", "카카오"])
    uploaded_file = st.file_uploader(f"[{media}] RAW 파일(CSV/XLSX)", type=["csv", "xlsx"])

if uploaded_file is None:
    st.info("👈 왼쪽에서 매체를 선택하고 파일을 업로드해 주세요!")
    st.stop()

# 파일 읽기 (인코딩 자동 파싱)
df = None
f_name = uploaded_file.name
if f_name.endswith('.xlsx'):
    df = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            break
        except:
            continue

if df is None:
    st.error("⚠️ 파일 형식을 확인할 수 없습니다.")
    st.stop()

st.subheader(f"📝 {media} RAW 데이터 확인")

# 매체별 컬럼 매핑 단순화
maps = {
    "네이버 SA": (['노출수', '노출 수'], ['클릭수', '클릭 수'], ['총비용', '광고비', '비용']),
    "네이버 GFA": (['노출수', '노출 수'], ['클릭수', '클릭 수'], ['소진액', '소진 금액', '광고비']),
    "구글": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['비용', 'Cost']),
    "메타(페이스북)": (['노출', 'Impressions'], ['링크 클릭', 'Clicks'], ['지출 금액', 'Amount Spent']),
    "카카오": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['소진금액', '캐시소진액'])
}

imp_keys, clk_keys, cost_keys = maps[media]
f_imp, f_clk, f_cost, f_camp = None, None, None, df.columns[0]

# 컬럼 자동 찾기
for c in df.columns:
    c_str = str(c).strip()
    if not f_imp and c_str in imp_keys: f_imp = c
    if not f_clk and c_str in clk_keys: f_clk = c
    if not f_cost and c_str in cost_keys: f_cost = c
    if '캠페인' in c_str or 'Campaign' in c_str: f_camp = c

# 숫자 정제 함수
def clean(s):
    return pd.to_numeric(s.astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

if f_imp: df[f_imp] = clean(df[f_imp]).astype(int)
if f_clk: df[f_clk] = clean(df
