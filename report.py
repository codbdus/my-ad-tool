import streamlit as st
import pandas as pd

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

# 파일 업로드 사이드바
with st.sidebar:
    media = st.selectbox("광고 매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("RAW 파일 업로드", type=["csv", "xlsx"])

if not f:
    st.info("👈 왼쪽에서 파일을 업로드해 주세요!")
    st.stop()

# 파일 읽기 및 데이터 분리 (네이버 SA 대응)
try:
    if f.name.endswith('.xlsx'):
        df = pd.read_excel(f)
    else:
        # 데이터가 쉼표로 뭉친 경우를 대비하여 라인별 읽기
        df = pd.read_csv(f, sep=',', encoding='utf-8-sig', engine='python')
        if df.shape[1] == 1: # 쉼표 분리가 안 된 경우 재시도
            f.seek(0)
            df = pd.read_csv(f, sep='\t', encoding='utf-8-sig', engine='python')
except:
    st.error("파일을 읽는 도중 오류가 발생했습니다.")
    st.stop()

# 컬럼명 공백 제거
df.columns = [str(c).strip() for c in df.columns]

# 지표 매칭 (유연한 검색)
ki = next((c for c in df.columns if '노출' in c), df.columns[1])
kc = next((c for c in df.columns if '클릭' in c), df.columns[2])
ks = next((c for c in df.columns if any(k in c for k in ['비용', '소진', '지출'])), df.columns[3])
kg = df.columns[0]

# 숫자 변환 및 합계 계산
ni = int(pd.to_numeric(df[ki].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum())
nc = int(pd.to_numeric(df[kc].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum())
ns = int(pd.to_numeric(df[ks].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum())

# 화면 출력
st.subheader("📝 RAW 데이터 확인")
st.dataframe(df[[kg, ki, kc, ks]], use_container_width=True)

st.markdown("---")
st.subheader("📈 주요 지표 요약")
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 노출수", f"{ni:,}회")
col2.metric("총 클릭수", f"{nc:,}회")
col3.metric("클릭률 CTR", f"{(nc/ni*100 if ni>0 else 0):.2f}%")
col4.metric("총 소진 금액", f"{ns:,}원")

st.markdown("---")
st.subheader("🤖 AI 자동화 성과 분석 코멘트")
if ni > 0:
    st.info(f"**[{media} 성과 요약]**\n총 {ni:,}회 노출되어 {nc:,}회 클릭되었으며, 평균 CPC는 {round(ns/nc) if nc>0 else 0:,}원입니다.")
else:
    st.warning("데이터 합계가 0입니다. 파일 형식을 확인해주세요.")
