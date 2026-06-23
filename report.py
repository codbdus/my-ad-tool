import streamlit as st
import pandas as pd

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    media = st.selectbox("광고 매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    uploaded_file = st.file_uploader("RAW 파일 업로드", type=["csv", "xlsx"])

if uploaded_file is None:
    st.info("👈 왼쪽에서 파일을 업로드해 주세요!")
    st.stop()

df = None
f_name = uploaded_file.name

if f_name.endswith('.xlsx'):
    df = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            if df.shape[1] == 1 or 'Unnamed' in str(df.columns[0]):
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=enc, sep=',', engine='python')
            if df.shape[1] <= 1:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=enc, sep='\t', engine='python')
            if not df.empty and df.shape[1] > 1: break
        except: continue

if df is None or df.empty:
    st.error("⚠️ 파일을 읽을 수 없습니다.")
    st.stop()

df.columns = [str(c).strip() for c in df.columns]

# 🔍 [시스템 진단 영역] 파일의 진짜 컬럼명을 대시보드 상단에 무조건 노출합니다.
st.warning(f"📢 [시스템 진단] 현재 인식된 파일의 컬럼명 목록: {list(df.columns)}")

# 핵심 컬럼 매칭 (검색 단어 대폭 확장)
f_imp = next((c for c in df.columns if any(k in c for k in ['노출수', '노출 수', '노출', 'Impressions', 'Imp'])), None)
f_clk = next((c for c in df.columns if any(k in c for k in ['클릭수', '클릭 수', '클릭', 'Clicks', '링크 클릭', '클릭 수(회)'])), None)
f_cost = next((c for c in df.columns if any(k in c for k in ['총비용', '광고비', '비용', '소진', '지출', '총비용(VAT포함)'])), None)
f_camp = next((c for c in df.columns if any(k in c for k in ['캠페인', 'Campaign', '광고상품', '광고그룹', '소재', '키워드'])), df.columns[0])

def to_num(series):
    if series is None: return pd.Series(0, index=df.index)
    return pd.to_numeric(series.astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0)

df_clean = df.copy()
if f_imp: df_clean[f_imp] = to_num(df[f_imp])
if f_
