import streamlit as st
import pandas as pd

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    media = st.selectbox("매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("파일 업로드", type=["csv", "xlsx"])

if not f:
    st.info("👈 왼쪽 파일을 업로드해 주세요!")
    st.stop()

try:
    # 1. 파일 읽기 시도
    if f.name.endswith('.xlsx'):
        df_raw = pd.read_excel(f)
    else:
        # 쉼표로 분리된 CSV 파일을 안전하게 읽기
        df_raw = pd.read_csv(f, sep=',', header=None, encoding='utf-8-sig', on_bad_lines='skip')

    # 2. 데이터 시작점 찾기 (10줄 이내에서 '노출' 또는 '클릭'이 포함된 행 찾기)
    start_row = 0
    for i in range(min(10, len(df_raw))):
        if any('노출' in str(cell) or '클릭' in str(cell) for cell in df_raw.iloc[i]):
            start_row = i
            break
    
    # 3. 데이터 재구성
    df = df_raw.iloc[start_row+1:].copy()
    df.columns = [str(c).strip() for c in df_raw.iloc[start_row]]
    
    # 4. 필수 지표 매칭 (오류 방지 위해 인덱스 대신 이름으로 찾기)
    def find_col(k):
        return next((c for c in df.columns if k in c), None)
    
    ki, kc, ks = find_col('노출'), find_col('클릭'), find_col('비용')
    
    # 5. 수치 데이터 정제
    def clean(col):
        if not col: return 0
        return pd.to_numeric(df[col].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0)

    ni, nc, ns = int(clean(ki).sum()), int(clean(kc).sum()), int(clean(ks).sum())

    # 6. 화면 출력
    st.subheader("📝 RAW 데이터 확인")
    st.dataframe(df.head(10), use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("노출수", f"{ni:,}회")
    col2.metric("클릭수", f"{nc:,}회")
    col3.metric("CTR", f"{(nc/ni*100 if ni>0 else 0):.2f}%")
    col4.metric("총 비용", f"{ns:,}원")
    
    if ni > 0:
        st.info(f"**[{media} 분석]** 총 {ni:,}회 노출, {nc:,}회 클릭 발생. 평균 CPC: {round(ns/nc) if nc>0 else 0:,}원")

except Exception as e:
    st.error(f"데이터 처리 오류: {e}. 파일 형식이 맞는지 확인해주세요.")
