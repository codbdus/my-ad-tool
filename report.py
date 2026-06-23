import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 통합 매체 광고 보고서")

f = st.file_uploader("파일 업로드", type=["csv", "xlsx"])
if f:
    try:
        df = pd.read_excel(f) if f.name.endswith('.xlsx') else pd.read_csv(f, sep=',', header=0, encoding='utf-8-sig', on_bad_lines='skip')
        df.columns = [str(c).strip() for c in df.columns]
        # 숫자 컬럼 찾기 및 합산
        vals = {c: pd.to_numeric(df[c].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum() for c in df.columns}
        
        st.dataframe(df.head(5))
        c1, c2, c3 = st.columns(3)
        c1.metric("노출", f"{int(vals.get(next((c for c in df.columns if '노출' in c), df.columns[1]), 0)):,}")
        c2.metric("클릭", f"{int(vals.get(next((c for c in df.columns if '클릭' in c), df.columns[2]), 0)):,}")
        c3.metric("비용", f"{int(vals.get(next((c for c in df.columns if '비용' in c), df.columns[3]), 0)):,}")
        
        st.info("AI 분석: 데이터 합산이 완료되었습니다.")
    except Exception as e:
        st.warning(f"데이터 확인 중: {e}")
