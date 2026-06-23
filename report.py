import streamlit as st
import pandas as pd
st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")
with st.sidebar:
    media = st.selectbox("매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("파일 업로드", type=["csv", "xlsx"])
if not f: st.info("👈 파일을 업로드해 주세요!"), st.stop()
try:
    if f.name.endswith('.xlsx'): df = pd.read_excel(f)
    else:
        raw = [l.decode('utf-8-sig', errors='ignore').split(',') for l in f.readlines()]
        t = next(i for i, r in enumerate(raw) if any('노출' in "".join(r) or '클릭' in "".join(r) for k in r))
        df = pd.DataFrame(raw[t+1:], columns=[x.strip() for x in raw[t]])
    df.columns = [str(c).strip() for c in df.columns]
    ki = next((c for c in df.columns if any(k in c for k in ['노출', 'Imp'])), df.columns[1])
    kc = next((c for c in df.columns if any(k in c for k in ['클릭', 'Click'])), df.columns[2])
    ks = next((c for c in df.columns if any(k in c for k in ['비용', '소진', 'Cost'])), df.columns[3])
    kg = df.columns[0]
    ni = int(pd.to_numeric(df[ki].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum())
    nc = int(pd.to_numeric(df[kc].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum())
    ns = int(pd.to_numeric(df[ks].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum())
    st.subheader("📝 RAW 데이터 확인")
    st.dataframe(df[[kg, ki, kc, ks]])
    st.subheader("📈 주요 지표")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("노출수", f"{ni:,}회"), c2.metric("클릭수", f"{nc:,}회"), c3.metric("CTR", f"{(nc/ni*100 if ni>0 else 0):.2f}%"), c4.metric("비용", f"{ns:,}원")
    if ni > 0: st.info(f"**AI 분석:** 총 {ni:,}회 노출되어 {nc:,}회 클릭되었으며, 평균 CPC는 {round(ns/nc) if nc>0 else 0:,}원입니다.")
except Exception as e: st.error(f"오류 발생: {e}")
    
