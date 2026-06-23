import streamlit as st
import pandas as pd

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    media = st.selectbox("광고 매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    uploaded_file = st.file_uploader("RAW 파일 업로드", type=["csv", "xlsx"])

if not uploaded_file:
    st.info("👈 왼쪽에서 파일을 업로드해 주세요!")
    st.stop()

df = None
if uploaded_file.name.endswith('.xlsx'):
    df = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'cp949', 'utf-8']:
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
st.warning(f"📢 [진단] 컬럼명 목록: {list(df.columns)}")

# [해결 핵심] 변수 매칭 및 연산을 한 줄로 축소하여 짤림 원천 차단
f_imp = next((c for c in df.columns if any(k in c for k in ['노출', 'Impressions', 'Imp'])), None)
f_clk = next((c for c in df.columns if any(k in c for k in ['클릭', 'Clicks'])), None)
f_cost = next((c for c in df.columns if any(k in c for k in ['비용', '광고비', '소진', '지출', 'Cost'])), None)
f_camp = next((c for c in df.columns if any(k in c for k in ['캠페인', 'Campaign', '광고상품', '그룹', '키워드'])), df.columns[0])

# 숫자가 아닌 문자 제거 후 합산하는 안전한 인라인 연산
def parse_sum(col):
    if not col or col not in df.columns: return 0
    return int(pd.to_numeric(df[col].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum())

t_imp = parse_sum(f_imp)
t_clk = parse_sum(
