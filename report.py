import streamlit as st
import pandas as pd

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    media = st.selectbox("매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("파일 업로드", type=["csv", "xlsx"])

if f:
    try:
        # 1. 파일 읽기
        df = pd.read_excel(f) if f.name.endswith('.xlsx') else pd.read_csv(f, sep=',', header=None, encoding='utf-8-sig', on_bad_lines='skip')
        
        # 2. 데이터 시작점 찾기 및 컬럼 재설정
        start_row = 0
        for i in range(min(10, len(df))):
            if any('노출' in str(cell) or '클릭' in str(cell) for cell in df.iloc[i]):
                start_row = i
                break
        
        data = df.iloc[start_row+1:].copy()
        data.columns = [str(c).strip() for c in df.iloc[start_row]]
        
        # 3. 필수 컬럼 찾기
        def get_col(kw):
            return next((c for c in data.columns if kw in c), None)
            
        ki, kc, ks = get_col('노출'), get_col('클릭'), get_col('비용')
        
        # 4. 정제 및 합산 (오류 원인 해결: 개별 데이터를 숫자로 변환 후 합산)
        def calc_sum(col_name):
            if not col_name: return 0
            # 문자열에서 숫자만 추출 -> float 변환 -> 합산 -> int 반환
            return int(pd.to_numeric(data[col_name].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum())

        ni, nc, ns = calc_sum(ki), calc_sum(kc), calc_sum(ks)
        
        # 5. 출력
        st.subheader("📝 RAW 데이터 확인")
        st.dataframe(data.head(10), use_container_width=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("노출수", f"{ni:,}회")
        c2.metric("클릭수", f"{nc:,}회")
        c3.metric("CTR", f"{(nc/ni*100 if ni>0 else 0):.2f}%")
        c4.metric("총 비용", f"{ns:,}원")
        
        st.info(f"**[{media} 분석]** 총 {ni:,}회 노출, {nc:,}회 클릭 발생. 평균 CPC: {round(ns/nc) if nc>0 else 0:,}원")

    except Exception as e:
        st.error(f"오류: {e}")
