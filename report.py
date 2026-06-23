import streamlit as st
import pandas as pd
st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")
with st.sidebar:
    media = st.selectbox("매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("파일", type=["csv", "xlsx"])
if not f: st.info("👈 파일을 업로드해 주세요!"), st.stop()
raw_lines = []
if f.name.endswith('.xlsx'):
    df = pd.read_excel(f)
else:
    for e in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            f.seek(0)
            raw_lines = [line.decode(e).strip() for line in f.readlines() if line.strip()]
            if raw_lines: break
        except: continue
    # 🎯 [핵심] 쉼표로 뭉친 문자열을 완전히 해체하여 강제로 완벽한 표(DataFrame) 생성
    parsed_data = [line.split(',') for line in raw_lines]
    t_idx = 0
    for i, row in enumerate(parsed_data):
        if any(k in "".join(row) for k in ['노출', '클릭', '비용', 'Impressions']): t_idx = i; break
    df = pd.DataFrame(parsed_data[t_idx+1:], columns=[x.strip() for x in parsed_data[t_idx]])
if df is None or df.empty: st.error("⚠️ 읽기 실패"), st.stop()
ki = next((c for c in df.columns if any(k in c for k in ['노출', 'Impressions', 'Imp'])), None)
kc = next((c for c in df.columns if any(k in c for k in ['클릭', 'Clicks'])), None)
ks = next((c for c in df.columns if any(k in c for k in ['비용', '광고비', '소진', '지출'])), None)
kg = next((c for c in df.columns if any(k in c for k in ['캠페인', 'Campaign', '상품', '그룹'])), df.columns[0])
ni = int(pd.to_numeric(df[ki].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()) if ki else 0
nc = int(pd.to_numeric(df[kc].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()) if kc else 0
ns = int(pd.to_numeric(df[ks].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()) if ks else 0
st.subheader("📝 RAW 데이터 확인")
st.dataframe(df[[c for c in [kg, ki, kc, ks] if c in df.columns]], use_container_width=True)
st.markdown("---")
if ni > 0:
    st.success(f"**[{media} 결과]** 노출: {ni:,}회 | 클릭: {nc:,}회 | CTR: {(nc/ni*100):.2f}% | 비용: {ns:,}원 | CPC: {round(ns/nc if nc>0 else 0):,}원")
else: st.warning("⚠️ 데이터 추출 실패. 파일 형식을 다시 확인해 주세요.")
    
