import streamlit as st
import pandas as pd

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    media = st.selectbox("광고 매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("RAW 파일 업로드", type=["csv", "xlsx"])

if f:
    try:
        # 1. 데이터 파싱 (안정적인 데이터 변환)
        if f.name.endswith('.xlsx'):
            df_raw = pd.read_excel(f)
        else:
            df_raw = pd.read_csv(f, sep=',', header=None, encoding='utf-8-sig', on_bad_lines='skip')
        
        # 데이터 시작점 찾기 (컬럼명이 포함된 행까지 건너뛰기)
        start_row = 0
        for i in range(min(15, len(df_raw))):
            if any('노출' in str(cell) or '클릭' in str(cell) for cell in df_raw.iloc[i]):
                start_row = i
                break
        
        df = df_raw.iloc[start_row+1:].copy()
        df.columns = [str(c).strip() for c in df_raw.iloc[start_row]]
        
        # 2. 필수 지표 추출
        def get_val(kw):
            col = next((c for c in df.columns if kw in c), None)
            if col:
                return pd.to_numeric(df[col].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum()
            return 0

        ni, nc, ns = int(get_val('노출')), int(get_val('클릭')), int(get_val('비용'))
        ctr = (nc / ni * 100) if ni > 0 else 0
        cpc = (ns / nc) if nc > 0 else 0

        # 3. 화면 구성
        st.subheader("📝 RAW 데이터 확인")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("📈 주요 지표 요약")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("총 노출수", f"{ni:,}회")
        c2.metric("총 클릭수", f"{nc:,}회")
        c3.metric("클릭률(CTR)", f"{ctr:.2f}%")
        c4.metric("총 소진비용", f"{ns:,}원")

        st.markdown("---")
        st.subheader("🤖 AI 성과 분석 코멘트")
        if ni > 0:
            st.info(f"**[{media} 광고 성과 분석]**\n\n"
                    f"이번 기간 동안 총 **{ni:,}회** 노출되어 **{nc:,}회**의 클릭이 발생했습니다. "
                    f"광고 효율(CTR)은 **{ctr:.2f}%**이며, 평균 클릭당 비용(CPC)은 **{round(cpc):,}원**으로 확인됩니다. "
                    f"총 예산은 **{ns:,}원**이 소진되었습니다.")
        else:
            st.warning("데이터 합계가 0입니다. 파일 내 컬럼명을 확인해 주세요.")

    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
