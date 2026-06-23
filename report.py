import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    list_m = ["네이버 SA", "네이버 GFA", "구글", "메타(페이스북)", "카카오"]
    media = st.selectbox("광고 매체 선택", list_m)
    uploaded_file = st.file_uploader(
        f"[{media}] RAW 파일", 
        type=["csv", "xlsx"]
    )

if uploaded_file is None:
    st.info("👈 왼쪽에서 매체를 선택하고 파일을 업로드해 주세요!")
    st.stop()

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

maps = {
    "네이버 SA": (['노출수', '노출 수'], ['클릭수', '클릭 수'], ['총비용', '광고비', '비용', '총비용(VAT포함)', '광고비(VAT포함)']),
    "네이버 GFA": (['노출수', '노출 수'], ['클릭수', '클릭 수'], ['소진액', '소진 금액', '광고비']),
    "구글": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['비용', 'Cost']),
    "메타(페이스북)": (['노출', 'Impressions'], ['링크 클릭', 'Clicks'], ['지출 금액', 'Amount Spent']),
    "카카오": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['소진금액', '캐시소진액'])
}

imp_keys, clk_keys, cost_keys = maps[media]
f_imp, f_clk, f_cost, f_camp = None, None, None, df.columns[0]

for c in df.columns:
    c_str = str(c).strip()
    if not f_imp and c_str in imp_keys:
        f_imp = c
    if not f_clk and c_str in clk_keys:
        f_clk = c
    if not f_cost and c_str in cost_keys:
        f_cost = c
    if '캠페인' in c_str or 'Campaign' in c_str:
        f_camp = c

# 데이터 전처리 오류 철저하게 방어 (숫자가 아닌 모든 문자/공백 제거)
def clean(s):
    if s is None:
        return pd.Series(0, index=df.index)
    # 정규식을 사용하여 숫자와 마이너스(-) 부호가 아닌 모든 문자(한글, 공백, 콤마 등)를 강제 제거
    s_clean = s.astype(str).str.replace(r'[^\d\-]', '', regex=True).str.strip()
    # 빈 값인 경우 0으로 치환 후 수치화
    s_clean = s_clean.replace('', '0')
    return pd.to_numeric(s_clean, errors='coerce').fillna(0)

if f_imp:
    df[f_imp] = clean(df[f_imp]).astype(int)
if f_clk:
    df[f_clk] = clean(df[f_clk]).astype(int)
if f_cost:
    df[f_cost]
