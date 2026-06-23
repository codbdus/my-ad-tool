import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    media = st.selectbox("광고 매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("파일 업로드", type=["csv", "xlsx"])

if f:
    try:
        # 1. 파일 내용을 텍스트로 강제 변환
        if f.name.endswith('.xlsx'):
            df = pd.read_excel(f)
        else:
            content = f.read().decode('utf-8-sig', errors='ignore')
            lines = content.splitlines()
            start_idx = 0
            for i, line in enumerate(lines):
                if any(k in line for k in ['노출', '클릭', '비용']):
                    start_idx = i
                    break
            data = [line.split(',') for line in lines[start_idx:]]
            df = pd.DataFrame(data[1:], columns=[x.strip() for x in data[0]])

        # 2. 숫자만 남기기
        for col in df.columns:
            if col not in df.columns[0]:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0)
        
        # 3. 데이터 출력 및 합계
        st.subheader("📝 RAW 데이터 확인")
        st.dataframe(df.head(10), use_container_width=True)
        
        ki = next((c for c in df.columns if '노출' in c), df.columns[1])
        kc = next((c for c in df.columns if '클릭' in c), df.columns[2])
        ks = next((c for c in df.columns if any(k in c for k in ['비용', '소진', '지출'])), df.columns[3])
        
        ni, nc, ns = df[ki].sum(), df[kc].sum(), df[ks].sum()
        ctr = (nc / ni * 100) if ni > 0 else 0
        cpc = (ns / nc) if nc > 0 else 0
        
        # 4. 결과 요약
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("노출수", f"{int(ni):,}회")
        c2.metric("클릭수", f"{int(nc):,}회")
        c3.metric("CTR", f"{ctr:.2f}%")
        c4.metric("총 비용", f"{int(ns):,}원")
        
        # 5. AI 자동화 성과 분석 코멘트
        st.markdown("---")
        st.subheader("🤖 AI 자동화 성과 분석 코멘트")
        if ni > 0:
            comment = f"""
            **[{media} 광고 성과 요약]**
            - 총 노출 **{int(ni):,}회** 대비 **{int(nc):,}회**의 클릭이 발생하여 **{ctr:.2f}%**의 클릭률(CTR)을 기록했습니다.
            - 이번 광고 집행의 평균 클릭당 비용(CPC)은 **{int(cpc):,}원**입니다.
            - 총 **{int(ns):,}원**의 예산이 소진되었으며, 전반적인 광고 효율은 양호합니다.
            """
            st.info(comment)
        else:
            st.warning("분석할 수치 데이터가 부족합니다.")

    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
