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
if uploaded_file.name.endswith('.xlsx'):
    df = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            # 쉼표로 한 열에 뭉친 네이버 SA 파일 강제 분리
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

# 핵심 컬럼 자동 매칭
f_imp = next((c for c in df.columns if any(k in c for k in ['노출수', '노출 수', '노출', 'Impressions'])), None)
f_clk = next((c for c in df.columns if any(k in c for k in ['클릭수', '클릭 수', '클릭', 'Clicks', '링크 클릭'])), None)
f_cost = next((c for c in df.columns if any(k in c for k in ['총비용', '광고비', '비용', '소진', '지출'])), None)
f_camp = next((c for c in df.columns if any(k in c for k in ['캠페인', 'Campaign', '광고상품', '광고그룹'])), df.columns[0])

def to_num(series):
    if series is None: return pd.Series(0, index=df.index)
    return pd.to_numeric(series.astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0)

df_clean = df.copy()
if f_imp: df_clean[f_imp] = to_num(df[f_imp])
if f_clk: df_clean[f_clk] = to_num(df[f_clk])
if f_cost: df_clean[f_cost] = to_num(df[f_cost])

st.subheader(f"📝 {media} RAW 데이터 확인")
st.dataframe(df[[c for c in [f_camp, f_imp, f_clk, f_cost] if c and c in df.columns]], use_container_width=True)

t_imp = int(df_clean[f_imp].sum()) if f_imp else 0
t_clk = int(df_clean[f_clk].sum()) if f_clk else 0
t_cost = int(df_clean[f_cost].sum()) if f_cost else 0
ctr = (t_clk / t_imp * 100) if t_imp > 0 else 0
cpc = (t_cost / t_clk) if t_clk > 0 else 0

st.markdown("---")
st.subheader(f"📈 {media} 주요 지표 요약")
c1
