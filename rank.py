import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import BytesIO

# 웹사이트 기본 설정
st.set_page_config(page_title="네이버 광고 순위 추적기 V3", layout="wide")
st.title("🎯 네이버 파워링크/광고 실시간 노출 순위 추적기")
st.markdown("입력하신 키워드로 네이버 PC/모바일의 **최상단 광고 영역(파워링크, 브랜드검색 등)**을 실시간 크롤링하여 우리 광고의 노출 순위를 추적합니다.")

# 사이드바 설정창
with st.sidebar:
    st.header("⚙️ 설정")
    input_keywords = st.text_input("분석할 키워드 (쉼표로 구분)", "뷰티디바이스, 메디큐브, 수분크림")
    my_brand = st.text_input("우리 브랜드 이름 (체크용)", "메디큐브")
    run_button = st.button("🚀 실시간 광고 순위 조회")

# 네이버 광고 영역 크롤링 함수
def fetch_naver_ad_rank(keywords, brand_name):
    results = []
    bar = st.progress(0)
    status_text = st.empty()
    
    # 기기 위장용 헤더 설정
    headers_pc = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    headers_mobile = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    for idx, kw in enumerate(keywords):
        status_text.text(f"🔍 '{kw}' 광고 영역 분석 중... ({idx+1}/{len(keywords)})")
        
        # --- [1] PC 광고 크롤링 ---
        pc_url = f"https://search.naver.com/search.naver?query={kw}"
        pc_rank = "미노출"
        try:
            res_pc = requests.get(pc_url, headers=headers_pc, timeout=5)
            soup_pc = BeautifulSoup(res_pc.text, "html.parser")
            
            # 파워링크 광고 제목 및 브랜드검색 타이틀 태그 타겟팅
            # 네이버 PC 파워링크 타이틀(.lnk_tit), 브랜드검색(.title, .txt_box)
            ad_titles_pc = [t.text.strip() for t in soup_pc.select(".power_inner .lnk_tit, .nad_ad .lnk_tit, .ad_brand .title, .ad_brand .txt_box")]
            
            # 중복 제거 및 빈 텍스트 정리
            ad_titles_pc = [t for t in ad_titles_pc if t]
            
            for i, title in enumerate(ad_titles_pc[:10]):
                if brand_name.lower() in title.lower():
                    pc_rank = f"광고 {i+1}위"
                    break
        except Exception as e:
            pc_rank = "오류 발생"
            
        time.sleep(0.6) # 차단 방지 매너 타임
        
        # --- [2] 모바일 광고 크롤링 ---
        mobile_url = f"https://m.search.naver.com/search.naver?query={kw}"
        mobile_rank = "미노출"
        try:
            res_mo = requests.get(mobile_url, headers=headers_mobile, timeout=5)
            soup_mo = BeautifulSoup(res_mo.text, "html.parser")
            
            # 모바일 파워링크(.inner .name, .ad_tit) 및 브랜드검색 타겟팅
            ad_titles_mo = [t.text.strip() for t in soup_mo.select(".nad_ad .name, .nad_ad .ad_tit, .brand_search .title, .brand_search .txt_box")]
            ad_titles_mo = [t for t in ad_titles_mo if t]
            
            for i, title in enumerate(ad_titles_mo[:10]):
                if brand_name.lower() in title.lower():
                    mobile_rank = f"광고 {i+1}위"
                    break
        except Exception as e:
            mobile_rank = "오류 발생"

        results.append({
            "키워드": kw,
            "🖥️ PC 광고 순위": pc_rank,
            "📱 모바일 광고 순위": mobile_rank,
            "조회 시간": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        bar.progress(int((idx + 1) / len(keywords) * 100))
        time.sleep(0.6)

    status_text.text("✅ 광고 순위 조회가 완료되었습니다!")
    return pd.DataFrame(results)

# 실행 버튼 클릭 시
if run_button:
    if not my_brand:
        st.error("⚠️ '우리 브랜드 이름'을 입력해 주세요!")
    else:
        kw_list = [k.strip() for k in input_keywords.split(",")]
        df_result = fetch_naver_ad_rank(kw_list, my_brand)
        
        st.subheader("📊 실시간 광고(파워링크/브랜드검색) 노출 현황")
        st.dataframe(df_result, use_container_width=True)
        
        # 입찰가 조정을 위한 마케팅 액션 가이드
        st.subheader("💡 실시간 입찰가 조정 가이드")
        for index, row in df_result.iterrows():
            kw = row["키워드"]
            pc = row["🖥️ PC 광고 순위"]
            mo = row["📱 모바일 광고 순위"]
            
            st.markdown(f"**📍 [{kw}] 광고 전략 가이드**")
            
            if "1위" in mo or "2위" in mo:
                st.success(f"🟢 **모바일 {mo} 노출 중:** 최상위권을 잘 방어하고 있습니다. 현재 입찰가를 유지하며 CPC 비용 효율을 모니터링하세요.")
            elif "3위" in mo or "4위" in mo:
                st.warning(f"🟡 **모바일 {mo} 노출 중:** 경쟁사에 밀려 순위가 조금 떨어졌습니다. 노출 증대를 위해 **모바일 입찰가 가중치를 5~10% 상향**하는 것을 검토하세요.")
            elif mo == "미노출":
                st.error(f"🔴 **모바일 미노출:** 모바일 광고 탭(상위 10위 안)에서 우리 브랜드가 보이지 않습니다. **입찰가를 과감히 올리거나 순위 경쟁 재진입**이 필요합니다.")
                
            st.write("---")
            
        # 엑셀 다운로드
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_result.to_excel(writer, sheet_name='광고_순위_리포트', index=False)
            
        st.download_button(
            label="📄 광고 순위 리포트 다운로드",
            data=output.getvalue(),
            file_name=f"naver_ad_ranking_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd
