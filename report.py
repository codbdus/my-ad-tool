import streamlit as st
import pandas as pd

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    media = st.selectbox("매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("파일 업로드", type=["csv", "xlsx"])

if f:
    # 1. 파일 안전 읽기 (오류 방지)
    try:
        df = pd.read_excel(f) if f.name.endswith('.xlsx') else pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        
        # 2. 필수 컬럼 찾기 (한글 키워드 기준)
        ki = next((c for c in df.columns if '노출' in c), df.columns[1])
        kc = next((c for c in df.columns if '클릭' in c), df.columns[2])
        ks = next((c for c in df.columns if any(k in c for k in ['비용', '소진', '지출'])), df.columns[3])
        
        # 3. 데이터 숫자 정제 및 합산 (안정적 연산)
        def to_num(col): return pd.to_numeric(df[col].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0)
        ni, nc, ns = int(to_num(ki).sum()), int(to_num(kc).sum()), int(to_num(ks).sum())
        
        # 4. 화면 구성 (오류 방지 위해 단순화)
        st.subheader("📝 RAW 데이터 확인")
        st.dataframe(df.head(10), use_container_width=True)
        
        st.subheader("📈 주요 지표 요약")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("노출수", f"{ni:,}회")
        c2.metric("클릭수", f"{nc:,}회")
        c3.metric("CTR", f"{(nc/ni*100 if ni>0 else 0):.2f}%")
        c4.metric("총 비용", f"{ns:,}원")
        
        st.subheader("🤖 AI 자동화 성과 분석 코멘트")
        if ni > 0:
            st.info(f"**[{media} 성과 분석]** 총 {ni:,}회 노출 중 {nc:,}회 클릭이 발생하였습니다. 평균 CPC는 {round(ns/nc) if nc>0 else 0:,}원입니다.")
        else:
            st.warning("데이터 합계 오류: 컬럼을 다시 확인하세요.")
            
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
