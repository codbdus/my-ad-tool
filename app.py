import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from io import BytesIO

# 웹사이트 제목 및 설명
st.set_page_config(page_title="광고 트래픽 분석기", layout="wide")
st.title("🔍 키워드 효율 시간대 분석 도구")
st.markdown("분석하고 싶은 키워드를 입력하면 **고효율 시간대**를 자동으로 찾아줍니다.")

# 사이드바: 키워드 입력창
with st.sidebar:
    st.header("설정")
    input_text = st.text_input("키워드를 입력하세요 (쉼표로 구분)", "탈모 샴푸, 두피 케어")
    keywords = [k.strip() for k in input_text.split(",")]
    run_button = st.button("분석 시작하기")

# 데이터 생성 로직 (샘플)
if run_button:
    st.subheader(f"📊 '{input_text}' 분석 결과")
    
    # 시간대 데이터 생성
    hours = [f"{h:02d}:00" for h in range(24)]
    weights = [0.01, 0.005, 0.004, 0.006, 0.01, 0.03, 0.05, 0.06, 0.06, 0.05, 0.06, 0.07, 0.06, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.08, 0.06, 0.04, 0.02, 0.01]
    
    all_data = []
    plt.figure(figsize=(10, 4))
    
    for kw in keywords:
        hourly_traffic = [int(1000 * w * random.uniform(0.8, 1.2)) for w in weights]
        all_data.append(hourly_traffic)
        plt.plot(hours, hourly_traffic, marker='o', label=kw)
    
    # 그래프 출력
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(plt)
    
    # 엑셀 다운로드 기능
    df = pd.DataFrame(all_data, index=keywords, columns=hours).T
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='분석결과')
    
    st.download_button(
        label="📄 분석 결과 엑셀 다운로드",
        data=output.getvalue(),
        file_name="keyword_analysis.xlsx",
        mime="application/vnd.ms-excel"
    )
    st.success("분석이 완료되었습니다! 위 버튼을 눌러 보고서를 다운로드하세요.")