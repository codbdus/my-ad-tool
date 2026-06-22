import streamlit as st
import pandas as pd
import random
import time
from io import BytesIO

# 웹사이트 기본 설정
st.set_page_config(page_title="브랜드 순위 추적기", layout="wide")
st.title("🎯 키워드별 자사 노출 순위 모니터링 도구")
st.markdown("궁금한 키워드를 입력하고 우리 브랜드명을 넣으면, 현재 네이버에서 몇 순위에 노출되고 있는지 실시간 가상 시뮬레이션을 합니다.")

# 사이드바 설정창
with st.sidebar:
    st.header("⚙️ 설정")
    input_keywords = st.text_input("분석할 키워드 (쉼표로 구분)", "스킨케어, 수분크림, 선크림 추천")
    my_brand = st.text_input("우리 브랜드 이름 (체크용)", "우리브랜드")
    run_button = st.button("🚀 실시간 순위 조회 시작")

# 순위를 매기는 시뮬레이션 함수
def check_ranking_simulation(keywords, brand_name):
    results = []
    bar = st.progress(0)
    status_text = st.empty()
    
    for idx, kw in enumerate(keywords):
        status_text.text(f"🔍 '{kw}' 키워드 검색 순위 분석 중... ({idx+1}/{len(keywords)})")
        time.sleep(0.4)
        
        # 가상의 순위 데이터 생성
        current_rank = random.choice([1, 2, 3, 4, 5, "5위권 밖", "미노출"])
        competitors = ["경쟁사A", "경쟁사B", "경쟁사C", "블로그 영역", "쇼핑 영역"]
        
        if isinstance(current_rank, int):
            competitors.insert(current_rank - 1, f"⭐ {brand_name} (우리 브랜드)")
            
        results.append({
            "키워드": kw,
            "우리 브랜드 순위": f"{current_rank}위" if isinstance(current_rank, int) else current_rank,
            "1위 노출 영역": competitors[0],
            "2위 노출 영역": competitors[1],
            "3위 노출 영역": competitors[2],
            "조회 시간": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        bar.progress(int((idx + 1) / len(keywords) * 100))
        
    status_text.text("✅ 모든 키워드 조회가 완료되었습니다!")
    return pd.DataFrame(results)

# 실행 버튼 클릭 시
if run_button:
    if not my_brand:
        st.error("⚠️ '우리 브랜드 이름'을 입력해 주세요!")
    else:
        kw_list = [k.strip() for k in input_keywords.split(",")]
        df_result = check_ranking_simulation(kw_list, my_brand)
        
        st.subheader("📊 실시간 순위 모니터링 현황")
        st.dataframe(df_result, use_container_width=True)
        
        st.subheader("💡 마케터용 입찰 전략 제안")
        for index, row in df_result.iterrows():
            kw = row["키워드"]
            rank = row["우리 브랜드 순위"]
            
            if "1위" in rank or "2위" in rank:
                st.info(f"🟢 **[{kw}]** 현재 **{rank}**로 최상위권에 노출 중입니다. 불필요한 경쟁보다 순위 유지 비용을 체크하세요.")
            elif "3위" in rank or "4위" in rank or "5위" in rank:
                st.warning(f"🟡 **[{kw}]** 현재 **{rank}**에 위치해 있습니다. 상위권 진입을 위해 **입찰가를 5~10% 소폭 상향** 조정을 검토해 보세요.")
            else:
                st.error(f"🔴 **[{kw}]** 현재 **{rank}** 상태입니다. 순위가 크게 밀려 있으니 **입찰가를 과감하게 상향**하거나 키워드를 재점검해야 합니다.")
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_result.to_excel(writer, sheet_name='순위리포트', index=False)
            
        st.write("")
        st.download_button(
            label="📄 순위 분석 리포트(Excel) 다운로드",
            data=output.getvalue(),
            file_name=f"ranking_report_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )
