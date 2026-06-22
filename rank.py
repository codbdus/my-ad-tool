import streamlit as st
import pandas as pd
import time
import hmac
import hashlib
import base64
import requests
from io import BytesIO

# 웹사이트 기본 설정
st.set_page_config(page_title="네이버 검색광고 대시보드 V6", layout="wide")
st.title("🚀 네이버 검색광고 공식 API 연동 모니터링 도구")
st.markdown("네이버 공식 API를 연결하여 차단 없이 **실시간 키워드 데이터 및 대시보드**를 조회합니다.")

# 사이드바 설정창
with st.sidebar:
    st.header("🔐 네이버 API 인증 정보")
    st.caption("네이버 검색광고 시스템 [도구 > SA API 사용 관리]에서 확인 가능합니다.")
    
    cust_id = st.text_input("1. CUSTOMER_ID (고객 ID)", type="password")
    api_key = st.text_input("2. API_KEY (라이선스 키)", type="password")
    secret_key = st.text_input("3. SECRET_KEY (비밀키)", type="password")
    
    st.divider()
    st.header("⚙️ 조회 설정")
    input_keywords = st.text_input("분석할 키워드 (쉼표로 구분)", "뷰티디바이스, 수분크림")
    run_button = st.button("📊 실시간 API 데이터 가져오기")

# 네이버 API용 정확한 암호화 헤더 생성 함수 (HMAC-SHA256)
def generate_signature(timestamp, method, uri, secret_key):
    # 네이버 API는 서비스 명칭을 포함한 전체 URI 경로로 서명해야 합니다.
    message = f"{timestamp}.{method}.{uri}"
    hash_result = hmac.new(
        bytes(secret_key, "utf-8"),
        bytes(message, "utf-8"),
        hashlib.sha256
    ).digest()
    return base64.b64encode(hash_result).decode("utf-8")

# 네이버 키워드 데이터 조회 함수 (404 해결 버전)
def get_keyword_stats(keywords_list, cust_id, api_key, secret_key):
    # 404의 원인: 키워드 통계(ncc) 서비스 경로를 정확히 명시해야 합니다.
    uri = "/ncc/keywordstats"
    method = "GET"
    
    # 쉼표로 연결된 키워드 문자열 생성
    kw_string = ",".join(keywords_list)
    
    # 네이버 공식 API 엔드포인트 통합 URL
    request_url = f"https://api.naver.com{uri}"
    
    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(timestamp, method, uri, secret_key)
    
    headers = {
        "X-Timestamp": timestamp,
        "X-API-KEY": api_key,
        "X-Customer": str(cust_id),
        "X-Signature": signature,
        "Content-Type": "application/json"
    }
    
    params = {
        "keywords": kw_string
    }
    
    try:
        res = requests.get(request_url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return pd.DataFrame(data.get("keywordList", []))
        else:
            st.error(f"❌ 네이버 API 통신 실패 (에러코드: {res.status_code})")
            st.caption(f"상세 에러 내용: {res.text}")
            return None
    except Exception as e:
        st.error(f"⚠️ 연결 중 오류 발생: {e}")
        return None

# 실행 버튼 클릭 시
if run_button:
    if not (cust_id and api_key and secret_key):
        st.error("⚠️ 네이버 API 인증 정보 3가지를 모두 입력해 주세요!")
    else:
        # 공백 제거 및 리스트화
        kw_list = [k.strip() for k in input_keywords.split(",")]
        
        with st.spinner("🔄 네이버 공식 광고 서버에서 데이터를 안전하게 가져오는 중..."):
            df_result = get_keyword_stats(kw_list, cust_id, api_key, secret_key)
            
        if df_result is not None and not df_result.empty:
            # 한글 컬럼명 매핑으로 가독성 확보
            df_result = df_result.rename(columns={
                'relKeyword': '키워드',
                'monthlyPcQcCnt': '월간 PC 검색수',
                'monthlyMobileQcCnt': '월간 모바일 검색수',
                'monthlyAvePcClkCnt': '월간 PC 평균 클릭수',
                'monthlyAveMobileClkCnt': '월간 모바일 평균 클릭수',
                'monthlyAvePcCtr': 'PC 평균 CTR (%)',
                'monthlyAveMobileCtr': '모바일 평균 CTR (%)'
            })
            
            st.subheader("📊 실시간 매체 데이터 대시보드")
            st.dataframe(df_result, use_container_width=True)
            
            # 퍼포먼스 마케터용 인사이트 자동 분석
            st.subheader("💡 채널별 타겟팅 가이드")
            for index, row in df_result.iterrows():
                kw = row["키워드"]
                
                # 데이터 변환 예외 처리
                try:
                    pc_search = int(str(row['월간 PC 검색수']).replace('<', '').replace(',', '').strip())
                except:
                    pc_search = 0
                try:
                    mo_search = int(str(row['월간 모바일 검색수']).replace('<', '').replace(',', '').strip())
                except:
                    mo_search = 0
                
                st.markdown(f"**📍 [{kw}] 매체 가치 분석**")
                if mo_search > pc_search * 3:
                    st.info(f"📱 모바일 검색 비중이 PC보다 **압도적으로 높습니다** (모바일 {mo_search:,}건 / PC {pc_search:,}건). 광고 예산 배정을 모바일에 80% 이상 집중하세요.")
                else:
                    st.success(f"🖥️ PC와 모바일 밸런스가 좋습니다 (모바일 {mo_search:,}건 / PC {pc_search:,}건). 두 매체 모두 모니터링이 필요합니다.")
                st.write("---")
                
            # 엑셀 다운로드
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_result.to_excel(writer, sheet_name='네이버_API_리포트', index=False)
                
            st.download_button(
                label="📄 API 원본 리포트 다운로드",
                data=output.getvalue(),
                file_name=f"naver_api_report_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.ms-excel"
            )
