import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")
st.title("📊 광고 보고서")
with st.sidebar:
    f = st.file_uploader("파일 업로드", type=["csv", "xlsx"])
if not f: st.stop()
try:
    if f.name.endswith('.xlsx'): df = pd.read_excel(f)
    else: df = pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
    df.columns = [str(c).strip() for c in df.columns]
    # 안전한 컬럼 선택: 첫 번째 컬럼이 없으면 에러 방지
    c_list = list(df.columns)
    ki = next((c for c in c_list if '노출' in c), c_list[0] if len(c_list)>0 else None)
    kc = next((c for c in c_list if '클릭' in c), c_list[0] if len(c_list)>0 else None)
    ks = next((c for c in c_list if any(k in c for k in ['비용','소진'])), c_list[0] if len(c_list)>0 else None)
    st.dataframe(df)
    ni = int(pd.to_numeric(df[ki].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()) if ki else 0
    nc = int(pd.to_numeric(df[kc].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()) if kc else 0
    ns = int(pd.to_numeric(df[ks].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()) if ks else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("노출", f"{ni:,}회"), c2.metric("클릭", f"{nc:,}회"), c3.metric("비용", f"{ns:,}원")
except Exception as e: st.error(f"오류: {e}")
