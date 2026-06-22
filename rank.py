import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import BytesIO

# 웹사이트 기본 설정
st.set_page_config(page_title="브랜드 순위 추적기 V2", layout="wide")
st.title("🎯 네이버 PC/모바일 실시간 노출 순위 추적기")
st.markdown("입력하신 키워드로 네이버 PC와 모바일 검색 결과를 실시간 크롤링하여 자사 브랜드 노출 순위를 추적합니다.")

# 사이드바 설정창
with st.sidebar:
    st.header("⚙️ 설정")
    input_keywords = st.text_input("분석할 키워드 (쉼표로 구분)", "메디큐브, 뷰티디바이스, 수분크림")
    my_brand = st.text_input("우리 브랜드 이름 (체크용)", "메디큐브")
    run_button = st.button("🚀 실시간 크롤링 시작")

# 네이버 실시간 크롤링 함수
def fetch_naver_rank(keywords, brand_name):
    results = []
    bar = st.progress(0)
    status_text = st.empty()
    
    # 네이버 보안 장치를 우회하기 위한 기기 위장용 브라우저 정보 (User-Agent)
    headers_pc = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    headers_mobile = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    }

    for idx, kw in enumerate(keywords):
        status_text.text(f"🔍 '{kw}' 키워드 (PC & 모바일) 긁어오는 중... ({idx+1}/{len(keywords)})")
        
        # --- [1] PC 크롤링 ---
        pc_url = f"https://search.naver.com/search.naver?query={kw}"
        pc_rank = "미노출"
        try:
            res_pc = requests.get(pc_url, headers=headers_pc, timeout=5)
            soup_pc = BeautifulSoup(res_pc.text, "html.parser")
            
            # 네이버 PC 검색 결과 문서들의 타이틀이나 텍스트 영역 수집
            titles_pc = [t.text for t in soup_pc.select(".api_txt_lines, .lnk_tit, .total_tit, .sh_blog_title")]
            
            for i, title in enumerate(titles_pc[:15]): # 상위 15개 분석
                if brand_name.lower() in title.lower():
                    pc_rank = f"{i+1}위"
                    break
        except Exception as e:
            pc_rank = "오류 발생"
            
        time.sleep(0.5) # 네이버 차단 방지용 매너 타임
        
        # --- [2] 모바일 크롤링 ---
        mobile_url = f"https://m.search.naver.com/search.naver?query={kw}"
        mobile_rank = "미노출"
        try:
            res_mo = requests.get(mobile_url, headers=headers_mobile, timeout=5)
            soup_mo = BeautifulSoup(res_mo.text, "html.parser")
            
            # 네이버 모바일 검색 결과 타이틀 영역 수집
            titles_mo = [t.text for t in soup_mo.select(".api_txt_lines, .total_tit, .subject, .name")]
            
            for i, title in enumerate(titles_mo[:15]):
                if brand_name.lower() in title.lower():
                    mobile_rank = f"{i+1}위"
                    break
        except Exception as e:
            mobile_rank = "오류 발생"

        results.append({
            "키워드": kw,
            "🖥️ PC 자사 순위": pc_rank,
            "📱 모바일 자사 순위": mobile_rank,
            "조회 시간": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        bar.progress(int((idx + 1) / len(keywords) * 100))
        time.sleep(0.5)

    status_text.text("✅ 조회가 완료되었습니다!")
    return pd.DataFrame(results)

# 실행 버튼 클릭 시
if run_button:
    if not my_brand:
        st.error("⚠️ '우리 브랜드 이름'을 입력해 주세요!")
    else:
        kw_list = [k.strip() for k in input_keywords.split(",")]
        df_result = fetch_naver_rank(kw_list, my_brand)
        
        st.subheader("📊 실시간 PC/모바일 노출 순위")
        st.dataframe(df_result, use_container_width=True)
        
        # 마케터용 인사이트 자동 생성
        st.subheader("💡 채널별 매체 전략 제안")
        for index, row in df_result.iterrows():
            kw = row["키워드"]
            pc = row["🖥️ PC 자사 순위"]
            mo = row["📱 모바일 자사 순위"]
            
            st.markdown(f"**📍 [{kw}] 키워드 진단**")
            st.write(f"- PC: `{pc}` / 모바일: `{mo}`")
            
            if pc == "미노출" and mo == "미노출":
                st.error("⚠️ 양대 채널에서 모두 확인되지 않습니다. 브랜드 검색광고나 파워링크 입찰가 상향이 시급합니다.")
            elif pc != "미노출" and mo == "미노출":
                st.warning("⚡ PC에서는 보이나 모바일 유저들에게 소외되어 있습니다. 모바일 가중치 입찰가를 높이세요.")
            elif pc == "미노출" and mo != "미노출":
                st.info("ℹ️ 모바일 위주로 노출방어가 잘 되고 있습니다. 주 타겟이 직장인(PC 위주)인지 확인 후 PC 입찰 조정을 검토하세요.")
            else:
                st.success("🎉 대단합니다! PC와 모바일 모두 안정적으로 노출을 확보하고 있습니다.")
            st.write("---")
            
        # 엑셀 다운로드
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_result.to_excel(writer, sheet_name='실시간_순위', index=False)
            
        st.download_button(
            label="📄 PC/모바일 순위 리포트 다운로드",
            data=output.getvalue(),
            file_name=f"naver_cross_ranking_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )
