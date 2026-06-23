import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    f = st.file_uploader("파일 업로드", type=["csv", "xlsx"])

if f:
    try:
        # 1. 파일 내용을 텍스트로 강제 변환
        if f.name.endswith('.xlsx'):
            df = pd.read_excel(f)
        else:
            # 파일을 텍스트로 읽어서 쉼표 기준 데이터 추출
            content = f.read().decode('utf-8-sig', errors='ignore')
            lines = content.splitlines()
            
            # 숫자 데이터가 시작되는 행 찾기
            start_idx = 0
            for i, line in enumerate(lines):
                if any(k in line for k in ['노출', '클릭', '비용']):
                    start_idx = i
                    break
            
            # 추출된 라인으로 데이터프레임 강제 생성
            data = [line.split(',') for line in lines[start_idx:]]
            df = pd.DataFrame(data[1:], columns=[x.strip() for x in data[0]])

        # 2. 숫자만 남기기 (오류 방지 핵심)
        for col in df.columns:
            if col not in df.columns[0]:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0)
        
        # 3. 데이터 출력 및 합계
        st.subheader("📝 RAW 데이터 확인")
        st.dataframe(df.head(10), use_container_width=True)
        
        # 컬럼 매칭
        ki = next((c for c in df.columns if '노출' in c), df.columns[1])
        kc = next((c for c in df.columns if '클릭' in c), df.columns[2])
        ks = next((c for c in df.columns if any(k in c for k in ['비용', '소진', '지출'])), df.columns[3])
        
        ni, nc, ns = df[ki].sum(), df[kc].sum(), df[ks].sum()
        
        # 4. 결과 요약
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("노출수", f"{int(ni):,}회")
        c2.metric("클릭수", f"{int(nc):,}회")
        c3.metric("CTR", f"{(nc/ni*100 if ni>0 else 0):.2f}%")
        c4.metric("총 비용", f"{int(ns):,}원")
        
        st.info(f"분석 완료: 총 노출 {int(ni):,}회, 클릭 {int(nc):,}회 발생하였습니다.")

    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
