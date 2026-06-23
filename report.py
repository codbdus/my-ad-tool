import streamlit as st
import pandas as pd
st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")
with st.sidebar:
    media = st.selectbox("광고 매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("RAW 파일 업로드", type=["csv", "xlsx"])
if not f:
    st.info("👈 왼쪽에서 파일을 업로드해 주세요!"), st.stop()
df = None
if f.name.endswith('.xlsx'): df = pd.read_excel(f)
else:
    for e in ['utf-8-sig', 'cp949', 'utf-8']:
        try:
            df = pd.read_csv(f, encoding=e)
            if df.shape[1] == 1 or 'Unnamed' in str(df.columns[0]):
                f.seek(0); df = pd.read_csv(f, encoding=e, sep=',', engine='python')
            if df.shape[1] <= 1:
                f.seek(0); df = pd.read_csv(f, encoding=e, sep='\t', engine='python')
            if not df.empty and df.shape[1] > 1: break
        except: continue
if df is None or df.empty: st.error("⚠️ 읽기 실패"), st.stop()
df.columns = [str(c).strip() for c in df.columns]
st.warning(f"📢 [진단] 컬럼명: {list(df.columns)}")
ki = next((c for c in df.columns if any(k in c for k in ['노출', 'Impressions', 'Imp'])), None)
kc = next((c for c in df.columns if any(k in c for k in ['클릭', 'Clicks'])), None)
ks = next((c for c in df.columns if any(k in c for k in ['비용', '광고비', '소진', '지출'])), None)
kg = next((c for c in df.columns if any(k in c for k in ['캠페인', 'Campaign', '상품', '그룹'])), df.columns[0])
ni = int(pd.to_numeric(df[ki].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()) if ki else 0
nc = int(pd.to_numeric(df[kc].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()) if kc else 0
ns = int(pd.to_numeric(df[ks].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()) if ks else 0
r = (nc / ni * 100) if ni > 0 else 0
p = (ns / nc) if nc > 0 else 0
st.subheader("📝 RAW 데이터 확인")
st.dataframe(df[[c for c in [kg, ki, kc, ks] if c in df.columns]], use_container_width=True)
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("총
