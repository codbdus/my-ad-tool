import streamlit as st
import pandas as pd
st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")
with st.sidebar:
    media = st.selectbox("매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("파일", type=["csv", "xlsx"])
if not f: st.info("👈 파일을 업로드해 주세요!"), st.stop()
raw = pd.read_excel(f) if f.name.endswith('.xlsx') else None
if raw is None:
    for e in ['utf-8-sig', 'cp949', 'utf-8']:
        try: raw = pd.read_csv(f, encoding=e, sep=None, engine='python'); break
        except: continue
if raw is None or raw.empty: st.error("⚠️ 읽기 실패"), st.stop()
# 상단 설명줄 자동 스킵 및 진짜 헤더 행 찾기
t_idx = 0
for i in range(min(10, len(raw))):
    row_s = "".join(raw.iloc[i].astype(str))
    if any(k in row_s for k in ['노출', '클릭', '비용', 'Impressions', 'Clicks']): t_idx = i; break
df = raw.iloc[t_idx+1:].copy() if t_idx > 0 else raw.copy()
df.columns = [str(x).strip() for x in (raw.iloc[t_idx] if t_idx > 0 else raw.columns)]
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
if ni > 0: st.success(f"**[{media} 결과]** 노출: {ni:,}회 | 클릭: {nc:,}회 | CTR: {(nc/ni*100):.2f}% | 비용: {ns:,}원 | CPC: {round(ns/nc if nc>0 else 0):,}원")
else: st.warning("⚠️ 합산 실패. 상단 표의 컬럼명을 확인하세요.")
